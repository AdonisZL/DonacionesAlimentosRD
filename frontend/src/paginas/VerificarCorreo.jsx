// Página de verificación de correo / 邮箱验证页 (RF-06)

import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { verificarCorreo } from "../api/autenticacion.js";
import Marca from "../componentes/Marca.jsx";

function VerificarCorreo() {
  const [params] = useSearchParams();
  const [estado, setEstado] = useState("cargando"); // cargando | exito | error

  useEffect(() => {
    const token = params.get("token");
    if (!token) {
      setEstado("error");
      return;
    }
    verificarCorreo(token)
      .then(() => setEstado("exito"))
      .catch(() => setEstado("error"));
  }, [params]);

  return (
    <div className="min-h-screen bg-hero-glow flex items-center justify-center p-margin-mobile">
      <div className="w-full max-w-md bg-surface-container-lowest rounded-3xl shadow-[0_18px_50px_-20px_rgba(11,28,48,0.35)] border border-outline-variant/30 p-xl text-center animar-escala">
        <div className="flex justify-center mb-lg">
          <Marca />
        </div>

        {estado === "cargando" && (
          <div className="space-y-md">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
              <span className="material-symbols-outlined text-primary animar-pulso" style={{ fontSize: "32px" }}>hourglass_top</span>
            </div>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Verificando tu correo…
            </p>
          </div>
        )}

        {estado === "exito" && (
          <>
            <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-md">
              <span className="material-symbols-outlined text-primary" style={{ fontSize: "48px" }}>check_circle</span>
            </div>
            <h1 className="font-headline-md text-headline-md text-on-surface mb-xs">
              ¡Correo verificado!
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant mb-lg">
              Tu cuenta ya está confirmada.
            </p>
            <Link
              to="/login"
              className="inline-flex items-center gap-xs py-sm px-lg rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 transition-all"
            >
              <span className="material-symbols-outlined text-sm">login</span>
              Iniciar sesión
            </Link>
          </>
        )}

        {estado === "error" && (
          <>
            <div className="w-20 h-20 bg-error/10 rounded-full flex items-center justify-center mx-auto mb-md">
              <span className="material-symbols-outlined text-error" style={{ fontSize: "48px" }}>error</span>
            </div>
            <h1 className="font-headline-md text-headline-md text-on-surface mb-xs">
              Enlace inválido o expirado
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant mb-lg">
              No se pudo verificar el correo. Solicita un nuevo enlace.
            </p>
            <Link
              to="/login"
              className="inline-flex items-center gap-xs py-sm px-lg rounded-lg border-2 border-tertiary/60 text-tertiary font-label-md text-label-md font-semibold hover:bg-tertiary/5 transition-all"
            >
              <span className="material-symbols-outlined text-sm">arrow_back</span>
              Volver a iniciar sesión
            </Link>
          </>
        )}
      </div>
    </div>
  );
}

export default VerificarCorreo;
