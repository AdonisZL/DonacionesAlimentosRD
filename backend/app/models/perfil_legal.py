"""Modelo de perfil legal / 法律信息模型 (RN-01, RF-01).

Guarda el RNC y el consentimiento de datos de los usuarios jurídicos.
保存法人用户的 RNC 与数据同意。
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.conexion import Base


class PerfilLegal(Base):
    """Tabla 'perfiles_legales' / 法律信息表."""

    __tablename__ = "perfiles_legales"

    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), primary_key=True
    )
    rnc = Column(String(11), unique=True)
    telefono = Column(String(20))
    consentimiento_172_13 = Column(Boolean, nullable=False, default=False)
    fecha_consentimiento = Column(DateTime(timezone=True))
