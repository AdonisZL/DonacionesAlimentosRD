// Página de consulta RNC/Cédula / RNC/身份证查询页面
// Permite buscar datos fiscales de la DGII vía MegaPlus API y autocompletar registro.

import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { consultarRNC, buscarPorNombre } from "../api/rnc.js";
import { useSesion } from "../context/ContextoSesion.jsx";
import EncabezadoApp from "../componentes/EncabezadoApp.jsx";
import PieDePagina from "../componentes/PieDePagina.jsx";

const ETIQUETA_ESTADO = {
  ACTIVO: "bg-green/10 text-green",
  SUSPENDIDO: "bg-amber/10 text-amber",
  "DADO DE BAJA": "bg-red/10 text-red",
  NORMAL: "bg-green/10 text-green",
};

function ConsultarRNC() {
  const { usuario } = useSesion();
  const navegar = useNavigate();

  const [modo, setModo] = useState("rnc"); // rnc | nombre
  const [rnc, setRnc] = useState("");
  const [nombre, setNombre] = useState("");
  const [resultado, setResultado] = useState(null);
  const [resultados, setResultados] = useState([]);
  const [error, setError] = useState(null);
  const [consultando, setConsultando] = useState(false);

  if (!usuario) return <Navigate to="/login" replace />;

  async function consultar(e) {
    e.preventDefault();
    setError(null);
    setResultado(null);
    setResultados([]);
    setConsultando(true);

    try {
      if (modo === "rnc") {
        if (!rnc.trim()) {
          setError("Ingresa un RNC o Cédula.");
          setConsultando(false);
          return;
        }
        const data = await consultarRNC(rnc.trim());
        if (data && !data.error) {
          setResultado(data);
          setError(null);
        } else {
          setResultado(null);
          setError(data?.mensaje || "RNC no encontrado en la DGII.");
        }
      } else {
        if (nombre.trim().length < 3) {
          setError("El nombre debe tener al menos 3 caracteres.");
          setConsultando(false);
          return;
        }
        const data = await buscarPorNombre(nombre.trim());
        if (data && !data.error) {
          setResultados(data.resultados || []);
          setError(null);
        } else {
          setResultados([]);
          setError(data?.mensaje || "Sin resultados.");
        }
      }
    } catch (err) {
      setResultado(null);
      setResultados([]);
      const detalle = err.response?.data?.detail;
      setError(detalle || "Error al consultar. Verifica el RNC/Cédula.");
    } finally {
      setConsultando(false);
    }
  }

  function irARegistroConDatos(datos) {
    navegar("/registro", {
      state: {
        rnc: datos.cedula_rnc?.replace(/-/g, "") || "",
        nombre_razon_social: datos.nombre_razon_social || "",
        nombre_comercial: datos.nombre_comercial || "",
      },
    });
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <EncabezadoApp />

      <main className="flex-1 w-full max-w-3xl mx-auto px-margin-mobile md:px-margin-desktop py-2xl">
        {/* Cabecera */}
        <div className="flex items-center gap-lg mb-xl">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary to-primary-container text-on-primary flex items-center justify-center shadow-lg shadow-primary/20">
            <span className="material-symbols-outlined text-2xl">account_balance</span>
          </div>
          <div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface page-header">
              Consultar RNC / Cédula
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Datos fiscales DGII vía MegaPlus API
            </p>
          </div>
        </div>

        {/* Selector de modo */}
        <div className="flex gap-xs mb-lg bg-surface-container-low rounded-xl p-xs">
          <button
            onClick={() => { setModo("rnc"); setResultado(null); setResultados([]); setError(null); }}
            className={`flex-1 py-sm rounded-lg font-label-md text-label-md transition-all ${
              modo === "rnc"
                ? "bg-surface text-on-surface shadow-sm font-semibold"
                : "text-on-surface-variant hover:text-on-surface"
            }`}
          >
            <span className="material-symbols-outlined text-sm align-middle mr-xs">fingerprint</span>
            Por RNC / Cédula
          </button>
          <button
            onClick={() => { setModo("nombre"); setResultado(null); setResultados([]); setError(null); }}
            className={`flex-1 py-sm rounded-lg font-label-md text-label-md transition-all ${
              modo === "nombre"
                ? "bg-surface text-on-surface shadow-sm font-semibold"
                : "text-on-surface-variant hover:text-on-surface"
            }`}
          >
            <span className="material-symbols-outlined text-sm align-middle mr-xs">search</span>
            Por Nombre
          </button>
        </div>

        {/* Formulario de búsqueda */}
        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl shadow-sm mb-xl">
          <form onSubmit={consultar} className="flex flex-col sm:flex-row gap-sm">
            {modo === "rnc" ? (
              <input
                type="text"
                value={rnc}
                onChange={(e) => setRnc(e.target.value)}
                placeholder="Ej: 131996035"
                maxLength={11}
                className="flex-1 px-sm py-sm bg-surface border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
            ) : (
              <input
                type="text"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                placeholder="Nombre o razón social (mín. 3 caracteres)"
                maxLength={100}
                className="flex-1 px-sm py-sm bg-surface border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
            )}
            <button
              type="submit"
              disabled={consultando}
              className="py-sm px-lg rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 hover:scale-[1.02] transition-all disabled:opacity-60 flex items-center justify-center gap-xs"
            >
              <span className="material-symbols-outlined text-sm">search</span>
              {consultando ? "Consultando…" : "Buscar"}
            </button>
          </form>
        </section>

        {/* Mensajes */}
        {error && (
          <div className="flex items-center gap-sm rounded-lg bg-error-container px-sm py-sm text-on-error-container mb-md">
            <span className="material-symbols-outlined text-sm">error</span>
            <span className="font-body-md text-sm">{error}</span>
          </div>
        )}

        {/* Resultado individual (RNC) */}
        {resultado && !resultado.error && (
          <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl shadow-sm mb-xl animar-aparecer">
            <div className="flex items-center justify-between mb-md">
              <h2 className="font-headline-md text-headline-md text-on-surface">
                {resultado.nombre_razon_social || "Contribuyente"}
              </h2>
              <span
                className={`font-label-sm text-label-sm px-sm py-xs rounded-full ${
                  ETIQUETA_ESTADO[resultado.estado] || "bg-gray/10 text-gray"
                }`}
              >
                {resultado.estado || "N/D"}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-md">
              <FichaDato etiqueta="RNC / Cédula" valor={resultado.cedula_rnc || "N/D"} icono="fingerprint" />
              <FichaDato etiqueta="Nombre Comercial" valor={resultado.nombre_comercial || "—"} icono="store" />
              <FichaDato etiqueta="Régimen de Pagos" valor={resultado.regimen_de_pagos || "N/D"} icono="payments" />
              <FichaDato etiqueta="Facturador Electrónico" valor={resultado.facturador_electronico || "N/D"} icono="receipt" />
              <FichaDato etiqueta="Administración Local" valor={resultado.administracion_local || "N/D"} icono="location_city" />
              <FichaDato etiqueta="Categoría" valor={resultado.categoria || "—"} icono="category" />
            </div>

            {resultado.actividad_economica && (
              <div className="mt-md p-md rounded-lg bg-surface-container-low border border-outline-variant/20">
                <span className="font-label-sm text-label-sm text-on-surface-variant">Actividad Económica</span>
                <p className="font-body-md text-sm text-on-surface mt-xs">{resultado.actividad_economica}</p>
              </div>
            )}

            <div className="mt-lg flex justify-end">
              <button
                onClick={() => irARegistroConDatos(resultado)}
                className="py-sm px-lg rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 hover:scale-[1.02] transition-all flex items-center gap-xs"
              >
                <span className="material-symbols-outlined text-sm">person_add</span>
                Usar para registro
              </button>
            </div>
          </section>
        )}

        {/* Resultados múltiples (búsqueda por nombre) */}
        {resultados.length > 0 && (
          <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 overflow-hidden shadow-sm mb-xl animar-aparecer">
            <div className="px-xl py-md border-b border-outline-variant/20">
              <span className="font-label-md text-label-md text-on-surface font-semibold">
                {resultados.length} resultado(s)
              </span>
            </div>
            <div className="divide-y divide-outline-variant/10">
              {resultados.map((r, i) => (
                <div
                  key={r.cedula_rnc || i}
                  className="flex flex-col sm:flex-row sm:items-center justify-between gap-sm px-xl py-lg hover:bg-surface-container-low transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-label-md text-label-md text-on-surface font-semibold truncate">
                      {r.nombre_razon_social || "Sin nombre"}
                    </p>
                    <div className="flex items-center gap-sm mt-xs">
                      <span className="font-label-sm text-on-surface-variant">{r.cedula_rnc}</span>
                      <span
                        className={`font-label-xs px-xs py-0.5 rounded-full ${
                          ETIQUETA_ESTADO[r.estado] || "bg-gray/10 text-gray"
                        }`}
                      >
                        {r.estado}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => irARegistroConDatos(r)}
                    className="shrink-0 py-xs px-md rounded-lg bg-primary/10 text-primary font-label-sm hover:bg-primary hover:text-on-primary transition-all"
                  >
                    Usar
                  </button>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Sin resultados */}
        {modo === "nombre" && !consultando && resultados.length === 0 && !error && nombre.length >= 3 && (
          <div className="flex flex-col items-center gap-sm py-xl text-center">
            <span className="material-symbols-outlined text-4xl text-on-surface-variant/30">search_off</span>
            <p className="font-body-md text-on-surface-variant">Sin resultados para "{nombre}"</p>
          </div>
        )}
      </main>
      <PieDePagina />
    </div>
  );
}

// Componente auxiliar para mostrar un dato / 数据展示辅助组件
function FichaDato({ etiqueta, valor, icono }) {
  return (
    <div className="flex items-start gap-sm p-sm rounded-lg bg-surface-container-low border border-outline-variant/20">
      <span className="material-symbols-outlined text-on-surface-variant text-lg mt-0.5">{icono}</span>
      <div className="min-w-0">
        <span className="font-label-xs text-on-surface-variant/70 block">{etiqueta}</span>
        <span className="font-body-md text-sm text-on-surface break-words">{valor}</span>
      </div>
    </div>
  );
}

export default ConsultarRNC;
