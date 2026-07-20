"""Rutas de administración / 管理路由 (OE5, RF-28/29/32).

Protegidas por RBAC (solo administrador): panel de métricas, gestión de
usuarios y consulta de la bitácora de auditoría.
受 RBAC 保护（仅管理员）：指标面板、用户管理与审计查询。
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.conexion import obtener_sesion
from app.models.usuario import Usuario
from app.schemas.admin import AuditoriaLeer, CambiarEstado, UsuarioAdmin
from app.services import servicio_admin, servicio_auditoria
from app.utils.dependencias import requerir_roles

enrutador = APIRouter(prefix="/api/admin", tags=["administracion"])

# RF-28: todas las rutas exigen rol administrador / 全部路由需管理员角色
solo_admin = requerir_roles("administrador")


@enrutador.get("/panel")
def panel(
    sesion: Session = Depends(obtener_sesion),
    _admin: Usuario = Depends(solo_admin),
):
    """Métricas del panel administrativo (RF-32) / 管理面板指标."""
    return servicio_admin.metricas_panel(sesion)


@enrutador.get("/usuarios", response_model=list[UsuarioAdmin])
def listar_usuarios(
    sesion: Session = Depends(obtener_sesion),
    _admin: Usuario = Depends(solo_admin),
):
    """Lista de usuarios del sistema / 系统用户列表."""
    return servicio_admin.listar_usuarios(sesion)


@enrutador.put("/usuarios/{id_usuario}/estado", response_model=UsuarioAdmin)
def cambiar_estado(
    id_usuario: uuid.UUID,
    datos: CambiarEstado,
    request: Request,
    sesion: Session = Depends(obtener_sesion),
    admin: Usuario = Depends(solo_admin),
):
    """Activa, desactiva o suspende una cuenta / 启用、停用或暂停账号 (RF-28)."""
    try:
        usuario = servicio_admin.cambiar_estado_usuario(
            sesion, id_usuario, datos.estado
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    # RF-29: auditoría del cambio de estado.
    servicio_auditoria.registrar(
        sesion,
        accion="cambiar_estado_usuario",
        id_usuario=admin.id_usuario,
        entidad="usuarios",
        id_entidad=id_usuario,
        detalles={"nuevo_estado": datos.estado},
        ip_origen=(request.client.host if request.client else None),
    )
    return _fila_usuario(sesion, usuario)


@enrutador.get("/auditoria", response_model=list[AuditoriaLeer])
def auditoria(
    sesion: Session = Depends(obtener_sesion),
    _admin: Usuario = Depends(solo_admin),
):
    """Bitácora de auditoría (RF-29) / 审计日志."""
    eventos = servicio_auditoria.listar(sesion, limite=100)
    return [
        AuditoriaLeer(
            id_bitacora=e.id_bitacora,
            id_usuario=e.id_usuario,
            accion=e.accion,
            entidad_afectada=e.entidad_afectada,
            id_entidad_afectada=e.id_entidad_afectada,
            ip_origen=str(e.ip_origen) if e.ip_origen is not None else None,
            creado_en=e.creado_en,
        )
        for e in eventos
    ]


def _fila_usuario(sesion: Session, usuario: Usuario) -> dict:
    """Adapta un usuario al esquema del panel / 转为面板用户行."""
    from app.models.rol import Rol

    rol = sesion.get(Rol, usuario.id_rol)
    return {
        "id_usuario": usuario.id_usuario,
        "nombre": f"{usuario.nombre} {usuario.apellido or ''}".strip(),
        "email": usuario.email,
        "rol": rol.nombre if rol else "",
        "estado": usuario.estado,
        "email_verificado": usuario.email_verificado,
        "creado_en": usuario.creado_en,
    }
