// Página de derechos ARCO / ARCO 权利页面 (RN-19, Ley 172-13)
// Permite al usuario ejercer sus derechos de Acceso, Rectificación, Cancelación y Oposición.
// 允许用户行使其访问、更正、删除和反对权。

import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import { crearSolicitudArco, obtenerMisSolicitudes } from "../api/arco.js";
import { useSesion } from "../context/ContextoSesion.jsx";
import EncabezadoApp from "../componentes/EncabezadoApp.jsx";
import PieDePagina from "../componentes/PieDePagina.jsx";

const TIPOS_ARCO = [
  {
    valor: "acceso",
    etiqueta: "Acceso",
    icono: "visibility",
    descripcion: "Solicitar copia de mis datos personales almacenados en el sistema.",
  },
  {
    valor: "rectificacion",
    etiqueta: "Rectificación",
    icono: "edit",
    descripcion: "Corregir datos personales inexactos o incompletos.",
  },
  {
    valor: "cancelacion",
    etiqueta: "Cancelación",
    icono: "delete",
    descripcion: "Solicitar la eliminación de mis datos cuando ya no sean necesarios.",
  },
  {
    valor: "oposicion",
    etiqueta: "Oposición",
    icono: "block",
    descripcion: "Oponerme al tratamiento de mis datos para fines específicos.",
  },
];

const ETIQUETA_ESTADO = {
  recibida: { texto: "Recibida", color: "bg-primary/10 text-primary border-primary/20" },
  en_proceso: { texto: "En proceso", color: "bg-amber/10 text-amber border-amber/20" },
  resuelta: { texto: "Resuelta", color: "bg-green/10 text-green border-green/20" },
  rechazada: { texto: "Rechazada", color: "bg-red/10 text-red border-red/20" },
  vencida: { texto: "Vencida", color: "bg-gray/10 text-gray border-gray/20" },
};

