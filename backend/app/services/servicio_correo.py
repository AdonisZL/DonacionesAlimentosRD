"""Servicio de correo / 邮件服务.

Si hay credenciales SMTP en .env (smtp_host, smtp_usuario, smtp_contrasena,
correo_remitente), envía correos reales por smtplib (biblioteca estándar).
Si no, mantiene el modo simulado: imprime en la consola del backend.
若 .env 配置了 SMTP 凭证，则通过标准库 smtplib 真实发送；否则保持模拟模式。
"""

import smtplib
from email.message import EmailMessage

from app.config.configuracion import configuracion


def enviar_correo(destinatario: str, asunto: str, cuerpo: str) -> bool:
    """Envía un correo real (SMTP) o lo simula por consola / 发送或模拟邮件.

    Devuelve True solo si el envío real tuvo éxito.
    仅当真实发送成功时返回 True。
    """
    if not configuracion.correo_activo:
        _simular(destinatario, asunto, cuerpo)
        return False

    mensaje = EmailMessage()
    mensaje["From"] = configuracion.correo_remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.set_content(cuerpo)

    try:
        with smtplib.SMTP(
            configuracion.smtp_host, configuracion.smtp_puerto, timeout=15
        ) as servidor:
            servidor.starttls()
            servidor.login(configuracion.smtp_usuario, configuracion.smtp_contrasena)
            servidor.send_message(mensaje)
    except Exception as error:  # noqa: BLE001 — no exponer el error al usuario
        print(
            f"[CORREO ERROR] No se pudo enviar a {destinatario}: {error}",
            flush=True,
        )
        return False

    print(f"[CORREO REAL] Enviado a {destinatario}: {asunto}", flush=True)
    return True


def _simular(destinatario: str, asunto: str, cuerpo: str) -> None:
    """Imprime el correo en consola / 控制台打印模拟邮件."""
    print("\n" + "=" * 64)
    print(f"[CORREO SIMULADO] Para: {destinatario}")
    print(f"Asunto: {asunto}")
    print(cuerpo)
    print("=" * 64 + "\n", flush=True)
