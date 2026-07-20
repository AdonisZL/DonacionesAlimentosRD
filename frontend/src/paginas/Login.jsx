// Página de inicio de sesión / 登录页 (RF-04) — estilo ImpactDR, solo español

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { iniciarSesion } from "../api/autenticacion.js";
import { useSesion } from "../context/ContextoSesion.jsx";
import Marca from "../componentes/Marca.jsx";
import imagenLogin from "../../fotos/01.png";

function Login() {
  const [email, setEmail] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [verClave, setVerClave] = useState(false);
  const [error, setError] = useState(null);
  const [enviando, setEnviando] = useState(false);
  const { guardarSesion } = useSesion();
  const navegar = useNavigate();

  async function enviar(evento) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      const datos = await iniciarSesion(email, contrasena);
      guardarSesion(datos);
      navegar("/");
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(
        typeof detalle === "string" ? detalle : "No se pudo iniciar sesión.",
      );
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="flex w-full min-h-screen">
      {/* Lado izquierdo: imagen inspiradora */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden items-end p-2xl">
        <div
          className="absolute inset-0 bg-cover bg-center scale-105"
          style={{ backgroundImage: `url(${imagenLogin})` }}
        ></div>
        <div className="absolute inset-0 bg-gradient-to-t from-primary/90 via-on-surface/55 to-on-surface/20"></div>

        {/* Tarjeta glass flotante */}
        <div className="absolute top-xl right-xl glass-card px-md py-sm rounded-2xl shadow-xl flex items-center gap-sm animar-flotar">
          <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
            eco
          </span>
          <div>
            <p className="font-headline-md text-headline-md font-bold text-on-surface leading-none">FEFO</p>
            <p className="font-label-sm text-label-sm text-on-surface-variant">Cero desperdicio</p>
          </div>
        </div>

        <div className="relative z-10 max-w-lg mb-xl animar-aparecer">
          <div className="mb-lg">
            <Marca claro />
          </div>
          <div className="inline-flex items-center gap-sm bg-white/15 text-surface-bright px-md py-1 rounded-full border border-white/25 mb-md">
            <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>verified</span>
            <span className="font-label-sm text-label-sm uppercase tracking-wider">Compromiso dominicano</span>
          </div>
          <h1 className="font-display-lg text-display-lg text-surface-bright mb-md leading-tight">
            Rescatamos alimentos, alimentamos comunidades.
          </h1>
          <p className="font-body-lg text-body-lg text-surface-container-low opacity-90">
            Plataforma para donar, gestionar y distribuir excedentes de alimentos con
            trazabilidad en la República Dominicana.
          </p>
        </div>
      </div>

      {/* Lado derecho: formulario */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-margin-mobile md:p-margin-desktop bg-hero-glow">
        <div className="w-full max-w-md animar-aparecer">
          <div className="flex items-center justify-between mb-lg">
            <Link
              to="/"
              className="inline-flex items-center gap-xs text-on-surface-variant hover:text-primary font-label-md text-label-md transition-colors"
            >
              <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>arrow_back</span>
              Inicio
            </Link>
            <div className="lg:hidden">
              <Marca />
            </div>
          </div>

          <div className="bg-surface-container-lowest p-lg md:p-xl rounded-3xl shadow-[0_18px_50px_-20px_rgba(11,28,48,0.35)] border border-outline-variant/30">
            <div className="mb-xl">
              <h2 className="font-headline-lg text-headline-lg text-on-tertiary-container mb-xs">
                Bienvenido de nuevo
              </h2>
              <p className="font-body-md text-body-md text-on-surface-variant">
                Inicia sesión para continuar.
              </p>
            </div>
            <form className="space-y-lg" onSubmit={enviar}>
              {error && (
                <div className="flex items-center gap-sm rounded-lg bg-error/10 border border-error/20 px-sm py-sm text-error">
                  <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>
                    error
                  </span>
                  <span className="font-body-md text-sm">{error}</span>
                </div>
              )}
              <div className="space-y-xs">
                <label className="block font-label-md text-label-md text-on-surface font-semibold" htmlFor="email">
                  Correo electrónico
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute inset-y-0 left-0 pl-sm flex items-center text-outline-variant pointer-events-none">
                    mail
                  </span>
                  <input
                    id="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="ejemplo@correo.com"
                    className="block w-full pl-xl pr-sm py-sm font-body-md text-body-md text-on-surface bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary/30 focus:border-primary focus:outline-none transition-all placeholder:text-outline-variant/60"
                  />
                </div>
              </div>
              <div className="space-y-xs">
                <div className="flex justify-between items-center">
                  <label className="block font-label-md text-label-md text-on-surface font-semibold" htmlFor="password">
                    Contraseña
                  </label>
                  <Link
                    to="/recuperar-password"
                    className="font-label-sm text-label-sm text-tertiary hover:text-on-tertiary-container transition-colors"
                  >
                    ¿Olvidaste tu contraseña?
                  </Link>
                </div>
                <div className="relative">
                  <span className="material-symbols-outlined absolute inset-y-0 left-0 pl-sm flex items-center text-outline-variant pointer-events-none">
                    lock
                  </span>
                  <input
                    id="password"
                    type={verClave ? "text" : "password"}
                    required
                    value={contrasena}
                    onChange={(e) => setContrasena(e.target.value)}
                    placeholder="••••••••"
                    className="block w-full pl-xl pr-xl py-sm font-body-md text-body-md text-on-surface bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary/30 focus:border-primary focus:outline-none transition-all placeholder:text-outline-variant/60"
                  />
                  <button
                    type="button"
                    onClick={() => setVerClave((v) => !v)}
                    className="material-symbols-outlined absolute inset-y-0 right-0 pr-sm flex items-center text-outline-variant hover:text-primary transition-colors"
                    aria-label={verClave ? "Ocultar contraseña" : "Mostrar contraseña"}
                  >
                    {verClave ? "visibility_off" : "visibility"}
                  </button>
                </div>
              </div>
              <div className="pt-sm space-y-md">
                <button
                  type="submit"
                  disabled={enviando}
                  className="w-full flex justify-center py-sm px-md rounded-lg shadow-sm font-label-md text-label-md font-semibold text-on-primary bg-primary hover:shadow-lg hover:shadow-primary/25 hover:scale-[1.01] transition-all disabled:opacity-60 disabled:hover:scale-100"
                >
                  {enviando ? "Entrando…" : "Iniciar sesión"}
                </button>
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-outline-variant/50"></div>
                  </div>
                  <div className="relative flex justify-center">
                    <span className="px-sm bg-surface-container-lowest font-body-md text-body-md text-on-surface-variant">
                      O
                    </span>
                  </div>
                </div>
                <Link
                  to="/registro"
                  className="w-full flex justify-center py-sm px-md border border-tertiary/60 rounded-lg font-label-md text-label-md font-semibold text-tertiary hover:bg-tertiary/5 hover:border-tertiary transition-all"
                >
                  Crear cuenta
                </Link>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
