"""Modelo de token de recuperación de contraseña / 密码恢复令牌模型 (RF-05).

Guarda el hash del token (no el token en claro), su expiración (15 min) y si ya se usó.
仅保存令牌哈希（不存明文）、过期时间（15 分钟）与是否已使用。
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.conexion import Base


class TokenRecuperacion(Base):
    """Tabla 'tokens_recuperacion_password' / 密码恢复令牌表."""

    __tablename__ = "tokens_recuperacion_password"

    id_token = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    token_hash = Column(String(255), nullable=False)
    usado = Column(Boolean, nullable=False, default=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    expira_en = Column(DateTime(timezone=True), nullable=False)
