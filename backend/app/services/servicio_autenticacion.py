"""Servicio de autenticación / 认证服务.

Lógica de registro, búsqueda y autenticación de usuarios (OE1).
用户注册、查询与认证逻辑。
"""

import uuid
from datetime import datetime, timedelta, timezone

from geoalchemy2 import WKTElement
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.consentimiento_dato import ConsentimientoDatos
from app.models.direccion_sede import DireccionSede
from app.models.perfil_legal import PerfilLegal
from app.models.token_recuperacion import TokenRecuperacion
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioActualizar, UsuarioCrear
from app.services.servicio_correo import enviar_correo
from app.utils.seguridad import (
    crear_token_verificacion,
    decodificar_token,
    generar_token_aleatorio,
    hashear_contrasena,
    hashear_token,
    verificar_contrasena,
)

# RF-30: protección contra fuerza bruta / 防暴力破解
MAX_INTENTOS_FALLIDOS = 5
MINUTOS_BLOQUEO = 10


def obtener_usuario_por_email(sesion: Session, email: str) -> Usuario | None:
    """Busca un usuario por su correo / 按邮箱查找用户."""
    return sesion.execute(
        select(Usuario).where(Usuario.email == email)
    ).scalar_one_or_none()


def esta_bloqueado(usuario: Usuario) -> bool:
    """Indica si la cuenta está bloqueada temporalmente / 账号是否临时锁定 (RF-30)."""
    if usuario.bloqueado_hasta is None:
        return False
    return usuario.bloqueado_hasta > datetime.now(timezone.utc)


def registrar_intento_fallido(sesion: Session, usuario: Usuario) -> None:
    """Suma un intento fallido; bloquea al llegar al máximo / 记录失败，达上限则锁定."""
    usuario.intentos_fallidos = (usuario.intentos_fallidos or 0) + 1
    if usuario.intentos_fallidos >= MAX_INTENTOS_FALLIDOS:
        usuario.bloqueado_hasta = datetime.now(timezone.utc) + timedelta(
            minutes=MINUTOS_BLOQUEO
        )
        usuario.intentos_fallidos = 0
    sesion.commit()


def reiniciar_intentos(sesion: Session, usuario: Usuario) -> None:
    """Reinicia intentos y actualiza el último acceso / 重置失败次数并更新最近登录."""
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    usuario.ultimo_acceso = datetime.now(timezone.utc)
    sesion.commit()


def registrar_usuario(
    sesion: Session, datos: UsuarioCrear, ip_origen: str | None = None
) -> Usuario:
    """Crea un usuario y registra su consentimiento / 创建用户并记录同意 (RF-01, RF-31)."""
    usuario = Usuario(
        nombre=datos.nombre,
        apellido=datos.apellido,
        telefono=datos.telefono,
        email=str(datos.email),
        contrasena_hash=hashear_contrasena(datos.contrasena),
        id_rol=datos.id_rol,
        subtipo_donante=(datos.subtipo_donante or None),
        estado="activo",
        email_verificado=False,
    )
    sesion.add(usuario)
    sesion.flush()  # obtiene id_usuario sin cerrar la transacción / 获取 id，不提交

    # RF-31 / RN-18: registrar el consentimiento de datos (Ley 172-13).
    sesion.add(
        ConsentimientoDatos(
            id_usuario=usuario.id_usuario,
            tipo_consentimiento="tratamiento_datos_172_13",
            version_documento="1.0",
            aceptado=datos.consentimiento_172_13,
            ip_origen=ip_origen,
        )
    )

    # Perfil legal (RNC) si se proporcionó / 若提供 RNC 则创建法律信息 (RN-01)
    if datos.rnc:
        sesion.add(
            PerfilLegal(
                id_usuario=usuario.id_usuario,
                rnc=datos.rnc,
                telefono=datos.telefono,
                consentimiento_172_13=datos.consentimiento_172_13,
                fecha_consentimiento=datetime.now(timezone.utc),
            )
        )

    # Sede (dirección + coordenadas) si se proporcionaron / 若提供地址与坐标则创建场所
    if (
        datos.direccion_texto
        and datos.latitud is not None
        and datos.longitud is not None
    ):
        punto = WKTElement(f"POINT({datos.longitud} {datos.latitud})", srid=4326)
        sesion.add(
            DireccionSede(
                id_usuario=usuario.id_usuario,
                nombre_sede=datos.nombre,
                direccion_texto=datos.direccion_texto,
                coordenadas=punto,
                capacidad_diaria_kg=datos.capacidad_diaria_kg,
                tiene_cadena_frio=datos.tiene_cadena_frio,
                horario_atencion=datos.horario_atencion,
                rnc=datos.rnc,
            )
        )

    try:
        sesion.commit()
    except IntegrityError as error:
        sesion.rollback()
        raise ValueError(
            "El RNC ya está registrado o hay un dato duplicado."
        ) from error
    sesion.refresh(usuario)
    return usuario


