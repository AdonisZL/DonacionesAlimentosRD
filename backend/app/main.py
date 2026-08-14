"""Punto de entrada de la API / API 入口.

Registra middlewares (CORS) y los routers por dominio.
注册中间件（CORS）与各领域路由。
"""

import asyncio
import contextlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.configuracion import configuracion
from app.database.conexion import SesionLocal
from app.services import servicio_emparejamiento
from app.utils.cifrado import configurar_clave_aes

from app.routers import (
    admin,
    arco,
    autenticacion,
    emparejamiento,
    inventario,
    reporte,
    rnc,
    roles,
)

# RN-12: intervalo de la tarea que libera lotes con plazo de retiro vencido.
MINUTOS_TAREA_LIBERACION = 10


async def _tarea_liberar_vencidos() -> None:
    """Libera periódicamente los lotes cuyo plazo de 48h expiró (RN-12)."""
    while True:
        await asyncio.sleep(MINUTOS_TAREA_LIBERACION * 60)
        sesion = SesionLocal()
        try:
            servicio_emparejamiento.liberar_vencidos(sesion)
        finally:
            sesion.close()


@contextlib.asynccontextmanager
async def ciclo_de_vida(_app: FastAPI):
    """Arranca/detiene la tarea de fondo de liberación de lotes (RN-12)."""
    tarea = asyncio.create_task(_tarea_liberar_vencidos())
    yield
    tarea.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await tarea


app = FastAPI(title="Sistema de Donaciones de Alimentos", version="1.0", lifespan=ciclo_de_vida)

# Inicializar cifrado AES-256 para datos sensibles (RNF-12) / 初始化 AES-256 加密
if configuracion.clave_aes256:
    configurar_clave_aes(configuracion.clave_aes256)

# CORS: permitir el frontend de Vite en desarrollo / 允许开发环境的 Vite 前端
ORIGENES_PERMITIDOS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers / 路由
app.include_router(roles.enrutador)
app.include_router(autenticacion.enrutador)
app.include_router(inventario.enrutador)
app.include_router(emparejamiento.enrutador)
app.include_router(reporte.enrutador)
app.include_router(admin.enrutador)
app.include_router(arco.enrutador)
app.include_router(rnc.enrutador)


@app.get("/")
def raiz():
    """Endpoint de salud / 健康检查端点."""
    return {"mensaje": "API funcionando correctamente"}
