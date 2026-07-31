"""Esquemas Pydantic de usuario / 用户 Pydantic 模式.

Validan la entrada y salida de la API de registro y autenticación.
校验注册与认证 API 的输入/输出。
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# Símbolos permitidos para la política de contraseña / 密码允许的符号
_PATRON_SIMBOLO = re.compile(r"[^A-Za-z0-9]")


# Subtipos de donante válidos según RF-01 (actualizado 2026-07-27)
# 根据 RF-01 有效的捐赠者子类型（2026-07-27 更新）
SUBTIPOS_DONANTE_VALIDOS = {"formal", "informal", "independiente"}


class UsuarioCrear(BaseModel):
    """Datos para registrar un usuario / 注册用户的数据 (RF-01/02/03)."""

    nombre: str = Field(min_length=1, max_length=100)
    apellido: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)
    email: EmailStr
    contrasena: str = Field(min_length=10, max_length=72)
    id_rol: uuid.UUID
    # Subtipo solo aplica a donantes (formal/informal/independiente) / 仅捐赠者适用
    subtipo_donante: str | None = None

    # Campos por rol (opcionales) / 角色专属字段（可选）
    rnc: str | None = Field(default=None, max_length=11)
    direccion: str | None = Field(default=None, max_length=150)
    direccion_texto: str | None = Field(default=None, max_length=255)
    latitud: float | None = None
    longitud: float | None = None
    capacidad_diaria_kg: float | None = None
    tiene_cadena_frio: bool = False
    horario_atencion: str | None = Field(default=None, max_length=255)

    # RN-18 / RF-31: consentimiento Ley 172-13, obligatorio para procesar datos.
    consentimiento_172_13: bool = False

    @field_validator("contrasena")
    @classmethod
    def validar_politica_contrasena(cls, valor: str) -> str:
        """Aplica la política de contraseña RNF-15 / 应用密码策略."""
        if len(valor) < 10:
            raise ValueError("La contraseña debe tener al menos 10 caracteres.")
        if not any(c.isupper() for c in valor):
            raise ValueError("La contraseña debe incluir al menos una mayúscula.")
        if not any(c.isdigit() for c in valor):
            raise ValueError("La contraseña debe incluir al menos un número.")
        if not _PATRON_SIMBOLO.search(valor):
            raise ValueError("La contraseña debe incluir al menos un símbolo.")
        return valor

    @field_validator("rnc")
    @classmethod
    def validar_rnc(cls, valor: str | None) -> str | None:
        """El RNC, si se indica, debe tener 9 u 11 dígitos / RNC 若填写须为9或11位数字 (RN-01)."""
        if valor in (None, ""):
            return None
        if not (valor.isdigit() and len(valor) in (9, 11)):
            raise ValueError(
                "El RNC debe tener 9 dígitos (empresa) o 11 dígitos (cédula)."
            )
        return valor

    @field_validator("subtipo_donante")
    @classmethod
    def validar_subtipo_donante(cls, valor: str | None) -> str | None:
        """Valida que el subtipo de donante sea uno de los 3 permitidos (RF-01)."""
        if valor in (None, ""):
            return None
        if valor not in SUBTIPOS_DONANTE_VALIDOS:
            raise ValueError(
                f"El subtipo de donante debe ser uno de: "
                f"{', '.join(sorted(SUBTIPOS_DONANTE_VALIDOS))}."
            )
        return valor


class UsuarioLeer(BaseModel):
    """Datos públicos de un usuario para respuestas / API 返回的用户公开数据."""

    model_config = ConfigDict(from_attributes=True)

    id_usuario: uuid.UUID
    nombre: str
    apellido: str | None = None
    telefono: str | None = None
    email: EmailStr | None = None
    id_rol: uuid.UUID
    subtipo_donante: str | None = None
    email_verificado: bool
    estado: str
    creado_en: datetime


class UsuarioActualizar(BaseModel):
    """Datos editables del perfil / 可编辑的资料 (RF-07)."""

    nombre: str | None = Field(default=None, max_length=100)
    apellido: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)


class DatosLogin(BaseModel):
    """Credenciales de inicio de sesión / 登录凭证 (RF-04)."""

    email: EmailStr
    contrasena: str


class Token(BaseModel):
    """Respuesta de autenticación con el JWT / 认证响应（含 JWT）."""

    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioLeer


class SolicitarRecuperacion(BaseModel):
    """Solicitud de recuperación de contraseña / 找回密码请求 (RF-05)."""

    email: EmailStr


class RestablecerContrasena(BaseModel):
    """Restablecimiento de contraseña con token / 用令牌重置密码 (RF-05)."""

    token: str
    nueva_contrasena: str = Field(min_length=10, max_length=72)

    @field_validator("nueva_contrasena")
    @classmethod
    def validar_politica(cls, valor: str) -> str:
        """Aplica la política de contraseña RNF-15 / 应用密码策略."""
        if len(valor) < 10:
            raise ValueError("La contraseña debe tener al menos 10 caracteres.")
        if not any(c.isupper() for c in valor):
            raise ValueError("La contraseña debe incluir al menos una mayúscula.")
        if not any(c.isdigit() for c in valor):
            raise ValueError("La contraseña debe incluir al menos un número.")
        if not _PATRON_SIMBOLO.search(valor):
            raise ValueError("La contraseña debe incluir al menos un símbolo.")
        return valor


class SedeLeer(BaseModel):
    """Datos de la sede/dirección del usuario / 用户地址场所数据."""

    model_config = ConfigDict(from_attributes=True)

    id_sede: uuid.UUID | None = None
    direccion: str | None = None
    direccion_texto: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    capacidad_diaria_kg: float | None = None
    tiene_cadena_frio: bool = False
    horario_atencion: str | None = None
    estado: str | None = None
