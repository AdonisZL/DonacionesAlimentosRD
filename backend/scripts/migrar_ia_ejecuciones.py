"""Migración puntual / 一次性迁移: ampliar ia_ejecuciones.tipo_ejecucion a VARCHAR(30).

El valor 'justificacion_narrativa' (23 caracteres) no cabía en VARCHAR(20).
'justificacion_narrativa'（23 字符）无法放入 VARCHAR(20)。

Uso (desde backend): venv\\Scripts\\python.exe scripts\\migrar_ia_ejecuciones.py
"""

import sys
from pathlib import Path

import psycopg2

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config.configuracion import configuracion  # noqa: E402


def main() -> None:
    conexion = psycopg2.connect(
        host=configuracion.bd_host,
        port=configuracion.bd_puerto,
        user=configuracion.bd_usuario,
        password=configuracion.bd_contrasena,
        dbname=configuracion.bd_nombre,
    )
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "ALTER TABLE ia_ejecuciones "
                "ALTER COLUMN tipo_ejecucion TYPE VARCHAR(30);"
            )
        conexion.commit()
        print("Columna ia_ejecuciones.tipo_ejecucion ampliada a VARCHAR(30).")
    finally:
        conexion.close()


if __name__ == "__main__":
    main()
