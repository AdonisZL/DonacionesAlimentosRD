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
    distancia_google_km: float | None = None
    tiempo_estimado_min: float | None = None
    tiene_cadena_frio: bool | None = None
    capacidad_diaria_kg: float | None = None
    compatible: bool = True
    motivo_incompatible: str | None = None
    justificacion_ia: str | None = None
    score_fefo: float | None = None


class BuscarCandidatos(BaseModel):
    """Parámetros de búsqueda de receptores / 搜索参数 (RF-17).

    RN-10: radio inicial de 10 km, máximo 15 km para el piloto de SDO.
    """

    id_lote: uuid.UUID
    radio_km: float = Field(default=10, gt=0, le=15)


class EmparejamientoCrear(BaseModel):
    """Datos para crear un emparejamiento sugerido / 创建建议匹配的数据."""

    id_lote: uuid.UUID
    id_sede: uuid.UUID
    radio_km: float = Field(default=10, gt=0, le=15)


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
    prioridad_fefo_score: float | None = None
    aprobado_por_operador: uuid.UUID | None = None


class RetroalimentacionCrear(BaseModel):
    """Calificación de una entrega completada / 对已完成交付的评分 (RF-22)."""

    calificacion: int = Field(ge=1, le=5)
    comentario: str | None = None


class CompletarEntrega(BaseModel):
    """Datos para completar un emparejamiento / 完成匹配的数据 (RN-14)."""

    archivo_evidencia_url: str = Field(min_length=1, max_length=255)


class NotificacionLeer(BaseModel):
    """Notificación para respuesta / 返回的通知 (RF-21)."""

    model_config = ConfigDict(from_attributes=True)

    id_notificacion: uuid.UUID
    titulo: str | None = None
    mensaje: str | None = None
    leido: bool | None = None
    creado_en: datetime | None = None


class EvidenciaLeer(BaseModel):
    """Evidencia de entrega para respuesta / 返回的交付凭证 (RF-25)."""

    model_config = ConfigDict(from_attributes=True)

    id_evidencia: uuid.UUID
    id_entrega: uuid.UUID
    tipo_archivo: str | None = None
    archivo_url: str
    subido_en: datetime | None = None
