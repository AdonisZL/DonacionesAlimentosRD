"""Servicio de emparejamiento / 匹配服务 (OE3, RF-17 … RF-22).

Búsqueda geográfica (PostGIS) de receptores compatibles, creación de matches
con justificación de IA (simulada), confirmación, rechazo/reasignación,
notificaciones y retroalimentación.
基于 PostGIS 的兼容接收方搜索、匹配创建（含模拟 AI 说明）、确认、拒绝/重分配、通知与反馈。
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.categoria_alimento import CategoriaAlimento
from app.models.direccion_sede import DireccionSede
from app.models.emparejamiento import Emparejamiento
from app.models.entrega_transaccion import EntregaTransaccion
from app.models.ia_ejecucion import IaEjecucion
from app.models.lote_inventario import LoteInventario
from app.models.notificacion import Notificacion
from app.models.producto import Producto
from app.models.retroalimentacion import Retroalimentacion
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.schemas.emparejamiento import RetroalimentacionCrear
from app.services import servicio_ia

# RN-12: retiro máximo 48 horas tras confirmar / 确认后最长 48 小时取货
HORAS_LIMITE_RETIRO = 48


def _requiere_cadena_frio(sesion: Session, id_producto: int) -> bool:
    """Indica si el producto requiere cadena de frío / 产品是否需要冷链 (RN-07)."""
    producto = sesion.get(Producto, id_producto)
    if producto is None:
        return False
    categoria = sesion.get(CategoriaAlimento, producto.id_categoria_alimento)
    return bool(categoria and categoria.requiere_cadena_frio)


def _obtener_sede_origen(sesion: Session, lote: LoteInventario) -> DireccionSede | None:
    """Sede de origen del lote (propia o del dueño) / 批次来源场所."""
    if lote.id_sede:
        sede = sesion.get(DireccionSede, lote.id_sede)
        if sede is not None:
            return sede
    return (
        sesion.execute(
            select(DireccionSede).where(DireccionSede.id_usuario == lote.id_usuario)
        )
        .scalars()
        .first()
    )


def buscar_candidatos(
    sesion: Session, usuario: Usuario, id_lote: uuid.UUID, radio_km: float
) -> list[dict]:
    """Busca receptores compatibles dentro del radio (RF-17/18) / 搜索半径内的兼容接收方."""
    lote = sesion.get(LoteInventario, id_lote)
    if lote is None:
        raise ValueError("El lote indicado no existe.")
    if lote.id_usuario != usuario.id_usuario:
        raise PermissionError("Solo puedes emparejar tus propios lotes.")

    sede_origen = _obtener_sede_origen(sesion, lote)
    if sede_origen is None:
        raise ValueError(
            "El lote no tiene una sede con ubicación. Registra una sede con "
            "coordenadas para poder buscar receptores."
        )

    producto = sesion.get(Producto, lote.id_producto)
    nombre_producto = producto.nombre_producto if producto else "Lote"
    requiere_frio = _requiere_cadena_frio(sesion, lote.id_producto)
    peso = float(lote.peso_total) if lote.peso_total is not None else None

    radio_m = radio_km * 1000
    distancia_km = (
        func.ST_Distance(DireccionSede.coordenadas, sede_origen.coordenadas) / 1000.0
    ).label("distancia_km")

    consulta = (
        select(DireccionSede, Usuario, distancia_km)
        .join(Usuario, Usuario.id_usuario == DireccionSede.id_usuario)
        .join(Rol, Rol.id_rol == Usuario.id_rol)
        .where(Rol.nombre.in_(("receptor", "banco_alimentos")))
        .where(Usuario.estado == "activo")
        .where(DireccionSede.id_usuario != lote.id_usuario)
        .where(
            func.ST_DWithin(DireccionSede.coordenadas, sede_origen.coordenadas, radio_m)
        )
        .order_by(distancia_km)
    )

    candidatos: list[dict] = []
    for sede, _dueno, dist in sesion.execute(consulta).all():
        dist_km = round(float(dist), 2)
        cap = (
            float(sede.capacidad_diaria_kg)
            if sede.capacidad_diaria_kg is not None
            else None
        )
        compatible = True
        motivo = None
        if requiere_frio and not sede.tiene_cadena_frio:
            compatible = False
            motivo = "La sede no dispone de cadena de frío requerida."
        elif peso is not None and cap is not None and peso > cap:
            compatible = False
            motivo = "El peso del lote supera la capacidad diaria de la sede."

        ia = servicio_ia.generar_justificacion(
            nombre_producto=nombre_producto,
            nombre_sede=sede.nombre_sede or "sede receptora",
            distancia_km=dist_km,
            radio_km=radio_km,
            requiere_cadena_frio=requiere_frio,
            tiene_cadena_frio=bool(sede.tiene_cadena_frio),
            capacidad_diaria_kg=cap,
        )

        candidatos.append(
            {
                "id_sede": sede.id_sede,
                "id_usuario": sede.id_usuario,
                "nombre_sede": sede.nombre_sede,
                "direccion_texto": sede.direccion_texto,
                "distancia_km": dist_km,
                "tiene_cadena_frio": bool(sede.tiene_cadena_frio),
                "capacidad_diaria_kg": cap,
                "compatible": compatible,
                "motivo_incompatible": motivo,
                "justificacion_ia": ia["respuesta"],
            }
        )
    return candidatos


def crear_emparejamiento(
    sesion: Session,
    usuario: Usuario,
    id_lote: uuid.UUID,
    id_sede: uuid.UUID,
    radio_km: float,
) -> Emparejamiento:
    """Crea un match sugerido con justificación de IA / 创建建议匹配 (RF-17/18)."""
    lote = sesion.get(LoteInventario, id_lote)
    if lote is None:
        raise ValueError("El lote indicado no existe.")
    if lote.id_usuario != usuario.id_usuario:
        raise PermissionError("Solo puedes emparejar tus propios lotes.")
    if lote.estado != "disponible":
        raise ValueError("El lote no está disponible para emparejar.")

    sede = sesion.get(DireccionSede, id_sede)
    if sede is None:
        raise ValueError("La sede receptora no existe.")
    sede_origen = _obtener_sede_origen(sesion, lote)
    if sede_origen is None:
        raise ValueError("El lote no tiene una sede de origen con ubicación.")

    requiere_frio = _requiere_cadena_frio(sesion, lote.id_producto)
    if requiere_frio and not sede.tiene_cadena_frio:
        raise ValueError(
            "El lote requiere cadena de frío y la sede seleccionada no la tiene (RN-07)."
        )

    # Distancia real con PostGIS / 用 PostGIS 计算实际距离
    dist_m = sesion.execute(
        select(
            func.ST_Distance(DireccionSede.coordenadas, sede_origen.coordenadas)
        ).where(DireccionSede.id_sede == id_sede)
    ).scalar_one()
    dist_km = round(float(dist_m) / 1000.0, 2)
    if dist_km > 75:
        raise ValueError("La sede está fuera del radio máximo permitido (75 km).")

    emparejamiento = Emparejamiento(
        id_lote=id_lote,
        id_sede=id_sede,
        distancia_km=dist_km,
        estado_tramite="sugerido",
    )
    sesion.add(emparejamiento)
    sesion.flush()

    # RF-18: registrar la justificación de la IA (simulada) / 记录模拟 AI 说明
    producto = sesion.get(Producto, lote.id_producto)
    ia = servicio_ia.generar_justificacion(
        nombre_producto=producto.nombre_producto if producto else "Lote",
        nombre_sede=sede.nombre_sede or "sede receptora",
        distancia_km=dist_km,
        radio_km=radio_km,
        requiere_cadena_frio=requiere_frio,
        tiene_cadena_frio=bool(sede.tiene_cadena_frio),
        capacidad_diaria_kg=(
            float(sede.capacidad_diaria_kg)
            if sede.capacidad_diaria_kg is not None
            else None
        ),
    )
    sesion.add(
        IaEjecucion(
            id_emparejamiento=emparejamiento.id_emparejamiento,
            tipo_ejecucion="justificacion_narrativa",
            prompt=ia["prompt"],
            respuesta=ia["respuesta"],
            modelo=ia["modelo"],
            tokens_usados=ia["tokens_usados"],
            confianza=ia["confianza"],
        )
    )
    sesion.commit()
    sesion.refresh(emparejamiento)
    return emparejamiento


def _justificacion_de(sesion: Session, id_emparejamiento: uuid.UUID) -> str | None:
    """Última justificación de IA del match / 匹配的最新 AI 说明."""
    ia = (
        sesion.execute(
            select(IaEjecucion)
            .where(IaEjecucion.id_emparejamiento == id_emparejamiento)
            .where(IaEjecucion.tipo_ejecucion == "justificacion_narrativa")
            .order_by(IaEjecucion.creado_en.desc())
        )
        .scalars()
        .first()
    )
    return ia.respuesta if ia else None


def _enriquecer(sesion: Session, emp: Emparejamiento) -> dict:
    """Añade producto, sede y justificación al match / 补充产品、场所与说明."""
    lote = sesion.get(LoteInventario, emp.id_lote)
    producto = sesion.get(Producto, lote.id_producto) if lote else None
    sede = sesion.get(DireccionSede, emp.id_sede)
    return {
        "id_emparejamiento": emp.id_emparejamiento,
        "id_lote": emp.id_lote,
        "id_sede": emp.id_sede,
        "distancia_km": float(emp.distancia_km),
        "estado_tramite": emp.estado_tramite,
        "fecha_limite_retiro": emp.fecha_limite_retiro,
        "creado_en": emp.creado_en,
        "nombre_producto": producto.nombre_producto if producto else None,
        "nombre_sede": sede.nombre_sede if sede else None,
        "justificacion_ia": _justificacion_de(sesion, emp.id_emparejamiento),
    }


def listar_emparejamientos(sesion: Session, usuario: Usuario) -> list[dict]:
    """Lista los matches del usuario (como donante o receptor) / 列出用户的匹配."""
    # Matches de mis lotes / 我的批次的匹配
    consulta = (
        select(Emparejamiento)
        .join(LoteInventario, LoteInventario.id_lote == Emparejamiento.id_lote)
        .join(DireccionSede, DireccionSede.id_sede == Emparejamiento.id_sede)
        .where(
            (LoteInventario.id_usuario == usuario.id_usuario)
            | (DireccionSede.id_usuario == usuario.id_usuario)
        )
        .order_by(Emparejamiento.creado_en.desc())
    )
    emps = sesion.execute(consulta).scalars().all()
    return [_enriquecer(sesion, emp) for emp in emps]


def _crear_notificacion(
    sesion: Session, id_usuario: uuid.UUID, titulo: str, mensaje: str
) -> None:
    """Crea una notificación en plataforma / 创建平台通知 (RF-21)."""
    sesion.add(Notificacion(id_usuario=id_usuario, titulo=titulo, mensaje=mensaje))


def confirmar_emparejamiento(
    sesion: Session, usuario: Usuario, id_emparejamiento: uuid.UUID
) -> Emparejamiento:
    """Confirma el match y notifica a ambas partes / 确认匹配并通知双方 (RF-19/21)."""
    emp = sesion.get(Emparejamiento, id_emparejamiento)
    if emp is None:
        raise ValueError("El emparejamiento no existe.")
    if emp.estado_tramite != "sugerido":
        raise ValueError("Solo se pueden confirmar emparejamientos sugeridos.")

    lote = sesion.get(LoteInventario, emp.id_lote)
    sede = sesion.get(DireccionSede, emp.id_sede)
    # Confirmación por el donante (dueño del lote) o el receptor de la sede.
    if usuario.id_usuario not in (lote.id_usuario, sede.id_usuario):
        raise PermissionError("No tienes permiso sobre este emparejamiento.")

    emp.estado_tramite = "confirmado"
    emp.fecha_limite_retiro = datetime.now(timezone.utc) + timedelta(
        hours=HORAS_LIMITE_RETIRO
    )
    lote.estado = "reservado"

    producto = sesion.get(Producto, lote.id_producto)
    nombre = producto.nombre_producto if producto else "el lote"
    _crear_notificacion(
        sesion,
        lote.id_usuario,
        "Emparejamiento confirmado",
        f"Tu lote «{nombre}» fue confirmado con «{sede.nombre_sede}». "
        f"Retiro antes de {emp.fecha_limite_retiro:%Y-%m-%d %H:%M}.",
    )
    _crear_notificacion(
        sesion,
        sede.id_usuario,
        "Emparejamiento confirmado",
        f"Se te asignó «{nombre}». Coordina el retiro antes de "
        f"{emp.fecha_limite_retiro:%Y-%m-%d %H:%M}.",
    )
    sesion.commit()
    sesion.refresh(emp)
    return emp


def rechazar_emparejamiento(
    sesion: Session, usuario: Usuario, id_emparejamiento: uuid.UUID
) -> Emparejamiento:
    """Rechaza el match y libera el lote para reasignar / 拒绝并释放批次 (RF-20)."""
    emp = sesion.get(Emparejamiento, id_emparejamiento)
    if emp is None:
        raise ValueError("El emparejamiento no existe.")
    if emp.estado_tramite not in ("sugerido", "confirmado"):
        raise ValueError("Este emparejamiento no se puede rechazar.")

    lote = sesion.get(LoteInventario, emp.id_lote)
    sede = sesion.get(DireccionSede, emp.id_sede)
    if usuario.id_usuario not in (lote.id_usuario, sede.id_usuario):
        raise PermissionError("No tienes permiso sobre este emparejamiento.")

    emp.estado_tramite = "rechazado"
    # RF-20: el lote vuelve a estar disponible para un nuevo emparejamiento.
    if lote.estado in ("reservado", "asignado"):
        lote.estado = "disponible"
    _crear_notificacion(
        sesion,
        lote.id_usuario,
        "Emparejamiento rechazado",
        "El emparejamiento fue rechazado; el lote está disponible de nuevo.",
    )
    sesion.commit()
    sesion.refresh(emp)
    return emp


def completar_emparejamiento(
    sesion: Session, usuario: Usuario, id_emparejamiento: uuid.UUID
) -> EntregaTransaccion:
    """Marca el match como completado y crea la entrega / 完成匹配并创建交付."""
    emp = sesion.get(Emparejamiento, id_emparejamiento)
    if emp is None:
        raise ValueError("El emparejamiento no existe.")
    if emp.estado_tramite != "confirmado":
        raise ValueError("Solo se completan emparejamientos confirmados.")

    lote = sesion.get(LoteInventario, emp.id_lote)
    sede = sesion.get(DireccionSede, emp.id_sede)
    if usuario.id_usuario not in (lote.id_usuario, sede.id_usuario):
        raise PermissionError("No tienes permiso sobre este emparejamiento.")

    emp.estado_tramite = "completado"
    lote.estado = "entregado"
    entrega = EntregaTransaccion(
        id_emparejamiento=emp.id_emparejamiento,
        estado_entrega="completada",
        fecha_completado=datetime.now(timezone.utc),
    )
    sesion.add(entrega)
    sesion.commit()
    sesion.refresh(entrega)
    return entrega


def crear_retroalimentacion(
    sesion: Session,
    usuario: Usuario,
    id_emparejamiento: uuid.UUID,
    datos: RetroalimentacionCrear,
) -> Retroalimentacion:
    """Registra la calificación de una entrega completada / 记录评分 (RF-22)."""
    emp = sesion.get(Emparejamiento, id_emparejamiento)
    if emp is None:
        raise ValueError("El emparejamiento no existe.")
    entrega = (
        sesion.execute(
            select(EntregaTransaccion).where(
                EntregaTransaccion.id_emparejamiento == id_emparejamiento
            )
        )
        .scalars()
        .first()
    )
    if entrega is None:
        raise ValueError("La entrega aún no está registrada (completa el match).")

    retro = Retroalimentacion(
        id_entrega=entrega.id_entrega,
        id_usuario=usuario.id_usuario,
        calificacion=datos.calificacion,
        comentario=datos.comentario,
    )
    sesion.add(retro)
    sesion.commit()
    sesion.refresh(retro)
    return retro


# --- Notificaciones / 通知 -------------------------------------------------


def listar_notificaciones(sesion: Session, usuario: Usuario) -> list[Notificacion]:
    """Notificaciones del usuario / 用户通知 (RF-21)."""
    return (
        sesion.execute(
            select(Notificacion)
            .where(Notificacion.id_usuario == usuario.id_usuario)
            .order_by(Notificacion.creado_en.desc())
        )
        .scalars()
        .all()
    )


def marcar_notificacion_leida(
    sesion: Session, usuario: Usuario, id_notificacion: uuid.UUID
) -> Notificacion:
    """Marca una notificación como leída / 将通知标记为已读."""
    noti = sesion.get(Notificacion, id_notificacion)
    if noti is None or noti.id_usuario != usuario.id_usuario:
        raise ValueError("Notificación no encontrada.")
    noti.leido = True
    sesion.commit()
    sesion.refresh(noti)
    return noti
