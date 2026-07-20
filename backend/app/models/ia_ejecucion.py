"""Modelo de ejecución de IA / AI 执行记录模型 (RF-18).

Registra las llamadas a la IA (simuladas): prompt, respuesta y metadatos.
记录（模拟的）AI 调用：提示词、响应与元数据。
"""

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base


class IaEjecucion(Base):
    """Tabla 'ia_ejecuciones' / AI 执行记录表."""

    __tablename__ = "ia_ejecuciones"

    id_ejecucion = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_emparejamiento = Column(
        UUID(as_uuid=True), ForeignKey("emparejamientos.id_emparejamiento")
    )
    tipo_ejecucion = Column(String(20), nullable=False)
    prompt = Column(Text)
    respuesta = Column(Text)
    modelo = Column(String(50))
    tokens_usados = Column(Integer)
    confianza = Column(Numeric(4, 2))
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "tipo_ejecucion IN ('normalizacion_ner', 'justificacion_narrativa')",
            name="chk_tipo_ejecucion",
        ),
    )
