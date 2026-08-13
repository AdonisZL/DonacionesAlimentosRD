"""Modelo de perfil legal / 法律信息模型 (RN-01, RF-01).

Guarda el RNC y cédula cifrados con AES-256-GCM y su hash para blind indexing.
保存用 AES-256-GCM 加密的 RNC 与身份证及其盲索引哈希。
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, LargeBinary, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.conexion import Base


class PerfilLegal(Base):
    """Tabla 'perfiles_legales' / 法律信息表."""

    __tablename__ = "perfiles_legales"

    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), primary_key=True
    )
    telefono = Column(String(20))
    consentimiento_172_13 = Column(Boolean, nullable=False, default=False)
    fecha_consentimiento = Column(DateTime(timezone=True))
    # Campos para RNC cifrado (AES-256-GCM + blind indexing)
    rnc_cifrado = Column(LargeBinary)
    rnc_hash_busqueda = Column(String(64), unique=True)  # HMAC-SHA256
    # Campos para cédula cifrada (AES-256-GCM + blind indexing)
    cedula_cifrada = Column(LargeBinary)
    cedula_hash_busqueda = Column(String(64), unique=True)  # HMAC-SHA256
    # Nota: RN-01/RNF-12: cifrado AES-256-GCM en la aplicación,
    #       rnc_hash_busqueda y cedula_hash_busqueda para validar sin exponer texto claro
