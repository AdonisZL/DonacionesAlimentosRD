// Página de administración / 管理页 (OE5 — RF-28/29/32)

import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import {
  cambiarEstadoUsuario,
  obtenerAuditoria,
  obtenerPanelAdmin,
  obtenerUsuariosAdmin,
} from "../api/admin.js";
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
      const [p, u, a] = await Promise.all([
        obtenerPanelAdmin(),
        obtenerUsuariosAdmin(),
        obtenerAuditoria(),
      ]);
      setPanel(p);
      setUsuarios(u);
      setAuditoria(a);
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

  if (esAdmin === false) {
    return (
      <div className="min-h-screen bg-background flex flex-col">
        <EncabezadoApp />
        <main className="flex-1 max-w-3xl w-full mx-auto px-margin-mobile md:px-margin-desktop py-2xl">
          <div className="bg-surface-container-lowest rounded-2xl border border-error/30 p-xl text-center">
            <span className="material-symbols-outlined text-error" style={{ fontSize: "40px" }}>
              lock
            </span>
            <h1 className="font-headline-md text-headline-md text-on-surface mt-sm">
              Acceso restringido
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Esta sección es solo para administradores.
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
        <h1 className="font-headline-lg text-headline-lg text-on-surface">
          Panel de administración
        </h1>

        {error && <p className="font-body-md text-sm text-error">{error}</p>}
        {mensaje && (
          <div className="flex items-center gap-sm rounded-lg bg-primary-container/20 px-sm py-sm text-on-primary-container">
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
      </main>
      <PieDePagina />
    </div>
  );
}

function Metrica({ icono, valor, etiqueta, color }) {
  return (
    <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-lg flex items-center gap-md">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
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
