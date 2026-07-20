"""Modelo de producto / 产品模型 (RF-09).

Producto genérico asociado a una categoría de alimento y a una perecibilidad.
关联食物分类与易腐性的通用产品。
"""

from sqlalchemy import Column, ForeignKey, Integer, String

from app.database.conexion import Base


class Producto(Base):
    """Tabla 'productos' / 产品表."""

    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True)
    id_categoria_alimento = Column(
        Integer,
        ForeignKey("categorias_alimentos.id_categoria_alimento"),
        nullable=False,
    )
    id_perecibilidad = Column(
        Integer,
        ForeignKey("categorias_perecibilidad.id_perecibilidad"),
        nullable=False,
    )
    nombre_producto = Column(String(150), nullable=False)
    codigo_barra = Column(String(50))
    descripcion = Column(String(255))
    marca = Column(String(100))
    imagen_url = Column(String(255))
    unidad_predeterminada = Column(String(20))
