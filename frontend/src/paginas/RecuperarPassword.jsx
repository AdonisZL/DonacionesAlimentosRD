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
    <div className="min-h-screen bg-surface flex items-center justify-center p-margin-mobile">
      <div className="w-full max-w-md glass-panel rounded-xl p-xl">
        <div className="flex justify-center mb-lg">
          <Marca />
        </div>

        {enviado ? (
          <div className="text-center">
            <span
              className="material-symbols-outlined text-primary"
              style={{ fontSize: "48px" }}
            >
              mark_email_read
            </span>
            <h1 className="font-headline-md text-headline-md text-on-surface mt-sm mb-xs">
              Revisa tu correo
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant mb-lg">
              Si el correo existe, enviamos un enlace para restablecer tu
              contraseña (válido 15 minutos).
            </p>
            <Link
              to="/login"
              className="text-primary hover:underline font-label-md text-label-md"
            >
              Volver a iniciar sesión
            </Link>
          </div>
        ) : (
          <form className="flex flex-col gap-md" onSubmit={enviar}>
            <h1 className="font-headline-md text-headline-md text-on-surface">
              Recuperar contraseña
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Ingresa tu correo y te enviaremos un enlace.
            </p>
            <div className="flex flex-col gap-xs">
              <label
                className="font-label-md text-label-md text-on-surface"
                htmlFor="email"
              >
                Correo electrónico
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-sm py-sm bg-surface-container-lowest border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>
            <button
              type="submit"
              disabled={enviando}
              className="w-full py-sm rounded-lg bg-primary-container text-on-primary font-label-md text-label-md hover:bg-primary transition-colors disabled:opacity-60"
            >
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
