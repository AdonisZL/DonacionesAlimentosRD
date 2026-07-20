// Página de restablecimiento de contraseña / 重置密码页 (RF-05)

import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { restablecerContrasena } from "../api/autenticacion.js";
import Marca from "../componentes/Marca.jsx";

function RestablecerPassword() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const [contrasena, setContrasena] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [error, setError] = useState(null);
  const [enviando, setEnviando] = useState(false);
  const navegar = useNavigate();

  async function enviar(evento) {
    evento.preventDefault();
    setError(null);
    if (contrasena !== confirmar) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    setEnviando(true);
    try {
      await restablecerContrasena(token, contrasena);
      navegar("/login");
    } catch (err) {
      const detalle = err.response?.data?.detail;
      const mensaje = Array.isArray(detalle) ? detalle[0]?.msg : detalle;
      setError(mensaje || "No se pudo restablecer la contraseña.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center p-margin-mobile">
      <div className="w-full max-w-md glass-panel rounded-xl p-xl">
        <div className="flex justify-center mb-lg">
          <Marca />
        </div>
        <form className="flex flex-col gap-md" onSubmit={enviar}>
          <h1 className="font-headline-md text-headline-md text-on-surface">
            Nueva contraseña
          </h1>
          {error && <p className="font-body-md text-sm text-error">{error}</p>}
          {!token && (
            <p className="font-body-md text-sm text-error">
              Falta el token del enlace.
            </p>
          )}
          <div className="flex flex-col gap-xs">
            <label
              className="font-label-md text-label-md text-on-surface"
              htmlFor="c1"
            >
              Contraseña
            </label>
            <input
              id="c1"
              type="password"
              required
              value={contrasena}
              onChange={(e) => setContrasena(e.target.value)}
              className="w-full px-sm py-sm bg-surface-container-lowest border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
            />
            <small className="font-label-sm text-label-sm text-on-surface-variant">
              Mín. 10 caracteres, con mayúscula, número y símbolo.
            </small>
          </div>
          <div className="flex flex-col gap-xs">
            <label
              className="font-label-md text-label-md text-on-surface"
              htmlFor="c2"
            >
              Confirmar contraseña
            </label>
            <input
              id="c2"
              type="password"
              required
              value={confirmar}
              onChange={(e) => setConfirmar(e.target.value)}
              className="w-full px-sm py-sm bg-surface-container-lowest border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
            />
          </div>
          <button
            type="submit"
            disabled={enviando || !token}
            className="w-full py-sm rounded-lg bg-primary-container text-on-primary font-label-md text-label-md hover:bg-primary transition-colors disabled:opacity-60"
          >
            {enviando ? "Guardando…" : "Restablecer contraseña"}
          </button>
          <Link
            to="/login"
            className="text-center text-tertiary hover:underline font-label-sm text-label-sm"
          >
            Volver a iniciar sesión
          </Link>
        </form>
      </div>
    </div>
  );
}

export default RestablecerPassword;
