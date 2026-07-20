"""Modelo de notificación / 通知模型 (RF-21).

Avisos en plataforma para donantes y receptores.
面向捐赠者与接收方的平台通知。
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base


class Notificacion(Base):
    """Tabla 'notificaciones' / 通知表."""

    __tablename__ = "notificaciones"

    id_notificacion = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    titulo = Column(String(150))
    mensaje = Column(Text)
    leido = Column(Boolean, default=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
