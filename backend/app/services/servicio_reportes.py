"""Servicio de reportes / 报表服务 (OE4, RF-23 … RF-27).

Genera reportes de donaciones, inventario (FEFO) y asignaciones; simula la
exportación a Google Sheets y el reporte fiscal DGII inmutable (cadena de hash).
生成捐赠、库存（FEFO）与分配报表；模拟导出 Google Sheets 与不可变财务报表（哈希链）。
"""

import csv
import hashlib
import io
import json
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from app.models.categoria_alimento import CategoriaAlimento
from app.models.direccion_sede import DireccionSede
from app.models.emparejamiento import Emparejamiento
from app.models.entrega_transaccion import EntregaTransaccion
from app.models.lote_inventario import LoteInventario
from app.models.producto import Producto
from app.models.reporte_consolidado import ReporteConsolidado
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.services import servicio_auditoria, servicio_inventario
from app.services.certificacion_pdf_service import CertificacionFiscalPDF
from app.services.dgii_606_service import DGII606Exporter

# URL base simulada de Google Sheets / 模拟的表格基础地址
URL_SHEETS_SIMULADA = "https://docs.google.com/spreadsheets/d/SIMULADO-{id}/edit"
MODELO_FISCAL = "DGII-Norma-06-2018 (simulado)"


def _rol_nombre(sesion: Session, usuario: Usuario) -> str:
    """Devuelve el nombre del rol del usuario / 返回用户角色名."""
    rol = sesion.get(Rol, usuario.id_rol)
    return rol.nombre if rol else ""


def _puede_ver_todo(sesion: Session, usuario: Usuario) -> bool:
    """Banco y administrador ven todos los datos / 食物银行与管理员可看全部."""
    return _rol_nombre(sesion, usuario) in ("banco_alimentos", "administrador")


# --- RF-23: reporte de donaciones por período -----------------------------


def reporte_donaciones(
    sesion: Session,
    usuario: Usuario,
    desde: date | None = None,
    hasta: date | None = None,
    id_donante: uuid.UUID | None = None,
    id_categoria: int | None = None,
    estado: str | None = None,
) -> dict:
    """Reporte de donaciones (lotes registrados) con filtros / 带过滤的捐赠报表."""
    consulta = (
        select(LoteInventario, Producto, CategoriaAlimento, Usuario)
        .join(Producto, Producto.id_producto == LoteInventario.id_producto)
        .join(
            CategoriaAlimento,
            CategoriaAlimento.id_categoria_alimento == Producto.id_categoria_alimento,
        )
        .join(Usuario, Usuario.id_usuario == LoteInventario.id_usuario)
    )

    if not _puede_ver_todo(sesion, usuario):
        consulta = consulta.where(LoteInventario.id_usuario == usuario.id_usuario)
    elif id_donante is not None:
        consulta = consulta.where(LoteInventario.id_usuario == id_donante)

    if desde is not None:
        consulta = consulta.where(cast(LoteInventario.creado_en, Date) >= desde)
    if hasta is not None:
        consulta = consulta.where(cast(LoteInventario.creado_en, Date) <= hasta)
    if id_categoria is not None:
        consulta = consulta.where(Producto.id_categoria_alimento == id_categoria)
    if estado:
        consulta = consulta.where(LoteInventario.estado == estado)

    consulta = consulta.order_by(LoteInventario.creado_en.desc())

    filas: list[dict] = []
    total_kg = 0.0
    for lote, producto, categoria, donante in sesion.execute(consulta).all():
        peso = float(lote.peso_total) if lote.peso_total is not None else None
        if peso:
            total_kg += peso
        filas.append(
            {
                "id_lote": lote.id_lote,
                "fecha": lote.creado_en,
                "donante": f"{donante.nombre} {donante.apellido or ''}".strip(),
                "producto": producto.nombre_producto,
                "categoria": categoria.nombre_categoria,
                "cantidad": float(lote.cantidad_disponible),
                "unidad": lote.unidad_medida,
                "peso_kg": peso,
                "estado": lote.estado,
            }
        )
    return {
        "filas": filas,
        "total_lotes": len(filas),
        "total_kg": round(total_kg, 2),
    }


# --- RF-24: reporte de inventario actual (FEFO) ----------------------------


def reporte_inventario(sesion: Session, usuario: Usuario) -> list[dict]:
    """Inventario actual ordenado FEFO / 当前库存（FEFO 排序）."""
    solo_propios = not _puede_ver_todo(sesion, usuario)
    return servicio_inventario.listar_lotes(sesion, usuario, solo_propios=solo_propios)


