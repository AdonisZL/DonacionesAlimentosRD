"""Modelo de retroalimentación / 反馈模型 (RF-22).

Calificación (1–5) y comentario sobre una entrega completada.
对已完成交付的评分（1–5）与评论。
"""

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    SmallInteger,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base


class Retroalimentacion(Base):
    """Tabla 'retroalimentacion' / 反馈表."""

    __tablename__ = "retroalimentacion"

    id_retroalimentacion = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    id_entrega = Column(
        UUID(as_uuid=True),
        ForeignKey("entregas_transacciones.id_entrega"),
        nullable=False,
    )
    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    calificacion = Column(SmallInteger, nullable=False)
    comentario = Column(Text)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("calificacion BETWEEN 1 AND 5", name="chk_calificacion_rango"),
    )
