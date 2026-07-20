"""Prueba manual del flujo de autenticación / 认证流程手动测试.

Requiere el backend corriendo en http://127.0.0.1:8000.
需要后端运行在 http://127.0.0.1:8000。

Uso / 用法 (desde backend):
    venv\\Scripts\\python.exe scripts\\probar_auth.py
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


def pedir(url, metodo="GET", datos=None, token=None):
    """Realiza una petición HTTP y devuelve (código, cuerpo JSON)."""
    cabeceras = {"Content-Type": "application/json"}
    if token:
        cabeceras["Authorization"] = f"Bearer {token}"
    cuerpo = json.dumps(datos).encode("utf-8") if datos is not None else None
    peticion = urllib.request.Request(
        url, data=cuerpo, headers=cabeceras, method=metodo
    )
    try:
        with urllib.request.urlopen(peticion) as respuesta:
            return respuesta.status, json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def main() -> None:
    with SesionLocal() as sesion:
        donante = sesion.execute(
            select(Rol).where(Rol.nombre == "donante")
        ).scalar_one()
        id_donante = str(donante.id_rol)

    email = "juan.test@ejemplo.com"
    datos = {
        "nombre": "Juan",
        "apellido": "Perez",
        "email": email,
        "contrasena": "Prueba123!",
        "id_rol": id_donante,
        "consentimiento_172_13": True,
    }

    cod, resp = pedir(f"{BASE}/api/auth/registro", "POST", datos)
    if cod == 201:
        print(f"1) Registro: {cod} OK -> {resp['usuario']['email']}")
    else:
        print(f"1) Registro: {cod} -> {resp}")

    cod, login = pedir(
        f"{BASE}/api/auth/login", "POST", {"email": email, "contrasena": "Prueba123!"}
    )
    token = login.get("access_token") if cod == 200 else None
    print(f"2) Login: {cod} -> {'token recibido' if token else login}")

    if token:
        cod, yo = pedir(f"{BASE}/api/auth/yo", token=token)
        print(f"3) GET /yo: {cod} -> {yo.get('email')} | estado: {yo.get('estado')}")

    cod, _ = pedir(
        f"{BASE}/api/auth/registro",
        "POST",
        {**datos, "email": "debil@ejemplo.com", "contrasena": "corta"},
    )
    print(f"4) Contrasena debil (esperado 422): {cod}")

    cod, yo = pedir(f"{BASE}/api/auth/yo")
    print(f"5) GET /yo sin token (esperado 401): {cod}")


if __name__ == "__main__":
    main()
