"""Rutas de consulta RNC/Cédula / RNC/身份证查询路由.

Proxy hacia la API MegaPlus DGII para consultar datos fiscales.
代理 MegaPlus DGII API 查询税务数据。
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.rnc import BusquedaNombreSolicitud, ConsultaRNCSolicitud
from app.services import servicio_rnc

enrutador = APIRouter(prefix="/api/rnc", tags=["rnc"])


@enrutador.post("/consultar")
def consultar_rnc(datos: ConsultaRNCSolicitud):
    """Consulta datos fiscales por RNC o Cédula (DGII).

    Llama a la API de MegaPlus para obtener razón social, nombre comercial,
    estado, actividad económica y más del contribuyente.
    通过 MegaPlus API 查询纳税人的公司名、商号、状态、经济活动等税务数据。
    """
    resultado = servicio_rnc.consultar_por_rnc(datos.rnc)

    if resultado.get("error"):
        codigo = resultado.get("codigo_http", 502)
        raise HTTPException(
            status_code=min(codigo, 502),
            detail=resultado.get("mensaje", "Error al consultar RNC."),
        )

    return resultado


@enrutador.post("/buscar")
def buscar_por_nombre(datos: BusquedaNombreSolicitud):
    """Busca contribuyentes por nombre o razón social.

    Devuelve lista paginada de resultados que coinciden parcialmente
    con el término de búsqueda.
    按名称或公司名搜索纳税人，返回分页匹配结果列表。
    """
    resultado = servicio_rnc.buscar_por_nombre(datos.buscar)

    if resultado.get("error"):
        codigo = resultado.get("codigo_http", 502)
        raise HTTPException(
            status_code=min(codigo, 502),
            detail=resultado.get("mensaje", "Error al buscar."),
        )

    return resultado