function MisDerechos() {
  const { usuario } = useSesion();
  const [solicitudes, setSolicitudes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [form, setForm] = useState({ tipo_solicitud: "", descripcion: "" });
  const [error, setError] = useState(null);
  const [exito, setExito] = useState(null);
  const [enviando, setEnviando] = useState(false);

  if (!usuario) return <Navigate to="/login" replace />;

  useEffect(() => {
    cargarSolicitudes();
  }, []);

  async function cargarSolicitudes() {
    setCargando(true);
    try {
      const data = await obtenerMisSolicitudes();
      setSolicitudes(data);
    } catch {
      setError("No se pudieron cargar tus solicitudes.");
    } finally {
      setCargando(false);
    }
  }

  async function enviarSolicitud(e) {
    e.preventDefault();
    setError(null);
    setExito(null);
    if (!form.tipo_solicitud) {
      setError("Selecciona el tipo de derecho que deseas ejercer.");
      return;
    }
    setEnviando(true);
    try {
      await crearSolicitudArco(form);
      setExito("¡Solicitud creada! Recibirás respuesta en un máximo de 15 días hábiles.");
      setForm({ tipo_solicitud: "", descripcion: "" });
      setMostrarFormulario(false);
      cargarSolicitudes();
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(detalle || "No se pudo crear la solicitud.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <EncabezadoApp />

      <main className="flex-1 w-full max-w-3xl mx-auto px-margin-mobile md:px-margin-desktop py-2xl">
        {/* Cabecera */}
        <div className="flex items-center gap-lg mb-xl">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary to-primary-container text-on-primary flex items-center justify-center shadow-lg shadow-primary/20">
            <span className="material-symbols-outlined text-2xl">shield_person</span>
          </div>
          <div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface page-header">
              Mis derechos ARCO
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Ley 172-13 — Protección de datos personales
            </p>
          </div>
        </div>

        {/* Mensajes */}
        {error && (
          <div className="flex items-center gap-sm rounded-lg bg-error-container px-sm py-sm text-on-error-container mb-md">
            <span className="material-symbols-outlined text-sm">error</span>
            <span className="font-body-md text-sm">{error}</span>
          </div>
        )}
        {exito && (
          <div className="flex items-center gap-sm rounded-lg bg-primary/10 border border-primary/20 px-sm py-sm text-primary mb-md">
            <span className="material-symbols-outlined text-sm">check_circle</span>
            <span className="font-body-md text-sm">{exito}</span>
          </div>
        )}

        {/* Botón nueva solicitud */}
        {!mostrarFormulario && (
          <button
            onClick={() => setMostrarFormulario(true)}
            className="mb-lg py-sm px-lg rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 hover:scale-[1.02] transition-all flex items-center gap-xs"
          >
            <span className="material-symbols-outlined text-sm">add</span>
            Nueva solicitud ARCO
          </button>
        )}

        {/* Formulario nueva solicitud */}
        {mostrarFormulario && (
          <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl shadow-sm mb-xl">
            <h2 className="font-headline-md text-headline-md text-on-surface mb-md">
              Nueva solicitud
            </h2>
            <form onSubmit={enviarSolicitud} className="flex flex-col gap-md">
              {/* Selección de tipo ARCO */}
              <div className="flex flex-col gap-sm">
                <span className="font-label-md text-label-md text-on-surface">Derecho a ejercer</span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-sm">
                  {TIPOS_ARCO.map((t) => (
                    <label
                      key={t.valor}
                      className={`flex flex-col items-center gap-xs p-md border-2 rounded-xl cursor-pointer transition-all duration-200 text-center ${
                        form.tipo_solicitud === t.valor
                          ? "border-primary bg-primary/5 shadow-sm"
                          : "border-outline-variant/40 hover:bg-surface-container-low"
                      }`}
                    >
                      <input
                        type="radio"
                        name="tipo"
                        value={t.valor}
                        checked={form.tipo_solicitud === t.valor}
                        onChange={(e) => setForm((f) => ({ ...f, tipo_solicitud: e.target.value }))}
                        className="sr-only"
                      />
                      <span className="material-symbols-outlined text-2xl text-primary">{t.icono}</span>
                      <span className="font-label-md text-label-md text-on-surface font-semibold">{t.etiqueta}</span>
                      <span className="font-label-sm text-label-sm text-on-surface-variant">{t.descripcion}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Descripción */}
              <div className="flex flex-col gap-xs">
                <label className="font-label-md text-label-md text-on-surface" htmlFor="descripcion">
                  Detalle de la solicitud
                </label>
                <textarea
                  id="descripcion"
                  rows={3}
                  value={form.descripcion}
                  onChange={(e) => setForm((f) => ({ ...f, descripcion: e.target.value }))}
                  placeholder="Describe qué dato deseas acceder, corregir, eliminar o a qué tratamiento te opones..."
                  className="w-full px-sm py-sm bg-surface border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all placeholder:text-outline-variant/60 resize-y"
                />
              </div>

              {/* Botones */}
              <div className="flex justify-end gap-sm pt-sm border-t border-outline-variant/30">
                <button
                  type="button"
                  onClick={() => setMostrarFormulario(false)}
                  className="py-sm px-lg rounded-lg text-on-surface-variant hover:text-on-surface font-label-md text-label-md transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={enviando}
                  className="py-sm px-lg rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 hover:scale-[1.02] transition-all disabled:opacity-60 flex items-center gap-xs"
                >
                  <span className="material-symbols-outlined text-sm">send</span>
                  {enviando ? "Enviando…" : "Enviar solicitud"}
                </button>
              </div>
            </form>
          </section>
        )}

        {/* Lista de solicitudes */}
        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl shadow-sm">
          <h2 className="font-headline-md text-headline-md text-on-surface mb-md">
            Historial de solicitudes
          </h2>
          {cargando ? (
            <p className="font-body-md text-body-md text-on-surface-variant">Cargando…</p>
          ) : solicitudes.length === 0 ? (
            <div className="flex flex-col items-center gap-sm py-xl text-center">
              <span className="material-symbols-outlined text-4xl text-on-surface-variant/40">folder_open</span>
              <p className="font-body-md text-body-md text-on-surface-variant">
                No has ejercido ningún derecho ARCO todavía.
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-sm">
              {solicitudes.map((s) => {
                const estadoInfo = ETIQUETA_ESTADO[s.estado] || ETIQUETA_ESTADO.recibida;
                return (
                  <div
                    key={s.id_solicitud}
                    className="flex flex-col sm:flex-row sm:items-center gap-sm p-md rounded-xl border border-outline-variant/20 hover:border-outline-variant/40 transition-colors"
                  >
                    <div className="flex-1 flex flex-col gap-xs">
                      <div className="flex items-center gap-sm">
                        <span className="font-label-md text-label-md text-on-surface font-semibold capitalize">
                          {s.tipo_solicitud}
                        </span>
                        <span className={`font-label-sm text-label-sm px-xs py-0.5 rounded-full border ${estadoInfo.color}`}>
                          {estadoInfo.texto}
                        </span>
                      </div>
                      {s.descripcion && (
                        <p className="font-body-md text-sm text-on-surface-variant">
                          {s.descripcion}
                        </p>
                      )}
                      <div className="flex flex-wrap gap-x-md gap-y-xs font-label-sm text-label-sm text-on-surface-variant/70">
                        <span>{new Date(s.fecha_solicitud).toLocaleDateString("es-DO")}</span>
                        <span>Límite: {new Date(s.fecha_limite_respuesta).toLocaleDateString("es-DO")}</span>
                      </div>
                      {s.respuesta && (
                        <div className="mt-xs p-sm rounded-lg bg-surface-container-low border border-outline-variant/20">
                          <span className="font-label-sm text-label-sm text-on-surface-variant">Respuesta:</span>
                          <p className="font-body-md text-sm text-on-surface mt-xs">{s.respuesta}</p>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </main>
      <PieDePagina />
    </div>
  );
}

export default MisDerechos;
