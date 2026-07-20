"""Modelo de entrega/transacción / 交付事务模型.

Registra la entrega asociada a un emparejamiento completado (base RF-22/RF-25).
记录已完成匹配对应的交付（RF-22/RF-25 基础）。
"""

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base


class EntregaTransaccion(Base):
    """Tabla 'entregas_transacciones' / 交付事务表."""

    __tablename__ = "entregas_transacciones"

    id_entrega = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_emparejamiento = Column(
        UUID(as_uuid=True),
        ForeignKey("emparejamientos.id_emparejamiento"),
        nullable=False,
    )
    estado_entrega = Column(String(20), nullable=False, default="pendiente")
    fecha_completado = Column(DateTime(timezone=True))
    hash_fiscal_dgii = Column(String(128))
    hash_anterior = Column(String(128))
    nombre_receptor = Column(String(150))
    firma_url = Column(String(255))
    documento_firmado_url = Column(String(255))
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "estado_entrega IN ('pendiente', 'completada', 'rechazada')",
            name="chk_estado_entrega",
        ),
    )
