// Página de administración / 管理页 (OE5 — RF-28/29/32)

import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import {
  cambiarEstadoUsuario,
  obtenerAuditoria,
  obtenerPanelAdmin,
  obtenerUsuariosAdmin,
} from "../api/admin.js";
import { obtenerTodasSolicitudes, resolverSolicitud } from "../api/arco.js";
import { obtenerRoles } from "../api/autenticacion.js";
import { useSesion } from "../context/ContextoSesion.jsx";
import EncabezadoApp from "../componentes/EncabezadoApp.jsx";
import PieDePagina from "../componentes/PieDePagina.jsx";

const ESTADOS = ["activo", "inactivo", "suspendido"];

function Admin() {
  const { usuario } = useSesion();

  const [esAdmin, setEsAdmin] = useState(null); // null = comprobando
  const [panel, setPanel] = useState(null);
  const [usuarios, setUsuarios] = useState([]);
  const [auditoria, setAuditoria] = useState([]);
  const [solicitudesArco, setSolicitudesArco] = useState([]);
  const [solicitudEnCurso, setSolicitudEnCurso] = useState(null);
  const [respuestaArco, setRespuestaArco] = useState({ estado: "resuelta", respuesta: "" });
  const [error, setError] = useState(null);
  const [mensaje, setMensaje] = useState(null);

  useEffect(() => {
    if (!usuario) return;
    obtenerRoles()
      .then((roles) => {
        const rol = roles.find((r) => r.id_rol === usuario.id_rol);
        const admin = rol?.nombre === "administrador";
        setEsAdmin(admin);
        if (admin) cargar();
      })
      .catch(() => setEsAdmin(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!usuario) return <Navigate to="/login" replace />;

  async function cargar() {
    setError(null);
    try {
      const [p, u, a, s] = await Promise.all([
        obtenerPanelAdmin(),
        obtenerUsuariosAdmin(),
        obtenerAuditoria(),
        obtenerTodasSolicitudes(),
      ]);
      setPanel(p);
      setUsuarios(u);
      setAuditoria(a);
      setSolicitudesArco(s);
    } catch {
      setError("No se pudieron cargar los datos de administración.");
    }
  }

  async function cambiar(idUsuario, estado) {
    setError(null);
    setMensaje(null);
    try {
      await cambiarEstadoUsuario(idUsuario, estado);
      setMensaje("Estado actualizado.");
      await cargar();
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo cambiar el estado.");
    }
  }

  function abrirResolucionArco(solicitud) {
    setError(null);
    setMensaje(null);
    setRespuestaArco({ estado: "resuelta", respuesta: "" });
    setSolicitudEnCurso(solicitud);
  }

  async function enviarResolucionArco(evento) {
    evento.preventDefault();
    if (!respuestaArco.respuesta.trim()) {
      setError("Escribe la respuesta para el solicitante.");
      return;
    }
    setError(null);
    setMensaje(null);
    try {
      await resolverSolicitud(solicitudEnCurso.id_solicitud, respuestaArco);
      setMensaje("Solicitud ARCO resuelta.");
      setSolicitudEnCurso(null);
      await cargar();
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo resolver la solicitud.");
    }
  }

  if (esAdmin === false) {
    return (
      <div className="min-h-screen bg-background flex flex-col">
        <EncabezadoApp />
        <main className="flex-1 max-w-3xl w-full mx-auto px-margin-mobile md:px-margin-desktop py-2xl flex items-center justify-center">
          <div className="bg-surface-container-lowest rounded-3xl border border-error/20 p-2xl text-center max-w-md shadow-xl">
            <div className="w-20 h-20 bg-error/10 rounded-full flex items-center justify-center mx-auto mb-lg">
              <span className="material-symbols-outlined text-error" style={{ fontSize: "40px" }}>
                lock
              </span>
            </div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface mb-sm">
              Acceso restringido
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Esta sección es solo para administradores del sistema.
            </p>
          </div>
        </main>
        <PieDePagina />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <EncabezadoApp />

      <main className="flex-1 w-full max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop py-2xl flex flex-col gap-xl">
        <div>
          <div className="flex items-center gap-sm mb-sm">
            <span className="material-symbols-outlined text-primary">admin_panel_settings</span>
            <h1 className="font-headline-lg text-headline-lg text-on-surface page-header">
              Panel de administración
            </h1>
          </div>
          <p className="font-body-md text-body-md text-on-surface-variant">
            Gestión global del sistema, usuarios y auditoría.
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
            <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>check_circle</span>
            <span className="font-body-md text-sm">{mensaje}</span>
          </div>
        )}

        {/* Métricas (RF-32) */}
        {panel && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-lg">
              <Metrica icono="scale" valor={`${panel.kg_rescatados} kg`} etiqueta="Kg rescatados" color="text-primary bg-primary-container/20" />
              <Metrica icono="percent" valor={`${panel.tasa_efectividad}%`} etiqueta="Tasa de efectividad" color="text-tertiary bg-tertiary-container/20" />
              <Metrica icono="hub" valor={panel.emparejamientos_completados} etiqueta="Emparejamientos completados" color="text-secondary bg-secondary-container/20" />
              <Metrica icono="group" valor={Object.values(panel.usuarios_por_rol).reduce((a, b) => a + b, 0)} etiqueta="Usuarios registrados" color="text-primary bg-primary-container/20" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
              <Distribucion titulo="Por perecibilidad" datos={panel.distribucion_perecibilidad} />
              <Distribucion titulo="Usuarios por rol" datos={panel.usuarios_por_rol} />
              <Distribucion titulo="Lotes por estado" datos={panel.lotes_por_estado} />
            </div>
          </>
        )}

        {/* Usuarios (RF-28) */}
        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl">
          <h2 className="font-headline-md text-headline-md text-on-surface mb-md">Usuarios</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-outline-variant/40 text-on-surface-variant font-label-sm text-label-sm">
                  <th className="py-sm pr-md">Nombre</th>
                  <th className="py-sm pr-md">Correo</th>
                  <th className="py-sm pr-md">Rol</th>
                  <th className="py-sm pr-md">Estado</th>
                  <th className="py-sm pr-md">Acción</th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map((u) => (
                  <tr key={u.id_usuario} className="border-b border-outline-variant/20 font-body-md text-body-md text-on-surface">
                    <td className="py-sm pr-md">{u.nombre}</td>
                    <td className="py-sm pr-md break-all">{u.email}</td>
                    <td className="py-sm pr-md capitalize">{u.rol.replace("_", " ")}</td>
                    <td className="py-sm pr-md">
                      <span className={`inline-block rounded-full px-sm py-[2px] font-label-sm text-label-sm capitalize ${
                        u.estado === "activo" ? "bg-primary-container/30 text-on-primary-container" : "bg-error/15 text-error"
                      }`}>
                        {u.estado}
                      </span>
                    </td>
                    <td className="py-sm pr-md">
                      <select
                        value={u.estado}
                        onChange={(e) => cambiar(u.id_usuario, e.target.value)}
                        className="rounded-lg border border-outline-variant bg-surface-container-lowest px-sm py-xs font-body-md text-sm text-on-surface"
                      >
                        {ESTADOS.map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Auditoría (RF-29) */}
        {/* Auditoría (RF-29) */}
        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl">
          <h2 className="font-headline-md text-headline-md text-on-surface mb-md">
            Bitácora de auditoría
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-outline-variant/40 text-on-surface-variant font-label-sm text-label-sm">
                  <th className="py-sm pr-md">Fecha</th>
                  <th className="py-sm pr-md">Acción</th>
                  <th className="py-sm pr-md">Entidad</th>
                  <th className="py-sm pr-md">IP</th>
                </tr>
              </thead>
              <tbody>
                {auditoria.map((a) => (
                  <tr key={a.id_bitacora} className="border-b border-outline-variant/20 font-body-md text-body-md text-on-surface">
                    <td className="py-sm pr-md">{a.creado_en ? new Date(a.creado_en).toLocaleString() : "—"}</td>
                    <td className="py-sm pr-md">{a.accion}</td>
                    <td className="py-sm pr-md">{a.entidad_afectada || "—"}</td>
                    <td className="py-sm pr-md">{a.ip_origen || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Solicitudes ARCO (RN-19, Ley 172-13) */}
        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl">
          <h2 className="font-headline-md text-headline-md text-on-surface mb-md flex items-center gap-sm">
            <span className="material-symbols-outlined text-primary">shield_person</span>
            Solicitudes ARCO
          </h2>
          {solicitudesArco.length === 0 ? (
            <p className="font-body-md text-on-surface-variant">No hay solicitudes registradas.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-outline-variant/40 text-on-surface-variant font-label-sm text-label-sm">
                    <th className="py-sm pr-md">Fecha</th>
                    <th className="py-sm pr-md">Tipo</th>
                    <th className="py-sm pr-md">Descripción</th>
                    <th className="py-sm pr-md">Límite (15 días hábiles)</th>
                    <th className="py-sm pr-md">Estado</th>
                    <th className="py-sm pr-md">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {solicitudesArco.map((s) => (
                    <tr key={s.id_solicitud} className="border-b border-outline-variant/20 font-body-md text-body-md text-on-surface align-top">
                      <td className="py-sm pr-md">{new Date(s.fecha_solicitud).toLocaleDateString()}</td>
                      <td className="py-sm pr-md capitalize">{s.tipo_solicitud}</td>
                      <td className="py-sm pr-md max-w-xs truncate" title={s.descripcion || ""}>
                        {s.descripcion || "—"}
                      </td>
                      <td className="py-sm pr-md">{s.fecha_limite_respuesta}</td>
                      <td className="py-sm pr-md">
                        <span className={`inline-block rounded-full px-sm py-[2px] font-label-sm text-label-sm capitalize ${
                          s.estado === "resuelta"
                            ? "bg-primary-container/30 text-on-primary-container"
                            : s.estado === "rechazada" || s.estado === "vencida"
                              ? "bg-error/15 text-error"
                              : "bg-secondary-container/30 text-on-secondary-container"
                        }`}>
                          {s.estado}
                        </span>
                      </td>
                      <td className="py-sm pr-md">
                        {["recibida", "en_proceso"].includes(s.estado) ? (
                          <button
                            type="button"
                            onClick={() => abrirResolucionArco(s)}
                            className="text-tertiary font-label-md text-label-md hover:underline"
                          >
                            Resolver
                          </button>
                        ) : (
                          <span className="text-on-surface-variant font-label-sm text-label-sm">
                            {s.respuesta ? "Respondida" : "—"}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      {/* Modal de resolución de solicitud ARCO */}
      {solicitudEnCurso && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-on-surface/40 backdrop-blur-sm px-margin-mobile">
          <div className="w-full max-w-md bg-surface-container-lowest rounded-2xl border border-outline-variant/30 shadow-xl p-xl animar-escala">
            <div className="flex items-center gap-sm mb-md">
              <span className="material-symbols-outlined text-primary">shield_person</span>
              <h2 className="font-headline-md text-headline-md text-on-surface">
                Resolver solicitud ARCO
              </h2>
            </div>
            <p className="font-body-md text-sm text-on-surface-variant mb-md capitalize">
              Tipo: {solicitudEnCurso.tipo_solicitud} — {solicitudEnCurso.descripcion || "sin detalle"}
            </p>
            <form onSubmit={enviarResolucionArco} className="flex flex-col gap-md">
              <div className="flex flex-col gap-xs">
                <span className="font-label-md text-label-md text-on-surface">Resultado</span>
                <div className="flex gap-sm">
                  {["resuelta", "rechazada"].map((op) => (
                    <label
                      key={op}
                      className={`flex-1 text-center py-sm rounded-lg border-2 cursor-pointer capitalize font-label-md text-label-md transition-all ${
                        respuestaArco.estado === op
                          ? "border-primary bg-primary/5 text-primary font-semibold"
                          : "border-outline-variant/40 text-on-surface-variant"
                      }`}
                    >
                      <input
                        type="radio"
                        name="estado_arco"
                        value={op}
                        checked={respuestaArco.estado === op}
                        onChange={() => setRespuestaArco((r) => ({ ...r, estado: op }))}
                        className="sr-only"
                      />
                      {op}
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex flex-col gap-xs">
                <label htmlFor="respuesta_arco" className="font-label-md text-label-md text-on-surface">
                  Respuesta para el solicitante
                </label>
                <textarea
                  id="respuesta_arco"
                  rows={3}
                  value={respuestaArco.respuesta}
                  onChange={(e) => setRespuestaArco((r) => ({ ...r, respuesta: e.target.value }))}
                  className="w-full px-sm py-sm bg-surface border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all resize-y"
                />
              </div>
              <div className="flex justify-end gap-sm pt-sm border-t border-outline-variant/30">
                <button
                  type="button"
                  onClick={() => setSolicitudEnCurso(null)}
                  className="py-sm px-lg rounded-lg text-on-surface-variant hover:text-on-surface font-label-md text-label-md transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="py-sm px-lg rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 transition-all flex items-center gap-xs"
                >
                  <span className="material-symbols-outlined text-sm">check</span>
                  Enviar resolución
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <PieDePagina />
    </div>
  );
}

function Metrica({ icono, valor, etiqueta, color }) {
  return (
    <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-lg flex items-center gap-md hover-lift-sm group">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform ${color}`}>
        <span className="material-symbols-outlined">{icono}</span>
      </div>
      <div>
        <p className="font-headline-md text-headline-md text-on-surface">{valor}</p>
        <p className="font-label-sm text-label-sm text-on-surface-variant">{etiqueta}</p>
      </div>
    </div>
  );
}

function Distribucion({ titulo, datos }) {
  const entradas = Object.entries(datos || {});
  return (
    <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-lg">
      <h3 className="font-label-md text-label-md text-on-surface-variant mb-sm">{titulo}</h3>
      {entradas.length === 0 ? (
        <p className="font-body-md text-sm text-on-surface-variant">Sin datos.</p>
      ) : (
        <ul className="flex flex-col gap-xs">
          {entradas.map(([k, v]) => (
            <li key={k} className="flex justify-between font-body-md text-body-md text-on-surface">
              <span className="capitalize">{k.replace("_", " ")}</span>
              <span className="font-label-md">{v}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Admin;
