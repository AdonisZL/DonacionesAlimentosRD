"""Servicio de inventario / 库存服务 (OE2).

Lógica FEFO: registro de lotes, ventana de vencimiento, alertas, ajustes y
bitácora inmutable (RF-09 … RF-16).
FEFO 逻辑：批次登记、临期窗口、预警、调整与不可变日志。
"""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categoria_alimento import CategoriaAlimento
from app.models.categoria_perecibilidad import CategoriaPerecibilidad
from app.models.historial_estado_lote import HistorialEstadoLote
from app.models.lote_inventario import LoteInventario
from app.models.merma import Merma
from app.models.producto import Producto
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.schemas.inventario import AjusteInventario, LoteCrear, ProductoCrear
from app.services import servicio_auditoria

# RF-13: umbral de alerta de vencimiento (días) / 临期预警阈值（天）
DIAS_ALERTA_VENCIMIENTO = 3


def calcular_ventana(fecha_vencimiento: date) -> int:
    """Días restantes hasta el vencimiento (RF-11) / 距到期的剩余天数."""
    return (fecha_vencimiento - date.today()).days


def _es_banco(sesion: Session, usuario: Usuario) -> bool:
    """Indica si el usuario tiene rol 'banco_alimentos' / 是否为食物银行角色 (RF-15)."""
    rol = sesion.get(Rol, usuario.id_rol)
    return rol is not None and rol.nombre == "banco_alimentos"


# --- Catálogos / 目录 ------------------------------------------------------


def listar_categorias_alimentos(sesion: Session) -> list[CategoriaAlimento]:
    """Devuelve las categorías de alimentos / 返回食物分类."""
    return (
        sesion.execute(
            select(CategoriaAlimento).order_by(CategoriaAlimento.nombre_categoria)
        )
        .scalars()
        .all()
    )


def listar_categorias_perecibilidad(sesion: Session) -> list[CategoriaPerecibilidad]:
    """Devuelve las categorías de perecibilidad / 返回易腐性分类 (RF-10)."""
    return (
        sesion.execute(
            select(CategoriaPerecibilidad).order_by(
                CategoriaPerecibilidad.id_perecibilidad
            )
        )
        .scalars()
        .all()
    )


def listar_productos(sesion: Session) -> list[Producto]:
    """Devuelve los productos registrados / 返回已登记产品."""
    return (
        sesion.execute(select(Producto).order_by(Producto.nombre_producto))
        .scalars()
        .all()
    )


def crear_producto(sesion: Session, datos: ProductoCrear) -> Producto:
    """Crea un producto asociado a categoría y perecibilidad / 创建产品 (RF-09)."""
    if sesion.get(CategoriaAlimento, datos.id_categoria_alimento) is None:
        raise ValueError("La categoría de alimento no existe.")
    if sesion.get(CategoriaPerecibilidad, datos.id_perecibilidad) is None:
        raise ValueError("La categoría de perecibilidad no existe.")

    producto = Producto(
        id_categoria_alimento=datos.id_categoria_alimento,
        id_perecibilidad=datos.id_perecibilidad,
        nombre_producto=datos.nombre_producto,
        codigo_barra=datos.codigo_barra,
        descripcion=datos.descripcion,
        marca=datos.marca,
        unidad_predeterminada=datos.unidad_predeterminada,
    )
    sesion.add(producto)
    sesion.commit()
    sesion.refresh(producto)
    return producto


# --- Lotes / 批次 ----------------------------------------------------------


def registrar_lote(
    sesion: Session, usuario: Usuario, datos: LoteCrear
) -> LoteInventario:
    """Registra un lote de inventario / 登记库存批次 (RF-09, RF-11, RF-14)."""
    producto = sesion.get(Producto, datos.id_producto)
    if producto is None:
        raise ValueError("El producto indicado no existe.")

    # RF-14: rechazo automático si la ventana es <= 0 (ya vencido).
    ventana = calcular_ventana(datos.fecha_vencimiento)
    if ventana <= 0:
        raise ValueError(
            "El lote está vencido o vence hoy; no se puede registrar (RF-14)."
        )

    lote = LoteInventario(
        id_usuario=usuario.id_usuario,
        id_producto=datos.id_producto,
        id_sede=datos.id_sede,
        cantidad_disponible=datos.cantidad_disponible,
        unidad_medida=datos.unidad_medida or producto.unidad_predeterminada,
        peso_total=datos.peso_total,
        peso_disponible=datos.peso_total,
        fecha_produccion=datos.fecha_produccion,
        fecha_vencimiento=datos.fecha_vencimiento,
        temperatura_requerida=datos.temperatura_requerida,
        estado="disponible",
    )
    sesion.add(lote)
    sesion.flush()  # obtiene id_lote / 获取 id_lote

    # RF-16: bitácora inmutable del alta / 登记的不可变日志
    sesion.add(
        HistorialEstadoLote(
            id_usuario=usuario.id_usuario,
            id_lote=lote.id_lote,
            estado_anterior=None,
            estado_nuevo="disponible",
            motivo="Alta de lote",
        )
    )
    sesion.commit()
    sesion.refresh(lote)
    return lote


