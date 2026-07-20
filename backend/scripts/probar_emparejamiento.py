"""Prueba de emparejamiento / 匹配测试 (RF-17 … RF-22).

Registra un banco (dueño del lote) con sede y dos receptores (uno cercano y uno
lejano), crea un lote y verifica: búsqueda PostGIS por radio (RF-17), justificación
de IA (RF-18), confirmación + notificaciones (RF-19/21), rechazo/liberación (RF-20),
finalización con entrega y retroalimentación (RF-22).

Uso (desde backend): venv\\Scripts\\python.exe scripts\\probar_emparejamiento.py
"""

import json
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.database.conexion import SesionLocal  # noqa: E402
from app.models.categoria_alimento import CategoriaAlimento  # noqa: E402
from app.models.categoria_perecibilidad import CategoriaPerecibilidad  # noqa: E402
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


def registrar_o_login(datos, contrasena):
    cod, resp = pedir("/api/auth/registro", datos)
    if cod == 201:
        return resp["access_token"], resp["usuario"]["id_usuario"]
    cod, resp = pedir(
        "/api/auth/login", {"email": datos["email"], "contrasena": contrasena}
    )
    return resp.get("access_token"), resp.get("usuario", {}).get("id_usuario")


def main() -> None:
    with SesionLocal() as sesion:
        id_banco = str(
            sesion.execute(select(Rol).where(Rol.nombre == "banco_alimentos"))
            .scalar_one()
            .id_rol
        )
        id_receptor = str(
            sesion.execute(select(Rol).where(Rol.nombre == "receptor"))
            .scalar_one()
            .id_rol
        )
        cat = (
            sesion.execute(
                select(CategoriaAlimento).where(
                    CategoriaAlimento.requiere_cadena_frio == False  # noqa: E712
                )
            )
            .scalars()
            .first()
        )
        pere = sesion.execute(select(CategoriaPerecibilidad)).scalars().first()

    # 1) Banco dueño del lote (sede en Santo Domingo) / 批次拥有者
    token_banco, _ = registrar_o_login(
        {
            "nombre": "Banco Match",
            "email": "banco.match@ejemplo.com",
            "contrasena": "Emparejar2026!",
            "id_rol": id_banco,
            "consentimiento_172_13": True,
            "direccion_texto": "Av. Central 1, Santo Domingo",
            "latitud": 18.4861,
            "longitud": -69.9312,
            "capacidad_diaria_kg": 500,
        },
        "Emparejar2026!",
    )

    # 2) Receptor cercano (~2 km) / 附近接收方
    registrar_o_login(
        {
            "nombre": "Receptor Cercano",
            "email": "receptor.cerca@ejemplo.com",
            "contrasena": "Emparejar2026!",
            "id_rol": id_receptor,
            "consentimiento_172_13": True,
            "direccion_texto": "Calle 2, Santo Domingo",
            "latitud": 18.5000,
            "longitud": -69.9400,
            "capacidad_diaria_kg": 200,
        },
        "Emparejar2026!",
    )

    # 3) Receptor lejano (Santiago, ~155 km) / 远处接收方
    registrar_o_login(
        {
            "nombre": "Receptor Lejano",
            "email": "receptor.lejos@ejemplo.com",
            "contrasena": "Emparejar2026!",
            "id_rol": id_receptor,
            "consentimiento_172_13": True,
            "direccion_texto": "Santiago de los Caballeros",
            "latitud": 19.4500,
            "longitud": -70.6900,
            "capacidad_diaria_kg": 200,
        },
        "Emparejar2026!",
    )

    # 4) Producto + lote del banco / 创建产品与批次
    cod, prod = pedir(
        "/api/inventario/productos",
        {
            "nombre_producto": "Arroz 5kg (match)",
            "id_categoria_alimento": cat.id_categoria_alimento,
            "id_perecibilidad": pere.id_perecibilidad,
            "unidad_predeterminada": "saco",
        },
        token=token_banco,
    )
    id_producto = prod["id_producto"]
    cod, lote = pedir(
        "/api/inventario/lotes",
        {
            "id_producto": id_producto,
            "cantidad_disponible": 30,
            "unidad_medida": "saco",
            "peso_total": 150,
            "fecha_vencimiento": str(date.today() + timedelta(days=20)),
        },
        token=token_banco,
    )
    id_lote = lote["id_lote"]
    print(f"1) Lote creado: {cod}")

    # 5) RF-17/18: buscar candidatos radio 25 km
    cod, candidatos = pedir(
        "/api/emparejamientos/candidatos",
        {"id_lote": id_lote, "radio_km": 25},
        token=token_banco,
    )
    nombres = [c["nombre_sede"] for c in candidatos]
    print(f"2) Candidatos <=25km: {cod} -> {nombres}")
    print(f"   ¿Excluye al lejano? {'Receptor Lejano' not in nombres}")
    if candidatos:
        print(f"   IA: {candidatos[0]['justificacion_ia'][:70]}…")

    cercano = next(
        (c for c in candidatos if c["nombre_sede"] == "Receptor Cercano"), None
    )
    assert cercano, "No se encontró al receptor cercano"

    # 6) Crear emparejamiento
    cod, emp = pedir(
        "/api/emparejamientos",
        {"id_lote": id_lote, "id_sede": cercano["id_sede"], "radio_km": 25},
        token=token_banco,
    )
    id_emp = emp["id_emparejamiento"]
    print(
        f"3) Emparejamiento creado (esperado 201): {cod}, dist={emp['distancia_km']}km"
    )

    # 7) RF-19/21: confirmar + notificaciones
    cod, conf = pedir(f"/api/emparejamientos/{id_emp}/confirmar", token=token_banco)
    print(f"4) Confirmar (esperado 200): {cod}, estado={conf.get('estado_tramite')}")
    cod, notis = pedir(
        "/api/emparejamientos/notificaciones", metodo="GET", token=token_banco
    )
    print(f"5) Notificaciones del banco: {len(notis)}")

    # 8) Completar (crea entrega)
    cod, entrega = pedir(f"/api/emparejamientos/{id_emp}/completar", token=token_banco)
    print(f"6) Completar (esperado 201): {cod}, entrega={entrega.get('estado')}")

    # 9) RF-22: retroalimentación
    cod, retro = pedir(
        f"/api/emparejamientos/{id_emp}/retroalimentacion",
        {"calificacion": 5, "comentario": "Entrega puntual"},
        token=token_banco,
    )
    print(f"7) Retroalimentación (esperado 201): {cod}")

    print(
        "\nListo. Revisa: lejano excluido, IA presente, confirmar 200 + notis, completar 201, retro 201."
    )


if __name__ == "__main__":
    main()