# --- RF-25: reporte de asignaciones completadas ----------------------------


def reporte_asignaciones(sesion: Session, usuario: Usuario) -> dict:
    """Asignaciones completadas con su entrega / 已完成分配及其交付."""
    consulta = (
        select(Emparejamiento, LoteInventario, Producto, DireccionSede)
        .join(LoteInventario, LoteInventario.id_lote == Emparejamiento.id_lote)
        .join(Producto, Producto.id_producto == LoteInventario.id_producto)
        .join(DireccionSede, DireccionSede.id_sede == Emparejamiento.id_sede)
        .where(Emparejamiento.estado_tramite == "completado")
        .order_by(Emparejamiento.creado_en.desc())
    )
    if not _puede_ver_todo(sesion, usuario):
        consulta = consulta.where(
            (LoteInventario.id_usuario == usuario.id_usuario)
            | (DireccionSede.id_usuario == usuario.id_usuario)
        )

    filas: list[dict] = []
    for emp, _lote, producto, sede in sesion.execute(consulta).all():
        entrega = (
            sesion.execute(
                select(EntregaTransaccion).where(
                    EntregaTransaccion.id_emparejamiento == emp.id_emparejamiento
                )
            )
            .scalars()
            .first()
        )
        filas.append(
            {
                "id_emparejamiento": emp.id_emparejamiento,
                "fecha": emp.creado_en,
                "producto": producto.nombre_producto,
                "sede_receptora": sede.nombre_sede,
                "distancia_km": float(emp.distancia_km),
                "estado_entrega": entrega.estado_entrega if entrega else "pendiente",
                "evidencias": 0,
            }
        )
    return {"filas": filas, "total": len(filas)}


# --- RF-26: exportación a Google Sheets (simulada) -------------------------


def _filas_a_csv(filas: list[dict]) -> str:
    """Convierte filas a texto CSV / 将行转换为 CSV 文本."""
    if not filas:
        return ""
    salida = io.StringIO()
    escritor = csv.DictWriter(salida, fieldnames=list(filas[0].keys()))
    escritor.writeheader()
    for fila in filas:
        escritor.writerow({k: ("" if v is None else v) for k, v in fila.items()})
    return salida.getvalue()


def exportar_sheets(
    sesion: Session,
    usuario: Usuario,
    tipo: str,
    desde: date | None = None,
    hasta: date | None = None,
) -> dict:
    """Simula la exportación a Google Sheets y guarda el reporte / 模拟导出并保存 (RF-26)."""
    if tipo == "donaciones":
        datos = reporte_donaciones(sesion, usuario, desde=desde, hasta=hasta)
        filas = datos["filas"]
    elif tipo == "inventario":
        filas = reporte_inventario(sesion, usuario)
    elif tipo == "asignaciones":
        filas = reporte_asignaciones(sesion, usuario)["filas"]
    else:
        raise ValueError("Tipo de exportación no válido.")

    filas_serializables = [
        {
            k: (str(v) if isinstance(v, (uuid.UUID, datetime)) else v)
            for k, v in f.items()
        }
        for f in filas
    ]
    csv_texto = _filas_a_csv(filas_serializables)

    reporte = ReporteConsolidado(
        creado_por=usuario.id_usuario,
        tipo_reporte="exportacion_sheets",
        parametros_busqueda={
            "tipo": tipo,
            "desde": str(desde) if desde else None,
            "hasta": str(hasta) if hasta else None,
            "filas_exportadas": len(filas_serializables),
        },
        estado="emitido",
    )
    sesion.add(reporte)
    sesion.flush()
    reporte.url_archivo = URL_SHEETS_SIMULADA.format(id=reporte.id_reporte)
    sesion.commit()
    sesion.refresh(reporte)

    return {
        "id_reporte": str(reporte.id_reporte),
        "url": reporte.url_archivo,
        "filas_exportadas": len(filas_serializables),
        "csv": csv_texto,
    }


# --- RF-27: reporte fiscal DGII inmutable (cadena de hash, simulado) -------


def _ultimo_hash_fiscal(sesion: Session) -> str | None:
    """Hash del último reporte fiscal emitido / 最近财务报表的哈希."""
    reporte = (
        sesion.execute(
            select(ReporteConsolidado)
            .where(ReporteConsolidado.tipo_reporte == "fiscal_dgii")
            .order_by(ReporteConsolidado.fecha_generacion.desc())
        )
        .scalars()
        .first()
    )
    if reporte and reporte.parametros_busqueda:
        return reporte.parametros_busqueda.get("hash")
    return None


