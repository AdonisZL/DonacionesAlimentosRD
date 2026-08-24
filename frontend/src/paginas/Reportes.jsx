// Página de reportes / 报表页 (OE4 — RF-23 … RF-27)

import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import {
  descargarCertificadoPdf,
  descargarDgii606,
  exportarSheets,
  generarReporteFiscal,
  obtenerReporteAsignaciones,
  obtenerReporteDonaciones,
  obtenerReporteInventario,
} from "../api/reportes.js";
import { obtenerRoles } from "../api/autenticacion.js";
import { useSesion } from "../context/ContextoSesion.jsx";
import EncabezadoApp from "../componentes/EncabezadoApp.jsx";
import PieDePagina from "../componentes/PieDePagina.jsx";

// Dispara la descarga de un blob en el navegador / 在浏览器中下载 Blob
function descargarBlob(blob, nombreArchivo) {
  const url = window.URL.createObjectURL(blob);
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = nombreArchivo;
  document.body.appendChild(enlace);
  enlace.click();
  enlace.remove();
  window.URL.revokeObjectURL(url);
}

const PESTANAS = [
  { id: "donaciones", texto: "Donaciones", icono: "inventory" },
  { id: "inventario", texto: "Inventario (FEFO)", icono: "list_alt" },
  { id: "asignaciones", texto: "Asignaciones", icono: "assignment_turned_in" },
  { id: "fiscal", texto: "Fiscal DGII", icono: "receipt_long" },
];

const HOY = new Date();

