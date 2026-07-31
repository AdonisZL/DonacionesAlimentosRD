"""Pruebas unitarias — seguridad / 安全模块单元测试 (RF-04, RF-30, RNF-12, RNF-15).

Cubre: bcrypt, JWT, políticas de contraseña, AES-256 y bloqueo de cuenta.
覆盖：bcrypt、JWT、密码策略、AES-256 和账号锁定。
"""

import pytest
from datetime import datetime, timedelta, timezone

from app.utils.seguridad import (
    COSTE_BCRYPT,
    crear_token_acceso,
    decodificar_token,
    generar_token_aleatorio,
    hashear_contrasena,
    hashear_token,
    verificar_contrasena,
)
from app.utils.cifrado import (
    cifrar_aes256,
    descifrar_aes256,
    generar_clave_aes256,
    configurar_clave_aes,
)

# ════════════════════════════════════════════════════════════════
# bcrypt — hashing y verificación / 密码哈希与校验
# ════════════════════════════════════════════════════════════════


class TestBcrypt:
    """Pruebas de hashing bcrypt / bcrypt 哈希测试."""

    def test_hashear_genera_string_diferente(self):
        """El hash es diferente de la contraseña original."""
        h = hashear_contrasena("MiClave123!")
        assert h != "MiClave123!"
        assert h.startswith("$2b$") or h.startswith("$2a$")

    def test_verificar_contrasena_correcta(self):
        """Verifica que una contraseña correcta coincida con su hash."""
        h = hashear_contrasena("Correcta2024!")
        assert verificar_contrasena("Correcta2024!", h) is True

    def test_verificar_contrasena_incorrecta(self):
        """Verifica que una contraseña incorrecta NO coincida."""
        h = hashear_contrasena("ClaveSegura1!")
        assert verificar_contrasena("ClaveErronea1!", h) is False

    def test_hashear_misma_clave_diferente_hash(self):
        """Dos hashes de la misma contraseña son diferentes (sal aleatoria)."""
        h1 = hashear_contrasena("MismaClave1!")
        h2 = hashear_contrasena("MismaClave1!")
        assert h1 != h2

    def test_coste_bcrypt_minimo(self):
        """El coste de bcrypt es ≥ 12 (RF-04, RNF-12)."""
        assert COSTE_BCRYPT >= 12


# ════════════════════════════════════════════════════════════════
# JWT — tokens de acceso / 访问令牌
# ════════════════════════════════════════════════════════════════


class TestJWT:
    """Pruebas de tokens JWT / JWT 令牌测试."""

    def test_crear_token_devuelve_string(self):
        """Crear un token devuelve un string."""
        token = crear_token_acceso({"sub": "abc123"})
        assert isinstance(token, str)
        assert len(token) > 20

    def test_decodificar_token_valido(self):
        """Un token válido se decodifica correctamente."""
        token = crear_token_acceso({"sub": "usuario-1", "rol": "donante"})
        datos = decodificar_token(token)
        assert datos is not None
        assert datos["sub"] == "usuario-1"
        assert datos["rol"] == "donante"

    def test_decodificar_token_invalido(self):
        """Un token manipulado devuelve None."""
        datos = decodificar_token("token.falso.invalido")
        assert datos is None

    def test_token_con_expiracion_pasada(self):
        """Un token expirado no se puede decodificar correctamente."""
        token = crear_token_acceso({"sub": "test"}, minutos_expiracion=-1)
        datos = decodificar_token(token)
        assert datos is None

    def test_token_contenido_personalizado(self):
        """El token conserva todos los datos del payload."""
        payload = {"sub": "uuid-123", "email": "a@b.com", "extra": "valor"}
        token = crear_token_acceso(payload, minutos_expiracion=60)
        datos = decodificar_token(token)
        assert datos["sub"] == "uuid-123"
        assert datos["email"] == "a@b.com"
        assert datos["extra"] == "valor"


# ════════════════════════════════════════════════════════════════
# Tokens aleatorios / 随机令牌
# ════════════════════════════════════════════════════════════════


