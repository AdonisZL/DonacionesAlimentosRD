"""Modelo de lote de inventario / 库存批次模型 (RF-09, RF-12, RF-14).

Cada lote representa una cantidad de un producto con su fecha de vencimiento.
每个批次表示某产品的一定数量及其到期日。
"""

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base

# Estados válidos del lote / 批次有效状态
ESTADOS_LOTE = (
    "disponible",
    "reservado",
    "asignado",
    "entregado",
    "vencido",
    "retirado",
)


class LoteInventario(Base):
    """Tabla 'lotes_inventario' / 库存批次表."""

    __tablename__ = "lotes_inventario"

    id_lote = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    id_producto = Column(
        Integer,
        ForeignKey("productos.id_producto"),
        nullable=False,
    )
    id_sede = Column(UUID(as_uuid=True), ForeignKey("direcciones_sedes.id_sede"))
    cantidad_disponible = Column(Numeric(10, 2), nullable=False)
    unidad_medida = Column(String(10))
    peso_total = Column(Numeric(10, 2))
    peso_disponible = Column(Numeric(10, 2))
    fecha_produccion = Column(Date)
    fecha_vencimiento = Column(Date, nullable=False)
    temperatura_requerida = Column(String(30))
    estado = Column(String(20), nullable=False, default="disponible")
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "estado IN ('disponible', 'reservado', 'asignado', "
            "'entregado', 'vencido', 'retirado')",
            name="chk_estado_lote",
        ),
    )