def autenticar_usuario(sesion: Session, email: str, contrasena: str) -> Usuario | None:
    """Valida credenciales y devuelve el usuario o None / 校验凭证 (RF-04)."""
    usuario = obtener_usuario_por_email(sesion, email)
    if usuario is None or not usuario.contrasena_hash:
        return None
    if not verificar_contrasena(contrasena, usuario.contrasena_hash):
        return None
    return usuario


def actualizar_perfil(
    sesion: Session, usuario: Usuario, datos: UsuarioActualizar
) -> Usuario:
    """Actualiza los datos de contacto del usuario / 更新用户联系资料 (RF-07)."""
    if datos.nombre is not None:
        usuario.nombre = datos.nombre
    if datos.apellido is not None:
        usuario.apellido = datos.apellido
    if datos.telefono is not None:
        usuario.telefono = datos.telefono
    sesion.commit()
    sesion.refresh(usuario)
    return usuario


def desactivar_cuenta(sesion: Session, usuario: Usuario) -> None:
    """Baja lógica: conserva el historial / 逻辑注销：保留历史 (RF-08, Ley 11-92)."""
    usuario.estado = "inactivo"
    sesion.commit()


# URL del frontend para los enlaces de correo / 邮件链接用的前端地址
URL_FRONTEND = "http://localhost:5173"
MINUTOS_EXPIRACION_RECUPERACION = 15


def enviar_verificacion_correo(usuario: Usuario) -> None:
    """Envía (simulado) el enlace de verificación de correo / 发送验证链接 (RF-06)."""
    token = crear_token_verificacion(str(usuario.id_usuario))
    enlace = f"{URL_FRONTEND}/verificar-correo?token={token}"
    enviar_correo(
        usuario.email,
        "Verifica tu correo — DonacionesRD",
        f"Hola {usuario.nombre}, confirma tu cuenta abriendo este enlace:\n{enlace}",
    )


def verificar_correo(sesion: Session, token: str) -> bool:
    """Marca el correo como verificado si el token es válido / 验证邮箱 (RF-06)."""
    datos = decodificar_token(token)
    if not datos or datos.get("tipo") != "verificacion_correo":
        return False
    id_usuario = datos.get("sub")
    if not id_usuario:
        return False
    usuario = sesion.get(Usuario, uuid.UUID(str(id_usuario)))
    if usuario is None:
        return False
    usuario.email_verificado = True
    sesion.commit()
    return True


def solicitar_recuperacion(sesion: Session, email: str) -> None:
    """Genera y 'envía' un token de recuperación (15 min) / 生成并发送恢复令牌 (RF-05)."""
    usuario = obtener_usuario_por_email(sesion, email)
    if usuario is None:
        return  # no revelar si el correo existe / 不泄露邮箱是否存在
    token = generar_token_aleatorio()
    sesion.add(
        TokenRecuperacion(
            id_usuario=usuario.id_usuario,
            token_hash=hashear_token(token),
            expira_en=datetime.now(timezone.utc)
            + timedelta(minutes=MINUTOS_EXPIRACION_RECUPERACION),
        )
    )
    sesion.commit()
    enlace = f"{URL_FRONTEND}/restablecer-password?token={token}"
    enviar_correo(
        usuario.email,
        "Restablece tu contraseña — DonacionesRD",
        f"Usa este enlace (válido 15 minutos) para crear una nueva contraseña:\n{enlace}",
    )


def restablecer_contrasena(sesion: Session, token: str, nueva_contrasena: str) -> bool:
    """Cambia la contraseña si el token es válido y no expiró / 用令牌重置密码 (RF-05)."""
    registro = sesion.execute(
        select(TokenRecuperacion).where(
            TokenRecuperacion.token_hash == hashear_token(token),
            TokenRecuperacion.usado.is_(False),
        )
    ).scalar_one_or_none()
    if registro is None or registro.expira_en < datetime.now(timezone.utc):
        return False
    usuario = sesion.get(Usuario, registro.id_usuario)
    if usuario is None:
        return False
    usuario.contrasena_hash = hashear_contrasena(nueva_contrasena)
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    registro.usado = True
    sesion.commit()
    return True
