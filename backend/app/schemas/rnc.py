"""Esquemas Pydantic de RNC / RNC Pydantic 模式.

Validan las solicitudes de consulta de RNC/Cédula a través de MegaPlus API.
校验通过 MegaPlus API 查询 RNC/身份证的请求。
"""

from pydantic import BaseModel, Field, field_validator


class ConsultaRNCSolicitud(BaseModel):
    """Solicitud de consulta por RNC o Cédula / RNC 或身份证查询请求."""

    rnc: str = Field(
        min_length=9,
        max_length=11,
        description="RNC (9 dígitos) o Cédula (11 dígitos) sin guiones",
    )

    @field_validator("rnc")
    @classmethod
    def validar_rnc(cls, valor: str) -> str:
        valor_limpio = valor.strip()
        if not valor_limpio.isdigit():
            raise ValueError("El RNC/Cédula debe contener solo dígitos.")
        if len(valor_limpio) not in (9, 11):
            raise ValueError("El RNC debe tener 9 dígitos o la cédula 11 dígitos.")
        return valor_limpio


class BusquedaNombreSolicitud(BaseModel):
    """Solicitud de búsqueda por nombre / 按名称搜索请求."""

    buscar: str = Field(
        min_length=3,
        max_length=100,
        description="Nombre o razón social a buscar (mín. 3 caracteres)",
    )

    @field_validator("buscar")
    @classmethod
    def validar_buscar(cls, valor: str) -> str:
        return valor.strip()
