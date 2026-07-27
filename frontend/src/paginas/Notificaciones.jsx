// Página de notificaciones / 通知页面 (RF-21)
// Lista completa con opción de marcar como leídas individualmente.

import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import { obtenerNotificaciones, marcarNotificacionLeida } from "../api/emparejamiento.js";
import { useSesion } from "../context/ContextoSesion.jsx";
import EncabezadoApp from "../componentes/EncabezadoApp.jsx";
import PieDePagina from "../componentes/PieDePagina.jsx";

function Notificaciones() {
  const { usuario } = useSesion();
  const [notificaciones, setNotificaciones] = useState([]);
  const [cargando, setCargando] = useState(true);

  if (!usuario) return <Navigate to="/login" replace />;

  useEffect(() => {
    cargar();
  }, []);

  async function cargar() {
    setCargando(true);
    try {
      setNotificaciones(await obtenerNotificaciones());
    } catch {
      // silencioso
    } finally {
      setCargando(false);
    }
  }

  async function marcarLeida(id) {
    try {
      await marcarNotificacionLeida(id);
      setNotificaciones((prev) =>
        prev.map((n) => (n.id_notificacion === id ? { ...n, leido: true } : n)),
      );
    } catch {
      // silencioso
    }
  }

  const noLeidas = notificaciones.filter((n) => !n.leido).length;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <EncabezadoApp />

      <main className="flex-1 w-full max-w-3xl mx-auto px-margin-mobile md:px-margin-desktop py-2xl">
        {/* Cabecera */}
        <div className="flex items-center gap-lg mb-xl">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary to-primary-container text-on-primary flex items-center justify-center shadow-lg shadow-primary/20">
            <span className="material-symbols-outlined text-2xl">notifications</span>
          </div>
          <div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface page-header">
              Notificaciones
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant">
              {noLeidas > 0
                ? `${noLeidas} sin leer`
                : "Todo al día"}
            </p>
          </div>
        </div>

        {/* Lista */}
        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 overflow-hidden shadow-sm">
          {cargando ? (
            <div className="flex justify-center py-2xl">
              <span className="font-body-md text-body-md text-on-surface-variant">Cargando…</span>
            </div>
          ) : notificaciones.length === 0 ? (
            <div className="flex flex-col items-center gap-sm py-2xl text-center">
              <span className="material-symbols-outlined text-5xl text-on-surface-variant/20">notifications_off</span>
              <p className="font-body-md text-body-md text-on-surface-variant">
                No tienes notificaciones todavía.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-outline-variant/10">
              {notificaciones.map((n) => (
                <div
                  key={n.id_notificacion}
                  className={`flex items-start gap-md px-xl py-lg transition-colors ${!n.leido ? "bg-primary/3" : "hover:bg-surface-container-low"}`}
                >
                  {/* Ícono de estado */}
                  <button
                    onClick={() => !n.leido && marcarLeida(n.id_notificacion)}
                    className="shrink-0 mt-0.5"
                    title={n.leido ? "Leída" : "Marcar como leída"}
                  >
                    <span
                      className={`material-symbols-outlined text-xl ${!n.leido ? "text-primary" : "text-on-surface-variant/30"}`}
                      style={!n.leido ? { fontVariationSettings: "'FILL' 1" } : {}}
                    >
                      {!n.leido ? "circle" : "check_circle"}
                    </span>
                  </button>

                  {/* Contenido */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-sm mb-xs">
                      <span className={`font-label-md text-label-md ${!n.leido ? "text-on-surface font-semibold" : "text-on-surface-variant"}`}>
                        {n.titulo || "Notificación"}
                      </span>
                      <span className="font-label-xs text-on-surface-variant/50 whitespace-nowrap">
                        {new Date(n.creado_en).toLocaleString("es-DO", {
                          day: "numeric",
                          month: "short",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                    </div>
                    <p className="font-body-md text-sm text-on-surface-variant">
                      {n.mensaje || ""}
                    </p>
                  </div>

                  {/* Botón marcar leída */}
                  {!n.leido && (
                    <button
                      onClick={() => marcarLeida(n.id_notificacion)}
                      className="shrink-0 py-xs px-sm rounded-lg text-primary font-label-sm hover:bg-primary/8 transition-colors"
                    >
                      Leída
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
      <PieDePagina />
    </div>
  );
}

export default Notificaciones;
