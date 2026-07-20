// Llamadas de reportes / 报表相关请求 (OE4)

import { cliente } from "./cliente.js";

// Reporte de donaciones por período / 按期捐赠报表 (RF-23)
export async function obtenerReporteDonaciones(filtros = {}) {
  const { data } = await cliente.get("/api/reportes/donaciones", { params: filtros });
  return data;
}

// Reporte de inventario actual (FEFO) / 当前库存报表 (RF-24)
export async function obtenerReporteInventario() {
  const { data } = await cliente.get("/api/reportes/inventario");
  return data;
}

// Reporte de asignaciones completadas / 已完成分配报表 (RF-25)
export async function obtenerReporteAsignaciones() {
  const { data } = await cliente.get("/api/reportes/asignaciones");
  return data;
}

// Exportar a Google Sheets (simulado) / 导出到表格（模拟）(RF-26)
export async function exportarSheets(tipo, desde = null, hasta = null) {
  const { data } = await cliente.post("/api/reportes/exportar-sheets", {
    tipo,
    desde,
    hasta,
  });
  return data;
}

// Reporte fiscal DGII (simulado) / 财务报表（模拟）(RF-27)
export async function generarReporteFiscal(anio, mes, idReporteRectificado = null) {
  const { data } = await cliente.post("/api/reportes/fiscal", {
    anio,
    mes,
    id_reporte_rectificado: idReporteRectificado,
  });
  return data;
}

// Listar reportes generados / 列出已生成报表
export async function obtenerReportes() {
  const { data } = await cliente.get("/api/reportes");
  return data;
}
