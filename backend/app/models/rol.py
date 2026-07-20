"""Modelo ORM del rol / 角色 ORM 模型 (RN-03).

Cada usuario posee un único rol principal en el sistema.
每个用户在系统中拥有唯一的主要角色。
"""

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.conexion import Base


class Rol(Base):
    """Tabla 'roles' / 角色表."""

    __tablename__ = "roles"

    id_rol = Column(UUID(as_uuid=True), primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(255))
