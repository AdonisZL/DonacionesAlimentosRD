"""Modelo de categoría de perecibilidad / 易腐性分类模型 (RN-05, RF-10).

Define el umbral mínimo de días de ventana antes del vencimiento por tipo.
按类型定义临期前的最小天数阈值。
"""

from sqlalchemy import Column, Integer, String

from app.database.conexion import Base


class CategoriaPerecibilidad(Base):
    """Tabla 'categorias_perecibilidad' / 易腐性分类表."""

    __tablename__ = "categorias_perecibilidad"

    id_perecibilidad = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    dias_minimos_ventana = Column(Integer, nullable=False)
