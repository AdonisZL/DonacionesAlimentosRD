"""Punto de entrada de la API / API 入口.

Registra middlewares (CORS) y los routers por dominio.
注册中间件（CORS）与各领域路由。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.configuracion import configuracion
from app.utils.cifrado import configurar_clave_aes

from app.routers import (
    admin,
    arco,
    autenticacion,
    emparejamiento,
    inventario,
    reporte,
    roles,
)

app = FastAPI(title="Sistema de Donaciones de Alimentos", version="1.0")

# Inicializar cifrado AES-256 para datos sensibles (RNF-12) / 初始化 AES-256 加密
if configuracion.clave_aes256:
    configurar_clave_aes(configuracion.clave_aes256)

# CORS: permitir el frontend de Vite en desarrollo / 允许开发环境的 Vite 前端
ORIGENES_PERMITIDOS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_PERMITIDOS,
    allow_credentials=True,
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


@app.get("/")
def raiz():
    """Endpoint de salud / 健康检查端点."""
    return {"mensaje": "API funcionando correctamente"}
