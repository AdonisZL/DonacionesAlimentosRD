// Llamadas de inventario / 库存相关请求 (OE2)

import { cliente } from "./cliente.js";

// Catálogo de categorías de alimentos / 食物分类目录
export async function obtenerCategoriasAlimentos() {
  const { data } = await cliente.get("/api/inventario/categorias-alimentos");
  return data;
}

// Catálogo de perecibilidad / 易腐性目录 (RF-10)
export async function obtenerCategoriasPerecibilidad() {
  const { data } = await cliente.get("/api/inventario/categorias-perecibilidad");
  return data;
}

// Lista de productos / 产品列表
export async function obtenerProductos() {
  const { data } = await cliente.get("/api/inventario/productos");
  return data;
}

// Crear producto / 创建产品 (RF-09)
export async function crearProducto(datos) {
  const { data } = await cliente.post("/api/inventario/productos", datos);
  return data;
}

// Registrar lote / 登记批次 (RF-09, RF-14)
export async function registrarLote(datos) {
  const { data } = await cliente.post("/api/inventario/lotes", datos);
  return data;
}

// Listar lotes (orden FEFO) / 列出批次（FEFO 排序）(RF-12)
export async function obtenerLotes() {
  const { data } = await cliente.get("/api/inventario/lotes");
  return data;
}

// Alertas de vencimiento / 临期预警 (RF-13)
export async function obtenerAlertas() {
  const { data } = await cliente.get("/api/inventario/alertas");
  return data;
}

// Historial inmutable de un lote / 批次不可变历史 (RF-16)
export async function obtenerHistorialLote(idLote) {
  const { data } = await cliente.get(`/api/inventario/lotes/${idLote}/historial`);
  return data;
}

// Ajuste manual de inventario (solo banco) / 手动调整（仅食物银行）(RF-15)
export async function ajustarInventario(idLote, datos) {
  const { data } = await cliente.post(
    `/api/inventario/lotes/${idLote}/ajuste`,
    datos,
  );
  return data;
}
