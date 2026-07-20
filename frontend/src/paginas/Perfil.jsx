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
        <h1 className="font-headline-lg text-headline-lg text-on-surface mb-lg">
          Mi perfil
        </h1>

        <section className="bg-surface-container-lowest rounded-xl border border-outline-variant/30 p-xl shadow-sm">
          <form className="flex flex-col gap-md" onSubmit={guardar}>
            {mensaje && (
              <div className="flex items-center gap-sm rounded-lg bg-primary-container/20 px-sm py-sm text-on-primary-container">
                <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>
                  check_circle
                </span>
                <span className="font-body-md text-sm">{mensaje}</span>
              </div>
            )}
            {error && <p className="font-body-md text-sm text-error">{error}</p>}

            <CampoPerfil id="nombre" etiqueta="Nombre" valor={form.nombre} onChange={(v) => cambiar("nombre", v)} />
            <CampoPerfil id="apellido" etiqueta="Apellido" valor={form.apellido} onChange={(v) => cambiar("apellido", v)} />
            <CampoPerfil id="telefono" etiqueta="Teléfono" valor={form.telefono} onChange={(v) => cambiar("telefono", v)} />

            <div className="flex flex-col gap-xs">
              <span className="font-label-sm text-label-sm text-on-surface-variant">
                Correo (no editable)
              </span>
              <span className="font-body-md text-body-md text-on-surface">
                {usuario.email}
              </span>
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={guardando}
                className="py-sm px-lg rounded-lg bg-primary-container text-on-primary font-label-md text-label-md hover:bg-primary transition-colors disabled:opacity-60"
              >
                {guardando ? "Guardando…" : "Guardar cambios"}
              </button>
            </div>
          </form>
        </section>

        <section className="mt-xl bg-surface-container-lowest rounded-xl border border-error/30 p-xl">
          <h2 className="font-headline-md text-headline-md text-on-surface mb-xs">
            Desactivar cuenta
          </h2>
          <p className="font-body-md text-body-md text-on-surface-variant mb-md">
            Tu cuenta quedará inactiva y no podrás iniciar sesión. Tu historial se
            conserva conforme a la ley.
          </p>
          <button
            type="button"
            onClick={desactivar}
            className="py-sm px-lg rounded-lg border border-error text-error font-label-md text-label-md hover:bg-error-container/30 transition-colors"
          >
            Desactivar mi cuenta
          </button>
        </section>
      </main>
      <PieDePagina />
    </div>
  );
}

function CampoPerfil({ id, etiqueta, valor, onChange }) {
  return (
    <div className="flex flex-col gap-xs">
      <label className="font-label-md text-label-md text-on-surface" htmlFor={id}>
        {etiqueta}
      </label>
      <input
        id={id}
        value={valor}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-sm py-sm bg-surface border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
      />
    </div>
  );
}

export default Perfil;
