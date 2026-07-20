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
  const [scrollY, setScrollY] = useState(0);

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

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  function salir() {
    cerrarSesion();
    navegar("/login");
  }

  const tieneSombra = scrollY > 8;

  return (
    <header
      className={`sticky top-0 z-40 bg-surface/85 backdrop-blur-md border-b transition-shadow duration-300 ${
        tieneSombra
          ? "border-outline-variant/20 shadow-[0_1px_12px_rgba(11,28,48,0.06)]"
          : "border-outline-variant/30"
      }`}
    >
      <div className="max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop h-16 flex items-center justify-between gap-md">
        <Link to="/" className="shrink-0">
          <Marca />
        </Link>

        {/* Navegación escritorio / 桌面导航 */}
        <nav className="hidden md:flex items-center gap-1">
          {enlaces.map((e) => (
            <NavLink
              key={e.a}
              to={e.a}
              end={e.a === "/"}
              className={({ isActive }) =>
                `relative flex items-center gap-xs px-md py-sm rounded-lg font-label-md text-label-md transition-all duration-200 ${
                  isActive
                    ? "bg-primary/10 text-primary font-semibold"
                    : "text-on-surface-variant hover:bg-surface-container-low hover:text-primary"
                }`
              }
            >
              <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>
                {e.icono}
              </span>
              {e.texto}
              {({ isActive }) =>
                isActive && (
                  <span className="absolute bottom-0.5 left-1/2 -translate-x-1/2 w-5 h-0.5 rounded-full bg-primary" />
                )
              }
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-sm">
          {usuario && (
            <span className="hidden sm:flex items-center gap-xs text-on-surface-variant font-label-md text-label-md">
              <span className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-container/30 to-primary/20 text-primary flex items-center justify-center font-headline-md ring-2 ring-primary/10">
                {(usuario.nombre || "?").charAt(0).toUpperCase()}
              </span>
              {usuario.nombre}
            </span>
          )}
          <button
            type="button"
            onClick={salir}
            className="flex items-center gap-xs py-sm px-md rounded-lg border border-outline-variant/60 text-on-surface hover:bg-surface-container-low hover:border-outline-variant transition-all font-label-md text-label-md"
          >
            <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>
              logout
            </span>
            <span className="hidden sm:inline">Salir</span>
          </button>
        </div>
      </div>

      {/* Navegación móvil / 移动端导航 */}
      <nav className="md:hidden flex items-center gap-1 overflow-x-auto px-margin-mobile pb-sm">
        {enlaces.map((e) => (
          <NavLink
            key={e.a}
            to={e.a}
            end={e.a === "/"}
            className={({ isActive }) =>
              `flex items-center gap-xs px-sm py-xs rounded-lg font-label-sm text-label-sm whitespace-nowrap transition-all duration-200 ${
                isActive
                  ? "bg-primary/10 text-primary font-semibold"
                  : "text-on-surface-variant active:bg-surface-container-low"
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
