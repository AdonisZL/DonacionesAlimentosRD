"""Configuración central del backend / 后端中央配置.

Lee las variables desde el archivo .env usando Pydantic Settings.
使用 Pydantic Settings 从 .env 读取变量。
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Raíz del backend (…/backend). El archivo .env vive aquí.
# 后端根目录（…/backend），.env 就在此处。
RAIZ_BACKEND = Path(__file__).resolve().parents[2]


class Configuracion(BaseSettings):
    """Variables de configuración de la aplicación / 应用配置变量."""

    model_config = SettingsConfigDict(
        env_file=RAIZ_BACKEND / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Base de datos / 数据库
    bd_host: str = "localhost"
    bd_puerto: int = 5432
    bd_nombre: str = "donaciones_alimentos"
    bd_usuario: str = "postgres"
    bd_contrasena: str = ""

    # Seguridad / 安全 (fases posteriores / 后续阶段)
    jwt_secreto: str = "cambiar_en_produccion"
    jwt_algoritmo: str = "HS256"
    jwt_minutos_expiracion: int = 60

    @property
    def url_base_datos(self) -> str:
        """Cadena de conexión SQLAlchemy / SQLAlchemy 连接字符串."""
        return (
            f"postgresql+psycopg2://{self.bd_usuario}:{self.bd_contrasena}"
            f"@{self.bd_host}:{self.bd_puerto}/{self.bd_nombre}"
        )


# Instancia única de configuración / 全局唯一配置实例
configuracion = Configuracion()
