// Página de recuperación de contraseña / 找回密码页 (RF-05)

import { useState } from "react";
import { Link } from "react-router-dom";

import { solicitarRecuperacion } from "../api/autenticacion.js";
import Marca from "../componentes/Marca.jsx";

function RecuperarPassword() {
  const [email, setEmail] = useState("");
  const [enviado, setEnviado] = useState(false);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento) {
    evento.preventDefault();
    setEnviando(true);
    try {
      await solicitarRecuperacion(email);
    } catch {
      // No revelamos si el correo existe / 不泄露邮箱是否存在
    } finally {
      setEnviado(true);
      setEnviando(false);
    }
  }

  return (
    <div className="min-h-screen bg-hero-glow flex items-center justify-center p-margin-mobile">
      <div className="w-full max-w-md bg-surface-container-lowest rounded-3xl shadow-[0_18px_50px_-20px_rgba(11,28,48,0.35)] border border-outline-variant/30 p-xl animar-escala">
        <div className="flex justify-center mb-lg">
          <Marca />
        </div>

        {enviado ? (
          <div className="text-center">
            <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-md">
              <span className="material-symbols-outlined text-primary" style={{ fontSize: "48px" }}>mark_email_read</span>
            </div>
            <h1 className="font-headline-md text-headline-md text-on-surface mb-xs">
              Revisa tu correo
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant mb-lg">
              Si el correo existe, enviamos un enlace para restablecer tu
              contraseña (válido 15 minutos).
            </p>
            <Link
              to="/login"
              className="inline-flex items-center gap-xs text-primary hover:underline font-label-md text-label-md font-semibold"
            >
              <span className="material-symbols-outlined text-sm">arrow_back</span>
              Volver a iniciar sesión
            </Link>
          </div>
        ) : (
          <form className="flex flex-col gap-md" onSubmit={enviar}>
            <div className="text-center mb-sm">
              <div className="w-16 h-16 bg-tertiary/10 rounded-full flex items-center justify-center mx-auto mb-md">
                <span className="material-symbols-outlined text-tertiary" style={{ fontSize: "32px" }}>lock_reset</span>
              </div>
              <h1 className="font-headline-md text-headline-md text-on-surface">
                Recuperar contraseña
              </h1>
              <p className="font-body-md text-body-md text-on-surface-variant">
                Ingresa tu correo y te enviaremos un enlace.
              </p>
            </div>
            <div className="flex flex-col gap-xs">
              <label
                className="font-label-md text-label-md text-on-surface font-semibold"
                htmlFor="email"
              >
                Correo electrónico
              </label>
              <div className="relative">
                <span className="material-symbols-outlined absolute inset-y-0 left-0 pl-sm flex items-center text-outline-variant pointer-events-none">mail</span>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="ejemplo@correo.com"
                  className="w-full pl-xl pr-sm py-sm bg-surface-container-lowest border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all placeholder:text-outline-variant/60"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={enviando}
              className="w-full py-sm rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 hover:scale-[1.01] transition-all disabled:opacity-60 disabled:hover:scale-100 flex items-center justify-center gap-xs"
            >
              <span className="material-symbols-outlined text-sm">send</span>
              {enviando ? "Enviando…" : "Enviar enlace"}
            </button>
            <Link
              to="/login"
              className="text-center text-tertiary hover:underline font-label-sm text-label-sm"
            >
              Volver
            </Link>
          </form>
        )}
      </div>
    </div>
  );
}

export default RecuperarPassword;
