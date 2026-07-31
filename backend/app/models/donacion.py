"""Modelo de donación / 捐赠模型 (RF-07, RF-08).

Registra cada entrega de alimentos por un donante.
记录捐赠者每次的食物捐赠。
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base


class Donacion(Base):
    """Tabla 'donaciones' / 捐赠表."""

    __tablename__ = "donaciones"

    id_donacion = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    fecha_donacion = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    comprobante_url = Column(String(255))
    observaciones = Column(Text)
    creado_en = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
