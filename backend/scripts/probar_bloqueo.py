"""Prueba de bloqueo por intentos fallidos / 失败锁定测试 (RF-30).

Registra un usuario, falla 5 veces el login y comprueba que la 6.ª vez
(incluso con la contraseña correcta) la cuenta está bloqueada (423).
注册用户，登录失败5次，第6次即使密码正确也应被锁定 (423)。

Uso (desde backend): venv\\Scripts\\python.exe scripts\\probar_bloqueo.py
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.database.conexion import SesionLocal  # noqa: E402
from app.models.rol import Rol  # noqa: E402

BASE = "http://127.0.0.1:8000"


def pedir(ruta, datos):
    peticion = urllib.request.Request(
        f"{BASE}{ruta}",
        data=json.dumps(datos).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(peticion) as respuesta:
            return respuesta.status
    except urllib.error.HTTPError as error:
        return error.code


def main() -> None:
    with SesionLocal() as sesion:
        donante = sesion.execute(
            select(Rol).where(Rol.nombre == "donante")
        ).scalar_one()
        id_donante = str(donante.id_rol)

    email = "bloqueo.test@ejemplo.com"
    correcta = "Bloqueo2026!"

    cod = pedir(
        "/api/auth/registro",
        {
            "nombre": "Test Bloqueo",
            "email": email,
            "contrasena": correcta,
            "id_rol": id_donante,
            "consentimiento_172_13": True,
        },
    )
    print(f"Registro (201 nuevo / 409 si ya existe): {cod}")

    for intento in range(1, 6):
        codigo = pedir(
            "/api/auth/login", {"email": email, "contrasena": "Incorrecta1!"}
        )
        print(f"Intento fallido {intento} (esperado 401): {codigo}")

    codigo = pedir("/api/auth/login", {"email": email, "contrasena": correcta})
    print(f"6.º intento con contraseña correcta (esperado 423 bloqueado): {codigo}")


if __name__ == "__main__":
    main()
