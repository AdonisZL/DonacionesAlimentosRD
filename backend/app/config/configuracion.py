"""Configuración central de la aplicación / 应用中心配置.

Carga las variables de entorno desde ``backend/.env`` usando pydantic-settings.
从 ``backend/.env`` 加载环境变量。
"""

from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

# Ruta del directorio backend (donde vive el .env) / backend 目录（.env 所在位置）
_RUTA_BACKEND = Path(__file__).resolve().parents[2]


class Configuracion(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno / 应用配置."""

    # Base de datos PostgreSQL / 数据库
    bd_host: str = "localhost"
    bd_puerto: int = 5432
    bd_nombre: str = "donaciones_alimentos"
    bd_usuario: str = "postgres"
    bd_contrasena: str = ""

    # Seguridad JWT / JWT 安全
    jwt_secreto: str = "cambiar_por_una_clave_larga_y_secreta"
    jwt_algoritmo: str = "HS256"
    jwt_minutos_expiracion: int = 60

    # Cifrado AES-256 para datos sensibles (RNF-12) / AES-256 敏感数据加密
    clave_aes256: str = ""

    # Correo (SMTP) — simulado por defecto / 邮件（SMTP）— 默认模拟
    correo_activo: bool = False
    correo_remitente: str = ""
    smtp_host: str = ""
    smtp_puerto: int = 587
    smtp_usuario: str = ""
    smtp_contrasena: str = ""

    # MegaPlus API (consulta RNC/Cédula) / MegaPlus API（RNC 查询）
    megaplus_api_url: str = "http://localhost:9000"

    model_config = SettingsConfigDict(
        env_file=_RUTA_BACKEND / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def url_base_datos(self) -> str:
        """URL de conexión para SQLAlchemy / SQLAlchemy 连接 URL."""
        usuario = quote_plus(self.bd_usuario)
        contrasena = quote_plus(self.bd_contrasena)
        return (
            f"postgresql+psycopg2://{usuario}:{contrasena}"
            f"@{self.bd_host}:{self.bd_puerto}/{self.bd_nombre}"
        )


configuracion = Configuracion()
