"""Rutas de inventario / 库存路由 (OE2).

Catálogos, productos, lotes (FEFO), alertas, historial y ajustes.
目录、产品、批次（FEFO）、预警、历史与调整。
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.conexion import obtener_sesion
from app.models.usuario import Usuario
from app.schemas.inventario import (
    AjusteInventario,
    CategoriaAlimentoLeer,
    CategoriaPerecibilidadLeer,
    HistorialLeer,
    LoteCrear,
    LoteLeer,
    ProductoCrear,
    ProductoLeer,
)
from app.services import servicio_inventario
from app.utils.dependencias import obtener_usuario_actual

enrutador = APIRouter(prefix="/api/inventario", tags=["inventario"])


@enrutador.get("/categorias-alimentos", response_model=list[CategoriaAlimentoLeer])
def listar_categorias_alimentos(sesion: Session = Depends(obtener_sesion)):
    """Catálogo de categorías de alimentos / 食物分类目录."""
    return servicio_inventario.listar_categorias_alimentos(sesion)


@enrutador.get(
    "/categorias-perecibilidad", response_model=list[CategoriaPerecibilidadLeer]
)
def listar_categorias_perecibilidad(sesion: Session = Depends(obtener_sesion)):
    """Catálogo de perecibilidad (RF-10) / 易腐性目录."""
    return servicio_inventario.listar_categorias_perecibilidad(sesion)


@enrutador.get("/productos", response_model=list[ProductoLeer])
def listar_productos(sesion: Session = Depends(obtener_sesion)):
    """Lista de productos / 产品列表."""
    return servicio_inventario.listar_productos(sesion)


@enrutador.post(
    "/productos", response_model=ProductoLeer, status_code=status.HTTP_201_CREATED
)
def crear_producto(
    datos: ProductoCrear,
    sesion: Session = Depends(obtener_sesion),
    _usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Crea un producto / 创建产品 (RF-09)."""
    try:
        return servicio_inventario.crear_producto(sesion, datos)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@enrutador.post("/lotes", response_model=LoteLeer, status_code=status.HTTP_201_CREATED)
def registrar_lote(
    datos: LoteCrear,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Registra un lote de inventario / 登记库存批次 (RF-09, RF-14)."""
    try:
        lote = servicio_inventario.registrar_lote(sesion, usuario, datos)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return _enriquecer(sesion, lote)


@enrutador.get("/lotes", response_model=list[LoteLeer])
def listar_lotes(
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Lista los lotes propios ordenados FEFO / 按 FEFO 列出自有批次 (RF-12)."""
    return servicio_inventario.listar_lotes(sesion, usuario, solo_propios=True)


@enrutador.get("/alertas", response_model=list[LoteLeer])
def listar_alertas(
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Lotes con vencimiento <= 3 días / 临期批次 (RF-13)."""
    return servicio_inventario.listar_alertas(sesion, usuario)


@enrutador.get("/lotes/{id_lote}/historial", response_model=list[HistorialLeer])
def obtener_historial(
    id_lote: uuid.UUID,
    sesion: Session = Depends(obtener_sesion),
    _usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Historial inmutable de un lote / 批次不可变历史 (RF-16)."""
    if servicio_inventario.obtener_lote(sesion, id_lote) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado."
        )
    return servicio_inventario.obtener_historial(sesion, id_lote)


@enrutador.post("/lotes/{id_lote}/ajuste", response_model=LoteLeer)
def ajustar_inventario(
    id_lote: uuid.UUID,
    datos: AjusteInventario,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Ajuste manual de inventario (solo banco) / 手动调整（仅食物银行）(RF-15)."""
    try:
        lote = servicio_inventario.ajustar_inventario(sesion, usuario, id_lote, datos)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return _enriquecer(sesion, lote)


def _enriquecer(sesion: Session, lote) -> dict:
    """Adapta un lote ORM al esquema enriquecido / 将 ORM 批次转为富数据."""
    return servicio_inventario._enriquecer_lote(sesion, lote)
