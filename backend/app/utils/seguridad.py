"""Utilidades de seguridad / 安全工具.

- Hashing de contraseñas con bcrypt (coste >= 12) — RF-04 / RNF-12.
- Generación y validación de tokens JWT — RF-04.
密码用 bcrypt 哈希（成本 >= 12）；JWT 令牌的生成与校验。
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config.configuracion import configuracion

# Coste (rounds) de bcrypt / bcrypt 成本因子 (RF-04, RNF-12)
COSTE_BCRYPT = 12


def hashear_contrasena(contrasena: str) -> str:
    """Devuelve el hash bcrypt de una contraseña / 返回密码的 bcrypt 哈希."""
    sal = bcrypt.gensalt(rounds=COSTE_BCRYPT)
    return bcrypt.hashpw(contrasena.encode("utf-8"), sal).decode("utf-8")


def verificar_contrasena(contrasena: str, hash_almacenado: str) -> bool:
    """Verifica una contraseña contra su hash / 校验密码是否与哈希匹配."""
    try:
        return bcrypt.checkpw(
            contrasena.encode("utf-8"), hash_almacenado.encode("utf-8")
        )
    except ValueError:
        return False


def crear_token_acceso(datos: dict, minutos_expiracion: int | None = None) -> str:
    """Genera un JWT firmado con expiración / 生成带过期时间的签名 JWT."""
    minutos = minutos_expiracion or configuracion.jwt_minutos_expiracion
    expira = datetime.now(timezone.utc) + timedelta(minutes=minutos)
    contenido = {**datos, "exp": expira}
    return jwt.encode(
        contenido,
        configuracion.jwt_secreto,
        algorithm=configuracion.jwt_algoritmo,
    )


def decodificar_token(token: str) -> dict | None:
    """Decodifica y valida un JWT; devuelve None si es inválido / 解码并校验 JWT."""
    try:
        return jwt.decode(
            token,
            configuracion.jwt_secreto,
            algorithms=[configuracion.jwt_algoritmo],
        )
    except JWTError:
        return None


def crear_token_verificacion(id_usuario: str) -> str:
    """JWT de verificación de correo, válido 24 h / 邮箱验证 JWT（有效 24 小时） (RF-06)."""
    return crear_token_acceso(
        {"sub": id_usuario, "tipo": "verificacion_correo"},
        minutos_expiracion=60 * 24,
    )


def generar_token_aleatorio() -> str:
    """Token opaco de un solo uso para recuperación / 一次性随机令牌 (RF-05)."""
    return secrets.token_urlsafe(32)


def hashear_token(token: str) -> str:
    """Hash SHA-256 del token de recuperación / 恢复令牌的 SHA-256 哈希."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