def _enriquecer_lote(sesion: Session, lote: LoteInventario) -> dict:
    """Añade producto, perecibilidad y datos FEFO al lote / 补充产品、易腐性与 FEFO 数据."""
    producto = sesion.get(Producto, lote.id_producto)
    perecibilidad = (
        sesion.get(CategoriaPerecibilidad, producto.id_perecibilidad)
        if producto
        else None
    )
    ventana = calcular_ventana(lote.fecha_vencimiento)
    dias_minimos = perecibilidad.dias_minimos_ventana if perecibilidad else None

    return {
        "id_lote": lote.id_lote,
        "id_usuario": lote.id_usuario,
        "id_producto": lote.id_producto,
        "id_sede": lote.id_sede,
        "cantidad_disponible": float(lote.cantidad_disponible),
        "unidad_medida": lote.unidad_medida,
        "peso_total": float(lote.peso_total) if lote.peso_total is not None else None,
        "fecha_produccion": lote.fecha_produccion,
        "fecha_vencimiento": lote.fecha_vencimiento,
        "temperatura_requerida": lote.temperatura_requerida,
        "estado": lote.estado,
        "creado_en": lote.creado_en,
        "nombre_producto": producto.nombre_producto if producto else None,
        "nombre_perecibilidad": perecibilidad.nombre if perecibilidad else None,
        "ventana_dias": ventana,
        "dias_minimos_ventana": dias_minimos,
        "en_alerta": 0 < ventana <= DIAS_ALERTA_VENCIMIENTO,
        "bajo_umbral": dias_minimos is not None and ventana < dias_minimos,
    }


def listar_lotes(
    sesion: Session, usuario: Usuario, solo_propios: bool = True
) -> list[dict]:
    """Lista lotes ordenados FEFO (vencimiento ascendente) / 按 FEFO 排序 (RF-12)."""
    consulta = select(LoteInventario).order_by(LoteInventario.fecha_vencimiento.asc())
    if solo_propios:
        consulta = consulta.where(LoteInventario.id_usuario == usuario.id_usuario)
    lotes = sesion.execute(consulta).scalars().all()
    return [_enriquecer_lote(sesion, lote) for lote in lotes]


def listar_alertas(sesion: Session, usuario: Usuario) -> list[dict]:
    """Lotes disponibles con vencimiento <= 3 días / 临期（<=3天）批次 (RF-13)."""
    lotes = listar_lotes(sesion, usuario, solo_propios=True)
    return [
        lote for lote in lotes if lote["estado"] == "disponible" and lote["en_alerta"]
    ]


def obtener_lote(sesion: Session, id_lote: uuid.UUID) -> LoteInventario | None:
    """Recupera un lote por su id / 按 id 获取批次."""
    return sesion.get(LoteInventario, id_lote)


def obtener_historial(sesion: Session, id_lote: uuid.UUID) -> list[HistorialEstadoLote]:
    """Historial inmutable de un lote / 批次的不可变历史 (RF-16)."""
    return (
        sesion.execute(
            select(HistorialEstadoLote)
            .where(HistorialEstadoLote.id_lote == id_lote)
            .order_by(HistorialEstadoLote.fecha.asc())
        )
        .scalars()
        .all()
    )


def ajustar_inventario(
    sesion: Session,
    usuario: Usuario,
    id_lote: uuid.UUID,
    datos: AjusteInventario,
) -> LoteInventario:
    """Ajuste manual de inventario con merma y bitácora / 手动调整库存 (RF-15, RF-16)."""
    if not _es_banco(sesion, usuario):
        raise PermissionError(
            "Solo un banco de alimentos puede ajustar el inventario (RF-15)."
        )

    lote = sesion.get(LoteInventario, id_lote)
    if lote is None:
        raise ValueError("El lote indicado no existe.")

    cantidad_actual = float(lote.cantidad_disponible)
    if datos.cantidad_afectada > cantidad_actual:
        raise ValueError(
            "La cantidad afectada no puede superar la cantidad disponible."
        )

    estado_anterior = lote.estado
    nueva_cantidad = cantidad_actual - datos.cantidad_afectada
    lote.cantidad_disponible = nueva_cantidad
    if nueva_cantidad == 0:
        lote.estado = "retirado"

    # RF-15: registrar la merma con su motivo obligatorio / 记录必填原因的损耗
    sesion.add(
        Merma(
            id_lote=lote.id_lote,
            id_usuario_responsable=usuario.id_usuario,
            motivo=datos.motivo,
            detalle=datos.detalle,
            cantidad_afectada=datos.cantidad_afectada,
            unidad_medida=lote.unidad_medida,
        )
    )

    # RF-16: bitácora inmutable del ajuste / 调整的不可变日志
    sesion.add(
        HistorialEstadoLote(
            id_usuario=usuario.id_usuario,
            id_lote=lote.id_lote,
            estado_anterior=estado_anterior,
            estado_nuevo=lote.estado,
            motivo=(
                f"Ajuste ({datos.motivo}): -{datos.cantidad_afectada} "
                f"{lote.unidad_medida or ''}".strip()
            ),
        )
    )
    # RF-29: auditoría del ajuste manual de inventario.
    servicio_auditoria.registrar(
        sesion,
        accion="ajuste_inventario",
        id_usuario=usuario.id_usuario,
        entidad="lotes_inventario",
        id_entidad=lote.id_lote,
        detalles={
            "motivo": datos.motivo,
            "cantidad_afectada": datos.cantidad_afectada,
        },
        confirmar=False,
    )
    sesion.commit()
    sesion.refresh(lote)
    return lote
