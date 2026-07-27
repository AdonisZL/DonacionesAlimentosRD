"""Servicio de derechos ARCO / ARCO 权利服务 (RN-19).

Lógica de negocio para crear, consultar y resolver solicitudes ARCO
conforme a la Ley 172-13 (respuesta en ≤ 15 días hábiles).
根据第 172-13 号法律处理 ARCO 请求的创建、查询和解决（≤ 15 个工作日响应）。
"""

import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.solicitud_arco import SolicitudArco
from app.models.usuario import Usuario
from app.schemas.arco import SolicitudArcoCrear

# RN-19: días hábiles para responder una solicitud ARCO
# ARCO 请求的响应工作日天数
DIAS_HABILES_RESPUESTA_ARCO = 15


def _calcular_fecha_limite(fecha_solicitud: date) -> date:
    """Calcula la fecha límite sumando días hábiles (solo excluye fines de semana).

    Calcula el plazo sumando días corridos y agregando 2 días extra por cada
    5 días hábiles para cubrir fines de semana.
    计算截止日期：加日历天数，每 5 个工作日额外加 2 天覆盖周末。
    """
    dias_extra_finde = (DIAS_HABILES_RESPUESTA_ARCO // 5) * 2
    dias_totales = DIAS_HABILES_RESPUESTA_ARCO + dias_extra_finde
    return fecha_solicitud + timedelta(days=dias_totales)


def crear_solicitud(
    sesion: Session,
    usuario: Usuario,
    datos: SolicitudArcoCrear,
) -> SolicitudArco:
    """Crea una nueva solicitud ARCO para el usuario / 为用户创建新的 ARCO 请求."""
    hoy = date.today()
    solicitud = SolicitudArco(
        id_usuario=usuario.id_usuario,
        tipo_solicitud=datos.tipo_solicitud,
        descripcion=datos.descripcion,
        estado="recibida",
        fecha_limite_respuesta=_calcular_fecha_limite(hoy),
    )
    sesion.add(solicitud)
    sesion.commit()
    sesion.refresh(solicitud)
    return solicitud


def mis_solicitudes(
    sesion: Session,
    usuario: Usuario,
) -> list[SolicitudArco]:
    """Devuelve todas las solicitudes ARCO del usuario / 返回用户的所有 ARCO 请求."""
    return list(
        sesion.execute(
            select(SolicitudArco)
            .where(SolicitudArco.id_usuario == usuario.id_usuario)
            .order_by(SolicitudArco.fecha_solicitud.desc())
        )
        .scalars()
        .all()
    )


def listar_todas(sesion: Session) -> list[SolicitudArco]:
    """Devuelve todas las solicitudes ARCO (solo admin) / 返回所有 ARCO 请求（仅管理员）."""
    return list(
        sesion.execute(
            select(SolicitudArco).order_by(SolicitudArco.fecha_solicitud.desc())
        )
        .scalars()
        .all()
    )


def resolver_solicitud(
    sesion: Session,
    id_solicitud: uuid.UUID,
    estado: str,
    respuesta: str,
    id_administrador: uuid.UUID,
) -> SolicitudArco:
    """Resuelve (aprueba/rechaza) una solicitud ARCO / 解决（批准/拒绝）ARCO 请求."""
    solicitud = sesion.get(SolicitudArco, id_solicitud)
    if solicitud is None:
        raise ValueError("Solicitud ARCO no encontrada.")

    if solicitud.estado in ("resuelta", "rechazada", "vencida"):
        raise ValueError(
            f"No se puede resolver una solicitud en estado '{solicitud.estado}'."
        )

    solicitud.estado = estado
    solicitud.respuesta = respuesta
    solicitud.atendido_por = id_administrador
    solicitud.fecha_resolucion = datetime.now(timezone.utc)
    sesion.commit()
    sesion.refresh(solicitud)
    return solicitud


def marcar_vencidas(sesion: Session) -> int:
    """Marca como vencidas las solicitudes cuya fecha límite ya pasó.

    Marca las solicitudes pendientes cuya fecha_limite_respuesta < hoy
    y que aún están en estado 'recibida' o 'en_proceso'.
    将已过截止日期且尚未解决的请求标记为已过期。
    """
    hoy = date.today()
    resultado = (
        sesion.query(SolicitudArco)
        .filter(
            SolicitudArco.estado.in_(["recibida", "en_proceso"]),
            SolicitudArco.fecha_limite_respuesta < hoy,
        )
        .update({"estado": "vencida"}, synchronize_session=False)
    )
    sesion.commit()
    return resultado
