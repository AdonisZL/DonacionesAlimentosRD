"""Datos de demostración / 演示数据 (para probar en el navegador).

Crea usuarios con credenciales conocidas, productos, lotes con distintos
vencimientos (algunos en alerta) y emparejamientos en varios estados.
Idempotente: si un usuario ya existe, inicia sesión en lugar de recrearlo.
幂等：用户已存在则登录。

Uso (desde backend): venv\\Scripts\\python.exe scripts\\datos_demo.py
Requiere el backend corriendo en http://127.0.0.1:8000.
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
CLAVE = "DemoRD2026!"


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


def registrar_o_login(datos):
    cod, resp = pedir("/api/auth/registro", datos)
    if cod == 201:
        return resp["access_token"], resp["usuario"]["id_usuario"], True
    cod, resp = pedir("/api/auth/login", {"email": datos["email"], "contrasena": CLAVE})
    return resp.get("access_token"), resp.get("usuario", {}).get("id_usuario"), False


def ids_catalogos():
    with SesionLocal() as sesion:
        roles = {
            r.nombre: str(r.id_rol) for r in sesion.execute(select(Rol)).scalars().all()
        }
        categorias = {
            c.nombre_categoria: c.id_categoria_alimento
            for c in sesion.execute(select(CategoriaAlimento)).scalars().all()
        }
        perecibilidad = {
            p.nombre: p.id_perecibilidad
            for p in sesion.execute(select(CategoriaPerecibilidad)).scalars().all()
        }
    return roles, categorias, perecibilidad


def main() -> None:
    roles, cat, pere = ids_catalogos()

    # --- Usuarios de demo / 演示用户 -------------------------------------
    print("Creando usuarios de demo…")
    token_banco, _, _ = registrar_o_login(
        {
            "nombre": "Banco Central de Alimentos",
            "email": "banco.demo@ejemplo.com",
            "contrasena": CLAVE,
            "id_rol": roles["banco_alimentos"],
            "consentimiento_172_13": True,
            "rnc": "13100000001",
            "direccion_texto": "Av. 27 de Febrero 100, Santo Domingo",
            "latitud": 18.4861,
            "longitud": -69.9312,
            "capacidad_diaria_kg": 800,
            "tiene_cadena_frio": True,
            "horario_atencion": "Lun-Vie 8:00-17:00",
        }
    )

    token_donante, _, _ = registrar_o_login(
        {
            "nombre": "Supermercado La Sirena",
            "email": "donante.demo@ejemplo.com",
            "contrasena": CLAVE,
            "id_rol": roles["donante"],
            "subtipo_donante": "formal",
            "consentimiento_172_13": True,
            "rnc": "13100000002",
            "direccion_texto": "Av. Winston Churchill 50, Santo Domingo",
            "latitud": 18.4700,
            "longitud": -69.9400,
            "capacidad_diaria_kg": 300,
        }
    )

    registrar_o_login(
        {
            "nombre": "Comedor Esperanza",
            "email": "comedor.demo@ejemplo.com",
            "contrasena": CLAVE,
            "id_rol": roles["receptor"],
            "consentimiento_172_13": True,
            "direccion_texto": "Calle Duarte 20, Santo Domingo",
            "latitud": 18.5000,
            "longitud": -69.9450,
            "capacidad_diaria_kg": 250,
            "tiene_cadena_frio": True,
        }
    )

    registrar_o_login(
        {
            "nombre": "Fundación Manos Unidas",
            "email": "fundacion.demo@ejemplo.com",
            "contrasena": CLAVE,
            "id_rol": roles["receptor"],
            "consentimiento_172_13": True,
            "direccion_texto": "Av. Máximo Gómez 80, Santo Domingo",
            "latitud": 18.4950,
            "longitud": -69.9100,
            "capacidad_diaria_kg": 150,
            "tiene_cadena_frio": False,
        }
    )

    # --- Productos y lotes / 产品与批次 ----------------------------------
    # (nombre, categoría, perecibilidad, unidad, cadena_frio_producto)
    productos = [
        ("Arroz Selecto 5kg", "Granos y cereales", "No perecedero", "saco"),
        ("Atún enlatado 140g", "Enlatados y conservas", "No perecedero", "lata"),
        ("Pan integral", "Panadería y repostería", "Perecedero", "unidad"),
        ("Leche entera 1L", "Lácteos y huevos", "Perecedero", "litro"),
        ("Plátanos maduros", "Frutas y vegetales", "Semi-perecedero", "kg"),
        ("Pollo congelado", "Alimentos congelados", "Congelado", "kg"),
    ]

    def crear_producto(token, nombre, categoria, perecibilidad, unidad):
        cod, resp = pedir(
            "/api/inventario/productos",
            {
                "nombre_producto": nombre,
                "id_categoria_alimento": cat[categoria],
                "id_perecibilidad": pere[perecibilidad],
                "unidad_predeterminada": unidad,
            },
            token=token,
        )
        return resp.get("id_producto")

    def crear_lote(token, id_producto, cantidad, unidad, dias, peso):
        return pedir(
            "/api/inventario/lotes",
            {
                "id_producto": id_producto,
                "cantidad_disponible": cantidad,
                "unidad_medida": unidad,
                "peso_total": peso,
                "fecha_vencimiento": str(date.today() + timedelta(days=dias)),
            },
            token=token,
        )

    print("Creando productos y lotes del banco…")
    ids_prod = {}
    for nombre, categoria, perecibilidad, unidad in productos:
        ids_prod[nombre] = crear_producto(
            token_banco, nombre, categoria, perecibilidad, unidad
        )

    # Lotes del banco (con vencimientos variados; algunos en alerta <=3 días)
    lotes_banco = [
        ("Arroz Selecto 5kg", 40, "saco", 60, 200),
        ("Atún enlatado 140g", 120, "lata", 90, 17),
        ("Pan integral", 30, "unidad", 2, 15),  # alerta
        ("Leche entera 1L", 50, "litro", 3, 50),  # alerta (cadena de frío)
        ("Plátanos maduros", 80, "kg", 6, 80),
        ("Pollo congelado", 60, "kg", 45, 60),
    ]
    for nombre, cant, unidad, dias, peso in lotes_banco:
        crear_lote(token_banco, ids_prod[nombre], cant, unidad, dias, peso)

    # Lotes del donante (usa sus propios productos)
    print("Creando productos y lotes del donante…")
    prod_donante = crear_producto(
        token_donante, "Vegetales mixtos", "Frutas y vegetales", "Semi-perecedero", "kg"
    )
    for cant, dias, peso in [(25, 2, 25), (40, 10, 40), (15, 20, 15)]:
        crear_lote(token_donante, prod_donante, cant, "kg", dias, peso)

    # --- Emparejamientos de demo / 演示匹配 ------------------------------
    print("Creando emparejamientos de demo…")
    # Lote no perecedero del banco (arroz) -> buscar receptores y emparejar
    cod, lotes = pedir("/api/inventario/lotes", metodo="GET", token=token_banco)
    if not isinstance(lotes, list):
        print(f"  [aviso] No se pudieron leer los lotes ({cod}): {lotes}")
        lotes = []
    lote_arroz = next(
        (l for l in lotes if l["nombre_producto"] == "Arroz Selecto 5kg"), None
    )
    lote_atun = next(
        (l for l in lotes if l["nombre_producto"] == "Atún enlatado 140g"), None
    )

    def emparejar(lote, confirmar=False, completar=False):
        if not lote:
            return
        cod, cands = pedir(
            "/api/emparejamientos/candidatos",
            {"id_lote": lote["id_lote"], "radio_km": 25},
            token=token_banco,
        )
        compat = next((c for c in cands if c.get("compatible")), None)
        if not compat:
            return
        cod, emp = pedir(
            "/api/emparejamientos",
            {"id_lote": lote["id_lote"], "id_sede": compat["id_sede"], "radio_km": 25},
            token=token_banco,
        )
        id_emp = emp.get("id_emparejamiento")
        if id_emp and confirmar:
            pedir(f"/api/emparejamientos/{id_emp}/confirmar", token=token_banco)
        if id_emp and completar:
            pedir(f"/api/emparejamientos/{id_emp}/completar", token=token_banco)

    emparejar(lote_arroz, confirmar=True, completar=True)  # asignación completada
    emparejar(lote_atun, confirmar=False)  # emparejamiento sugerido (pendiente)

    print("\n=== ¡Datos de demo listos! / 演示数据已就绪 ===")
    print("Credenciales (contraseña común: DemoRD2026!) / 登录凭证：")
    print("  · Banco:      banco.demo@ejemplo.com")
    print("  · Donante:    donante.demo@ejemplo.com")
    print("  · Receptor 1: comedor.demo@ejemplo.com")
    print("  · Receptor 2: fundacion.demo@ejemplo.com")
    print(
        "\nInicia sesión como 'banco.demo' para ver inventario, emparejamientos y reportes."
    )


if __name__ == "__main__":
    main()
