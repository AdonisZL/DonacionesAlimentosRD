// Llamadas de derechos ARCO / ARCO 权利请求 (RN-19, Ley 172-13)

import { cliente } from "./cliente.js";

// Crear una solicitud ARCO / 创建 ARCO 请求
export async function crearSolicitudArco(datos) {
  const { data } = await cliente.post("/api/arco/solicitudes", datos);
  return data;
}

// Listar mis solicitudes ARCO / 列出我的 ARCO 请求
export async function obtenerMisSolicitudes() {
  const { data } = await cliente.get("/api/arco/mis-solicitudes");
  return data;
}

// Admin: listar todas las solicitudes / 管理员：列出所有请求
export async function obtenerTodasSolicitudes() {
  const { data } = await cliente.get("/api/arco/admin/todas");
  return data;
}

// Admin: resolver solicitud / 管理员：解决请求
export async function resolverSolicitud(idSolicitud, datos) {
  const { data } = await cliente.put(
    `/api/arco/admin/${idSolicitud}/resolver`,
    datos,
  );
  return data;
}
