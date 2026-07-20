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
    <div className="min-h-screen bg-hero-glow flex items-center justify-center p-margin-mobile">
      <div className="w-full max-w-md bg-surface-container-lowest rounded-3xl shadow-[0_18px_50px_-20px_rgba(11,28,48,0.35)] border border-outline-variant/30 p-xl animar-escala">
        <div className="flex justify-center mb-lg">
          <Marca />
        </div>
        <form className="flex flex-col gap-md" onSubmit={enviar}>
          <div className="text-center mb-sm">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-md">
              <span className="material-symbols-outlined text-primary" style={{ fontSize: "32px" }}>lock</span>
            </div>
            <h1 className="font-headline-md text-headline-md text-on-surface">
              Nueva contraseña
            </h1>
          </div>
          {error && (
            <div className="flex items-center gap-sm rounded-lg bg-error/10 border border-error/20 px-sm py-sm text-error">
              <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>error</span>
              <span className="font-body-md text-sm">{error}</span>
            </div>
          )}
          {!token && (
            <div className="flex items-center gap-sm rounded-lg bg-error/10 border border-error/20 px-sm py-sm text-error">
              <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>link_off</span>
              <span className="font-body-md text-sm">Falta el token del enlace.</span>
            </div>
          )}
          <div className="flex flex-col gap-xs">
            <label className="font-label-md text-label-md text-on-surface font-semibold" htmlFor="c1">
              Contraseña
            </label>
            <div className="relative">
              <span className="material-symbols-outlined absolute inset-y-0 left-0 pl-sm flex items-center text-outline-variant pointer-events-none">lock</span>
              <input
                id="c1"
                type="password"
                required
                value={contrasena}
                onChange={(e) => setContrasena(e.target.value)}
                className="w-full pl-xl pr-sm py-sm bg-surface-container-lowest border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
            </div>
            <small className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-xs">
              <span className="material-symbols-outlined text-sm">info</span>
              Mín. 10 caracteres, con mayúscula, número y símbolo.
            </small>
          </div>
          <div className="flex flex-col gap-xs">
            <label className="font-label-md text-label-md text-on-surface font-semibold" htmlFor="c2">
              Confirmar contraseña
            </label>
            <div className="relative">
              <span className="material-symbols-outlined absolute inset-y-0 left-0 pl-sm flex items-center text-outline-variant pointer-events-none">lock</span>
              <input
                id="c2"
                type="password"
                required
                value={confirmar}
                onChange={(e) => setConfirmar(e.target.value)}
                className="w-full pl-xl pr-sm py-sm bg-surface-container-lowest border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={enviando || !token}
            className="w-full py-sm rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 hover:scale-[1.01] transition-all disabled:opacity-60 disabled:hover:scale-100 flex items-center justify-center gap-xs"
          >
            <span className="material-symbols-outlined text-sm">save</span>
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
