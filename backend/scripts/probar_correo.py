"""Prueba de verificación de correo y recuperación / 邮箱验证与找回密码测试 (RF-06, RF-05).

Requiere el backend corriendo. / 需要后端运行。
Uso (desde backend): venv\\Scripts\\python.exe scripts\\probar_correo.py
"""

import json
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.database.conexion import SesionLocal  # noqa: E402
from app.models.rol import Rol  # noqa: E402
from app.models.token_recuperacion import TokenRecuperacion  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402
from app.utils.seguridad import (  # noqa: E402
    crear_token_verificacion,
    generar_token_aleatorio,
    hashear_token,
)

BASE = "http://127.0.0.1:8000"


def pedir(ruta, datos=None, metodo="POST"):
    cuerpo = json.dumps(datos).encode("utf-8") if datos is not None else None
    peticion = urllib.request.Request(
        f"{BASE}{ruta}",
        data=cuerpo,
        headers={"Content-Type": "application/json"},
        method=metodo,
    )
    try:
        with urllib.request.urlopen(peticion) as respuesta:
            return respuesta.status
    except urllib.error.HTTPError as error:
        return error.code


def main() -> None:
    email = "correo.test@ejemplo.com"
    with SesionLocal() as sesion:
        donante = sesion.execute(
            select(Rol).where(Rol.nombre == "donante")
        ).scalar_one()
        usuario = sesion.execute(
            select(Usuario).where(Usuario.email == email)
        ).scalar_one_or_none()
        if usuario is None:
            pedir(
                "/api/auth/registro",
                {
                    "nombre": "Correo Test",
                    "email": email,
                    "contrasena": "Correo2026!",
                    "id_rol": str(donante.id_rol),
                    "consentimiento_172_13": True,
                },
            )
            usuario = sesion.execute(
                select(Usuario).where(Usuario.email == email)
            ).scalar_one()
        id_usuario = str(usuario.id_usuario)

    # RF-06: verificación de correo
    token_v = crear_token_verificacion(id_usuario)
    cod = pedir(f"/api/auth/verificar-correo?token={token_v}", metodo="GET")
    print(f"1) Verificar correo (esperado 200): {cod}")
    with SesionLocal() as sesion:
        u = sesion.get(Usuario, uuid.UUID(id_usuario))
        print(f"2) email_verificado en BD: {u.email_verificado}")

    cod = pedir("/api/auth/verificar-correo?token=token_malo", metodo="GET")
    print(f"3) Token de verificación inválido (esperado 400): {cod}")

    # RF-05: solicitar recuperación (imprime el enlace en la consola del backend)
    cod = pedir("/api/auth/recuperar-password", {"email": email})
    print(f"4) Solicitar recuperación (esperado 200): {cod}")

    # RF-05: crear un token propio y restablecer
    token_r = generar_token_aleatorio()
    with SesionLocal() as sesion:
        sesion.add(
            TokenRecuperacion(
                id_usuario=uuid.UUID(id_usuario),
                token_hash=hashear_token(token_r),
                expira_en=datetime.now(timezone.utc) + timedelta(minutes=15),
            )
        )
        sesion.commit()

    cod = pedir(
        "/api/auth/restablecer-password",
        {"token": token_r, "nueva_contrasena": "NuevaClave2026!"},
    )
    print(f"5) Restablecer contraseña (esperado 200): {cod}")

    cod = pedir("/api/auth/login", {"email": email, "contrasena": "NuevaClave2026!"})
    print(f"6) Login con la nueva contraseña (esperado 200): {cod}")

    cod = pedir(
        "/api/auth/restablecer-password",
        {"token": token_r, "nueva_contrasena": "OtraClave2026!"},
    )
    print(f"7) Reusar token ya usado (esperado 400): {cod}")


if __name__ == "__main__":
    main()
