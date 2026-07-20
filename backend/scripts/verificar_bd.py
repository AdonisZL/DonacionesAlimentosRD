"""Verifica el estado de la base de datos / 验证数据库状态.

Muestra el número de tablas base, la versión de PostGIS y los datos semilla.
显示基础表数量、PostGIS 版本与种子数据。

Uso / 用法 (desde la carpeta backend / 在 backend 目录下):
    venv\\Scripts\\python.exe scripts\\verificar_bd.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from app.database.conexion import motor  # noqa: E402


def main() -> None:
    with motor.connect() as con:
        tablas = con.execute(
            text(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
            )
        ).scalar()
        postgis = con.execute(
            text("SELECT extversion FROM pg_extension WHERE extname = 'postgis'")
        ).scalar()
        roles = [
            r[0] for r in con.execute(text("SELECT nombre FROM roles ORDER BY nombre"))
        ]
        perecibilidad = [
            (p[0], p[1])
            for p in con.execute(
                text(
                    "SELECT nombre, dias_minimos_ventana FROM categorias_perecibilidad "
                    "ORDER BY id_perecibilidad"
                )
            )
        ]
        categorias = con.execute(
            text("SELECT count(*) FROM categorias_alimentos")
        ).scalar()

    print(f"Tablas base (public) / 基础表数量: {tablas}")
    print(f"PostGIS: {postgis}")
    print(f"Roles ({len(roles)}): {roles}")
    print(f"Perecibilidad ({len(perecibilidad)}): {perecibilidad}")
    print(f"Categorias de alimentos / 食物分类数量: {categorias}")


if __name__ == "__main__":
    main()
