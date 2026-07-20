"""Modelo de bitácora de auditoría / 审计日志模型 (RF-29).

Registro inmutable de acciones sensibles: quién, qué, cuándo e IP de origen.
敏感操作的不可变记录：谁、做了什么、何时、来源 IP。
"""

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.sql import func

from app.database.conexion import Base


class BitacoraAuditoria(Base):
    """Tabla 'bitacora_auditoria' / 审计日志表."""

    __tablename__ = "bitacora_auditoria"

    id_bitacora = Column(BigInteger, primary_key=True, autoincrement=True)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"))
    accion = Column(String(50), nullable=False)
    entidad_afectada = Column(String(50))
    id_entidad_afectada = Column(String(100))
    detalles_antes_despues = Column(JSONB)
    ip_origen = Column(INET)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
