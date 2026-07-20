"""Prueba de perfil, desactivación y consentimiento / RF-07, RF-08, RF-31.

Registra un usuario, verifica el consentimiento en BD, edita el perfil,
desactiva la cuenta y comprueba que ya no puede iniciar sesión (403).

Uso (desde backend): venv\\Scripts\\python.exe scripts\\probar_perfil.py
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select, text  # noqa: E402

from app.database.conexion import SesionLocal  # noqa: E402
from app.models.rol import Rol  # noqa: E402

BASE = "http://127.0.0.1:8000"


def pedir(ruta, datos=None, metodo="POST", token=None):
    cabeceras = {"Content-Type": "application/json"}
    if token:
        cabeceras["Authorization"] = f"Bearer {token}"
    cuerpo = json.dumps(datos).encode("utf-8") if datos is not None else None
    peticion = urllib.request.Request(
        f"{BASE}{ruta}", data=cuerpo, headers=cabeceras, method=metodo
    )
    try:
        with urllib.request.urlopen(peticion) as respuesta:
            return respuesta.status, json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        cuerpo_error = error.read().decode("utf-8")
        return error.code, json.loads(cuerpo_error) if cuerpo_error else {}


def main() -> None:
    with SesionLocal() as sesion:
        donante = sesion.execute(
            select(Rol).where(Rol.nombre == "donante")
        ).scalar_one()
        id_donante = str(donante.id_rol)

    email = "perfil.test@ejemplo.com"
    cod, resp = pedir(
        "/api/auth/registro",
        {
            "nombre": "Perfil Test",
            "email": email,
            "contrasena": "Perfil2026!",
            "id_rol": id_donante,
            "consentimiento_172_13": True,
        },
    )
    print(f"1) Registro: {cod}")
    if cod == 201:
        token = resp["access_token"]
        id_usuario = resp["usuario"]["id_usuario"]
    else:
        cod, resp = pedir(
            "/api/auth/login", {"email": email, "contrasena": "Perfil2026!"}
        )
        token = resp.get("access_token")
        id_usuario = resp.get("usuario", {}).get("id_usuario")

    with SesionLocal() as sesion:
        fila = sesion.execute(
            text(
                "SELECT tipo_consentimiento, aceptado FROM consentimiento_datos "
                "WHERE id_usuario = CAST(:u AS uuid) "
                "ORDER BY fecha_consentimiento DESC LIMIT 1"
            ),
            {"u": id_usuario},
        ).first()
    print(f"2) consentimiento_datos (RF-31): {tuple(fila) if fila else None}")

    cod, resp = pedir(
        "/api/auth/perfil",
        {"telefono": "809-555-1234", "apellido": "Editado"},
        metodo="PUT",
        token=token,
    )
    print(f"3) Editar perfil (esperado 200): {cod} -> apellido={resp.get('apellido')}")

    cod, _ = pedir("/api/auth/desactivar", metodo="POST", token=token)
    print(f"4) Desactivar cuenta (esperado 200): {cod}")

    cod, _ = pedir("/api/auth/login", {"email": email, "contrasena": "Perfil2026!"})
    print(f"5) Login tras desactivar (esperado 403): {cod}")


if __name__ == "__main__":
    main()
