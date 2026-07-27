"""Modelo de solicitudes ARCO / ARCO 请求模型 (RN-19).

Gestión de derechos de Acceso, Rectificación, Cancelación y Oposición
conforme a la Ley 172-13 de protección de datos personales.
根据第 172-13 号个人数据保护法管理访问、更正、删除和反对权。
"""

import uuid

from sqlalchemy import CheckConstraint, Column, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.conexion import Base


class SolicitudArco(Base):
    """Tabla 'solicitudes_arco' / ARCO 请求表 (RN-19)."""

    __tablename__ = "solicitudes_arco"

    id_solicitud = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    tipo_solicitud = Column(
        String(20),
        CheckConstraint(
            "tipo_solicitud IN ('acceso', 'rectificacion', 'cancelacion', 'oposicion')"
        ),
        nullable=False,
    )
    descripcion = Column(Text)
    estado = Column(
        String(20),
        CheckConstraint(
            "estado IN ('recibida', 'en_proceso', 'resuelta', 'rechazada', 'vencida')"
        ),
        default="recibida",
        nullable=False,
    )
    fecha_solicitud = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # RN-19: respuesta en ≤ 15 días hábiles / 在 ≤ 15 个工作日内响应
    fecha_limite_respuesta = Column(Date, nullable=False)
    fecha_resolucion = Column(DateTime(timezone=True))
    atendido_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"))
    respuesta = Column(Text)

    # Relaciones / 关联
    usuario = relationship("Usuario", foreign_keys=[id_usuario], lazy="selectin")
    administrador = relationship(
        "Usuario", foreign_keys=[atendido_por], lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<SolicitudArco {self.tipo_solicitud} - {self.estado}>"
