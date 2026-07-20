"""Rutas de roles / 角色路由.

Endpoint de prueba para verificar la conexión con la base de datos.
用于验证数据库连接的测试端点。
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.conexion import obtener_sesion
from app.models.rol import Rol
from app.schemas.rol import RolLeer

enrutador = APIRouter(prefix="/api/roles", tags=["roles"])


@enrutador.get("", response_model=list[RolLeer])
def listar_roles(sesion: Session = Depends(obtener_sesion)) -> list[Rol]:
    """Devuelve todos los roles ordenados por nombre / 返回所有角色（按名称排序）."""
    return sesion.execute(select(Rol).order_by(Rol.nombre)).scalars().all()
