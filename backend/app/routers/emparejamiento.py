"""Rutas de emparejamiento / 匹配路由 (OE3, RF-17 … RF-22).

Búsqueda de receptores, creación/confirmación/rechazo de matches,
finalización, retroalimentación y notificaciones.
接收方搜索、匹配创建/确认/拒绝、完成、反馈与通知。
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.conexion import obtener_sesion
from app.models.usuario import Usuario
from app.schemas.emparejamiento import (
    BuscarCandidatos,
    CandidatoEmparejamiento,
    EmparejamientoCrear,
    EmparejamientoLeer,
    NotificacionLeer,
    RetroalimentacionCrear,
)
from app.services import servicio_emparejamiento
from app.utils.dependencias import obtener_usuario_actual

enrutador = APIRouter(prefix="/api/emparejamientos", tags=["emparejamientos"])


@enrutador.post("/candidatos", response_model=list[CandidatoEmparejamiento])
def buscar_candidatos(
    datos: BuscarCandidatos,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Busca receptores compatibles por cercanía (RF-17/18) / 搜索附近兼容接收方."""
    try:
        return servicio_emparejamiento.buscar_candidatos(
            sesion, usuario, datos.id_lote, datos.radio_km
        )
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@enrutador.post(
    "", response_model=EmparejamientoLeer, status_code=status.HTTP_201_CREATED
)
def crear_emparejamiento(
    datos: EmparejamientoCrear,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Crea un emparejamiento sugerido con justificación de IA / 创建建议匹配."""
    try:
        emp = servicio_emparejamiento.crear_emparejamiento(
            sesion, usuario, datos.id_lote, datos.id_sede, datos.radio_km
        )
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return servicio_emparejamiento._enriquecer(sesion, emp)


@enrutador.get("", response_model=list[EmparejamientoLeer])
def listar_emparejamientos(
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Lista los emparejamientos del usuario / 列出用户的匹配."""
    return servicio_emparejamiento.listar_emparejamientos(sesion, usuario)


@enrutador.post("/{id_emparejamiento}/confirmar", response_model=EmparejamientoLeer)
def confirmar_emparejamiento(
    id_emparejamiento: uuid.UUID,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Confirma el emparejamiento y notifica (RF-19/21) / 确认匹配并通知."""
    try:
        emp = servicio_emparejamiento.confirmar_emparejamiento(
            sesion, usuario, id_emparejamiento
        )
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return servicio_emparejamiento._enriquecer(sesion, emp)


@enrutador.post("/{id_emparejamiento}/rechazar", response_model=EmparejamientoLeer)
def rechazar_emparejamiento(
    id_emparejamiento: uuid.UUID,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Rechaza el emparejamiento y libera el lote (RF-20) / 拒绝并释放批次."""
    try:
        emp = servicio_emparejamiento.rechazar_emparejamiento(
            sesion, usuario, id_emparejamiento
        )
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return servicio_emparejamiento._enriquecer(sesion, emp)


@enrutador.post("/{id_emparejamiento}/completar", status_code=status.HTTP_201_CREATED)
def completar_emparejamiento(
    id_emparejamiento: uuid.UUID,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Completa el emparejamiento y crea la entrega / 完成匹配并创建交付."""
    try:
        entrega = servicio_emparejamiento.completar_emparejamiento(
            sesion, usuario, id_emparejamiento
        )
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return {"id_entrega": str(entrega.id_entrega), "estado": entrega.estado_entrega}


@enrutador.post(
    "/{id_emparejamiento}/retroalimentacion", status_code=status.HTTP_201_CREATED
)
def crear_retroalimentacion(
    id_emparejamiento: uuid.UUID,
    datos: RetroalimentacionCrear,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Registra la calificación de la entrega (RF-22) / 记录交付评分."""
    try:
        retro = servicio_emparejamiento.crear_retroalimentacion(
            sesion, usuario, id_emparejamiento, datos
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return {
        "id_retroalimentacion": str(retro.id_retroalimentacion),
        "calificacion": retro.calificacion,
    }


@enrutador.get("/notificaciones", response_model=list[NotificacionLeer])
def listar_notificaciones(
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Notificaciones del usuario (RF-21) / 用户通知."""
    return servicio_emparejamiento.listar_notificaciones(sesion, usuario)


@enrutador.post(
    "/notificaciones/{id_notificacion}/leida", response_model=NotificacionLeer
)
def marcar_leida(
    id_notificacion: uuid.UUID,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Marca una notificación como leída / 将通知标记为已读."""
    try:
        return servicio_emparejamiento.marcar_notificacion_leida(
            sesion, usuario, id_notificacion
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
