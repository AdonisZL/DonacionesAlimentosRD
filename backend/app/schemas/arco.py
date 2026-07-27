"""Esquemas Pydantic de ARCO / ARCO Pydantic 模式 (RN-19).

Validan la entrada y salida de la API de derechos ARCO.
校验 ARCO 权利 API 的输入/输出。
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Tipos de solicitud ARCO válidos / 有效的 ARCO 请求类型
TIPOS_ARCO_VALIDOS = {"acceso", "rectificacion", "cancelacion", "oposicion"}

# Estados de solicitud / 请求状态
ESTADOS_ARCO_VALIDOS = {
    "recibida",
    "en_proceso",
    "resuelta",
    "rechazada",
    "vencida",
}


class SolicitudArcoCrear(BaseModel):
    """Datos para crear una solicitud ARCO / 创建 ARCO 请求的数据."""

    tipo_solicitud: str = Field(
        description="Tipo de derecho: acceso, rectificacion, cancelacion, oposicion",
    )
    descripcion: str | None = Field(
        default=None,
        max_length=2000,
        description="Detalle de la solicitud (qué dato, por qué, etc.) / 请求详情",
    )

    @field_validator("tipo_solicitud")
    @classmethod
    def validar_tipo(cls, valor: str) -> str:
        if valor not in TIPOS_ARCO_VALIDOS:
            raise ValueError(
                f"Tipo de solicitud inválido. Debe ser: "
                f"{', '.join(sorted(TIPOS_ARCO_VALIDOS))}."
            )
        return valor


class SolicitudArcoResolver(BaseModel):
    """Datos para que el administrador resuelva una solicitud / 管理员解决请求的数据."""

    estado: str = Field(description="resuelta o rechazada")
    respuesta: str = Field(
        min_length=1,
        max_length=2000,
        description="Respuesta oficial al titular / 给申请人的正式回复",
    )

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor: str) -> str:
        if valor not in {"resuelta", "rechazada"}:
            raise ValueError("El estado debe ser 'resuelta' o 'rechazada'.")
        return valor


class SolicitudArcoLeer(BaseModel):
    """Datos de una solicitud ARCO para respuestas / API 返回的 ARCO 请求数据."""

    model_config = ConfigDict(from_attributes=True)

    id_solicitud: uuid.UUID
    id_usuario: uuid.UUID
    tipo_solicitud: str
    descripcion: str | None = None
    estado: str
    fecha_solicitud: datetime
    fecha_limite_respuesta: date
    fecha_resolucion: datetime | None = None
    atendido_por: uuid.UUID | None = None
    respuesta: str | None = None
