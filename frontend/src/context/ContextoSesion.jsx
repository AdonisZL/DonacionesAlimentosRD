// Contexto de sesión / 会话上下文
// Guarda el usuario y el token en localStorage. / 将用户与令牌保存在 localStorage。

import { createContext, useContext, useEffect, useState } from "react";

const ContextoSesion = createContext(null);

export function SesionProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const usuarioGuardado = localStorage.getItem("usuario");
    if (usuarioGuardado) {
      setUsuario(JSON.parse(usuarioGuardado));
    }
    setCargando(false);
  }, []);

  function guardarSesion(datos) {
    localStorage.setItem("token", datos.access_token);
    localStorage.setItem("usuario", JSON.stringify(datos.usuario));
    setUsuario(datos.usuario);
  }

  function cerrarSesion() {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");
    setUsuario(null);
  }

  function actualizarUsuario(nuevoUsuario) {
    localStorage.setItem("usuario", JSON.stringify(nuevoUsuario));
    setUsuario(nuevoUsuario);
  }

  return (
    <ContextoSesion.Provider
      value={{ usuario, cargando, guardarSesion, cerrarSesion, actualizarUsuario }}
    >
      {children}
    </ContextoSesion.Provider>
  );
}

export function useSesion() {
  return useContext(ContextoSesion);
}
