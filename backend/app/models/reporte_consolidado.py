"""Modelo de reporte consolidado / 合并报表模型 (OE4, RF-23 … RF-27).

Guarda los reportes generados (donaciones, inventario, asignaciones, fiscal).
Los reportes fiscales son inmutables y se encadenan por hash (RN-17).
保存生成的报表；财务报表不可变并以哈希链式连接。
"""

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.database.conexion import Base

# Tipos de reporte / 报表类型
TIPOS_REPORTE = (
    "donaciones",
    "inventario",
    "asignaciones",
    "exportacion_sheets",
    "fiscal_dgii",
)


class ReporteConsolidado(Base):
    """Tabla 'reportes_consolidados' / 合并报表表."""

    __tablename__ = "reportes_consolidados"

    id_reporte = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creado_por = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    tipo_reporte = Column(String(30), nullable=False)
    url_archivo = Column(String(255))
    parametros_busqueda = Column(JSONB)
    version = Column(Integer, nullable=False, default=1)
    id_reporte_rectificado = Column(
        UUID(as_uuid=True), ForeignKey("reportes_consolidados.id_reporte")
    )
    estado = Column(String(20), nullable=False, default="emitido")
    fecha_generacion = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "estado IN ('borrador', 'emitido', 'rectificado')",
            name="chk_estado_reporte",
        ),
    )
