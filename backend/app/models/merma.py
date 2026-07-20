"""Modelo de merma / 损耗模型 (RF-15).

Registra pérdidas o retiros de inventario con su motivo obligatorio.
记录库存的损失或撤回，附带必填原因。
"""

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base

# Motivos válidos de merma / 损耗有效原因
MOTIVOS_MERMA = (
    "vencimiento",
    "dano_fisico",
    "contaminacion",
    "rechazo_en_destino",
    "otro",
)


class Merma(Base):
    """Tabla 'mermas' / 损耗表."""

    __tablename__ = "mermas"

    id_merma = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_lote = Column(
        UUID(as_uuid=True), ForeignKey("lotes_inventario.id_lote"), nullable=False
    )
    id_usuario_responsable = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    motivo = Column(String(30), nullable=False)
    detalle = Column(Text)
    cantidad_afectada = Column(Numeric(10, 2), nullable=False)
    unidad_medida = Column(String(10))
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "motivo IN ('vencimiento', 'dano_fisico', 'contaminacion', "
            "'rechazo_en_destino', 'otro')",
            name="chk_motivo_merma",
        ),
    )