def reporte_fiscal(
    sesion: Session,
    usuario: Usuario,
    anio: int,
    mes: int,
    id_reporte_rectificado: uuid.UUID | None = None,
) -> dict:
    """Genera un reporte fiscal inmutable encadenado por hash / 生成不可变财务报表 (RF-27)."""
    if not _puede_ver_todo(sesion, usuario):
        raise PermissionError(
            "Solo un banco de alimentos o el administrador puede emitir reportes fiscales."
        )

    # Rango del mes solicitado / 所选月份的范围
    desde = date(anio, mes, 1)
    hasta = date(anio + (mes // 12), (mes % 12) + 1, 1)

    consulta = (
        select(
            func.count(LoteInventario.id_lote),
            func.coalesce(func.sum(LoteInventario.peso_total), 0),
        )
        .where(cast(LoteInventario.creado_en, Date) >= desde)
        .where(cast(LoteInventario.creado_en, Date) < hasta)
    )
    total_lotes, total_kg = sesion.execute(consulta).one()

    contenido = {
        "periodo": f"{anio:04d}-{mes:02d}",
        "total_lotes": int(total_lotes or 0),
        "total_kg": float(total_kg or 0),
        "norma": "DGII 06-2018",
        "generado_en": datetime.now(timezone.utc).isoformat(),
    }

    version = 1
    if id_reporte_rectificado is not None:
        anterior = sesion.get(ReporteConsolidado, id_reporte_rectificado)
        if anterior is None:
            raise ValueError("El reporte a rectificar no existe.")
        anterior.estado = "rectificado"
        version = (anterior.version or 1) + 1

    hash_anterior = _ultimo_hash_fiscal(sesion)
    base = json.dumps(contenido, sort_keys=True) + (hash_anterior or "")
    hash_actual = hashlib.sha256(base.encode("utf-8")).hexdigest()

    reporte = ReporteConsolidado(
        creado_por=usuario.id_usuario,
        tipo_reporte="fiscal_dgii",
        parametros_busqueda={
            "contenido": contenido,
            "hash": hash_actual,
            "hash_anterior": hash_anterior,
            "modelo": MODELO_FISCAL,
        },
        version=version,
        id_reporte_rectificado=id_reporte_rectificado,
        estado="emitido",
    )
    sesion.add(reporte)
    sesion.flush()
    reporte.url_archivo = f"fiscal/DGII-{contenido['periodo']}-{hash_actual[:12]}.pdf"
    # RF-29: auditoría de la emisión del reporte fiscal.
    servicio_auditoria.registrar(
        sesion,
        accion="reporte_fiscal",
        id_usuario=usuario.id_usuario,
        entidad="reportes_consolidados",
        id_entidad=reporte.id_reporte,
        detalles={"periodo": contenido["periodo"], "hash": hash_actual},
        confirmar=False,
    )
    sesion.commit()
    sesion.refresh(reporte)

    return {
        "id_reporte": str(reporte.id_reporte),
        "version": reporte.version,
        "contenido": contenido,
        "hash": hash_actual,
        "hash_anterior": hash_anterior,
        "url_archivo": reporte.url_archivo,
    }


def listar_reportes(sesion: Session, usuario: Usuario) -> list[ReporteConsolidado]:
    """Reportes generados por el usuario / 用户生成的报表."""
    return (
        sesion.execute(
            select(ReporteConsolidado)
            .where(ReporteConsolidado.creado_por == usuario.id_usuario)
            .order_by(ReporteConsolidado.fecha_generacion.desc())
        )
        .scalars()
        .all()
    )


# --- Certificación fiscal PDF por lote (Ley 11-92, Art. 287) ---------------


def generar_certificado_pdf(
    sesion: Session,
    usuario: Usuario,
    id_lote: uuid.UUID,
    rnc_donante: str,
    valor_total_rd: Decimal,
) -> tuple[bytes, str, uuid.UUID]:
    """Genera la certificación fiscal PDF de un lote donado (RN-17, Ley 11-92).

    Devuelve (bytes_pdf, hash_sha256, id_reporte). El hash y los datos fiscales
    quedan guardados en `reportes_consolidados` para alimentar luego el
    formato de envío DGII 606.
    生成某批次的税务捐赠证明 PDF，返回 (PDF字节, SHA-256哈希, 报表ID)，
    并保存以供后续 DGII 606 导出使用。
    """
    lote = sesion.get(LoteInventario, id_lote)
    if lote is None:
        raise ValueError("El lote indicado no existe.")
    if not _puede_ver_todo(sesion, usuario) and lote.id_usuario != usuario.id_usuario:
        raise PermissionError("No tienes permiso para certificar este lote.")

    donante = sesion.get(Usuario, lote.id_usuario)
    producto = sesion.get(Producto, lote.id_producto)
    cantidad_kg = Decimal(str(lote.peso_total or lote.cantidad_disponible or 0))
    if cantidad_kg <= 0:
        raise ValueError("El lote no tiene cantidad válida para certificar.")

    pdf_gen = CertificacionFiscalPDF()
    buffer = pdf_gen.crear_certificacion(
        donante={
            "razon_social": (
                f"{donante.nombre} {donante.apellido or ''}".strip()
                if donante
                else "Donante"
            ),
            "rnc": rnc_donante,
            "direccion": "N/D",
            "telefono": donante.telefono if donante else "N/D",
        },
        detalles_alimentos=[
            {
                "descripcion": producto.nombre_producto if producto else "Alimento donado",
                "cantidad_kg": cantidad_kg,
                "valor_unitario_rd": (valor_total_rd / cantidad_kg),
            }
        ],
        fecha_donacion=lote.creado_en or datetime.now(timezone.utc),
    )
    pdf_bytes = buffer.getvalue()
    hash_documento = hashlib.sha256(pdf_bytes).hexdigest()
    ncf = pdf_gen.generar_ncf()

    reporte = ReporteConsolidado(
        creado_por=usuario.id_usuario,
        tipo_reporte="certificado_fiscal",
        parametros_busqueda={
            "id_lote": str(id_lote),
            "rnc_donante": rnc_donante,
            "valor_total_rd": float(valor_total_rd),
            "ncf": ncf,
            "fecha": (lote.creado_en or datetime.now(timezone.utc)).isoformat(),
        },
        estado="emitido",
        hash_documento=hash_documento,
    )
    sesion.add(reporte)
    sesion.flush()
    reporte.url_archivo = f"certificados/{reporte.id_reporte}.pdf"
    servicio_auditoria.registrar(
        sesion,
        accion="certificado_fiscal_pdf",
        id_usuario=usuario.id_usuario,
        entidad="lotes_inventario",
        id_entidad=id_lote,
        detalles={"hash_documento": hash_documento, "ncf": ncf},
        confirmar=False,
    )
    sesion.commit()

    return pdf_bytes, hash_documento, reporte.id_reporte


# --- RF-27 (extendido): exportación real al formato DGII 606 --------------


def generar_dgii_606(
    sesion: Session, usuario: Usuario, anio: int, mes: int
) -> str:
    """Genera el archivo DGII 606 a partir de los certificados fiscales del
    mes indicado (RNC|TipoID|Código|NCF|Fecha|Monto|...).
    根据当月已生成的税务证明，导出 DGII 606 格式文件。
    """
    if not _puede_ver_todo(sesion, usuario):
        raise PermissionError(
            "Solo un banco de alimentos o el administrador puede exportar el formato 606."
        )

    desde = date(anio, mes, 1)
    hasta = date(anio + (mes // 12), (mes % 12) + 1, 1)

    consulta = (
        select(ReporteConsolidado)
        .where(ReporteConsolidado.tipo_reporte == "certificado_fiscal")
        .where(cast(ReporteConsolidado.fecha_generacion, Date) >= desde)
        .where(cast(ReporteConsolidado.fecha_generacion, Date) < hasta)
        .order_by(ReporteConsolidado.fecha_generacion.asc())
    )

    donaciones: list[dict] = []
    for reporte in sesion.execute(consulta).scalars().all():
        datos = reporte.parametros_busqueda or {}
        rnc = str(datos.get("rnc_donante", ""))
        donaciones.append(
            {
                "rnc_donante": rnc,
                "tipo_identificacion": 1 if len(rnc) == 9 else 2,
                "codigo_concepto": "50",
                "ncf": datos.get("ncf", ""),
                "fecha_donacion": datetime.fromisoformat(datos["fecha"])
                if datos.get("fecha")
                else reporte.fecha_generacion,
                "valor_total_rd": Decimal(str(datos.get("valor_total_rd", 0))),
            }
        )

    exporter = DGII606Exporter()
    archivo = exporter.exportar_donaciones(donaciones)
    return archivo.getvalue()
