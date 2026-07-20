"""Servicio de auditoría / 审计服务 (RF-29).

Registra acciones sensibles en la bitácora inmutable (quién, qué, cuándo, IP).
将敏感操作记入不可变审计日志（谁、做了什么、何时、IP）。
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bitacora_auditoria import BitacoraAuditoria


def registrar(
    sesion: Session,
    accion: str,
    id_usuario: uuid.UUID | None = None,
    entidad: str | None = None,
    id_entidad: str | None = None,
    detalles: dict | None = None,
    ip_origen: str | None = None,
    confirmar: bool = True,
) -> None:
    """Añade un registro a la bitácora de auditoría / 写入审计日志.

    Si `confirmar` es False, no hace commit (para incluirse en otra transacción).
    若 `confirmar` 为 False，则不提交（以并入其他事务）。
    """
    sesion.add(
        BitacoraAuditoria(
            id_usuario=id_usuario,
            accion=accion,
            entidad_afectada=entidad,
            id_entidad_afectada=(str(id_entidad) if id_entidad is not None else None),
            detalles_antes_despues=detalles,
            ip_origen=ip_origen,
        )
    )
    if confirmar:
        sesion.commit()


def listar(sesion: Session, limite: int = 100) -> list[BitacoraAuditoria]:
    """Devuelve los eventos de auditoría más recientes / 返回最近的审计事件."""
    return (
        sesion.execute(
            select(BitacoraAuditoria)
            .order_by(BitacoraAuditoria.creado_en.desc())
            .limit(limite)
        )
        .scalars()
        .all()
    )
