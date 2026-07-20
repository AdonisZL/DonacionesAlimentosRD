"""Modelo de consentimiento de datos / 数据同意模型 (RF-31, RN-18, Ley 172-13).

Registra cada consentimiento otorgado por el usuario (tipo, versión, IP, fecha).
记录用户给出的每一次同意（类型、版本、IP、时间）。
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.sql import func

from app.database.conexion import Base


class ConsentimientoDatos(Base):
    """Tabla 'consentimiento_datos' / 数据同意表."""

    __tablename__ = "consentimiento_datos"

    id_consentimiento = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    tipo_consentimiento = Column(String(40), nullable=False)
    version_documento = Column(String(20), nullable=False)
    aceptado = Column(Boolean, nullable=False, default=False)
    ip_origen = Column(INET)
    fecha_consentimiento = Column(DateTime(timezone=True), server_default=func.now())
    fecha_revocacion = Column(DateTime(timezone=True))