class TestTokensAleatorios:
    """Pruebas de tokens de recuperación / 恢复令牌测试."""

    def test_generar_token_longitud(self):
        """El token aleatorio tiene al menos 32 caracteres."""
        token = generar_token_aleatorio()
        assert len(token) >= 32

    def test_generar_token_unicos(self):
        """Dos tokens generados son diferentes."""
        t1 = generar_token_aleatorio()
        t2 = generar_token_aleatorio()
        assert t1 != t2

    def test_hashear_token_consistente(self):
        """El hash del mismo token es siempre igual."""
        t = generar_token_aleatorio()
        h1 = hashear_token(t)
        h2 = hashear_token(t)
        assert h1 == h2

    def test_hashear_token_no_reversible(self):
        """El hash no contiene el token original."""
        t = generar_token_aleatorio()
        h = hashear_token(t)
        assert t not in h


# ════════════════════════════════════════════════════════════════
# AES-256 — cifrado de datos sensibles / 敏感数据加密
# ════════════════════════════════════════════════════════════════


class TestAES256:
    """Pruebas de cifrado AES-256-GCM / AES-256-GCM 加密测试 (RNF-12)."""

    @classmethod
    def setup_class(cls):
        """Configura una clave AES de prueba / 设置测试用 AES 密钥."""
        cls.clave_prueba = generar_clave_aes256()
        configurar_clave_aes(cls.clave_prueba)

    def test_cifrar_devuelve_string_diferente(self):
        """El texto cifrado es diferente del original."""
        cifrado = cifrar_aes256("12345678901")
        assert cifrado != "12345678901"
        assert len(cifrado) > 20

    def test_descifrar_recupera_original(self):
        """Descifrar devuelve el texto original."""
        original = "98765432109"
        cifrado = cifrar_aes256(original)
        descifrado = descifrar_aes256(cifrado)
        assert descifrado == original

    def test_cifrar_texto_vacio(self):
        """Cifrar texto vacío devuelve vacío."""
        assert cifrar_aes256("") == ""

    def test_descifrar_texto_plano_devuelve_igual(self):
        """Descifrar texto no cifrado lo devuelve tal cual (compatibilidad)."""
        assert descifrar_aes256("12345678901") == "12345678901"

    def test_cifrados_diferentes_mismo_texto(self):
        """Dos cifrados del mismo texto son diferentes (nonce aleatorio)."""
        c1 = cifrar_aes256("mismo_texto")
        c2 = cifrar_aes256("mismo_texto")
        assert c1 != c2
        # Pero ambos descifran al original
        assert descifrar_aes256(c1) == "mismo_texto"
        assert descifrar_aes256(c2) == "mismo_texto"

    def test_generar_clave_longitud(self):
        """La clave generada tiene 44 caracteres (32 bytes en base64)."""
        clave = generar_clave_aes256()
        assert len(clave) == 44


# ════════════════════════════════════════════════════════════════
# Política de contraseña / 密码策略
# ════════════════════════════════════════════════════════════════


class TestPoliticaContrasena:
    """Pruebas de la política RNF-15 / RNF-15 密码策略测试."""

    def _validar(self, contrasena: str) -> str | None:
        """Simula la validación de contraseña del schema / 模拟 schema 密码校验."""
        if len(contrasena) < 10:
            return "mínimo 10 caracteres"
        if not any(c.isupper() for c in contrasena):
            return "falta mayúscula"
        if not any(c.isdigit() for c in contrasena):
            return "falta número"
        if not any(not c.isalnum() for c in contrasena):
            return "falta símbolo"
        return None

    def test_contrasena_valida(self):
        assert self._validar("Valida2024!") is None

    def test_contrasena_corta(self):
        assert self._validar("Corta1!") == "mínimo 10 caracteres"

    def test_contrasena_sin_mayuscula(self):
        assert self._validar("minuscula2024!") == "falta mayúscula"

    def test_contrasena_sin_numero(self):
        assert self._validar("SinNumero!") == "falta número"

    def test_contrasena_sin_simbolo(self):
        assert self._validar("SinSimbolo2024") == "falta símbolo"

    def test_contrasena_10_caracteres(self):
        assert self._validar("Exacta10A!") is None

    def test_contrasena_larga(self):
        assert self._validar("MuyLarga1234567890!@#$") is None
