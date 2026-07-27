// Campana de notificaciones con badge / 通知铃铛（含未读徽章）

import { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";
import { obtenerNotificaciones, marcarNotificacionLeida } from "../api/emparejamiento.js";

function CampanaNotificaciones() {
  const [notificaciones, setNotificaciones] = useState([]);
  const [abierto, setAbierto] = useState(false);
  const ref = useRef(null);

  const noLeidas = notificaciones.filter((n) => !n.leido).length;

  useEffect(() => {
    cargar();
    const intervalo = setInterval(cargar, 60_000); // actualizar cada min / 每分钟刷新
    return () => clearInterval(intervalo);
  }, []);

  useEffect(() => {
    function cerrarFuera(e) {
      if (ref.current && !ref.current.contains(e.target)) setAbierto(false);
    }
    document.addEventListener("mousedown", cerrarFuera);
    return () => document.removeEventListener("mousedown", cerrarFuera);
  }, []);

  async function cargar() {
    try {
      setNotificaciones(await obtenerNotificaciones());
    } catch {
      // silencioso / 静默失败
    }
  }

  async function leer(id) {
    try {
      await marcarNotificacionLeida(id);
      setNotificaciones((prev) =>
        prev.map((n) => (n.id_notificacion === id ? { ...n, leido: true } : n)),
      );
    } catch {
      // silencioso
    }
  }

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setAbierto(!abierto)}
        className="relative p-sm rounded-lg text-on-surface-variant hover:text-primary hover:bg-surface-container-low transition-colors"
        aria-label={`Notificaciones${noLeidas > 0 ? ` (${noLeidas} sin leer)` : ""}`}
      >
        <span className="material-symbols-outlined" style={{ fontSize: "22px" }}>
          notifications
        </span>
        {noLeidas > 0 && (
          <span className="absolute -top-0.5 -right-0.5 w-5 h-5 rounded-full bg-error text-on-error font-label-xs flex items-center justify-center text-[11px] leading-none shadow-sm shadow-error/30 animate-pulse">
            {noLeidas > 9 ? "9+" : noLeidas}
          </span>
        )}
      </button>

      {/* Dropdown / 下拉面板 */}
      {abierto && (
        <div className="absolute right-0 top-full mt-xs w-80 max-h-[60vh] bg-surface-container-lowest rounded-2xl border border-outline-variant/30 shadow-xl shadow-on-surface/8 overflow-hidden z-50 animate-fade-in">
          <div className="flex items-center justify-between px-lg py-md border-b border-outline-variant/20">
            <span className="font-label-md text-label-md text-on-surface font-semibold">
              Notificaciones
            </span>
            <Link
              to="/notificaciones"
              onClick={() => setAbierto(false)}
              className="font-label-sm text-label-sm text-primary hover:underline"
            >
              Ver todas
            </Link>
          </div>

          <div className="overflow-y-auto max-h-[50vh]">
            {notificaciones.length === 0 ? (
              <div className="flex flex-col items-center gap-xs py-xl text-center">
                <span className="material-symbols-outlined text-3xl text-on-surface-variant/30">notifications_off</span>
                <span className="font-body-md text-sm text-on-surface-variant">Sin notificaciones</span>
              </div>
            ) : (
              notificaciones.slice(0, 5).map((n) => (
                <button
                  key={n.id_notificacion}
                  onClick={() => leer(n.id_notificacion)}
                  className={`w-full text-left px-lg py-md flex items-start gap-sm hover:bg-surface-container-low transition-colors border-b border-outline-variant/10 ${!n.leido ? "bg-primary/3" : ""}`}
                >
                  <span
                    className={`material-symbols-outlined text-lg mt-0.5 shrink-0 ${!n.leido ? "text-primary" : "text-on-surface-variant/50"}`}
                  >
                    {!n.leido ? "circle" : "notifications"}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className={`font-label-sm text-label-sm truncate ${!n.leido ? "text-on-surface font-semibold" : "text-on-surface-variant"}`}>
                      {n.titulo || "Notificación"}
                    </p>
                    <p className="font-body-md text-xs text-on-surface-variant truncate mt-0.5">
                      {n.mensaje || ""}
                    </p>
                    <p className="font-label-xs text-on-surface-variant/60 mt-1">
                      {new Date(n.creado_en).toLocaleString("es-DO")}
                    </p>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default CampanaNotificaciones;
