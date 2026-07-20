"""Servicio de administración / 管理服务 (OE5, RF-32).

Métricas del panel administrativo, gestión de usuarios y consulta de auditoría.
管理面板指标、用户管理与审计查询。
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.categoria_perecibilidad import CategoriaPerecibilidad
from app.models.emparejamiento import Emparejamiento
from app.models.lote_inventario import LoteInventario
from app.models.producto import Producto
from app.models.rol import Rol
from app.models.usuario import Usuario

ESTADOS_USUARIO = ("activo", "inactivo", "suspendido")


def metricas_panel(sesion: Session) -> dict:
    """Indicadores clave para el panel administrativo / 管理面板关键指标 (RF-32)."""
    # Kg rescatados: peso de lotes entregados / 已交付批次的重量
    kg_rescatados = sesion.execute(
        select(func.coalesce(func.sum(LoteInventario.peso_total), 0)).where(
            LoteInventario.estado == "entregado"
        )
    ).scalar_one()

    # Tasa de efectividad: emparejamientos completados / total / 匹配完成率
    total_emp = sesion.execute(
        select(func.count(Emparejamiento.id_emparejamiento))
    ).scalar_one()
    completados = sesion.execute(
        select(func.count(Emparejamiento.id_emparejamiento)).where(
            Emparejamiento.estado_tramite == "completado"
        )
    ).scalar_one()
    tasa_efectividad = round((completados / total_emp * 100) if total_emp else 0, 1)

    # Distribución por perecibilidad (nº de lotes) / 按易腐性分布
    filas = sesion.execute(
        select(
            CategoriaPerecibilidad.nombre,
            func.count(LoteInventario.id_lote),
        )
        .select_from(LoteInventario)
        .join(Producto, Producto.id_producto == LoteInventario.id_producto)
        .join(
            CategoriaPerecibilidad,
            CategoriaPerecibilidad.id_perecibilidad == Producto.id_perecibilidad,
        )
        .group_by(CategoriaPerecibilidad.nombre)
    ).all()
    distribucion_perecibilidad = {nombre: int(n) for nombre, n in filas}

    # Usuarios por rol / 按角色统计用户
    filas_rol = sesion.execute(
        select(Rol.nombre, func.count(Usuario.id_usuario))
        .select_from(Usuario)
        .join(Rol, Rol.id_rol == Usuario.id_rol)
        .group_by(Rol.nombre)
    ).all()
    usuarios_por_rol = {nombre: int(n) for nombre, n in filas_rol}

    # Lotes por estado / 按状态统计批次
    filas_estado = sesion.execute(
        select(LoteInventario.estado, func.count(LoteInventario.id_lote)).group_by(
            LoteInventario.estado
        )
    ).all()
    lotes_por_estado = {estado: int(n) for estado, n in filas_estado}

    return {
        "kg_rescatados": float(kg_rescatados or 0),
        "tasa_efectividad": tasa_efectividad,
        "total_emparejamientos": int(total_emp),
        "emparejamientos_completados": int(completados),
        "distribucion_perecibilidad": distribucion_perecibilidad,
        "usuarios_por_rol": usuarios_por_rol,
        "lotes_por_estado": lotes_por_estado,
    }


def listar_usuarios(sesion: Session) -> list[dict]:
    """Lista de usuarios con su rol / 用户列表（含角色）."""
    filas = sesion.execute(
        select(Usuario, Rol.nombre)
        .join(Rol, Rol.id_rol == Usuario.id_rol)
        .order_by(Usuario.creado_en.desc())
    ).all()
    return [
        {
            "id_usuario": u.id_usuario,
            "nombre": f"{u.nombre} {u.apellido or ''}".strip(),
            "email": u.email,
            "rol": nombre_rol,
            "estado": u.estado,
            "email_verificado": u.email_verificado,
            "creado_en": u.creado_en,
        }
        for u, nombre_rol in filas
    ]


def cambiar_estado_usuario(
    sesion: Session, id_usuario: uuid.UUID, nuevo_estado: str
) -> Usuario:
    """Cambia el estado de una cuenta / 修改账号状态 (activo/inactivo/suspendido)."""
    if nuevo_estado not in ESTADOS_USUARIO:
        raise ValueError(f"Estado inválido. Use uno de: {', '.join(ESTADOS_USUARIO)}.")
    usuario = sesion.get(Usuario, id_usuario)
    if usuario is None:
        raise ValueError("Usuario no encontrado.")
    usuario.estado = nuevo_estado
    if nuevo_estado == "activo":
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
    sesion.commit()
    sesion.refresh(usuario)
    return usuario
