"""Prueba de inventario FEFO / 库存 FEFO 测试 (RF-09 … RF-16).

Registra un banco de alimentos, crea un producto, registra lotes con distintas
fechas de vencimiento y verifica: orden FEFO (RF-12), alertas <=3 días (RF-13),
rechazo de vencidos (RF-14), ajuste manual con merma (RF-15) e historial (RF-16).

Uso (desde backend): venv\\Scripts\\python.exe scripts\\probar_inventario.py
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


def main() -> None:
    with SesionLocal() as sesion:
        id_banco = str(
            sesion.execute(select(Rol).where(Rol.nombre == "banco_alimentos"))
            .scalar_one()
            .id_rol
        )
        cat = sesion.execute(select(CategoriaAlimento)).scalars().first()
        pere = sesion.execute(
            select(CategoriaPerecibilidad).where(
                CategoriaPerecibilidad.nombre == "Perecedero"
            )
        ).scalar_one()
        id_cat = cat.id_categoria_alimento
        id_pere = pere.id_perecibilidad

    email = "banco.inv@ejemplo.com"
    cod, resp = pedir(
        "/api/auth/registro",
        {
            "nombre": "Banco Inventario",
            "email": email,
            "contrasena": "Inventario2026!",
            "id_rol": id_banco,
            "consentimiento_172_13": True,
        },
    )
    print(f"1) Registro banco: {cod}")
    if cod == 201:
        token = resp["access_token"]
    else:
        cod, resp = pedir(
            "/api/auth/login", {"email": email, "contrasena": "Inventario2026!"}
        )
        token = resp.get("access_token")
    assert token, "No se obtuvo token"

    # RF-09: crear producto
    cod, prod = pedir(
        "/api/inventario/productos",
        {
            "nombre_producto": "Leche entera 1L (prueba)",
            "id_categoria_alimento": id_cat,
            "id_perecibilidad": id_pere,
            "unidad_predeterminada": "unidad",
        },
        token=token,
    )
    print(f"2) Crear producto: {cod}")
    id_producto = prod["id_producto"]

    # RF-14: rechazo de lote vencido (fecha pasada -> 400/422)
    cod, _ = pedir(
        "/api/inventario/lotes",
        {
            "id_producto": id_producto,
            "cantidad_disponible": 10,
            "unidad_medida": "unidad",
            "fecha_vencimiento": str(date.today() - timedelta(days=1)),
        },
        token=token,
    )
    print(f"3) Rechazo lote vencido (esperado 400/422): {cod}")

    # RF-09: registrar 3 lotes con distintas fechas
    dias = [10, 2, 25]  # 2 días => alerta
    for d in dias:
        cod, _ = pedir(
            "/api/inventario/lotes",
            {
                "id_producto": id_producto,
                "cantidad_disponible": 20,
                "unidad_medida": "unidad",
                "fecha_vencimiento": str(date.today() + timedelta(days=d)),
            },
            token=token,
        )
        print(f"   · Lote vence en {d} días: {cod}")

    # RF-12: orden FEFO ascendente
    cod, lotes = pedir("/api/inventario/lotes", metodo="GET", token=token)
    ventanas = [l["ventana_dias"] for l in lotes]
    print(
        f"4) Lotes FEFO ventanas={ventanas} (¿ascendente? {ventanas == sorted(ventanas)})"
    )

    # RF-13: alertas <=3 días
    cod, alertas = pedir("/api/inventario/alertas", metodo="GET", token=token)
    print(f"5) Alertas <=3 días: {len(alertas)} lote(s)")

    # RF-15 + RF-16: ajuste manual (banco) y historial
    lote_alerta = next((l for l in lotes if l["ventana_dias"] == 2), lotes[0])
    id_lote = lote_alerta["id_lote"]
    cod, ajustado = pedir(
        f"/api/inventario/lotes/{id_lote}/ajuste",
        {"cantidad_afectada": 5, "motivo": "dano_fisico", "detalle": "Prueba"},
        token=token,
    )
    print(
        f"6) Ajuste banco (esperado 200): {cod} -> cantidad={ajustado.get('cantidad_disponible')}"
    )

    cod, hist = pedir(
        f"/api/inventario/lotes/{id_lote}/historial", metodo="GET", token=token
    )
    print(f"7) Historial del lote: {len(hist)} movimiento(s)")

    print(
        "\nListo. Revisa que: FEFO ascendente, alerta detectada, vencido rechazado, ajuste 200."
    )


if __name__ == "__main__":
    main()
