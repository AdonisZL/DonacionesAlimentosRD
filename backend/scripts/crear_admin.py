"""Crea (o reutiliza) el usuario administrador / 创建（或复用）管理员用户.

El rol administrador NO se puede auto-registrar por la API (RF-28); este script
lo crea directamente en la base de datos.
管理员角色无法通过 API 自助注册（RF-28），本脚本直接在数据库中创建。

Uso (desde backend): venv\\Scripts\\python.exe scripts\\crear_admin.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.database.conexion import SesionLocal  # noqa: E402
from app.models.rol import Rol  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402
from app.utils.seguridad import hashear_contrasena  # noqa: E402

EMAIL = "admin.demo@ejemplo.com"
CLAVE = "AdminRD2026!"


def main() -> None:
    with SesionLocal() as sesion:
        rol_admin = sesion.execute(
            select(Rol).where(Rol.nombre == "administrador")
        ).scalar_one()

        existente = sesion.execute(
            select(Usuario).where(Usuario.email == EMAIL)
        ).scalar_one_or_none()
        if existente:
            existente.contrasena_hash = hashear_contrasena(CLAVE)
            existente.estado = "activo"
            existente.email_verificado = True
            sesion.commit()
            print(f"Administrador actualizado: {EMAIL} / {CLAVE}")
            return

        admin = Usuario(
            nombre="Administrador",
            apellido="del Sistema",
            email=EMAIL,
            contrasena_hash=hashear_contrasena(CLAVE),
            id_rol=rol_admin.id_rol,
            estado="activo",
            email_verificado=True,
        )
        sesion.add(admin)
        sesion.commit()
        print(f"Administrador creado: {EMAIL} / {CLAVE}")


if __name__ == "__main__":
    main()
