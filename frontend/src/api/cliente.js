// Cliente HTTP / HTTP 客户端
// Centraliza las llamadas a la API del backend. / 集中管理对后端 API 的调用。

import axios from "axios";

// URL base del backend (configurable con VITE_URL_API) / 后端基础地址
const URL_BASE = import.meta.env.VITE_URL_API || "http://127.0.0.1:8000";

export const cliente = axios.create({
  baseURL: URL_BASE,
  headers: { "Content-Type": "application/json" },
});

// Adjunta el token JWT en cada petición si existe / 每次请求自动附加 JWT
cliente.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
