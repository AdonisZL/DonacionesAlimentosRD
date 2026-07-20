"""Inicializa la base de datos / 初始化数据库.

Pasos / 步骤:
  1. Crea la base de datos si no existe. / 若不存在则创建数据库。
  2. Aplica el esquema (01_esquema.sql). / 应用建表脚本。
  3. Inserta datos semilla (02_datos_semilla.sql). / 插入种子数据。

Uso / 用法 (desde la carpeta backend / 在 backend 目录下):
    venv\\Scripts\\python.exe scripts\\inicializar_bd.py

Requiere que backend/.env tenga la contraseña correcta de PostgreSQL.
需要在 backend/.env 中填入正确的 PostgreSQL 密码。
"""

import sys
from pathlib import Path

import psycopg2
from psycopg2 import sql

# Permitir importar el paquete app / 允许导入 app 包
RAIZ_BACKEND = Path(__file__).resolve().parents[1]
sys.path.append(str(RAIZ_BACKEND))

from app.config.configuracion import configuracion  # noqa: E402

DIRECTORIO_SQL = RAIZ_BACKEND / "basedatos"


def _conectar(nombre_bd: str):
    """Abre una conexión psycopg2 a la base indicada / 打开数据库连接."""
    return psycopg2.connect(
        host=configuracion.bd_host,
        port=configuracion.bd_puerto,
        user=configuracion.bd_usuario,
        password=configuracion.bd_contrasena,
        dbname=nombre_bd,
    )


def crear_base_datos_si_no_existe() -> None:
    """Crea la base de datos del proyecto si aún no existe / 若不存在则建库."""
    conexion = _conectar("postgres")
    conexion.autocommit = True
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (configuracion.bd_nombre,),
            )
            if cursor.fetchone():
                print(f"  · La base '{configuracion.bd_nombre}' ya existe.")
            else:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(configuracion.bd_nombre)
                    )
                )
                print(f"  · Base '{configuracion.bd_nombre}' creada.")
    finally:
        conexion.close()


def _esquema_ya_aplicado(cursor) -> bool:
    """Indica si el esquema ya fue creado (existe la tabla roles) / 表结构是否已存在."""
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'roles'
        )
        """)
    return cursor.fetchone()[0]


def _ejecutar_sql(cursor, ruta: Path) -> None:
    print(f"  · Ejecutando {ruta.name} …")
    cursor.execute(ruta.read_text(encoding="utf-8"))


def aplicar_esquema_y_semillas() -> None:
    """Aplica el esquema y los datos semilla en una transacción / 事务内应用表结构与种子."""
    conexion = _conectar(configuracion.bd_nombre)
    try:
        with conexion.cursor() as cursor:
            if _esquema_ya_aplicado(cursor):
                print("  · El esquema ya existe; se omite 01_esquema.sql.")
            else:
                _ejecutar_sql(cursor, DIRECTORIO_SQL / "01_esquema.sql")
            _ejecutar_sql(cursor, DIRECTORIO_SQL / "02_datos_semilla.sql")
        conexion.commit()
        print("  · Esquema y datos semilla aplicados.")
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def main() -> None:
    print("Inicializando base de datos / 正在初始化数据库 …")
    try:
        crear_base_datos_si_no_existe()
        aplicar_esquema_y_semillas()
    except psycopg2.OperationalError as error:
        print("\n[ERROR] No se pudo conectar a PostgreSQL / 无法连接数据库。")
        print(
            "Revisa BD_USUARIO y BD_CONTRASENA en backend/.env / 请检查 .env 中的用户与密码。"
        )
        print(f"Detalle / 详情: {error}")
        sys.exit(1)
    print(
        "\n¡Listo! Base de datos inicializada correctamente. / 完成！数据库初始化成功。"
    )


if __name__ == "__main__":
    main()
