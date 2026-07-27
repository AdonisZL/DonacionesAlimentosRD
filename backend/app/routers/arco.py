"""Rutas de derechos ARCO / ARCO 权利路由 (RN-19, Ley 172-13).

Permite a los usuarios crear solicitudes ARCO y consultar su estado,
y al administrador listar todas las solicitudes y resolverlas.
允许用户创建 ARCO 请求并查询状态，管理员可列出并解决所有请求。
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.conexion import obtener_sesion
from app.models.usuario import Usuario
from app.schemas.arco import (
    SolicitudArcoCrear,
    SolicitudArcoLeer,
    SolicitudArcoResolver,
)
from app.services import servicio_arco, servicio_auditoria
from app.utils.dependencias import obtener_usuario_actual, requerir_roles

enrutador = APIRouter(prefix="/api/arco", tags=["arco"])

solo_admin = requerir_roles("administrador")


@enrutador.post(
    "/solicitudes",
    response_model=SolicitudArcoLeer,
    status_code=status.HTTP_201_CREATED,
)
def crear_solicitud_arco(
    datos: SolicitudArcoCrear,
    request: Request,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Crea una solicitud de derecho ARCO (acceso/rectificación/cancelación/oposición).

    El usuario autenticado ejerce uno de los 4 derechos ARCO
    conforme a la Ley 172-13. El plazo máximo de respuesta es 15 días hábiles.
    认证用户行使 4 项 ARCO 权利之一，最长 15 个工作日响应。
    """
    try:
        solicitud = servicio_arco.crear_solicitud(sesion, usuario, datos)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err

    # Auditoría: registrar la creación de una solicitud ARCO / 审计：记录 ARCO 请求创建
    servicio_auditoria.registrar(
        sesion=sesion,
        accion="solicitud_arco_creada",
        id_usuario=usuario.id_usuario,
        entidad="solicitudes_arco",
        id_entidad=str(solicitud.id_solicitud),
        ip_origen=request.client.host if request.client else None,
    )
    return solicitud


@enrutador.get("/mis-solicitudes", response_model=list[SolicitudArcoLeer])
def mis_solicitudes_arco(
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Lista las solicitudes ARCO del usuario autenticado / 列出当前用户的 ARCO 请求."""
    return servicio_arco.mis_solicitudes(sesion, usuario)


@enrutador.get("/admin/todas", response_model=list[SolicitudArcoLeer])
def listar_todas_solicitudes(
    sesion: Session = Depends(obtener_sesion),
    _admin: Usuario = Depends(solo_admin),
):
    """Lista todas las solicitudes ARCO (solo admin) / 列出所有 ARCO 请求（仅管理员）."""
    # Marcar vencidas antes de listar / 列出前先标记过期的
    servicio_arco.marcar_vencidas(sesion)
    return servicio_arco.listar_todas(sesion)


@enrutador.put("/admin/{id_solicitud}/resolver", response_model=SolicitudArcoLeer)
def resolver_solicitud_arco(
    id_solicitud: uuid.UUID,
    datos: SolicitudArcoResolver,
    request: Request,
    sesion: Session = Depends(obtener_sesion),
    admin: Usuario = Depends(solo_admin),
):
    """Resuelve (aprueba o rechaza) una solicitud ARCO (solo admin).

    Solo el administrador puede resolver solicitudes ARCO.
    Debe proporcionar una respuesta oficial al titular.
    仅管理员可解决 ARCO 请求，需提供对申请人的正式回复。
    """
    try:
        solicitud = servicio_arco.resolver_solicitud(
            sesion,
            id_solicitud,
            datos.estado,
            datos.respuesta,
            admin.id_usuario,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err

    servicio_auditoria.registrar(
        sesion=sesion,
        accion="solicitud_arco_resuelta",
        id_usuario=admin.id_usuario,
        entidad="solicitudes_arco",
        id_entidad=str(id_solicitud),
        ip_origen=request.client.host if request.client else None,
    )
    return solicitud
