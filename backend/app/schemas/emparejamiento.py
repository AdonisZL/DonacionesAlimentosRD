"""Esquemas Pydantic de emparejamiento / 匹配 Pydantic 模式 (OE3).

Validan la búsqueda, creación, confirmación y retroalimentación de matches.
校验匹配的搜索、创建、确认与反馈。
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CandidatoEmparejamiento(BaseModel):
    """Receptor compatible sugerido (RF-17/18) / 兼容的接收方建议."""

    id_sede: uuid.UUID
    id_usuario: uuid.UUID
    nombre_sede: str | None = None
    direccion_texto: str | None = None
    distancia_km: float
    tiene_cadena_frio: bool | None = None
    capacidad_diaria_kg: float | None = None
    compatible: bool = True
    motivo_incompatible: str | None = None
    justificacion_ia: str | None = None


class BuscarCandidatos(BaseModel):
    """Parámetros de búsqueda de receptores / 搜索参数 (RF-17)."""

    id_lote: uuid.UUID
    radio_km: float = Field(default=25, gt=0, le=75)


class EmparejamientoCrear(BaseModel):
    """Datos para crear un emparejamiento sugerido / 创建建议匹配的数据."""

    id_lote: uuid.UUID
    id_sede: uuid.UUID
    radio_km: float = Field(default=25, gt=0, le=75)


class EmparejamientoLeer(BaseModel):
    """Emparejamiento para respuesta / 返回的匹配."""

    model_config = ConfigDict(from_attributes=True)

    id_emparejamiento: uuid.UUID
    id_lote: uuid.UUID
    id_sede: uuid.UUID
    distancia_km: float
    estado_tramite: str
    fecha_limite_retiro: datetime | None = None
    creado_en: datetime | None = None

    # Campos enriquecidos / 富数据
    nombre_producto: str | None = None
    nombre_sede: str | None = None
    justificacion_ia: str | None = None


class RetroalimentacionCrear(BaseModel):
    """Calificación de una entrega completada / 对已完成交付的评分 (RF-22)."""

    calificacion: int = Field(ge=1, le=5)
    comentario: str | None = None


class NotificacionLeer(BaseModel):
    """Notificación para respuesta / 返回的通知 (RF-21)."""

    model_config = ConfigDict(from_attributes=True)

    id_notificacion: uuid.UUID
    titulo: str | None = None
    mensaje: str | None = None
    leido: bool | None = None
    creado_en: datetime | None = None
