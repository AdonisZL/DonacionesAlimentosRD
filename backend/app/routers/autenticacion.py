"""Rutas de autenticación / 认证路由 (OE1).

Registro, inicio de sesión (JWT) y datos del usuario actual.
注册、登录（JWT）与当前用户信息。
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.conexion import obtener_sesion
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.schemas.usuario import (
    DatosLogin,
    RestablecerContrasena,
    SedeLeer,
    SolicitarRecuperacion,
    Token,
    UsuarioActualizar,
    UsuarioCrear,
    UsuarioLeer,
)
from app.services import servicio_auditoria, servicio_autenticacion
from app.utils.dependencias import obtener_usuario_actual
from app.utils.seguridad import crear_token_acceso, verificar_contrasena

enrutador = APIRouter(prefix="/api/auth", tags=["autenticacion"])


@enrutador.post("/registro", response_model=Token, status_code=status.HTTP_201_CREATED)
def registrar(
    datos: UsuarioCrear,
    request: Request,
    sesion: Session = Depends(obtener_sesion),
) -> Token:
    """Registra un nuevo usuario / 注册新用户 (RF-01, RF-31)."""
    # RN-18 / RF-31: sin consentimiento no se procesan datos personales.
    if not datos.consentimiento_172_13:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe aceptar el consentimiento de datos (Ley 172-13).",
        )
    # RF-28 (RBAC): el rol administrador no se puede auto-registrar.
    rol = sesion.get(Rol, datos.id_rol)
    if rol is not None and rol.nombre == "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No es posible registrarse como administrador.",
        )
    # RN-03: correo único.
    if servicio_autenticacion.obtener_usuario_por_email(sesion, str(datos.email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya está registrado.",
        )
    ip_origen = request.client.host if request.client else None
    try:
        usuario = servicio_autenticacion.registrar_usuario(
            sesion, datos, ip_origen=ip_origen
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    # RF-06: enviar (simulado) el enlace de verificación de correo.
    servicio_autenticacion.enviar_verificacion_correo(usuario)
    # RF-29: auditoría del registro.
    servicio_auditoria.registrar(
        sesion,
        accion="registro_usuario",
        id_usuario=usuario.id_usuario,
        entidad="usuarios",
        id_entidad=usuario.id_usuario,
        detalles={"email": str(datos.email), "rol": rol.nombre if rol else None},
        ip_origen=ip_origen,
    )
    token = crear_token_acceso({"sub": str(usuario.id_usuario)})
    return Token(access_token=token, usuario=UsuarioLeer.model_validate(usuario))


@enrutador.post("/login", response_model=Token)
def login(
    datos: DatosLogin,
    request: Request,
    sesion: Session = Depends(obtener_sesion),
) -> Token:
    """Inicia sesión y devuelve un JWT / 登录并返回 JWT (RF-04, RF-30)."""
    credenciales_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Correo o contraseña incorrectos.",
    )
    usuario = servicio_autenticacion.obtener_usuario_por_email(sesion, str(datos.email))
    if usuario is None:
        raise credenciales_error
    # RF-30: cuenta bloqueada por intentos fallidos.
    if servicio_autenticacion.esta_bloqueado(usuario):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=(
                "Cuenta bloqueada temporalmente por intentos fallidos. "
                "Intenta de nuevo en unos minutos."
            ),
        )
    if not usuario.contrasena_hash or not verificar_contrasena(
        datos.contrasena, usuario.contrasena_hash
    ):
        servicio_autenticacion.registrar_intento_fallido(sesion, usuario)
        raise credenciales_error
    # RF-08: cuenta desactivada no puede iniciar sesión.
    if usuario.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta está inactiva. Contacta al administrador.",
        )
    servicio_autenticacion.reiniciar_intentos(sesion, usuario)
    # RF-29: auditoría del inicio de sesión.
    servicio_auditoria.registrar(
        sesion,
        accion="login",
        id_usuario=usuario.id_usuario,
        entidad="usuarios",
        id_entidad=usuario.id_usuario,
        ip_origen=(request.client.host if request.client else None),
    )
    token = crear_token_acceso({"sub": str(usuario.id_usuario)})
    return Token(access_token=token, usuario=UsuarioLeer.model_validate(usuario))


@enrutador.get("/yo", response_model=UsuarioLeer)
def usuario_actual(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    """Devuelve el usuario autenticado / 返回当前登录用户."""
    return usuario


@enrutador.get("/verificar-correo")
def verificar_correo(token: str, sesion: Session = Depends(obtener_sesion)) -> dict:
    """Verifica el correo con el token del enlace / 用链接令牌验证邮箱 (RF-06)."""
    if not servicio_autenticacion.verificar_correo(sesion, token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enlace de verificación inválido o expirado.",
        )
    return {"mensaje": "Correo verificado correctamente."}


@enrutador.post("/recuperar-password")
def recuperar_password(
    datos: SolicitarRecuperacion, sesion: Session = Depends(obtener_sesion)
) -> dict:
    """Solicita un enlace de recuperación / 请求找回密码链接 (RF-05)."""
    servicio_autenticacion.solicitar_recuperacion(sesion, str(datos.email))
    return {
        "mensaje": "Si el correo existe, se enviaron instrucciones para restablecer la contraseña."
    }


@enrutador.post("/restablecer-password")
def restablecer_password(
    datos: RestablecerContrasena, sesion: Session = Depends(obtener_sesion)
) -> dict:
    """Restablece la contraseña con el token / 用令牌重置密码 (RF-05)."""
    if not servicio_autenticacion.restablecer_contrasena(
        sesion, datos.token, datos.nueva_contrasena
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enlace de restablecimiento inválido o expirado.",
        )
    return {"mensaje": "Contraseña restablecida correctamente."}


@enrutador.put("/perfil", response_model=UsuarioLeer)
def actualizar_perfil(
    datos: UsuarioActualizar,
    usuario: Usuario = Depends(obtener_usuario_actual),
    sesion: Session = Depends(obtener_sesion),
) -> Usuario:
    """Actualiza el perfil del usuario autenticado / 更新当前用户资料 (RF-07)."""
    return servicio_autenticacion.actualizar_perfil(sesion, usuario, datos)


@enrutador.post("/desactivar")
def desactivar_cuenta(
    usuario: Usuario = Depends(obtener_usuario_actual),
    sesion: Session = Depends(obtener_sesion),
) -> dict:
    """Baja lógica de la cuenta / 账号逻辑注销 (RF-08)."""
    servicio_autenticacion.desactivar_cuenta(sesion, usuario)
    return {"mensaje": "Cuenta desactivada. Tu historial se conserva."}


@enrutador.get("/sede", response_model=SedeLeer)
def obtener_sede(
    usuario: Usuario = Depends(obtener_usuario_actual),
    sesion: Session = Depends(obtener_sesion),
) -> dict:
    """Obtiene la sede/dirección del usuario autenticado / 获取当前用户的地址场所."""
    sede = servicio_autenticacion.obtener_sede_usuario(sesion, usuario.id_usuario)
    if sede is None:
        return {
            "id_sede": None,
            "direccion": None,
            "direccion_texto": None,
            "latitud": None,
            "longitud": None,
            "capacidad_diaria_kg": None,
            "tiene_cadena_frio": False,
            "horario_atencion": None,
            "estado": None,
        }
    # Convertir Decimal a float para JSON / 将 Decimal 转为 float
    capacidad = sede.get("capacidad_diaria_kg")
    if capacidad is not None:
        sede["capacidad_diaria_kg"] = float(capacidad)
    return sede
