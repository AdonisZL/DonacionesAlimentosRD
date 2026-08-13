"""Servicio de auditoría / 审计服务 (RF-29, Hallazgo 8).

Registra acciones sensibles en la bitácora inmutable (quién, qué, cuándo, IP)
y encadena cada registro con SHA-256 sobre el anterior para detectar
manipulaciones (no-repudio).
将敏感操作记入不可变审计日志（谁、做了什么、何时、IP），并用 SHA-256 与前一条
记录哈希链式连接，用于检测篡改（不可否认性）。
"""

import hashlib
import json
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bitacora_auditoria import BitacoraAuditoria


def _hash_registro(
    id_usuario: uuid.UUID | None,
    accion: str,
    entidad: str | None,
    detalles: dict | None,
    hash_anterior: str,
) -> str:
    """SHA-256(id_usuario||accion||entidad||detalles||hash_anterior), según el
    esquema documentado en el modelo BitacoraAuditoria / 按模型注释计算哈希."""
    base = "||".join(
        [
            str(id_usuario) if id_usuario else "",
            accion or "",
            entidad or "",
            json.dumps(detalles, sort_keys=True, default=str) if detalles else "",
            hash_anterior,
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def _ultimo_hash(sesion: Session) -> str:
    """Hash del último evento registrado (cadena) / 最近事件的哈希（链）."""
    ultimo = sesion.execute(
        select(BitacoraAuditoria.hash_actual)
        .order_by(BitacoraAuditoria.id_bitacora.desc())
        .limit(1)
    ).scalar_one_or_none()
    return ultimo or ""


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
    hash_anterior = _ultimo_hash(sesion)
    hash_actual = _hash_registro(id_usuario, accion, entidad, detalles, hash_anterior)
    sesion.add(
        BitacoraAuditoria(
            id_usuario=id_usuario,
            accion=accion,
            entidad_afectada=entidad,
            id_entidad_afectada=(str(id_entidad) if id_entidad is not None else None),
            detalles_antes_despues=detalles,
            ip_origen=ip_origen,
            hash_actual=hash_actual,
            hash_anterior=hash_anterior,
        )
    )
    if confirmar:
        sesion.commit()


def validar_integridad(sesion: Session, limite: int = 5000) -> dict:
    """Recalcula la cadena de hashes y detecta manipulaciones (Hallazgo 8).

    Nota: los eventos registrados antes de activar el hash-chaining tienen
    hash_actual="" y se reportan como "sin verificar" en vez de fallo.
    重新计算哈希链以检测篡改。启用哈希链之前的旧记录 hash_actual 为空，
    会标记为"未验证"而非"失败"。
    """
    eventos = (
        sesion.execute(
            select(BitacoraAuditoria)
            .order_by(BitacoraAuditoria.id_bitacora.asc())
            .limit(limite)
        )
        .scalars()
        .all()
    )

    hash_previo = ""
    verificados = 0
    sin_verificar = 0
    for evento in eventos:
        if not evento.hash_actual:
            sin_verificar += 1
            hash_previo = evento.hash_actual or ""
            continue
        esperado = _hash_registro(
            evento.id_usuario,
            evento.accion,
            evento.entidad_afectada,
            evento.detalles_antes_despues,
            hash_previo,
        )
        if evento.hash_actual != esperado:
            return {
                "integro": False,
                "id_bitacora_fallo": evento.id_bitacora,
                "revisados": verificados,
                "sin_verificar": sin_verificar,
            }
        hash_previo = evento.hash_actual
        verificados += 1

    return {
        "integro": True,
        "revisados": verificados,
        "sin_verificar": sin_verificar,
        "total": len(eventos),
    }


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
