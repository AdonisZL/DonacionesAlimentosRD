"""Modelo de evidencia de entrega / 交付凭证模型 (RF-25).

Registra fotos/comprobantes de las entregas completadas.
记录已完成交付的照片/凭证。
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.conexion import Base


class EvidenciaEntrega(Base):
    """Tabla 'evidencia_entrega' / 交付凭证表 (RF-25)."""

    __tablename__ = "evidencia_entrega"

    id_evidencia = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_entrega = Column(
        UUID(as_uuid=True),
        ForeignKey("entregas_transacciones.id_entrega"),
        nullable=False,
    )
    tipo_archivo = Column(String(20), default="imagen")
    archivo_url = Column(String(255), nullable=False)
    subido_en = Column(DateTime(timezone=True), server_default=func.now())

    # Relación / 关联
    entrega = relationship("EntregaTransaccion", backref="evidencias", lazy="selectin")

    def __repr__(self) -> str:
        return f"<EvidenciaEntrega {self.tipo_archivo} - {self.archivo_url[:30]}>"
