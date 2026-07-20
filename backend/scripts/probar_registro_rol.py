"""Prueba de registro con campos por rol / 角色专属字段注册测试.

Registra un receptor con RNC + dirección + coordenadas y verifica que se
escribieron 'perfiles_legales' y 'direcciones_sedes'.
注册一个含 RNC、地址、坐标的接收方，并验证多表写入。

Uso (desde backend): venv\\Scripts\\python.exe scripts\\probar_registro_rol.py
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


def registrar(datos):
    peticion = urllib.request.Request(
        f"{BASE}/api/auth/registro",
        data=json.dumps(datos).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(peticion) as respuesta:
            return respuesta.status, json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def main() -> None:
    with SesionLocal() as sesion:
        receptor = sesion.execute(
            select(Rol).where(Rol.nombre == "receptor")
        ).scalar_one()
        id_receptor = str(receptor.id_rol)

    datos = {
        "nombre": "Comedor Esperanza",
        "email": "comedor.esperanza@ejemplo.com",
        "contrasena": "Receptor2026!",
        "id_rol": id_receptor,
        "rnc": "13112345678",
        "direccion_texto": "Av. Duarte 45, Santo Domingo",
        "latitud": 18.4861,
        "longitud": -69.9312,
        "capacidad_diaria_kg": 150.5,
        "tiene_cadena_frio": True,
        "horario_atencion": "Lun-Vie 8:00-16:00",
        "consentimiento_172_13": True,
    }

    cod, resp = registrar(datos)
    print(f"1) Registro receptor: {cod}")
    if cod != 201:
        print("   ->", resp)
        return

    id_usuario = resp["usuario"]["id_usuario"]
    with SesionLocal() as sesion:
        perfil = sesion.execute(
            text(
                "SELECT rnc FROM perfiles_legales WHERE id_usuario = CAST(:u AS uuid)"
            ),
            {"u": id_usuario},
        ).first()
        sede = sesion.execute(
            text(
                "SELECT direccion_texto, capacidad_diaria_kg, tiene_cadena_frio, "
                "ST_AsText(coordenadas::geometry) "
                "FROM direcciones_sedes WHERE id_usuario = CAST(:u AS uuid)"
            ),
            {"u": id_usuario},
        ).first()

    print(f"2) perfiles_legales.rnc: {perfil[0] if perfil else None}")
    print(f"3) direcciones_sedes: {tuple(sede) if sede else None}")

    cod2, _ = registrar({**datos, "email": "otro@ejemplo.com", "rnc": "123"})
    print(f"4) RNC invalido (esperado 422): {cod2}")


if __name__ == "__main__":
    main()
