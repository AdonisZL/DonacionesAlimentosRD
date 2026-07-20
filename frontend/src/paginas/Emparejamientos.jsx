// Página de emparejamientos / 匹配页 (OE3 — RF-17 … RF-22)

import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import {
  buscarCandidatos,
  completarEmparejamiento,
  confirmarEmparejamiento,
  crearEmparejamiento,
  enviarRetroalimentacion,
  obtenerEmparejamientos,
  rechazarEmparejamiento,
} from "../api/emparejamiento.js";
import { obtenerLotes } from "../api/inventario.js";
import { useSesion } from "../context/ContextoSesion.jsx";
import EncabezadoApp from "../componentes/EncabezadoApp.jsx";
import PieDePagina from "../componentes/PieDePagina.jsx";

const COLOR_ESTADO = {
  sugerido: "badge-estado sugerido",
  confirmado: "badge-estado confirmado",
  rechazado: "badge-estado rechazado",
  expirado: "badge-estado expirado",
  completado: "badge-estado completado",
};

function Emparejamientos() {
  const { usuario } = useSesion();

  const [lotes, setLotes] = useState([]);
  const [matches, setMatches] = useState([]);
  const [idLote, setIdLote] = useState("");
  const [radio, setRadio] = useState(25);
  const [candidatos, setCandidatos] = useState([]);
  const [buscando, setBuscando] = useState(false);

  const [error, setError] = useState(null);
  const [mensaje, setMensaje] = useState(null);

  // Retroalimentación por match / 每个匹配的反馈
  const [retro, setRetro] = useState({});

  async function cargar() {
    setError(null);
    try {
      const [ls, ms] = await Promise.all([
        obtenerLotes(),
        obtenerEmparejamientos(),
      ]);
      setLotes(ls.filter((l) => l.estado === "disponible"));
      setMatches(ms);
    } catch {
      setError("No se pudieron cargar los datos.");
    }
  }

  useEffect(() => {
    if (usuario) cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!usuario) return <Navigate to="/login" replace />;

  async function buscar() {
    setError(null);
    setMensaje(null);
    setCandidatos([]);
    if (!idLote) {
      setError("Selecciona un lote disponible.");
      return;
    }
    setBuscando(true);
    try {
      const res = await buscarCandidatos(idLote, Number(radio));
      setCandidatos(res);
      if (res.length === 0) {
        setMensaje("No se encontraron receptores dentro del radio indicado.");
      }
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo buscar receptores.");
    } finally {
      setBuscando(false);
    }
  }

  async function sugerir(idSede) {
    setError(null);
    setMensaje(null);
    try {
      await crearEmparejamiento(idLote, idSede, Number(radio));
      setMensaje("Emparejamiento sugerido creado.");
      setCandidatos([]);
      setIdLote("");
      await cargar();
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo crear el emparejamiento.");
    }
  }

  async function accion(fn, id, exito) {
    setError(null);
    setMensaje(null);
    try {
      await fn(id);
      setMensaje(exito);
      await cargar();
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo completar la acción.");
    }
  }

  async function calificar(id) {
    const r = retro[id] || {};
    if (!r.calificacion) {
      setError("Indica una calificación (1–5).");
      return;
    }
    setError(null);
    setMensaje(null);
    try {
      await enviarRetroalimentacion(id, Number(r.calificacion), r.comentario || null);
      setMensaje("¡Gracias por tu calificación!");
      setRetro((prev) => ({ ...prev, [id]: {} }));
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo enviar la calificación.");
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <EncabezadoApp />

      <main className="flex-1 w-full max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop py-2xl flex flex-col gap-xl">
        <div>
          <div className="flex items-center gap-sm mb-sm">
            <span className="material-symbols-outlined text-primary">hub</span>
            <h1 className="font-headline-lg text-headline-lg text-on-surface page-header">
              Emparejamiento inteligente
            </h1>
          </div>
          <p className="font-body-md text-body-md text-on-surface-variant">
            Conecta tus lotes con los receptores más compatibles.
          </p>
        </div>

        {error && (
          <div className="flex items-center gap-sm rounded-lg bg-error/10 border border-error/20 px-sm py-sm text-error">
            <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>error</span>
            <span className="font-body-md text-sm">{error}</span>
          </div>
        )}
        {mensaje && (
          <div className="flex items-center gap-sm rounded-lg bg-primary/10 border border-primary/20 px-sm py-sm text-primary">
            <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>
              check_circle
            </span>
            <span className="font-body-md text-sm">{mensaje}</span>
          </div>
        )}

        {/* Búsqueda de receptores (RF-17) */}
        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl shadow-sm hover-lift-sm">
          <div className="flex items-center gap-sm mb-md">
            <span className="material-symbols-outlined text-primary">search</span>
            <h2 className="font-headline-md text-headline-md text-on-surface">
              Buscar receptores compatibles
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-md items-end">
            <div className="flex flex-col gap-xs md:col-span-2">
              <label htmlFor="lote" className="font-label-sm text-label-sm text-on-surface-variant">
                Lote disponible
              </label>
              <select
                id="lote"
                className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-sm py-sm font-body-md text-body-md text-on-surface"
                value={idLote}
                onChange={(e) => setIdLote(e.target.value)}
              >
                <option value="">Selecciona un lote…</option>
                {lotes.map((l) => (
                  <option key={l.id_lote} value={l.id_lote}>
                    {l.nombre_producto} · {l.cantidad_disponible} {l.unidad_medida || ""} · vence {l.fecha_vencimiento}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-xs">
              <label htmlFor="radio" className="font-label-sm text-label-sm text-on-surface-variant">
                Radio (km, máx. 75)
              </label>
              <input
                id="radio"
                type="number"
                min={1}
                max={75}
                value={radio}
                onChange={(e) => setRadio(e.target.value)}
                className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-sm py-sm font-body-md text-body-md text-on-surface"
              />
            </div>
          </div>
          <div className="mt-md">
            <button
              type="button"
              onClick={buscar}
              disabled={buscando}
              className="py-sm px-lg rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 hover:scale-[1.02] transition-all disabled:opacity-60 disabled:hover:scale-100 flex items-center gap-xs"
            >
              <span className="material-symbols-outlined text-sm">search</span>
              {buscando ? "Buscando…" : "Buscar receptores"}
            </button>
          </div>

          {/* Candidatos */}
          {candidatos.length > 0 && (
            <ul className="mt-lg flex flex-col gap-sm animar-lista">
              {candidatos.map((c) => (
                <li
                  key={c.id_sede}
                  className="rounded-xl border border-outline-variant/40 p-md flex flex-col gap-xs hover:border-primary/20 hover:bg-primary/[0.02] transition-all"
                >
                  <div className="flex items-center justify-between gap-md">
                    <div>
                      <p className="font-label-md text-label-md text-on-surface font-semibold">
                        {c.nombre_sede || "Sede receptora"} · {c.distancia_km} km
                      </p>
                      <p className="font-body-md text-sm text-on-surface-variant">
                        {c.direccion_texto || "Sin dirección"}
                      </p>
                    </div>
                    <button
                      type="button"
                      disabled={!c.compatible}
                      onClick={() => sugerir(c.id_sede)}
                      className="py-xs px-md rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-md hover:shadow-primary/20 hover:scale-[1.02] transition-all disabled:opacity-40 disabled:hover:scale-100"
                    >
                      Sugerir
                    </button>
                  </div>
                  <p className="font-body-md text-sm text-on-surface-variant italic flex items-start gap-xs">
                    <span className="material-symbols-outlined text-tertiary text-sm mt-0.5">psychology</span>
                    IA: {c.justificacion_ia}
                  </p>
                  {!c.compatible && (
                    <p className="font-body-md text-sm text-error flex items-center gap-xs">
                      <span className="material-symbols-outlined text-sm">block</span>
                      {c.motivo_incompatible}
                    </p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Emparejamientos (RF-19/20/21/22) */}
        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl shadow-sm hover-lift-sm">
          <div className="flex items-center gap-sm mb-md">
            <span className="material-symbols-outlined text-primary">link</span>
            <h2 className="font-headline-md text-headline-md text-on-surface">
              Mis emparejamientos
            </h2>
          </div>
          {matches.length === 0 ? (
            <p className="font-body-md text-on-surface-variant">
              Aún no hay emparejamientos.
            </p>
          ) : (
            <ul className="flex flex-col gap-md">
              {matches.map((m) => (
                <li
                  key={m.id_emparejamiento}
                  className="rounded-lg border border-outline-variant/40 p-md flex flex-col gap-sm"
                >
                  <div className="flex items-center justify-between gap-md flex-wrap">
                    <div>
                      <p className="font-label-md text-label-md text-on-surface">
                        {m.nombre_producto} → {m.nombre_sede} · {m.distancia_km} km
                      </p>
                      {m.fecha_limite_retiro && (
                        <p className="font-body-md text-sm text-on-surface-variant">
                          Retiro antes de: {new Date(m.fecha_limite_retiro).toLocaleString()}
                        </p>
                      )}
                    </div>
                    <span
                      className={`inline-block rounded-full px-sm py-[2px] font-label-sm text-label-sm capitalize font-semibold ${COLOR_ESTADO[m.estado_tramite] || ""}`}
                    >
                      {m.estado_tramite}
                    </span>
                  </div>

                  {m.justificacion_ia && (
                    <p className="font-body-md text-sm text-on-surface-variant italic flex items-start gap-xs">
                      <span className="material-symbols-outlined text-tertiary text-sm mt-0.5">psychology</span>
                      IA: {m.justificacion_ia}
                    </p>
                  )}

                  <div className="flex flex-wrap gap-sm">
                    {m.estado_tramite === "sugerido" && (
                      <>
                        <button
                          type="button"
                          onClick={() => accion(confirmarEmparejamiento, m.id_emparejamiento, "Emparejamiento confirmado.")}
                          className="py-xs px-md rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-md hover:shadow-primary/20 transition-all flex items-center gap-xs"
                        >
                          <span className="material-symbols-outlined text-sm">check</span>
                          Confirmar
                        </button>
                        <button
                          type="button"
                          onClick={() => accion(rechazarEmparejamiento, m.id_emparejamiento, "Emparejamiento rechazado.")}
                          className="py-xs px-md rounded-lg border-2 border-error/30 text-error font-label-md text-label-md font-semibold hover:bg-error/5 transition-all flex items-center gap-xs"
                        >
                          <span className="material-symbols-outlined text-sm">close</span>
                          Rechazar
                        </button>
                      </>
                    )}
                    {m.estado_tramite === "confirmado" && (
                      <>
                        <button
                          type="button"
                          onClick={() => accion(completarEmparejamiento, m.id_emparejamiento, "Entrega registrada.")}
                          className="py-xs px-md rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-md hover:shadow-primary/20 transition-all flex items-center gap-xs"
                        >
                          <span className="material-symbols-outlined text-sm">local_shipping</span>
                          Marcar entregado
                        </button>
                        <button
                          type="button"
                          onClick={() => accion(rechazarEmparejamiento, m.id_emparejamiento, "Emparejamiento rechazado.")}
                          className="py-xs px-md rounded-lg border-2 border-error/30 text-error font-label-md text-label-md font-semibold hover:bg-error/5 transition-all flex items-center gap-xs"
                        >
                          <span className="material-symbols-outlined text-sm">close</span>
                          Rechazar / reasignar
                        </button>
                      </>
                    )}
                    {m.estado_tramite === "completado" && (
                      <div className="flex flex-wrap items-end gap-sm">
                        <div className="flex flex-col gap-xs">
                          <label className="font-label-sm text-label-sm text-on-surface-variant">
                            Calificación (1–5)
                          </label>
                          <input
                            type="number"
                            min={1}
                            max={5}
                            value={(retro[m.id_emparejamiento] || {}).calificacion || ""}
                            onChange={(e) =>
                              setRetro((prev) => ({
                                ...prev,
                                [m.id_emparejamiento]: {
                                  ...(prev[m.id_emparejamiento] || {}),
                                  calificacion: e.target.value,
                                },
                              }))
                            }
                            className="w-24 rounded-lg border border-outline-variant bg-surface-container-lowest px-sm py-sm font-body-md text-body-md text-on-surface"
                          />
                        </div>
                        <div className="flex flex-col gap-xs">
                          <label className="font-label-sm text-label-sm text-on-surface-variant">
                            Comentario
                          </label>
                          <input
                            type="text"
                            value={(retro[m.id_emparejamiento] || {}).comentario || ""}
                            onChange={(e) =>
                              setRetro((prev) => ({
                                ...prev,
                                [m.id_emparejamiento]: {
                                  ...(prev[m.id_emparejamiento] || {}),
                                  comentario: e.target.value,
                                },
                              }))
                            }
                            className="rounded-lg border border-outline-variant bg-surface-container-lowest px-sm py-sm font-body-md text-body-md text-on-surface"
                          />
                        </div>
                        <button
                          type="button"
                          onClick={() => calificar(m.id_emparejamiento)}
                          className="py-sm px-md rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-md hover:shadow-primary/20 transition-all flex items-center gap-xs"
                        >
                          <span className="material-symbols-outlined text-sm">star</span>
                          Calificar
                        </button>
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
      <PieDePagina />
    </div>
  );
}

export default Emparejamientos;
