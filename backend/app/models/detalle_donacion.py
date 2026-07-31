"""Modelo de detalle de donación / 捐赠明细模型 (RF-07).

Desglose de productos incluidos en cada donación.
每笔捐赠中包含的产品明细。
"""

import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base


class DetalleDonacion(Base):
    """Tabla 'detalle_donaciones' / 捐赠明细表."""

    __tablename__ = "detalle_donaciones"

    id_detalle_donacion = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    id_donacion = Column(
        UUID(as_uuid=True),
        ForeignKey("donaciones.id_donacion"),
        nullable=False,
    )
    id_producto = Column(
        Integer,
        ForeignKey("productos.id_producto"),
        nullable=False,
    )
    cantidad = Column(Numeric(10, 2), nullable=False)
    unidad_medida = Column(String(20))
    fecha_vencimiento = Column(Date)
