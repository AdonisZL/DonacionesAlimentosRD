"""Esquemas Pydantic de inventario / 库存 Pydantic 模式 (OE2).

Validan la entrada y salida de productos, lotes, ajustes y mermas.
校验产品、批次、调整与损耗的输入/输出。
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.merma import MOTIVOS_MERMA


class CategoriaAlimentoLeer(BaseModel):
    """Categoría de alimento / 食物分类."""

    model_config = ConfigDict(from_attributes=True)

    id_categoria_alimento: int
    nombre_categoria: str
    requiere_cadena_frio: bool | None = None


class CategoriaPerecibilidadLeer(BaseModel):
    """Categoría de perecibilidad / 易腐性分类."""

    model_config = ConfigDict(from_attributes=True)

    id_perecibilidad: int
    nombre: str
    dias_minimos_ventana: int


class ProductoCrear(BaseModel):
    """Datos para crear un producto / 创建产品的数据 (RF-09)."""

    id_categoria_alimento: int
    id_perecibilidad: int
    nombre_producto: str = Field(min_length=1, max_length=150)
    codigo_barra: str | None = Field(default=None, max_length=50)
    descripcion: str | None = Field(default=None, max_length=255)
    marca: str | None = Field(default=None, max_length=100)
    unidad_predeterminada: str | None = Field(default=None, max_length=20)


class ProductoLeer(BaseModel):
    """Producto para respuesta / 返回的产品."""

    model_config = ConfigDict(from_attributes=True)

    id_producto: int
    id_categoria_alimento: int
    id_perecibilidad: int
    nombre_producto: str
    marca: str | None = None
    unidad_predeterminada: str | None = None


class LoteCrear(BaseModel):
    """Datos para registrar un lote / 登记批次的数据 (RF-09)."""

    id_producto: int
    id_sede: uuid.UUID | None = None
    cantidad_disponible: float = Field(gt=0)
    unidad_medida: str | None = Field(default=None, max_length=10)
    peso_total: float | None = Field(default=None, ge=0)
    fecha_produccion: date | None = None
    fecha_vencimiento: date
    temperatura_requerida: str | None = Field(default=None, max_length=30)

    @field_validator("fecha_vencimiento")
    @classmethod
    def _validar_vencimiento(cls, valor: date) -> date:
        """RF-14: la fecha de vencimiento no puede estar en el pasado."""
        if valor < date.today():
            raise ValueError(
                "La fecha de vencimiento no puede ser anterior a hoy (lote vencido)."
            )
        return valor


class LoteLeer(BaseModel):
    """Lote para respuesta, con datos FEFO calculados / 返回的批次（含 FEFO 计算）."""

    model_config = ConfigDict(from_attributes=True)

    id_lote: uuid.UUID
    id_usuario: uuid.UUID
    id_producto: int
    id_sede: uuid.UUID | None = None
    cantidad_disponible: float
    unidad_medida: str | None = None
    peso_total: float | None = None
    fecha_produccion: date | None = None
    fecha_vencimiento: date
    temperatura_requerida: str | None = None
    estado: str
    creado_en: datetime | None = None

    # Campos calculados (no persistidos) / 计算字段（非持久化）
    nombre_producto: str | None = None
    nombre_perecibilidad: str | None = None
    ventana_dias: int | None = None
    dias_minimos_ventana: int | None = None
    en_alerta: bool = False
    bajo_umbral: bool = False


class AjusteInventario(BaseModel):
    """Ajuste manual de inventario / 手动库存调整 (RF-15). Solo banco."""

    cantidad_afectada: float = Field(gt=0)
    motivo: str
    detalle: str | None = None

    @field_validator("motivo")
    @classmethod
    def _validar_motivo(cls, valor: str) -> str:
        """El motivo debe pertenecer al catálogo permitido / 原因须在允许目录内."""
        if valor not in MOTIVOS_MERMA:
            raise ValueError(
                f"Motivo inválido. Use uno de: {', '.join(MOTIVOS_MERMA)}."
            )
        return valor


class HistorialLeer(BaseModel):
    """Registro del historial de un lote / 批次历史记录 (RF-16)."""

    model_config = ConfigDict(from_attributes=True)

    id_historial: int
    id_usuario: uuid.UUID
    id_lote: uuid.UUID
    estado_anterior: str | None = None
    estado_nuevo: str
    motivo: str | None = None
    fecha: datetime | None = None
