"""Modelo de dirección/sede / 地址与场所模型 (RF-01/02/03).

Ubicación geográfica (PostGIS) y capacidades de receptores y bancos.
接收方与食物银行的地理位置（PostGIS）与容量。
"""

import uuid

from geoalchemy2 import Geography
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base


class DireccionSede(Base):
    """Tabla 'direcciones_sedes' / 地址场所表."""

    __tablename__ = "direcciones_sedes"

    id_sede = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    nombre_sede = Column(String(150))
    direccion_texto = Column(String(255))
    correo_contacto = Column(String(255))
    telefono_contacto = Column(String(20))
    horario_atencion = Column(String(255))
    estado = Column(String(20), default="activa")
    coordenadas = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    capacidad_diaria_kg = Column(Numeric(10, 2))
    tiene_cadena_frio = Column(Boolean, default=False)
    rnc = Column(String(11))
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
