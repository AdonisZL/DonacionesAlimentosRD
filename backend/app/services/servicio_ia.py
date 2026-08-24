"""Servicio de IA simulada / 模拟 AI 服务 (RF-18).

Al inicio NO se llama a Gemini: se genera una justificación narrativa
determinista (temperatura 0.0 conceptual) a partir de los datos del match.
Sustituible por la API real de Gemini más adelante.
初期不调用 Gemini：根据匹配数据生成确定性的叙述性说明。日后可替换为真实 API。
"""

import re
import unicodedata

MODELO_SIMULADO = "gemini-simulado-1.0"

# RF-18: unidades de medida reconocidas en la declaración libre / 声明文本中识别的计量单位
_PATRON_CANTIDAD = re.compile(
    r"(\d+[.,]?\d*)\s*"
    r"(kilos?|kilogramos?|kg|libras?|lb|litros?|lts?|l|unidades?|uds?|cajas?|sacos?|fundas?|latas?)\b",
    re.IGNORECASE,
)
_PATRON_DIAS = re.compile(r"vence[n]?\s+en\s+(\d+)\s*d[ií]as?", re.IGNORECASE)
_PATRON_FECHA = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_PALABRAS_FRIO = ("congelad", "refrigerad", "frio", "frío", "nevera", "congelador")

_MAPA_UNIDADES = {
    "kilo": "kg", "kilos": "kg", "kilogramo": "kg", "kilogramos": "kg", "kg": "kg",
    "libra": "lb", "libras": "lb", "lb": "lb",
    "litro": "l", "litros": "l", "lt": "l", "lts": "l", "l": "l",
    "unidad": "unidad", "unidades": "unidad", "ud": "unidad", "uds": "unidad",
    "caja": "caja", "cajas": "caja",
    "saco": "saco", "sacos": "saco",
    "funda": "funda", "fundas": "funda",
    "lata": "lata", "latas": "lata",
}


def _normalizar(texto: str) -> str:
    """Quita acentos y pasa a minúsculas para comparar / 去除重音并转小写以便比较."""
    sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sin_acentos.lower()


def interpretar_texto_libre(texto: str, catalogo_productos: list[dict]) -> dict:
    """Normaliza una declaración en lenguaje natural a campos de lote (RF-18).

    Simula el paso de reconocimiento de entidades (NER) que en producción
    ejecutaría Gemini (temperatura 0.0): extrae producto, cantidad, unidad,
    fecha de vencimiento y necesidad de cadena de frío desde texto libre.
    No decide nada del motor determinista, solo propone datos para que el
    donante los confirme antes de guardar (validación humana obligatoria).
    模拟 NER 步骤：从自由文本中提取产品、数量、单位、到期日期和冷链需求，
    仅用于预填表单，最终由用户确认（人工强制校验）。
    """
    texto_normalizado = _normalizar(texto)

    # Producto: coincidencia por substring contra el catálogo conocido.
    id_producto = None
    nombre_producto = None
    for producto in catalogo_productos:
        nombre = producto.get("nombre_producto", "")
        if nombre and _normalizar(nombre) in texto_normalizado:
            id_producto = producto.get("id_producto")
            nombre_producto = nombre
            break

    # Cantidad y unidad de medida.
    cantidad = None
    unidad = None
    coincidencia = _PATRON_CANTIDAD.search(texto)
    if coincidencia:
        cantidad = float(coincidencia.group(1).replace(",", "."))
        unidad = _MAPA_UNIDADES.get(coincidencia.group(2).lower(), coincidencia.group(2).lower())

    # Ventana de vencimiento: fecha explícita o "vence en N días".
    fecha_vencimiento = None
    coincidencia_fecha = _PATRON_FECHA.search(texto)
    if coincidencia_fecha:
        fecha_vencimiento = coincidencia_fecha.group(0)
    else:
        coincidencia_dias = _PATRON_DIAS.search(texto_normalizado)
        if coincidencia_dias:
            fecha_vencimiento = f"+{coincidencia_dias.group(1)}d"

    # Cadena de frío mencionada en el texto.
    requiere_frio = any(palabra in texto_normalizado for palabra in _PALABRAS_FRIO)

    entidades = {
        "id_producto": id_producto,
        "nombre_producto_detectado": nombre_producto,
        "cantidad": cantidad,
        "unidad_medida": unidad,
        "fecha_vencimiento_sugerida": fecha_vencimiento,
        "requiere_cadena_frio": requiere_frio,
    }

    campos_detectados = sum(
        1 for v in (id_producto, cantidad, unidad, fecha_vencimiento) if v not in (None, False)
    )
    confianza = round(min(0.95, 0.4 + 0.15 * campos_detectados), 2)

    prompt = (
        "Extrae entidades (producto, cantidad, unidad, vencimiento, cadena de "
        f"frío) del siguiente texto de un donante: «{texto}»."
    )
    respuesta = (
        f"Detecté "
        + (f"{cantidad:g} {unidad} de {nombre_producto}" if cantidad and nombre_producto else "datos parciales")
        + (f", con vencimiento {fecha_vencimiento}" if fecha_vencimiento else "")
        + (". Requiere cadena de frío." if requiere_frio else ".")
    )

    return {
        "prompt": prompt,
        "respuesta": respuesta,
        "modelo": MODELO_SIMULADO,
        "tokens_usados": len(texto.split()),
        "confianza": confianza,
        "entidades": entidades,
    }


def generar_justificacion(
    nombre_producto: str,
    nombre_sede: str,
    distancia_km: float,
    radio_km: float,
    requiere_cadena_frio: bool,
    tiene_cadena_frio: bool,
    capacidad_diaria_kg: float | None,
) -> dict:
    """Devuelve una justificación narrativa determinista / 生成确定性说明.

    No altera el resultado del algoritmo: solo lo explica en lenguaje natural.
    不改变算法结果，仅用自然语言解释。
    """
    partes = [
        f"Se recomienda asignar «{nombre_producto}» a «{nombre_sede}» "
        f"por encontrarse a {distancia_km:.1f} km, dentro del radio de "
        f"{radio_km:.0f} km establecido."
    ]
    if requiere_cadena_frio:
        if tiene_cadena_frio:
            partes.append("El lote requiere cadena de frío y la sede dispone de ella.")
        else:
            partes.append(
                "Advertencia: el lote requiere cadena de frío que la sede no tiene."
            )
    if capacidad_diaria_kg is not None:
        partes.append(
            f"La capacidad diaria de la sede es de {capacidad_diaria_kg:.0f} kg."
        )

    texto = " ".join(partes)
    prompt = (
        "Explica de forma breve y objetiva por qué este receptor es adecuado "
        f"para el lote (producto={nombre_producto}, sede={nombre_sede}, "
        f"distancia={distancia_km:.1f}km, radio={radio_km:.0f}km)."
    )
    return {
        "prompt": prompt,
        "respuesta": texto,
        "modelo": MODELO_SIMULADO,
        "tokens_usados": len(texto.split()),
        "confianza": 0.95,
    }

