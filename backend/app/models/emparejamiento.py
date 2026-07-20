"""Modelo de emparejamiento / 匹配模型 (OE3, RF-17 … RF-21).

Relaciona un lote con la sede de un receptor y su estado de trámite.
将批次与接收方场所关联，并记录其流转状态。
"""

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base

# Estados del trámite del emparejamiento / 匹配流转状态
ESTADOS_TRAMITE = (
    "sugerido",
    "confirmado",
    "rechazado",
    "expirado",
    "completado",
)


class Emparejamiento(Base):
    """Tabla 'emparejamientos' / 匹配表."""

    __tablename__ = "emparejamientos"

    id_emparejamiento = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_lote = Column(
        UUID(as_uuid=True), ForeignKey("lotes_inventario.id_lote"), nullable=False
    )
    id_sede = Column(
        UUID(as_uuid=True), ForeignKey("direcciones_sedes.id_sede"), nullable=False
    )
    distancia_km = Column(Numeric(6, 2), nullable=False)
    distancia_google_km = Column(Numeric(6, 2))
    tiempo_estimado_min = Column(Numeric(6, 2))
    estado_tramite = Column(String(20), nullable=False, default="sugerido")
    fecha_limite_retiro = Column(DateTime(timezone=True))
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "estado_tramite IN ('sugerido', 'confirmado', 'rechazado', "
            "'expirado', 'completado')",
            name="chk_estado_tramite",
        ),
        CheckConstraint("distancia_km <= 75", name="chk_radio_maximo"),
    )
