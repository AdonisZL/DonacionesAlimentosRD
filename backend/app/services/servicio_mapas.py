"""Servicio de mapas — Google Maps Distance Matrix / 地图服务 (RF-17).

Simula el cálculo de tiempos reales de viaje entre dos coordenadas
usando la API de Google Maps Distance Matrix.
(En modo simulación: estimación basada en distancia + factor de tráfico.)
模拟 Google Maps Distance Matrix API 计算两点间的实际行驶时间。

Cuando se integre la API real, reemplazar la función `_simular_tiempo()`
por la llamada HTTP a Google Maps Distance Matrix.
接入真实 API 时，将 `_simular_tiempo()` 替换为对 Google Maps 的 HTTP 调用。
"""

import math
import random

# Velocidad promedio urbana en km/h (RD) / 多米尼加城市平均车速
_VELOCIDAD_URBANA_KPH = 30.0

# Factor de tráfico aleatorio (±30%) / 随机交通系数
_FACTOR_TRAFICO_MIN = 0.8
_FACTOR_TRAFICO_MAX = 1.3


def _distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula la distancia en km entre dos puntos (fórmula Haversine).

    Calcula la distancia geodésica real, no la distancia en línea recta de PostGIS.
    使用 Haversine 公式计算两点间的真实地球距离（km）。
    """
    R = 6371.0  # Radio de la Tierra en km / 地球半径
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _simular_tiempo(distancia_km: float) -> tuple[float, float]:
    """Simula el tiempo de viaje y la distancia por carretera.

    En modo simulación:
    - distancia_google ≈ distancia_geodesica × 1.2 (carreteras no son rectas)
    - tiempo = distancia_google / velocidad × factor_tráfico

    模拟行驶时间与道路距离。模拟模式：
    - google 距离 ≈ 地理距离 × 1.2（道路非直线）
    - 时间 = google 距离 / 速度 × 交通系数
    """
    factor_ruta = 1.15 + random.uniform(-0.05, 0.15)  # 1.10–1.30
    distancia_google = distancia_km * factor_ruta
    factor_trafico = random.uniform(_FACTOR_TRAFICO_MIN, _FACTOR_TRAFICO_MAX)
    tiempo_min = (distancia_google / _VELOCIDAD_URBANA_KPH) * 60.0 * factor_trafico
    return round(distancia_google, 2), round(tiempo_min, 1)


def calcular_tiempo_viaje(
    lat_origen: float,
    lon_origen: float,
    lat_destino: float,
    lon_destino: float,
) -> dict:
    """Calcula distancia y tiempo de viaje entre dos puntos.

    Devuelve:
        {
            "distancia_google_km": float,  # Distancia por carretera / 道路距离
            "tiempo_estimado_min": float,  # Tiempo estimado de llegada / 预计到达时间
            "distancia_directa_km": float, # Distancia en línea recta / 直线距离
        }

    En producción, esto llamaría a la API de Google Maps Distance Matrix.
    生产环境中将调用 Google Maps Distance Matrix API。
    """
    distancia_directa = _distancia_haversine(
        lat_origen, lon_origen, lat_destino, lon_destino
    )
    distancia_google, tiempo = _simular_tiempo(distancia_directa)
    return {
        "distancia_google_km": distancia_google,
        "tiempo_estimado_min": tiempo,
        "distancia_directa_km": round(distancia_directa, 2),
    }


def ordenar_por_tiempo_llegada(
    candidatos: list[dict],
) -> list[dict]:
    """Ordena una lista de candidatos por tiempo estimado de llegada (ascendente).

    Cada candidato debe tener "latitud" y "longitud".
    Se usa como criterio de desempate después del FEFO (RN-14).
    按预计到达时间升序排列候选人列表，作为 FEFO 后的排序依据。
    """
    # La lógica principal se integra en buscar_candidatos() del servicio_emparejamiento.
    # Esta función es auxiliar para cuando se necesite ordenar fuera de ese flujo.
    # 主要逻辑集成在 servicio_emparejamiento 的 buscar_candidatos() 中。
    return sorted(
        candidatos,
        key=lambda c: c.get("tiempo_estimado_min", float("inf")),
    )
