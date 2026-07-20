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
    <div className="min-h-screen bg-surface flex items-center justify-center p-margin-mobile">
      <div className="w-full max-w-md glass-panel rounded-xl p-xl text-center">
        <div className="flex justify-center mb-lg">
          <Marca />
        </div>

        {estado === "cargando" && (
          <p className="font-body-md text-body-md text-on-surface-variant">
            Verificando tu correo…
          </p>
        )}

        {estado === "exito" && (
          <>
            <span
              className="material-symbols-outlined text-primary"
              style={{ fontSize: "48px" }}
            >
              check_circle
            </span>
            <h1 className="font-headline-md text-headline-md text-on-surface mt-sm mb-xs">
              ¡Correo verificado!
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant mb-lg">
              Tu cuenta ya está confirmada.
            </p>
            <Link
              to="/login"
              className="inline-block py-sm px-lg rounded-lg bg-primary-container text-on-primary font-label-md text-label-md hover:bg-primary transition-colors"
            >
              Iniciar sesión
            </Link>
          </>
        )}

        {estado === "error" && (
          <>
            <span
              className="material-symbols-outlined text-error"
              style={{ fontSize: "48px" }}
            >
              error
            </span>
            <h1 className="font-headline-md text-headline-md text-on-surface mt-sm mb-xs">
              Enlace inválido o expirado
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant mb-lg">
              No se pudo verificar el correo. Solicita un nuevo enlace.
            </p>
            <Link
              to="/login"
              className="inline-block py-sm px-lg rounded-lg border border-tertiary text-tertiary font-label-md text-label-md hover:bg-surface-container-low transition-colors"
            >
              Volver a iniciar sesión
            </Link>
          </>
        )}
      </div>
    </div>
  );
}

export default VerificarCorreo;
