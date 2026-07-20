"""Prueba de reportería / 报表测试 (RF-23 … RF-27).

Usa el banco creado en pruebas anteriores (con lotes) y verifica: reporte de
donaciones con filtros (RF-23), inventario FEFO (RF-24), asignaciones completadas
(RF-25), exportación a Sheets simulada (RF-26) y reporte fiscal con cadena de hash
(RF-27, incluida la vinculación hash_anterior de dos reportes consecutivos).

Uso (desde backend): venv\\Scripts\\python.exe scripts\\probar_reportes.py
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

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
    # Banco creado en probar_emparejamiento.py (tiene lotes y una asignación).
    cod, resp = pedir(
        "/api/auth/login",
        {"email": "banco.match@ejemplo.com", "contrasena": "Emparejar2026!"},
    )
    token = resp.get("access_token")
    assert token, "Ejecuta primero probar_emparejamiento.py"

    # RF-23: donaciones
    cod, don = pedir("/api/reportes/donaciones", metodo="GET", token=token)
    print(f"1) Donaciones: {cod} -> {don['total_lotes']} lote(s), {don['total_kg']} kg")

    # RF-24: inventario FEFO
    cod, inv = pedir("/api/reportes/inventario", metodo="GET", token=token)
    ventanas = [l["ventana_dias"] for l in inv]
    print(f"2) Inventario FEFO: {cod} -> {len(inv)} lote(s), ventanas={ventanas}")

    # RF-25: asignaciones completadas
    cod, asig = pedir("/api/reportes/asignaciones", metodo="GET", token=token)
    print(f"3) Asignaciones completadas: {cod} -> {asig['total']}")

    # RF-26: exportación a Sheets (simulada)
    cod, exp = pedir(
        "/api/reportes/exportar-sheets", {"tipo": "donaciones"}, token=token
    )
    print(f"4) Exportar Sheets (esperado 201): {cod} -> {exp.get('url', '')[:48]}…")

    # RF-27: reporte fiscal + cadena de hash (dos reportes)
    cod, f1 = pedir("/api/reportes/fiscal", {"anio": 2026, "mes": 7}, token=token)
    print(
        f"5) Fiscal #1 (esperado 201): {cod}, hash={f1.get('hash', '')[:16]}…, anterior={f1.get('hash_anterior')}"
    )
    cod, f2 = pedir("/api/reportes/fiscal", {"anio": 2026, "mes": 7}, token=token)
    print(
        f"6) Fiscal #2 (esperado 201): {cod}, anterior={str(f2.get('hash_anterior'))[:16]}…"
    )
    print(f"   ¿Encadenado? {f2.get('hash_anterior') == f1.get('hash')}")

    # Lista de reportes generados
    cod, lista = pedir("/api/reportes", metodo="GET", token=token)
    print(f"7) Reportes guardados: {cod} -> {len(lista)}")

    print(
        "\nListo. Revisa: donaciones/inventario/asignaciones 200, export 201, fiscal encadenado."
    )


if __name__ == "__main__":
    main()
