"""Esquemas Pydantic de reportes / 报表 Pydantic 模式 (OE4).

Filtros de consulta y estructuras de salida de los reportes.
报表的查询过滤与输出结构。
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class FilaDonacion(BaseModel):
    """Una fila del reporte de donaciones / 捐赠报表的一行 (RF-23)."""

    id_lote: uuid.UUID
    fecha: datetime | None = None
    donante: str | None = None
    producto: str | None = None
    categoria: str | None = None
    cantidad: float
    unidad: str | None = None
    peso_kg: float | None = None
    estado: str


class ReporteDonaciones(BaseModel):
    """Reporte de donaciones por período / 按期捐赠报表 (RF-23)."""

    filas: list[FilaDonacion]
    total_lotes: int
    total_kg: float


class FilaAsignacion(BaseModel):
    """Una asignación completada / 已完成分配 (RF-25)."""

    id_emparejamiento: uuid.UUID
    fecha: datetime | None = None
    producto: str | None = None
    sede_receptora: str | None = None
    distancia_km: float | None = None
    estado_entrega: str | None = None
    evidencias: int = 0


class ReporteAsignaciones(BaseModel):
    """Reporte de asignaciones completadas / 已完成分配报表 (RF-25)."""

    filas: list[FilaAsignacion]
    total: int


class SolicitudExportacion(BaseModel):
    """Solicitud de exportación a Google Sheets / 导出请求 (RF-26)."""

    tipo: str = Field(description="donaciones | inventario | asignaciones")
    desde: date | None = None
    hasta: date | None = None


class SolicitudFiscal(BaseModel):
    """Solicitud de reporte fiscal DGII / 财务报表请求 (RF-27)."""

    anio: int = Field(ge=2020, le=2100)
    mes: int = Field(ge=1, le=12)
    id_reporte_rectificado: uuid.UUID | None = None


class ReporteLeer(BaseModel):
    """Reporte consolidado guardado / 已保存的报表."""

    model_config = ConfigDict(from_attributes=True)

    id_reporte: uuid.UUID
    tipo_reporte: str
    url_archivo: str | None = None
    version: int
    estado: str
    fecha_generacion: datetime | None = None
