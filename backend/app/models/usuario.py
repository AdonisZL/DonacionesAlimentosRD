"""Modelo ORM de usuario / 用户 ORM 模型.

Refleja la tabla 'usuarios'. RN-03: cada usuario tiene un único rol.
对应 'usuarios' 表。RN-03：每个用户唯一角色。
"""

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base


class Usuario(Base):
    """Tabla 'usuarios' / 用户表."""

    __tablename__ = "usuarios"

    id_usuario = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100))
    telefono = Column(String(20))
    foto_perfil = Column(String(255))
    ultimo_acceso = Column(DateTime(timezone=True))
    email = Column(String(255), unique=True)
    email_verificado = Column(Boolean, default=False)
    contrasena_hash = Column(String(255))
    id_rol = Column(UUID(as_uuid=True), ForeignKey("roles.id_rol"), nullable=False)
    subtipo_donante = Column(String(20))
    id_usuario_registrador = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario")
    )
    intentos_fallidos = Column(SmallInteger, default=0)
    bloqueado_hasta = Column(DateTime(timezone=True))
    estado = Column(String(20), default="activo")
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
