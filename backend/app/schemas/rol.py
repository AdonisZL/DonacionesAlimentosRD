"""Esquemas Pydantic del rol / 角色 Pydantic 模式."""

import uuid

from pydantic import BaseModel, ConfigDict


class RolLeer(BaseModel):
    """Datos de un rol para respuesta de la API / API 返回的角色数据."""

    model_config = ConfigDict(from_attributes=True)

    id_rol: uuid.UUID
    nombre: str
    descripcion: str | None = None
