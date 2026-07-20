// Página de inventario / 库存页 (OE2 — RF-09 … RF-16)

import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import {
  ajustarInventario,
  crearProducto,
  obtenerAlertas,
  obtenerCategoriasAlimentos,
  obtenerCategoriasPerecibilidad,
  obtenerHistorialLote,
  obtenerLotes,
  obtenerProductos,
  registrarLote,
} from "../api/inventario.js";
import { obtenerRoles } from "../api/autenticacion.js";
import { useSesion } from "../context/ContextoSesion.jsx";
import EncabezadoApp from "../componentes/EncabezadoApp.jsx";
import PieDePagina from "../componentes/PieDePagina.jsx";

const MOTIVOS = [
  { valor: "vencimiento", texto: "Vencimiento" },
  { valor: "dano_fisico", texto: "Daño físico" },
  { valor: "contaminacion", texto: "Contaminación" },
  { valor: "rechazo_en_destino", texto: "Rechazo en destino" },
  { valor: "otro", texto: "Otro" },
];

function hoyISO() {
  return new Date().toISOString().slice(0, 10);
}

function Inventario() {
  const { usuario } = useSesion();

  const [lotes, setLotes] = useState([]);
  const [alertas, setAlertas] = useState([]);
  const [productos, setProductos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [perecibilidades, setPerecibilidades] = useState([]);
  const [esBanco, setEsBanco] = useState(false);

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const [mensaje, setMensaje] = useState(null);

  // Formulario de lote / 批次表单
  const [nuevoProducto, setNuevoProducto] = useState(false);
  const [form, setForm] = useState({
    id_producto: "",
    cantidad_disponible: "",
    unidad_medida: "kg",
    fecha_produccion: "",
    fecha_vencimiento: "",
    temperatura_requerida: "",
    // Producto nuevo / 新产品
    nombre_producto: "",
    id_categoria_alimento: "",
    id_perecibilidad: "",
    marca: "",
  });

  // Panel de detalle / 详情面板
  const [loteSel, setLoteSel] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [ajuste, setAjuste] = useState({
    cantidad_afectada: "",
    motivo: "vencimiento",
    detalle: "",
  });

  async function cargar() {
    setCargando(true);
    setError(null);
    try {
      const [ls, al, ps, cs, pcs, roles] = await Promise.all([
        obtenerLotes(),
        obtenerAlertas(),
        obtenerProductos(),
        obtenerCategoriasAlimentos(),
        obtenerCategoriasPerecibilidad(),
        obtenerRoles(),
      ]);
      setLotes(ls);
      setAlertas(al);
      setProductos(ps);
      setCategorias(cs);
      setPerecibilidades(pcs);
      const rol = roles.find((r) => r.id_rol === usuario?.id_rol);
      setEsBanco(rol?.nombre === "banco_alimentos");
    } catch {
      setError("No se pudo cargar el inventario.");
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    if (usuario) cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!usuario) return <Navigate to="/login" replace />;

  function cambiar(campo, valor) {
    setForm((anterior) => ({ ...anterior, [campo]: valor }));
  }

  async function enviarLote(evento) {
    evento.preventDefault();
    setError(null);
    setMensaje(null);
    try {
      let idProducto = form.id_producto;

      // Crear producto si el usuario eligió "nuevo" / 若选择新产品则先创建
      if (nuevoProducto) {
        if (
          !form.nombre_producto ||
          !form.id_categoria_alimento ||
          !form.id_perecibilidad
        ) {
          setError("Completa los datos del nuevo producto.");
          return;
        }
        const creado = await crearProducto({
          nombre_producto: form.nombre_producto,
          id_categoria_alimento: Number(form.id_categoria_alimento),
          id_perecibilidad: Number(form.id_perecibilidad),
          marca: form.marca || null,
          unidad_predeterminada: form.unidad_medida || null,
        });
        idProducto = creado.id_producto;
      }

      if (!idProducto) {
        setError("Selecciona o crea un producto.");
        return;
      }
      if (!form.fecha_vencimiento) {
        setError("Indica la fecha de vencimiento.");
        return;
      }

      await registrarLote({
        id_producto: Number(idProducto),
        cantidad_disponible: Number(form.cantidad_disponible),
        unidad_medida: form.unidad_medida || null,
        fecha_produccion: form.fecha_produccion || null,
        fecha_vencimiento: form.fecha_vencimiento,
        temperatura_requerida: form.temperatura_requerida || null,
      });
      setMensaje("Lote registrado correctamente.");
      setForm({
        id_producto: "",
        cantidad_disponible: "",
        unidad_medida: "kg",
        fecha_produccion: "",
        fecha_vencimiento: "",
        temperatura_requerida: "",
        nombre_producto: "",
        id_categoria_alimento: "",
        id_perecibilidad: "",
        marca: "",
      });
      setNuevoProducto(false);
      await cargar();
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo registrar el lote.");
    }
  }

  async function verHistorial(lote) {
    setLoteSel(lote);
    setAjuste({ cantidad_afectada: "", motivo: "vencimiento", detalle: "" });
    try {
      const h = await obtenerHistorialLote(lote.id_lote);
      setHistorial(h);
    } catch {
      setHistorial([]);
    }
  }

  async function enviarAjuste(evento) {
    evento.preventDefault();
    setError(null);
    setMensaje(null);
    try {
      await ajustarInventario(loteSel.id_lote, {
        cantidad_afectada: Number(ajuste.cantidad_afectada),
        motivo: ajuste.motivo,
        detalle: ajuste.detalle || null,
      });
      setMensaje("Ajuste registrado correctamente.");
      await cargar();
      const actualizado = { ...loteSel };
      await verHistorial(actualizado);
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo registrar el ajuste.");
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <EncabezadoApp />

      <main className="flex-1 w-full max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop py-2xl flex flex-col gap-xl">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-sm mb-sm">
              <span className="material-symbols-outlined text-primary">inventory_2</span>
              <h1 className="font-headline-lg text-headline-lg text-on-surface page-header">
                Inventario de alimentos
              </h1>
            </div>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Gestión FEFO de lotes y trazabilidad.
            </p>
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-sm rounded-lg bg-error/10 border border-error/20 px-sm py-sm text-error">
            <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>error</span>
            <span className="font-body-md text-sm">{error}</span>
          </div>
        )}
        {mensaje && (
          <div className="flex items-center gap-sm rounded-lg bg-primary/10 border border-primary/20 px-sm py-sm text-primary">
            <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>
              check_circle
            </span>
            <span className="font-body-md text-sm">{mensaje}</span>
          </div>
        )}

        {/* Alertas de vencimiento (RF-13) */}
        {alertas.length > 0 && (
          <section className="rounded-2xl border-2 border-secondary/30 bg-gradient-to-r from-secondary/5 to-transparent p-lg">
            <h2 className="font-headline-md text-headline-md text-on-surface mb-sm flex items-center gap-xs">
              <span className="material-symbols-outlined text-secondary animar-pulso">warning</span>
              Próximos a vencer (≤ 3 días)
            </h2>
            <ul className="flex flex-col gap-xs">
              {alertas.map((a) => (
                <li key={a.id_lote} className="font-body-md text-body-md text-on-surface flex items-center gap-sm py-1">
                  <span className="w-2 h-2 rounded-full bg-secondary" />
                  {a.nombre_producto} — vence en {a.ventana_dias} día(s) ·{" "}
                  <span className="font-semibold">{a.cantidad_disponible} {a.unidad_medida || ""}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Registrar lote (RF-09) */}
        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl shadow-sm hover-lift-sm">
          <div className="flex items-center gap-sm mb-md">
            <span className="material-symbols-outlined text-primary">add_circle</span>
            <h2 className="font-headline-md text-headline-md text-on-surface">
              Registrar lote
            </h2>
          </div>
          <form className="grid grid-cols-1 md:grid-cols-2 gap-md" onSubmit={enviarLote}>
            <div className="md:col-span-2 flex items-center gap-sm">
              <input
                id="nuevo-producto"
                type="checkbox"
                checked={nuevoProducto}
                onChange={(e) => setNuevoProducto(e.target.checked)}
              />
              <label htmlFor="nuevo-producto" className="font-label-md text-label-md text-on-surface">
                Crear un producto nuevo
              </label>
            </div>

            {!nuevoProducto ? (
              <Campo etiqueta="Producto" id="producto">
                <select
                  id="producto"
                  className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-sm py-sm font-body-md text-body-md text-on-surface"
                  value={form.id_producto}
                  onChange={(e) => cambiar("id_producto", e.target.value)}
                >
                  <option value="">Selecciona un producto…</option>
                  {productos.map((p) => (
                    <option key={p.id_producto} value={p.id_producto}>
                      {p.nombre_producto}
                    </option>
                  ))}
                </select>
              </Campo>
            ) : (
              <>
                <Campo etiqueta="Nombre del producto" id="nombre_producto">
                  <Input value={form.nombre_producto} onChange={(v) => cambiar("nombre_producto", v)} />
                </Campo>
                <Campo etiqueta="Marca (opcional)" id="marca">
                  <Input value={form.marca} onChange={(v) => cambiar("marca", v)} />
                </Campo>
                <Campo etiqueta="Categoría de alimento" id="cat">
                  <select
                    id="cat"
                    className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-sm py-sm font-body-md text-body-md text-on-surface"
                    value={form.id_categoria_alimento}
                    onChange={(e) => cambiar("id_categoria_alimento", e.target.value)}
                  >
                    <option value="">Selecciona…</option>
                    {categorias.map((c) => (
                      <option key={c.id_categoria_alimento} value={c.id_categoria_alimento}>
                        {c.nombre_categoria}
                      </option>
                    ))}
                  </select>
                </Campo>
                <Campo etiqueta="Perecibilidad" id="pere">
                  <select
                    id="pere"
                    className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-sm py-sm font-body-md text-body-md text-on-surface"
                    value={form.id_perecibilidad}
                    onChange={(e) => cambiar("id_perecibilidad", e.target.value)}
                  >
                    <option value="">Selecciona…</option>
                    {perecibilidades.map((p) => (
                      <option key={p.id_perecibilidad} value={p.id_perecibilidad}>
                        {p.nombre} (mín. {p.dias_minimos_ventana} días)
                      </option>
                    ))}
                  </select>
                </Campo>
              </>
            )}

            <Campo etiqueta="Cantidad" id="cantidad">
              <Input tipo="number" value={form.cantidad_disponible} onChange={(v) => cambiar("cantidad_disponible", v)} />
            </Campo>
            <Campo etiqueta="Unidad" id="unidad">
              <Input value={form.unidad_medida} onChange={(v) => cambiar("unidad_medida", v)} />
            </Campo>
            <Campo etiqueta="Fecha de producción (opcional)" id="fprod">
              <Input tipo="date" value={form.fecha_produccion} onChange={(v) => cambiar("fecha_produccion", v)} max={hoyISO()} />
            </Campo>
            <Campo etiqueta="Fecha de vencimiento" id="fvenc">
              <Input tipo="date" value={form.fecha_vencimiento} onChange={(v) => cambiar("fecha_vencimiento", v)} min={hoyISO()} />
            </Campo>
            <Campo etiqueta="Temperatura requerida (opcional)" id="temp">
              <Input value={form.temperatura_requerida} onChange={(v) => cambiar("temperatura_requerida", v)} />
            </Campo>

            <div className="md:col-span-2 flex justify-end">
              <button
                type="submit"
                className="py-sm px-lg rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 hover:scale-[1.02] transition-all flex items-center gap-xs"
              >
                <span className="material-symbols-outlined text-sm">add</span>
                Registrar lote
              </button>
            </div>
          </form>
        </section>

        {/* Lista FEFO (RF-12) */}
        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl shadow-sm hover-lift-sm">
          <div className="flex items-center gap-sm mb-md">
            <span className="material-symbols-outlined text-primary">format_list_numbered</span>
            <h2 className="font-headline-md text-headline-md text-on-surface">
              Mis lotes (orden FEFO)
            </h2>
          </div>
          {cargando ? (
            <p className="font-body-md text-on-surface-variant">Cargando…</p>
          ) : lotes.length === 0 ? (
            <p className="font-body-md text-on-surface-variant">
              Aún no tienes lotes registrados.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-outline-variant/40 text-on-surface-variant font-label-sm text-label-sm">
                    <th className="py-sm pr-md">Producto</th>
                    <th className="py-sm pr-md">Cantidad</th>
                    <th className="py-sm pr-md">Vencimiento</th>
                    <th className="py-sm pr-md">Ventana</th>
                    <th className="py-sm pr-md">Perecibilidad</th>
                    <th className="py-sm pr-md">Estado</th>
                    <th className="py-sm pr-md">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {lotes.map((l) => (
                    <tr key={l.id_lote} className="border-b border-outline-variant/20 font-body-md text-body-md text-on-surface">
                      <td className="py-sm pr-md">{l.nombre_producto}</td>
                      <td className="py-sm pr-md">
                        {l.cantidad_disponible} {l.unidad_medida || ""}
                      </td>
                      <td className="py-sm pr-md">{l.fecha_vencimiento}</td>
                      <td className="py-sm pr-md">
                        <BadgeVentana lote={l} />
                      </td>
                      <td className="py-sm pr-md">{l.nombre_perecibilidad || "—"}</td>
                      <td className="py-sm pr-md capitalize">{l.estado}</td>
                      <td className="py-sm pr-md">
                        <button
                          type="button"
                          onClick={() => verHistorial(l)}
                          className="text-tertiary font-label-md text-label-md hover:underline"
                        >
                          Ver
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Detalle: historial (RF-16) + ajuste (RF-15) */}
        {loteSel && (
          <section className="bg-surface-container-lowest rounded-xl border border-outline-variant/30 p-xl shadow-sm">
            <div className="flex items-center justify-between mb-md">
              <h2 className="font-headline-md text-headline-md text-on-surface">
                Detalle: {loteSel.nombre_producto}
              </h2>
              <button
                type="button"
                onClick={() => setLoteSel(null)}
                className="text-on-surface-variant hover:text-on-surface"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {/* Ajuste manual — solo banco (RF-15) */}
            {esBanco && loteSel.estado !== "retirado" && (
              <form className="grid grid-cols-1 md:grid-cols-4 gap-md mb-lg" onSubmit={enviarAjuste}>
                <Campo etiqueta="Cantidad a descontar" id="aj_cant">
                  <Input
                    tipo="number"
                    value={ajuste.cantidad_afectada}
                    onChange={(v) => setAjuste((a) => ({ ...a, cantidad_afectada: v }))}
                  />
                </Campo>
                <Campo etiqueta="Motivo" id="aj_mot">
                  <select
                    id="aj_mot"
                    className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-sm py-sm font-body-md text-body-md text-on-surface"
                    value={ajuste.motivo}
                    onChange={(e) => setAjuste((a) => ({ ...a, motivo: e.target.value }))}
                  >
                    {MOTIVOS.map((m) => (
                      <option key={m.valor} value={m.valor}>
                        {m.texto}
                      </option>
                    ))}
                  </select>
                </Campo>
                <Campo etiqueta="Detalle (opcional)" id="aj_det">
                  <Input
                    value={ajuste.detalle}
                    onChange={(v) => setAjuste((a) => ({ ...a, detalle: v }))}
                  />
                </Campo>
                <div className="flex items-end">
                  <button
                    type="submit"
                    className="w-full py-sm px-lg rounded-lg bg-primary-container text-on-primary font-label-md text-label-md hover:bg-primary transition-colors"
                  >
                    Ajustar
                  </button>
                </div>
              </form>
            )}

            <h3 className="font-label-md text-label-md text-on-surface-variant mb-sm">
              Historial de movimientos
            </h3>
            {historial.length === 0 ? (
              <p className="font-body-md text-on-surface-variant">Sin movimientos.</p>
            ) : (
              <ul className="flex flex-col gap-xs">
                {historial.map((h) => (
                  <li key={h.id_historial} className="font-body-md text-body-md text-on-surface">
                    <span className="text-on-surface-variant">
                      {new Date(h.fecha).toLocaleString()}
                    </span>{" "}
                    — {h.estado_anterior ? `${h.estado_anterior} → ` : ""}
                    {h.estado_nuevo}
                    {h.motivo ? ` · ${h.motivo}` : ""}
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}
      </main>
      <PieDePagina />
    </div>
  );
}

function BadgeVentana({ lote }) {
  const dias = lote.ventana_dias;
  let clases = "bg-surface-container-low text-on-surface-variant";
  if (dias <= 0) clases = "badge-estado vencido";
  else if (lote.en_alerta) clases = "badge-estado pendiente";
  else if (lote.bajo_umbral) clases = "bg-secondary/10 text-on-surface";
  else clases = "bg-primary/10 text-primary";
  return (
    <span className={`inline-block rounded-full px-sm py-[2px] font-label-sm text-label-sm font-semibold ${clases}`}>
      {dias <= 0 ? "⚠ " : ""}{dias} día(s)
    </span>
  );
}

function Campo({ etiqueta, id, children }) {
  return (
    <div className="flex flex-col gap-xs">
      <label htmlFor={id} className="font-label-sm text-label-sm text-on-surface-variant">
        {etiqueta}
      </label>
      {children}
    </div>
  );
}

function Input({ tipo = "text", value, onChange, min, max }) {
  return (
    <input
      type={tipo}
      value={value}
      min={min}
      max={max}
      onChange={(e) => onChange(e.target.value)}
      className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-sm py-sm font-body-md text-body-md text-on-surface"
    />
  );
}

export default Inventario;
