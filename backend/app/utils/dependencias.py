"""Dependencias de autenticación / 认证依赖.

Extrae y valida el usuario actual a partir del JWT (RF-28 base para RBAC).
从 JWT 中提取并校验当前用户（RBAC 基础）。
"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.conexion import obtener_sesion
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.utils.seguridad import decodificar_token

esquema_oauth = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def obtener_usuario_actual(
    token: str = Depends(esquema_oauth),
    sesion: Session = Depends(obtener_sesion),
) -> Usuario:
    """Devuelve el usuario autenticado o lanza 401 / 返回当前用户或抛 401."""
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    datos = decodificar_token(token)
    if datos is None:
        raise credenciales_invalidas

    id_usuario = datos.get("sub")
    if id_usuario is None:
        raise credenciales_invalidas
    try:
        id_uuid = uuid.UUID(str(id_usuario))
    except ValueError:
        raise credenciales_invalidas

    usuario = sesion.get(Usuario, id_uuid)
    if usuario is None:
        raise credenciales_invalidas
    return usuario


def requerir_roles(*nombres_rol: str):
    """Fábrica de dependencia RBAC / RBAC 依赖工厂 (RF-28).

    Devuelve una dependencia que exige que el usuario tenga uno de los roles
    indicados; de lo contrario responde 403.
    返回一个依赖：要求用户具备指定角色之一，否则返回 403。
    """

    def verificar(
        usuario: Usuario = Depends(obtener_usuario_actual),
        sesion: Session = Depends(obtener_sesion),
    ) -> Usuario:
        rol = sesion.get(Rol, usuario.id_rol)
        if rol is None or rol.nombre not in nombres_rol:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción.",
            )
        return usuario

    return verificar
