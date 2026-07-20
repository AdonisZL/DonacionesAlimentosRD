"""Esquemas Pydantic de administración / 管理 Pydantic 模式 (OE5)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UsuarioAdmin(BaseModel):
    """Usuario para la tabla del panel / 面板用户行."""

    model_config = ConfigDict(from_attributes=True)

    id_usuario: uuid.UUID
    nombre: str
    email: str | None = None
    rol: str
    estado: str
    email_verificado: bool | None = None
    creado_en: datetime | None = None


class CambiarEstado(BaseModel):
    """Nuevo estado de una cuenta / 账号新状态."""

    estado: str = Field(description="activo | inactivo | suspendido")


class AuditoriaLeer(BaseModel):
    """Evento de auditoría / 审计事件 (RF-29)."""

    model_config = ConfigDict(from_attributes=True)

    id_bitacora: int
    id_usuario: uuid.UUID | None = None
    accion: str
    entidad_afectada: str | None = None
    id_entidad_afectada: str | None = None
    ip_origen: str | None = None
    creado_en: datetime | None = None
