// Encabezado de la aplicación / 应用顶栏 (páginas internas)
// Barra de navegación fija con enlaces y sesión. / 固定导航栏 + 会话。

import { useEffect, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";

import { obtenerRoles } from "../api/autenticacion.js";
import { useSesion } from "../context/ContextoSesion.jsx";
import Marca from "./Marca.jsx";

const ENLACES = [
  { a: "/", texto: "Inicio", icono: "home" },
  { a: "/inventario", texto: "Inventario", icono: "inventory_2" },
  { a: "/emparejamientos", texto: "Emparejamientos", icono: "hub" },
  { a: "/reportes", texto: "Reportes", icono: "bar_chart" },
  { a: "/perfil", texto: "Perfil", icono: "person" },
];

const ENLACE_ADMIN = { a: "/admin", texto: "Admin", icono: "admin_panel_settings" };

function EncabezadoApp() {
  const { usuario, cerrarSesion } = useSesion();
  const navegar = useNavigate();
  const [enlaces, setEnlaces] = useState(ENLACES);

  useEffect(() => {
    if (!usuario) return;
    obtenerRoles()
      .then((roles) => {
        const rol = roles.find((r) => r.id_rol === usuario.id_rol);
        if (rol?.nombre === "administrador") {
          setEnlaces([...ENLACES, ENLACE_ADMIN]);
        }
      })
      .catch(() => {});
  }, [usuario]);

  function salir() {
    cerrarSesion();
    navegar("/login");
  }

  return (
    <header className="sticky top-0 z-40 bg-surface/85 backdrop-blur-md border-b border-outline-variant/30">
      <div className="max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop h-16 flex items-center justify-between gap-md">
        <Link to="/" className="shrink-0">
          <Marca />
        </Link>

        <nav className="hidden md:flex items-center gap-xs">
          {enlaces.map((e) => (
            <NavLink
              key={e.a}
              to={e.a}
              end={e.a === "/"}
              className={({ isActive }) =>
                `flex items-center gap-xs px-md py-sm rounded-lg font-label-md text-label-md transition-colors ${
                  isActive
                    ? "bg-primary-container/20 text-primary"
                    : "text-on-surface-variant hover:bg-surface-container-low hover:text-primary"
                }`
              }
            >
              <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>
                {e.icono}
              </span>
              {e.texto}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-sm">
          {usuario && (
            <span className="hidden sm:flex items-center gap-xs text-on-surface-variant font-label-md text-label-md">
              <span className="w-8 h-8 rounded-full bg-primary-container/25 text-primary flex items-center justify-center font-headline-md">
                {(usuario.nombre || "?").charAt(0).toUpperCase()}
              </span>
              {usuario.nombre}
            </span>
          )}
          <button
            type="button"
            onClick={salir}
            className="flex items-center gap-xs py-sm px-md rounded-lg border border-outline-variant text-on-surface hover:bg-surface-container-low transition-colors font-label-md text-label-md"
          >
            <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>
              logout
            </span>
            <span className="hidden sm:inline">Salir</span>
          </button>
        </div>
      </div>

      {/* Navegación móvil / 移动端导航 */}
      <nav className="md:hidden flex items-center gap-xs overflow-x-auto px-margin-mobile pb-sm">
        {enlaces.map((e) => (
          <NavLink
            key={e.a}
            to={e.a}
            end={e.a === "/"}
            className={({ isActive }) =>
              `flex items-center gap-xs px-sm py-xs rounded-lg font-label-sm text-label-sm whitespace-nowrap transition-colors ${
                isActive
                  ? "bg-primary-container/20 text-primary"
                  : "text-on-surface-variant"
              }`
            }
          >
            <span className="material-symbols-outlined" style={{ fontSize: "16px" }}>
              {e.icono}
            </span>
            {e.texto}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}

export default EncabezadoApp;
