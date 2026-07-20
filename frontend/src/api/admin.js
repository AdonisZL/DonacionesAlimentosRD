// Llamadas de administración / 管理相关请求 (OE5)

import { cliente } from "./cliente.js";

// Panel de métricas / 指标面板 (RF-32)
export async function obtenerPanelAdmin() {
  const { data } = await cliente.get("/api/admin/panel");
  return data;
}

// Lista de usuarios / 用户列表
export async function obtenerUsuariosAdmin() {
  const { data } = await cliente.get("/api/admin/usuarios");
  return data;
}

// Cambiar estado de una cuenta / 修改账号状态 (RF-28)
export async function cambiarEstadoUsuario(idUsuario, estado) {
  const { data } = await cliente.put(`/api/admin/usuarios/${idUsuario}/estado`, {
    estado,
  });
  return data;
}

// Bitácora de auditoría / 审计日志 (RF-29)
export async function obtenerAuditoria() {
  const { data } = await cliente.get("/api/admin/auditoria");
  return data;
}
