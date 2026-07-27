"""Utilidades de cifrado AES-256 / AES-256 加密工具 (RNF-12).

Cifrado a nivel de campo para datos sensibles (RNC, cédulas)
usando AES-256 en modo GCM (cifrado autenticado).
对敏感数据（RNC、身份证号）使用 AES-256-GCM 进行字段级加密。
"""

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Tamaño del nonce (12 bytes) recomendado para AES-GCM
# AES-GCM 推荐的 nonce 大小（12 字节）
_LONGITUD_NONCE = 12

# Clave AES-256 (32 bytes). Debe configurarse en .env / AES-256 密钥（32 字节），需在 .env 中配置
_CLAVE_AES: bytes | None = None


def configurar_clave_aes(clave_texto: str) -> None:
    """Configura la clave AES-256 a partir de una cadena en base64 o hexadecimal.

    La clave debe tener 32 bytes. Se acepta en formato:
    - base64 (44 caracteres) → decodificado a 32 bytes
    - hexadecimal (64 caracteres) → decodificado a 32 bytes
    配置 AES-256 密钥，支持 base64 或 hex 格式，必须是 32 字节。
    """
    global _CLAVE_AES

    if len(clave_texto) == 44:
        # Probablemente base64 / 可能是 base64
        try:
            _CLAVE_AES = base64.b64decode(clave_texto)
            if len(_CLAVE_AES) == 32:
                return
        except Exception:
            pass

    if len(clave_texto) == 64:
        # Probablemente hexadecimal / 可能是十六进制
        try:
            _CLAVE_AES = bytes.fromhex(clave_texto)
            if len(_CLAVE_AES) == 32:
                return
        except Exception:
            pass

    raise ValueError(
        "La clave AES-256 debe tener 32 bytes (64 caracteres hex o 44 base64). "
        'Genera una con: python -c "import os,base64; print(base64.b64encode(os.urandom(32)).decode())"'
    )


def _obtener_clave() -> bytes:
    """Devuelve la clave AES configurada o lanza error / 返回配置的 AES 密钥."""
    if _CLAVE_AES is None:
        raise RuntimeError(
            "La clave AES-256 no ha sido configurada. "
            "Llama a configurar_clave_aes() al iniciar la aplicación."
        )
    return _CLAVE_AES


def cifrar_aes256(texto_plano: str) -> str:
    """Cifra un texto con AES-256-GCM y devuelve el resultado en base64.

    Formato de salida: nonce (12 bytes) + ciphertext (+ tag) → base64.
    使用 AES-256-GCM 加密文本，返回 base64 编码的结果。
    """
    if not texto_plano:
        return texto_plano  # no cifrar vacíos / 不加密空值

    clave = _obtener_clave()
    nonce = os.urandom(_LONGITUD_NONCE)
    aesgcm = AESGCM(clave)
    datos_cifrados = aesgcm.encrypt(nonce, texto_plano.encode("utf-8"), None)
    # nonce + ciphertext (ya incluye tag)
    return base64.b64encode(nonce + datos_cifrados).decode("ascii")


def descifrar_aes256(texto_cifrado: str) -> str:
    """Descifra un texto previamente cifrado con cifrar_aes256().

    Si el texto no está en formato cifrado (no es base64 válido),
    se devuelve tal cual (compatibilidad con datos anteriores sin cifrar).
    解密由 cifrar_aes256() 加密的文本。如果文本不是有效的加密格式则原样返回。
    """
    if not texto_cifrado:
        return texto_cifrado

    try:
        datos = base64.b64decode(texto_cifrado)
    except Exception:
        # No es base64 → probablemente es texto plano antiguo / 不是 base64 → 可能是旧明文
        return texto_cifrado

    if len(datos) <= _LONGITUD_NONCE:
        return texto_cifrado

    nonce = datos[:_LONGITUD_NONCE]
    ciphertext = datos[_LONGITUD_NONCE:]

    try:
        clave = _obtener_clave()
        aesgcm = AESGCM(clave)
        return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
    except Exception:
        # Si falla el descifrado, devolver texto original (datos no cifrados)
        # 如果解密失败，返回原始文本（未加密的数据）
        return texto_cifrado


def generar_clave_aes256() -> str:
    """Genera una clave AES-256 aleatoria en base64 (para .env).

    生成随机的 AES-256 密钥（base64 格式，用于 .env）。
    """
    return base64.b64encode(os.urandom(32)).decode("ascii")
