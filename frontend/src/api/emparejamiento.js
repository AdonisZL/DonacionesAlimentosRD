// Llamadas de emparejamiento / 匹配相关请求 (OE3)

import { cliente } from "./cliente.js";

// Buscar receptores compatibles / 搜索兼容接收方 (RF-17/18)
export async function buscarCandidatos(idLote, radioKm = 25) {
  const { data } = await cliente.post("/api/emparejamientos/candidatos", {
    id_lote: idLote,
    radio_km: radioKm,
  });
  return data;
}

// Crear emparejamiento sugerido / 创建建议匹配
export async function crearEmparejamiento(idLote, idSede, radioKm = 25) {
  const { data } = await cliente.post("/api/emparejamientos", {
    id_lote: idLote,
    id_sede: idSede,
    radio_km: radioKm,
  });
  return data;
}

// Listar emparejamientos / 列出匹配
export async function obtenerEmparejamientos() {
  const { data } = await cliente.get("/api/emparejamientos");
  return data;
}

// Confirmar / 确认 (RF-19/21)
export async function confirmarEmparejamiento(id) {
  const { data } = await cliente.post(`/api/emparejamientos/${id}/confirmar`);
  return data;
}

// Rechazar / 拒绝 (RF-20)
export async function rechazarEmparejamiento(id) {
  const { data } = await cliente.post(`/api/emparejamientos/${id}/rechazar`);
  return data;
}

// Completar (crea entrega) / 完成（创建交付）
export async function completarEmparejamiento(id) {
  const { data } = await cliente.post(`/api/emparejamientos/${id}/completar`);
  return data;
}

// Retroalimentación / 反馈 (RF-22)
export async function enviarRetroalimentacion(id, calificacion, comentario) {
  const { data } = await cliente.post(
    `/api/emparejamientos/${id}/retroalimentacion`,
    { calificacion, comentario },
  );
  return data;
}

// Notificaciones / 通知 (RF-21)
export async function obtenerNotificaciones() {
  const { data } = await cliente.get("/api/emparejamientos/notificaciones");
  return data;
}

export async function marcarNotificacionLeida(id) {
  const { data } = await cliente.post(
    `/api/emparejamientos/notificaciones/${id}/leida`,
  );
  return data;
}
