"""Modelo de historial de estado de lote / 批次状态历史模型 (RF-16).

Bitácora inmutable: cada cambio de estado o cantidad deja un registro.
不可变日志：每次状态或数量变更都留下记录。
"""

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base


class HistorialEstadoLote(Base):
    """Tabla 'historial_estado_lote' / 批次状态历史表."""

    __tablename__ = "historial_estado_lote"

    id_historial = Column(BigInteger, primary_key=True, autoincrement=True)
    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    id_lote = Column(
        UUID(as_uuid=True), ForeignKey("lotes_inventario.id_lote"), nullable=False
    )
    estado_anterior = Column(String(20))
    estado_nuevo = Column(String(20), nullable=False)
    motivo = Column(Text)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
