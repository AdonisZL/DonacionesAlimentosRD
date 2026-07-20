"""Conexión a la base de datos / 数据库连接.

Define el motor (engine), la fábrica de sesiones y la base declarativa
que usarán los modelos ORM.
定义引擎、会话工厂与 ORM 模型使用的声明基类。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config.configuracion import configuracion

# Motor de conexión a PostgreSQL / PostgreSQL 连接引擎
motor = create_engine(
    configuracion.url_base_datos,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Fábrica de sesiones / 会话工厂
SesionLocal = sessionmaker(
    bind=motor,
    autoflush=False,
    autocommit=False,
    future=True,
)

# Base declarativa para los modelos / 模型声明基类
Base = declarative_base()


def obtener_sesion():
    """Provee una sesión de base de datos por petición / 每个请求提供一个数据库会话.

    Se usa como dependencia de FastAPI. / 作为 FastAPI 依赖使用。
    """
    sesion = SesionLocal()
    try:
        yield sesion
    finally:
        sesion.close()
