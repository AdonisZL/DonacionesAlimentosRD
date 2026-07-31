"""Servicio de consulta RNC/Cédula — MegaPlus API / RNC/身份证查询服务 (DGII).

Proxy hacia la API de MegaPlus para consultar datos fiscales y de identidad
de la DGII. Incluye caché simple para evitar consultas repetidas.
代理 MegaPlus API 查询 DGII 税务和身份数据。包含简单缓存避免重复查询。
"""

import httpx
from app.config.configuracion import configuracion

# Tiempo de espera para la API externa / 外部 API 超时时间
_TIMEOUT_SEGUNDOS = 10.0

# Caché simple en memoria (dict) para evitar consultas repetidas
# 内存简单缓存，避免重复查询
_cache: dict[str, dict] = {}


def _url_base() -> str:
    """Devuelve la URL base de MegaPlus API / 返回 MegaPlus API 基础 URL."""
    return configuracion.megaplus_api_url.rstrip("/")


def consultar_por_rnc(rnc: str) -> dict:
    """Consulta la ficha completa de un contribuyente por RNC o Cédula.

    Args:
        rnc: RNC (9 dígitos) o Cédula (11 dígitos) sin guiones.

    Returns:
        Dict con los datos del contribuyente o error.
    """
    # Validar formato básico / 基本格式校验
    rnc_limpio = rnc.strip()
    if not rnc_limpio.isdigit() or len(rnc_limpio) not in (9, 11):
        return {
            "error": True,
            "codigo_http": 400,
            "mensaje": "El RNC debe tener 9 dígitos o la cédula 11 dígitos.",
            "rnc_consultado": rnc_limpio,
        }

    # Verificar caché / 检查缓存
    clave_cache = f"rnc_{rnc_limpio}"
    if clave_cache in _cache:
        return _cache[clave_cache]

    try:
        with httpx.Client(timeout=_TIMEOUT_SEGUNDOS) as cliente:
            respuesta = cliente.get(
                f"{_url_base()}/api/consulta",
                params={"rnc": rnc_limpio},
            )
            datos = respuesta.json()
            # Guardar en caché solo si fue exitoso / 仅成功时缓存
            if not datos.get("error") and datos.get("codigo_http") == 200:
                _cache[clave_cache] = datos
            return datos
    except httpx.TimeoutException:
        return {
            "error": True,
            "codigo_http": 504,
            "mensaje": "La consulta a la DGII excedió el tiempo de espera. Intente nuevamente.",
            "rnc_consultado": rnc_limpio,
        }
    except httpx.ConnectError:
        return {
            "error": True,
            "codigo_http": 503,
            "mensaje": "No se pudo conectar con el servicio de consulta DGII.",
            "rnc_consultado": rnc_limpio,
        }
    except Exception as e:
        return {
            "error": True,
            "codigo_http": 500,
            "mensaje": f"Error inesperado al consultar: {str(e)}",
            "rnc_consultado": rnc_limpio,
        }


def buscar_por_nombre(buscar: str) -> dict:
    """Busca contribuyentes cuyo nombre coincida parcialmente.

    Args:
        buscar: Término de búsqueda (nombre o razón social parcial).

    Returns:
        Dict con lista de resultados paginados.
    """
    buscar_limpio = buscar.strip()
    if len(buscar_limpio) < 3:
        return {
            "error": True,
            "codigo_http": 400,
            "mensaje": "El término de búsqueda debe tener al menos 3 caracteres.",
        }

    clave_cache = f"nombre_{buscar_limpio.lower()}"
    if clave_cache in _cache:
        return _cache[clave_cache]

    try:
        with httpx.Client(timeout=_TIMEOUT_SEGUNDOS) as cliente:
            respuesta = cliente.get(
                f"{_url_base()}/api/consulta/nombres",
                params={"buscar": buscar_limpio},
            )
            datos = respuesta.json()
            if not datos.get("error"):
                _cache[clave_cache] = datos
            return datos
    except httpx.TimeoutException:
        return {
            "error": True,
            "codigo_http": 504,
            "mensaje": "La búsqueda excedió el tiempo de espera.",
        }
    except Exception as e:
        return {
            "error": True,
            "codigo_http": 500,
            "mensaje": f"Error al buscar: {str(e)}",
        }
