// Llamadas de autenticación / 认证相关请求 (OE1)

import { cliente } from "./cliente.js";

// Registro de usuario / 注册用户 (RF-01)
export async function registrarUsuario(datos) {
  const { data } = await cliente.post("/api/auth/registro", datos);
  return data;
}

// Inicio de sesión / 登录 (RF-04)
export async function iniciarSesion(email, contrasena) {
  const { data } = await cliente.post("/api/auth/login", { email, contrasena });
  return data;
}

// Usuario autenticado actual / 当前登录用户
export async function obtenerUsuarioActual() {
  const { data } = await cliente.get("/api/auth/yo");
  return data;
}

// Lista de roles / 角色列表
export async function obtenerRoles() {
  const { data } = await cliente.get("/api/roles");
  return data;
}

// Verificación de correo / 邮箱验证 (RF-06)
export async function verificarCorreo(token) {
  const { data } = await cliente.get(
    `/api/auth/verificar-correo?token=${encodeURIComponent(token)}`,
  );
  return data;
}

// Solicitar recuperación / 请求找回密码 (RF-05)
export async function solicitarRecuperacion(email) {
  const { data } = await cliente.post("/api/auth/recuperar-password", { email });
  return data;
}

// Restablecer contraseña / 重置密码 (RF-05)
export async function restablecerContrasena(token, nueva_contrasena) {
  const { data } = await cliente.post("/api/auth/restablecer-password", {
    token,
    nueva_contrasena,
  });
  return data;
}

// Actualizar perfil / 更新资料 (RF-07)
export async function actualizarPerfil(datos) {
  const { data } = await cliente.put("/api/auth/perfil", datos);
  return data;
}

// Desactivar cuenta / 停用账号 (RF-08)
export async function desactivarCuenta() {
  const { data } = await cliente.post("/api/auth/desactivar");
  return data;
}
