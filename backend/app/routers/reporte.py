"""Rutas de reportes / 报表路由 (OE4, RF-23 … RF-27).

Donaciones, inventario, asignaciones, exportación a Sheets y reporte fiscal.
捐赠、库存、分配、导出表格与财务报表。
"""

import uuid
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database.conexion import obtener_sesion
from app.models.usuario import Usuario
from app.schemas.reporte import (
    ReporteAsignaciones,
    ReporteDonaciones,
    ReporteLeer,
    SolicitudCertificado,
    SolicitudExportacion,
    SolicitudFiscal,
)
from app.services import servicio_reportes
from app.utils.dependencias import obtener_usuario_actual

enrutador = APIRouter(prefix="/api/reportes", tags=["reportes"])


@enrutador.get("/donaciones", response_model=ReporteDonaciones)
def reporte_donaciones(
    desde: date | None = None,
    hasta: date | None = None,
    id_donante: uuid.UUID | None = None,
    id_categoria: int | None = None,
    estado: str | None = None,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Reporte de donaciones por período (RF-23) / 按期捐赠报表."""
    return servicio_reportes.reporte_donaciones(
        sesion,
        usuario,
        desde=desde,
        hasta=hasta,
        id_donante=id_donante,
        id_categoria=id_categoria,
        estado=estado,
    )


@enrutador.get("/inventario")
def reporte_inventario(
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Reporte de inventario actual en orden FEFO (RF-24) / 当前库存报表."""
    return servicio_reportes.reporte_inventario(sesion, usuario)


@enrutador.get("/asignaciones", response_model=ReporteAsignaciones)
def reporte_asignaciones(
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Reporte de asignaciones completadas (RF-25) / 已完成分配报表."""
    return servicio_reportes.reporte_asignaciones(sesion, usuario)


@enrutador.post("/exportar-sheets", status_code=status.HTTP_201_CREATED)
def exportar_sheets(
    datos: SolicitudExportacion,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Exporta un reporte a Google Sheets (simulado, RF-26) / 导出到表格（模拟）."""
    try:
        return servicio_reportes.exportar_sheets(
            sesion, usuario, datos.tipo, desde=datos.desde, hasta=datos.hasta
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@enrutador.post("/fiscal", status_code=status.HTTP_201_CREATED)
def reporte_fiscal(
    datos: SolicitudFiscal,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Genera un reporte fiscal DGII inmutable (simulado, RF-27) / 生成不可变财务报表."""
    try:
        return servicio_reportes.reporte_fiscal(
            sesion,
            usuario,
            datos.anio,
            datos.mes,
            id_reporte_rectificado=datos.id_reporte_rectificado,
        )
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@enrutador.get("", response_model=list[ReporteLeer])
def listar_reportes(
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Lista los reportes generados por el usuario / 列出用户生成的报表."""
    return servicio_reportes.listar_reportes(sesion, usuario)


@enrutador.post("/lotes/{id_lote}/certificado-pdf")
def certificado_pdf(
    id_lote: uuid.UUID,
    datos: SolicitudCertificado,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Genera y descarga la certificación fiscal PDF de un lote (Ley 11-92)."""
    try:
        pdf_bytes, hash_documento, id_reporte = servicio_reportes.generar_certificado_pdf(
            sesion,
            usuario,
            id_lote,
            rnc_donante=datos.rnc_donante,
            valor_total_rd=Decimal(str(datos.valor_total_rd)),
        )
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="certificado_{id_reporte}.pdf"',
            "X-Hash-Documento": hash_documento,
        },
    )


@enrutador.get("/dgii-606", response_class=PlainTextResponse)
def exportar_dgii_606(
    anio: int,
    mes: int,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Exporta los certificados fiscales del mes al formato DGII 606 (.txt)."""
    try:
        contenido = servicio_reportes.generar_dgii_606(sesion, usuario, anio, mes)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    return PlainTextResponse(
        content=contenido,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="DONACIONES_{anio:04d}_{mes:02d}.txt"'
        },
    )
