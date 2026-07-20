"""Servicio de correo simulado / 模拟邮件服务.

Al inicio NO se envían correos reales: el contenido se imprime en la consola
del backend (donde corre Uvicorn). Sustituible por SMTP real más adelante.
初期不真正发送邮件，只在后端控制台打印。日后可替换为真实 SMTP。
"""


def enviar_correo(destinatario: str, asunto: str, cuerpo: str) -> None:
    """Simula el envío imprimiendo en consola / 通过打印模拟发送邮件."""
    print("\n" + "=" * 64)
    print(f"[CORREO SIMULADO] Para: {destinatario}")
    print(f"Asunto: {asunto}")
    print(cuerpo)
    print("=" * 64 + "\n", flush=True)
