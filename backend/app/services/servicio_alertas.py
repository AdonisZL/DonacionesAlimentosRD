"""Servicio de alertas por correo / 邮件预警服务 (RF-13).

Revisa lotes próximos a vencer (≤ 3 días) y notifica al donante
por correo electrónico (simulado en esta fase).
检查临期批次（≤ 3 天）并通过邮件通知捐赠者（当前阶段为模拟）。
"""

import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lote_inventario import LoteInventario
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.services.servicio_correo import enviar_correo

# Umbral de alerta: lotes que vencen en ≤ esta cantidad de días
# 预警阈值：距到期 ≤ 此天数的批次
DIAS_ALERTA_VENCIMIENTO = 3


def _lotes_por_vencer(sesion: Session) -> list[dict]:
    """Devuelve los lotes disponibles que vencen en ≤ 3 días / 返回 ≤ 3 天内到期的可用批次."""
    hoy = date.today()
    limite = hoy + timedelta(days=DIAS_ALERTA_VENCIMIENTO)

    consulta = (
        select(LoteInventario, Usuario, Producto)
        .join(Usuario, Usuario.id_usuario == LoteInventario.id_usuario)
        .join(Producto, Producto.id_producto == LoteInventario.id_producto)
        .where(LoteInventario.estado == "disponible")
        .where(LoteInventario.fecha_vencimiento <= limite)
        .where(LoteInventario.fecha_vencimiento >= hoy)
    )

    resultado: list[dict] = []
    for lote, usuario, producto in sesion.execute(consulta).all():
        dias_restantes = (lote.fecha_vencimiento - hoy).days
        resultado.append(
            {
                "id_lote": str(lote.id_lote),
                "donante": usuario.nombre,
                "email_donante": usuario.email,
                "producto": producto.nombre_producto,
                "cantidad": float(lote.cantidad_disponible),
                "unidad": lote.unidad_medida or "kg",
                "fecha_vencimiento": lote.fecha_vencimiento.isoformat(),
                "dias_restantes": dias_restantes,
            }
        )
    return resultado


def enviar_alertas_vencimiento(sesion: Session) -> dict:
    """Envía alertas por correo a donantes con lotes próximos a vencer.

    Devuelve un resumen de lotes alertados.
    向持有临期批次的捐赠者发送邮件预警。返回预警摘要。
    """
    lotes = _lotes_por_vencer(sesion)
    if not lotes:
        return {"alertas_enviadas": 0, "lotes_alertados": []}

    # Agrupar por donante / 按捐赠者分组
    por_donante: dict[str, list[dict]] = {}
    for lote_info in lotes:
        email = lote_info["email_donante"]
        if email not in por_donante:
            por_donante[email] = []
        por_donante[email].append(lote_info)

    alertas_enviadas = 0
    lotes_alertados: list[str] = []

    for email, lotes_donante in por_donante.items():
        donante = lotes_donante[0]["donante"]
        lineas = []
        for i, l in enumerate(lotes_donante, 1):
            lineas.append(
                f"  {i}. {l['producto']} — {l['cantidad']} {l['unidad']} — "
                f"Vence: {l['fecha_vencimiento']} "
                f"({l['dias_restantes']} día(s) restante(s))"
            )
            lotes_alertados.append(l["id_lote"])

        cuerpo = (
            f"Hola {donante},\n\n"
            f"Tienes {len(lotes_donante)} lote(s) próximo(s) a vencer:\n\n"
            + "\n".join(lineas)
            + "\n\nAccede a la plataforma para gestionarlos.\n"
            "Sistema de Donaciones de Alimentos RD"
        )

        # Simulado: imprimir en consola en vez de enviar correo real
        # 模拟：控制台打印代替真实邮件发送
        enviar_correo(
            destinatario=email,
            asunto=f"⚠️ {len(lotes_donante)} lote(s) próximo(s) a vencer",
            cuerpo=cuerpo,
        )
        alertas_enviadas += 1

    return {
        "alertas_enviadas": alertas_enviadas,
        "lotes_alertados": lotes_alertados,
        "total_lotes": len(lotes_alertados),
    }
