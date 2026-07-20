"""Servicio de IA simulada / 模拟 AI 服务 (RF-18).

Al inicio NO se llama a Gemini: se genera una justificación narrativa
determinista (temperatura 0.0 conceptual) a partir de los datos del match.
Sustituible por la API real de Gemini más adelante.
初期不调用 Gemini：根据匹配数据生成确定性的叙述性说明。日后可替换为真实 API。
"""

MODELO_SIMULADO = "gemini-simulado-1.0"


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