function Reportes() {
  const { usuario } = useSesion();

  const [pestana, setPestana] = useState("donaciones");
  const [esBanco, setEsBanco] = useState(false);
  const [error, setError] = useState(null);
  const [mensaje, setMensaje] = useState(null);

  // Donaciones
  const [filtros, setFiltros] = useState({ desde: "", hasta: "", estado: "" });
  const [donaciones, setDonaciones] = useState(null);
  // Inventario / asignaciones
  const [inventario, setInventario] = useState([]);
  const [asignaciones, setAsignaciones] = useState(null);
  // Fiscal
  const [fiscal, setFiscal] = useState({
    anio: HOY.getFullYear(),
    mes: HOY.getMonth() + 1,
  });
  const [resultadoFiscal, setResultadoFiscal] = useState(null);
  const [descargandoDgii606, setDescargandoDgii606] = useState(false);
  // Exportación
  const [exportacion, setExportacion] = useState(null);
  // Certificado fiscal PDF por lote (RF-27)
  const [certificadoLote, setCertificadoLote] = useState(null);
  const [certificadoForm, setCertificadoForm] = useState({ rnc_donante: "", valor_total_rd: "" });
  const [generandoCertificado, setGenerandoCertificado] = useState(false);

  useEffect(() => {
    if (!usuario) return;
    obtenerRoles()
      .then((roles) => {
        const rol = roles.find((r) => r.id_rol === usuario.id_rol);
        setEsBanco(["banco_alimentos", "administrador"].includes(rol?.nombre));
      })
      .catch(() => {});
    cargarDonaciones();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!usuario) return <Navigate to="/login" replace />;

  async function cargarDonaciones() {
    setError(null);
    try {
      const params = {};
      if (filtros.desde) params.desde = filtros.desde;
      if (filtros.hasta) params.hasta = filtros.hasta;
      if (filtros.estado) params.estado = filtros.estado;
      setDonaciones(await obtenerReporteDonaciones(params));
    } catch {
      setError("No se pudo cargar el reporte de donaciones.");
    }
  }

  async function cargarInventario() {
    setError(null);
    try {
      setInventario(await obtenerReporteInventario());
    } catch {
      setError("No se pudo cargar el inventario.");
    }
  }

  async function cargarAsignaciones() {
    setError(null);
    try {
      setAsignaciones(await obtenerReporteAsignaciones());
    } catch {
      setError("No se pudo cargar las asignaciones.");
    }
  }

  function cambiarPestana(id) {
    setPestana(id);
    setMensaje(null);
    setExportacion(null);
    if (id === "inventario" && inventario.length === 0) cargarInventario();
    if (id === "asignaciones" && asignaciones === null) cargarAsignaciones();
  }

  async function exportar(tipo) {
    setError(null);
    setMensaje(null);
    try {
      const res = await exportarSheets(
        tipo,
        filtros.desde || null,
        filtros.hasta || null,
      );
      setExportacion(res);
      setMensaje(`Exportado (simulado): ${res.filas_exportadas} fila(s).`);
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo exportar.");
    }
  }

  async function generarFiscal(evento) {
    evento.preventDefault();
    setError(null);
    setMensaje(null);
    try {
      const res = await generarReporteFiscal(
        Number(fiscal.anio),
        Number(fiscal.mes),
      );
      setResultadoFiscal(res);
      setMensaje("Reporte fiscal generado (inmutable).");
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo generar el reporte fiscal.");
    }
  }

  // RF-16/RF-27: exporta el anexo fiscal DGII 606 del mes seleccionado.
  async function exportarDgii606() {
    setError(null);
    setMensaje(null);
    setDescargandoDgii606(true);
    try {
      const blob = await descargarDgii606(Number(fiscal.anio), Number(fiscal.mes));
      descargarBlob(blob, `DONACIONES_${fiscal.anio}_${String(fiscal.mes).padStart(2, "0")}.txt`);
      setMensaje("Archivo DGII 606 descargado.");
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo exportar el DGII 606.");
    } finally {
      setDescargandoDgii606(false);
    }
  }

  function abrirModalCertificado(idLote) {
    setError(null);
    setMensaje(null);
    setCertificadoForm({ rnc_donante: "", valor_total_rd: "" });
    setCertificadoLote(idLote);
  }

  // RF-27: certificación fiscal PDF inmutable de un lote (Ley 11-92, Art. 287).
  async function generarCertificado(evento) {
    evento.preventDefault();
    if (!certificadoForm.rnc_donante || !certificadoForm.valor_total_rd) {
      setError("Indica el RNC del donante y el valor total en RD$.");
      return;
    }
    setError(null);
    setMensaje(null);
    setGenerandoCertificado(true);
    try {
      const blob = await descargarCertificadoPdf(
        certificadoLote,
        certificadoForm.rnc_donante,
        Number(certificadoForm.valor_total_rd),
      );
      descargarBlob(blob, `certificado_${certificadoLote}.pdf`);
      setMensaje("Certificado fiscal PDF descargado.");
      setCertificadoLote(null);
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo generar el certificado.");
    } finally {
      setGenerandoCertificado(false);
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <EncabezadoApp />

      <main className="flex-1 w-full max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop py-2xl flex flex-col gap-xl">
        <div>
          <div className="flex items-center gap-sm mb-sm">
            <span className="material-symbols-outlined text-primary">bar_chart</span>
            <h1 className="font-headline-lg text-headline-lg text-on-surface page-header">Reportería</h1>
          </div>
          <p className="font-body-md text-body-md text-on-surface-variant">
            Visualiza, filtra y exporta los datos de tu operación.
          </p>
        </div>

        {error && (
          <div className="flex items-center gap-sm rounded-lg bg-error/10 border border-error/20 px-sm py-sm text-error">
            <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>error</span>
            <span className="font-body-md text-sm">{error}</span>
          </div>
        )}
        {mensaje && (
          <div className="flex items-center gap-sm rounded-lg bg-primary/10 border border-primary/20 px-sm py-sm text-primary">
            <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>check_circle</span>
            <span className="font-body-md text-sm">{mensaje}</span>
          </div>
        )}

        {/* Pestañas */}
        <div className="flex flex-wrap gap-1 bg-surface-container-low rounded-2xl p-1 border border-outline-variant/20">
          {PESTANAS.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => cambiarPestana(p.id)}
              className={`flex items-center gap-xs px-md py-sm font-label-md text-label-md rounded-xl transition-all duration-200 ${
                pestana === p.id
                  ? "bg-primary text-on-primary shadow-md shadow-primary/20 font-semibold"
                  : "text-on-surface-variant hover:text-primary hover:bg-surface-container-lowest"
              }`}
            >
              <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>
                {p.icono}
              </span>
              {p.texto}
            </button>
          ))}
        </div>

        {/* Donaciones (RF-23) */}
        {pestana === "donaciones" && (
          <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl flex flex-col gap-md">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-md items-end">
              <Campo etiqueta="Desde" tipo="date" valor={filtros.desde} onChange={(v) => setFiltros((f) => ({ ...f, desde: v }))} />
              <Campo etiqueta="Hasta" tipo="date" valor={filtros.hasta} onChange={(v) => setFiltros((f) => ({ ...f, hasta: v }))} />
              <div className="flex flex-col gap-xs">
                <label className="font-label-sm text-label-sm text-on-surface-variant">Estado</label>
                <select
                  className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-sm py-sm font-body-md text-body-md text-on-surface"
                  value={filtros.estado}
                  onChange={(e) => setFiltros((f) => ({ ...f, estado: e.target.value }))}
                >
                  <option value="">Todos</option>
                  {["disponible", "reservado", "asignado", "entregado", "vencido", "retirado"].map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <button
                type="button"
                onClick={cargarDonaciones}
                className="py-sm px-lg rounded-lg bg-primary text-on-primary font-label-md text-label-md hover:shadow-lg transition-all"
              >
                Filtrar
              </button>
            </div>

            {donaciones && (
              <>
                <div className="flex flex-wrap gap-md">
                  <Tarjeta valor={donaciones.total_lotes} etiqueta="Lotes" />
                  <Tarjeta valor={`${donaciones.total_kg} kg`} etiqueta="Peso total" />
                  <button
                    type="button"
                    onClick={() => exportar("donaciones")}
                    className="ml-auto self-center inline-flex items-center gap-xs py-sm px-md rounded-lg border border-tertiary text-tertiary font-label-md text-label-md hover:bg-surface-container-low transition-colors"
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>table_view</span>
                    Exportar a Sheets
                  </button>
                </div>
                <Tabla
                  columnas={["Fecha", "Donante", "Producto", "Categoría", "Cantidad", "Estado", "Certificado"]}
                  filas={donaciones.filas.map((f) => [
                    f.fecha ? new Date(f.fecha).toLocaleDateString() : "—",
                    f.donante,
                    f.producto,
                    f.categoria,
                    `${f.cantidad} ${f.unidad || ""}`,
                    f.estado,
                    <button
                      key="cert"
                      type="button"
                      onClick={() => abrirModalCertificado(f.id_lote)}
                      className="inline-flex items-center gap-xs text-tertiary font-label-sm text-label-sm hover:underline"
                    >
                      <span className="material-symbols-outlined text-sm">picture_as_pdf</span>
                      PDF
                    </button>,
                  ])}
                />
              </>
            )}
          </section>
        )}

        {/* Inventario (RF-24) */}
        {pestana === "inventario" && (
          <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl flex flex-col gap-md">
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => exportar("inventario")}
                className="inline-flex items-center gap-xs py-sm px-md rounded-lg border border-tertiary text-tertiary font-label-md text-label-md hover:bg-surface-container-low transition-colors"
              >
                <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>table_view</span>
                Exportar a Sheets
              </button>
            </div>
            <Tabla
              columnas={["Producto", "Cantidad", "Vencimiento", "Ventana (días)", "Estado"]}
              filas={inventario.map((l) => [
                l.nombre_producto,
                `${l.cantidad_disponible} ${l.unidad_medida || ""}`,
                l.fecha_vencimiento,
                l.ventana_dias,
                l.estado,
              ])}
            />
          </section>
        )}

        {/* Asignaciones (RF-25) */}
        {pestana === "asignaciones" && (
          <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl flex flex-col gap-md">
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => exportar("asignaciones")}
                className="inline-flex items-center gap-xs py-sm px-md rounded-lg border border-tertiary text-tertiary font-label-md text-label-md hover:bg-surface-container-low transition-colors"
              >
                <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>table_view</span>
                Exportar a Sheets
              </button>
            </div>
            <Tabla
              columnas={["Fecha", "Producto", "Sede receptora", "Distancia", "Entrega"]}
              filas={(asignaciones?.filas || []).map((f) => [
                f.fecha ? new Date(f.fecha).toLocaleDateString() : "—",
                f.producto,
                f.sede_receptora,
                `${f.distancia_km} km`,
                f.estado_entrega,
              ])}
            />
          </section>
        )}

        {/* Fiscal DGII (RF-27) */}
        {pestana === "fiscal" && (
          <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl flex flex-col gap-md">
            {!esBanco ? (
              <p className="font-body-md text-on-surface-variant">
                Solo un banco de alimentos o el administrador puede emitir reportes fiscales.
              </p>
            ) : (
              <>
                <p className="font-body-md text-body-md text-on-surface-variant">
                  Genera un reporte fiscal mensual inmutable (Norma DGII 06-2018),
                  encadenado por hash para garantizar su integridad.
                </p>
                <form className="grid grid-cols-1 sm:grid-cols-3 gap-md items-end" onSubmit={generarFiscal}>
                  <Campo etiqueta="Año" tipo="number" valor={fiscal.anio} onChange={(v) => setFiscal((f) => ({ ...f, anio: v }))} />
                  <Campo etiqueta="Mes" tipo="number" valor={fiscal.mes} onChange={(v) => setFiscal((f) => ({ ...f, mes: v }))} />
                  <button
                    type="submit"
                    className="py-sm px-lg rounded-lg bg-primary text-on-primary font-label-md text-label-md hover:shadow-lg transition-all"
                  >
                    Generar reporte fiscal
                  </button>
                </form>
                <div>
                  <button
                    type="button"
                    onClick={exportarDgii606}
                    disabled={descargandoDgii606}
                    className="inline-flex items-center gap-xs py-sm px-md rounded-lg border border-tertiary text-tertiary font-label-md text-label-md hover:bg-surface-container-low transition-colors disabled:opacity-60"
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>description</span>
                    {descargandoDgii606 ? "Exportando…" : "Exportar anexo DGII 606 (.txt)"}
                  </button>
                </div>

                {resultadoFiscal && (
                  <div className="rounded-xl border border-outline-variant/40 bg-surface-container-low p-lg flex flex-col gap-xs">
                    <p className="font-label-md text-label-md text-on-surface">
                      Período {resultadoFiscal.contenido.periodo} · v{resultadoFiscal.version}
                    </p>
                    <p className="font-body-md text-body-md text-on-surface-variant">
                      {resultadoFiscal.contenido.total_lotes} lote(s) · {resultadoFiscal.contenido.total_kg} kg
                    </p>
                    <p className="font-body-md text-sm text-on-surface-variant break-all">
                      <span className="font-label-sm">hash:</span> {resultadoFiscal.hash}
                    </p>
                    <p className="font-body-md text-sm text-on-surface-variant break-all">
                      <span className="font-label-sm">hash anterior:</span>{" "}
                      {resultadoFiscal.hash_anterior || "— (primer reporte)"}
                    </p>
                    <p className="font-body-md text-sm text-primary break-all">
                      {resultadoFiscal.url_archivo}
                    </p>
                  </div>
                )}
              </>
            )}
          </section>
        )}

        {/* Resultado de exportación */}
        {exportacion && (
          <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl flex flex-col gap-sm">
            <h2 className="font-headline-md text-headline-md text-on-surface">Exportación (simulada)</h2>
            <a
              href={exportacion.url}
              target="_blank"
              rel="noreferrer"
              className="text-primary font-label-md text-label-md break-all hover:underline"
            >
              {exportacion.url}
            </a>
            {exportacion.csv && (
              <pre className="text-xs bg-surface-container-low rounded-lg p-md overflow-x-auto text-on-surface-variant">
                {exportacion.csv.slice(0, 800)}
                {exportacion.csv.length > 800 ? "…" : ""}
              </pre>
            )}
          </section>
        )}
      </main>

      {/* Modal de certificado fiscal PDF por lote (RF-27, Ley 11-92 Art. 287) */}
      {certificadoLote && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-on-surface/40 backdrop-blur-sm px-margin-mobile">
          <div className="w-full max-w-md bg-surface-container-lowest rounded-2xl border border-outline-variant/30 shadow-xl p-xl animar-escala">
            <div className="flex items-center gap-sm mb-md">
              <span className="material-symbols-outlined text-primary">picture_as_pdf</span>
              <h2 className="font-headline-md text-headline-md text-on-surface">
                Certificado fiscal del lote
              </h2>
            </div>
            <p className="font-body-md text-sm text-on-surface-variant mb-md">
              Genera la certificación de donación en PDF (Art. 287 del Código
              Tributario) con el RNC del donante y el valor comercial en RD$.
            </p>
            <form onSubmit={generarCertificado} className="flex flex-col gap-md">
              <Campo
                etiqueta="RNC del donante"
                valor={certificadoForm.rnc_donante}
                onChange={(v) => setCertificadoForm((f) => ({ ...f, rnc_donante: v }))}
              />
              <Campo
                etiqueta="Valor total (RD$)"
                tipo="number"
                valor={certificadoForm.valor_total_rd}
                onChange={(v) => setCertificadoForm((f) => ({ ...f, valor_total_rd: v }))}
              />
              <div className="flex justify-end gap-sm pt-sm border-t border-outline-variant/30">
                <button
                  type="button"
                  onClick={() => setCertificadoLote(null)}
                  className="py-sm px-lg rounded-lg text-on-surface-variant hover:text-on-surface font-label-md text-label-md transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={generandoCertificado}
                  className="py-sm px-lg rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 transition-all disabled:opacity-60 flex items-center gap-xs"
                >
                  <span className="material-symbols-outlined text-sm">download</span>
                  {generandoCertificado ? "Generando…" : "Descargar PDF"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <PieDePagina />
    </div>
  );
}

function Campo({ etiqueta, tipo = "text", valor, onChange }) {
  return (
    <div className="flex flex-col gap-xs">
      <label className="font-label-sm text-label-sm text-on-surface-variant">{etiqueta}</label>
      <input
        type={tipo}
        value={valor}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-sm py-sm font-body-md text-body-md text-on-surface"
      />
    </div>
  );
}

function Tarjeta({ valor, etiqueta }) {
  return (
    <div className="bg-surface-container-low rounded-xl px-lg py-md">
      <p className="font-headline-md text-headline-md text-on-surface">{valor}</p>
      <p className="font-label-sm text-label-sm text-on-surface-variant">{etiqueta}</p>
    </div>
  );
}

function Tabla({ columnas, filas }) {
  if (filas.length === 0) {
    return <p className="font-body-md text-on-surface-variant">Sin datos.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-outline-variant/40 text-on-surface-variant font-label-sm text-label-sm">
            {columnas.map((c) => (
              <th key={c} className="py-sm pr-md">{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((fila, i) => (
            <tr key={i} className="border-b border-outline-variant/20 font-body-md text-body-md text-on-surface">
              {fila.map((celda, j) => (
                <td key={j} className="py-sm pr-md capitalize">{celda}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Reportes;
