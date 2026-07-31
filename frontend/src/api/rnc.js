// Llamadas de consulta RNC/Cédula / RNC/身份证查询请求 (MegaPlus API)

import { cliente } from "./cliente.js";

// Consultar por RNC o Cédula (DGII) / 按 RNC 或身份证查询
export async function consultarRNC(rnc) {
  const { data } = await cliente.post("/api/rnc/consultar", { rnc });
  return data;
}

// Buscar contribuyentes por nombre / 按名称搜索纳税人
export async function buscarPorNombre(buscar) {
  const { data } = await cliente.post("/api/rnc/buscar", { buscar });
  return data;
}
