"""Modelo de categoría de alimento / 食物分类模型.

Catálogo de tipos de alimentos (RF-09). Indica si requiere cadena de frío.
食物类型目录（RF-09）。标明是否需要冷链。
"""

from sqlalchemy import Boolean, Column, Integer, String

from app.database.conexion import Base


class CategoriaAlimento(Base):
    """Tabla 'categorias_alimentos' / 食物分类表."""

    __tablename__ = "categorias_alimentos"

    id_categoria_alimento = Column(Integer, primary_key=True)
    nombre_categoria = Column(String(100), nullable=False)
    requiere_cadena_frio = Column(Boolean, default=False)
