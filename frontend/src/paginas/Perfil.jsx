// Página de perfil / 个人资料页 (RF-07 editar, RF-08 desactivar)

import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { actualizarPerfil, desactivarCuenta } from "../api/autenticacion.js";
import { useSesion } from "../context/ContextoSesion.jsx";
import EncabezadoApp from "../componentes/EncabezadoApp.jsx";
import PieDePagina from "../componentes/PieDePagina.jsx";

function Perfil() {
  const { usuario, cerrarSesion, actualizarUsuario } = useSesion();
  const navegar = useNavigate();
  const [form, setForm] = useState({
    nombre: usuario?.nombre || "",
    apellido: usuario?.apellido || "",
    telefono: usuario?.telefono || "",
  });
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);
  const [guardando, setGuardando] = useState(false);

  if (!usuario) return <Navigate to="/login" replace />;

  function cambiar(campo, valor) {
    setForm((anterior) => ({ ...anterior, [campo]: valor }));
  }

  async function guardar(evento) {
    evento.preventDefault();
    setError(null);
    setMensaje(null);
    setGuardando(true);
    try {
      const actualizado = await actualizarPerfil(form);
      actualizarUsuario(actualizado);
      setMensaje("Datos actualizados correctamente.");
    } catch {
      setError("No se pudo actualizar el perfil.");
    } finally {
      setGuardando(false);
    }
  }

  async function desactivar() {
    const ok = window.confirm(
      "¿Seguro que deseas desactivar tu cuenta? No podrás iniciar sesión, pero tu historial se conserva.",
    );
    if (!ok) return;
    try {
      await desactivarCuenta();
      cerrarSesion();
      navegar("/login");
    } catch {
      setError("No se pudo desactivar la cuenta.");
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <EncabezadoApp />

      <main className="flex-1 w-full max-w-3xl mx-auto px-margin-mobile md:px-margin-desktop py-2xl">
        {/* Cabecera con avatar */}
        <div className="flex items-center gap-lg mb-xl">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-primary-container text-on-primary flex items-center justify-center font-display-lg shadow-lg shadow-primary/20 ring-4 ring-primary/10">
            {(usuario.nombre || "?").charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface page-header">
              Mi perfil
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant">
              {usuario.email}
            </p>
          </div>
        </div>

        {/* Datos editables */}
        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl shadow-sm hover-lift-sm">
          <div className="flex items-center gap-sm mb-lg">
            <span className="material-symbols-outlined text-primary">edit</span>
            <h2 className="font-headline-md text-headline-md text-on-surface">Información personal</h2>
          </div>
          <form className="flex flex-col gap-md" onSubmit={guardar}>
            {mensaje && (
              <div className="flex items-center gap-sm rounded-lg bg-primary/10 border border-primary/20 px-sm py-sm text-primary">
                <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>
                  check_circle
                </span>
                <span className="font-body-md text-sm">{mensaje}</span>
              </div>
            )}
            {error && <p className="font-body-md text-sm text-error flex items-center gap-xs"><span className="material-symbols-outlined text-sm">error</span>{error}</p>}

            <CampoPerfil id="nombre" etiqueta="Nombre" icono="person" valor={form.nombre} onChange={(v) => cambiar("nombre", v)} />
            <CampoPerfil id="apellido" etiqueta="Apellido" icono="badge" valor={form.apellido} onChange={(v) => cambiar("apellido", v)} />
            <CampoPerfil id="telefono" etiqueta="Teléfono" icono="call" valor={form.telefono} onChange={(v) => cambiar("telefono", v)} />

            <div className="flex flex-col gap-xs bg-surface-container-low rounded-xl p-md border border-outline-variant/20">
              <span className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-xs">
                <span className="material-symbols-outlined text-sm">mail</span>
                Correo (no editable)
              </span>
              <span className="font-body-md text-body-md text-on-surface font-semibold">
                {usuario.email}
              </span>
            </div>

            <div className="flex justify-end pt-sm">
              <button
                type="submit"
                disabled={guardando}
                className="py-sm px-lg rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 hover:scale-[1.02] transition-all disabled:opacity-60 disabled:hover:scale-100 flex items-center gap-xs"
              >
                <span className="material-symbols-outlined text-sm">save</span>
                {guardando ? "Guardando…" : "Guardar cambios"}
              </button>
            </div>
          </form>
        </section>

        {/* Desactivar cuenta */}
        <section className="mt-xl bg-surface-container-lowest rounded-2xl border border-error/20 p-xl">
          <div className="flex items-center gap-sm mb-xs">
            <span className="material-symbols-outlined text-error">warning</span>
            <h2 className="font-headline-md text-headline-md text-on-surface">
              Zona de riesgo
            </h2>
          </div>
          <p className="font-body-md text-body-md text-on-surface-variant mb-md">
            Tu cuenta quedará inactiva y no podrás iniciar sesión. Tu historial se
            conserva conforme a la ley.
          </p>
          <button
            type="button"
            onClick={desactivar}
            className="py-sm px-lg rounded-lg border-2 border-error/40 text-error font-label-md text-label-md font-semibold hover:bg-error/5 hover:border-error transition-all"
          >
            Desactivar mi cuenta
          </button>
        </section>
      </main>
      <PieDePagina />
    </div>
  );
}

function CampoPerfil({ id, etiqueta, icono, valor, onChange }) {
  return (
    <div className="flex flex-col gap-xs">
      <label className="font-label-md text-label-md text-on-surface flex items-center gap-xs" htmlFor={id}>
        <span className="material-symbols-outlined text-on-surface-variant text-sm">{icono}</span>
        {etiqueta}
      </label>
      <input
        id={id}
        value={valor}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-sm py-sm bg-surface border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all placeholder:text-outline-variant/60"
      />
    </div>
  );
}

export default Perfil;
