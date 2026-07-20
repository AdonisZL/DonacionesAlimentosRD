// Página de registro / 注册页 (RF-01, RF-31) — asistente 2 pasos, solo español

import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { obtenerRoles, registrarUsuario } from "../api/autenticacion.js";
import { useSesion } from "../context/ContextoSesion.jsx";
import Marca from "../componentes/Marca.jsx";
import imagenRegistro from "../../fotos/01.png";

// Roles que pueden auto-registrarse (el administrador no) / 可自助注册的角色
const ROLES_UI = [
  {
    nombre: "donante",
    etiqueta: "Donante",
    icono: "volunteer_activism",
    descripcion: "Aporto excedentes de alimentos",
  },
  {
    nombre: "receptor",
    etiqueta: "Receptor",
    icono: "diversity_1",
    descripcion: "Fundación, comedor u ONG",
  },
  {
    nombre: "banco_alimentos",
    etiqueta: "Banco de Alimentos",
    icono: "warehouse",
    descripcion: "Entidad intermediaria",
  },
];

// Valida la política de contraseña en el frontend / 前端密码校验 (RNF-15)
function validarContrasena(contrasena) {
  if (contrasena.length < 10)
    return "La contraseña debe tener al menos 10 caracteres.";
  if (!/[A-Z]/.test(contrasena))
    return "La contraseña debe incluir al menos una mayúscula.";
  if (!/[0-9]/.test(contrasena))
    return "La contraseña debe incluir al menos un número.";
  if (!/[^A-Za-z0-9]/.test(contrasena))
    return "La contraseña debe incluir al menos un símbolo.";
  return null;
}

function Registro() {
  const [paso, setPaso] = useState(1);
  const [roles, setRoles] = useState([]);
  const [rolElegido, setRolElegido] = useState("");
  const [formulario, setFormulario] = useState({
    nombre: "",
    apellido: "",
    telefono: "",
    email: "",
    contrasena: "",
    confirmar_contrasena: "",
    id_rol: "",
    subtipo_donante: "",
    rnc: "",
    direccion_texto: "",
    latitud: "18.4861",
    longitud: "-69.9312",
    capacidad_diaria_kg: "",
    tiene_cadena_frio: false,
    horario_atencion: "",
    consentimiento_172_13: false,
  });
  const [error, setError] = useState(null);
  const [enviando, setEnviando] = useState(false);
  const { guardarSesion } = useSesion();
  const navegar = useNavigate();

  useEffect(() => {
    obtenerRoles()
      .then(setRoles)
      .catch(() => setError("No se pudieron cargar los roles."));
  }, []);

  function cambiar(campo, valor) {
    setFormulario((anterior) => ({ ...anterior, [campo]: valor }));
  }

  function elegirRol(nombreRol) {
    setRolElegido(nombreRol);
    const rol = roles.find((r) => r.nombre === nombreRol);
    cambiar("id_rol", rol ? rol.id_rol : "");
    if (nombreRol !== "donante") cambiar("subtipo_donante", "");
  }

  function irPaso2(evento) {
    evento.preventDefault();
    setError(null);
    if (!formulario.nombre || !formulario.email || !formulario.contrasena) {
      setError("Completa nombre, correo y contraseña.");
      return;
    }
    const errorContrasena = validarContrasena(formulario.contrasena);
    if (errorContrasena) {
      setError(errorContrasena);
      return;
    }
    if (formulario.contrasena !== formulario.confirmar_contrasena) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    setPaso(2);
  }

  async function enviar(evento) {
    evento.preventDefault();
    setError(null);
    if (!formulario.id_rol) {
      setError("Selecciona un tipo de cuenta.");
      return;
    }
    if (!formulario.consentimiento_172_13) {
      setError("Debes aceptar el tratamiento de datos (Ley 172-13).");
      return;
    }
    setEnviando(true);
    try {
      const payload = { ...formulario };
      delete payload.confirmar_contrasena;
      for (const clave of [
        "rnc",
        "direccion_texto",
        "capacidad_diaria_kg",
        "horario_atencion",
        "subtipo_donante",
      ]) {
        if (payload[clave] === "") payload[clave] = null;
      }
      if (payload.direccion_texto) {
        payload.latitud = parseFloat(payload.latitud);
        payload.longitud = parseFloat(payload.longitud);
      } else {
        payload.latitud = null;
        payload.longitud = null;
      }
      if (payload.capacidad_diaria_kg != null) {
        payload.capacidad_diaria_kg = parseFloat(payload.capacidad_diaria_kg);
      }
      const datos = await registrarUsuario(payload);
      guardarSesion(datos);
      navegar("/");
    } catch (err) {
      const detalle = err.response?.data?.detail;
      const mensaje = Array.isArray(detalle) ? detalle[0]?.msg : detalle;
      setError(mensaje || "No se pudo completar el registro.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="min-h-screen bg-hero-glow flex items-center justify-center p-margin-mobile md:p-margin-desktop">
      <div className="w-full max-w-[1024px] bg-surface-container-lowest rounded-3xl shadow-[0_18px_40px_-24px_rgba(11,28,48,0.4)] overflow-hidden flex flex-col md:flex-row border border-outline-variant/30 animar-aparecer">
        {/* Lado visual */}
        <div className="hidden md:flex md:w-5/12 relative overflow-hidden p-xl flex-col justify-between">
          <div
            className="absolute inset-0 bg-cover bg-center scale-105"
            style={{ backgroundImage: `url(${imagenRegistro})` }}
          ></div>
          <div className="absolute inset-0 bg-gradient-to-t from-primary/90 via-on-surface/55 to-on-surface/25"></div>

          <div className="relative z-10">
            <div className="mb-lg">
              <Marca claro />
            </div>
            <div className="inline-flex items-center gap-sm bg-white/15 text-surface-bright px-md py-1 rounded-full border border-white/25 mb-md">
              <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>diversity_3</span>
              <span className="font-label-sm text-label-sm uppercase tracking-wider">Red de impacto</span>
            </div>
            <h2 className="font-headline-lg text-headline-lg text-surface-bright mb-md leading-tight">
              Únete a la red de impacto
            </h2>
            <p className="font-body-md text-body-md text-surface-container-low opacity-90">
              Conectamos donantes, receptores y bancos de alimentos en la República
              Dominicana.
            </p>
          </div>
          <div className="relative z-10 mt-2xl">
            <div className="glass-card p-lg rounded-2xl">
              <div className="flex items-center gap-sm mb-sm">
                <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
                  security
                </span>
                <span className="font-label-md text-label-md text-on-surface">Gestión transparente</span>
              </div>
              <p className="font-body-md text-sm text-on-surface-variant">
                Tus datos se protegen conforme a la Ley 172-13.
              </p>
            </div>
          </div>
        </div>

        {/* Formulario */}
        <div className="w-full md:w-7/12 p-lg md:p-xl flex flex-col">
          <div className="flex items-center justify-between mb-lg">
            <Link
              to="/"
              className="inline-flex items-center gap-xs text-on-surface-variant hover:text-primary font-label-md text-label-md transition-colors"
            >
              <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>arrow_back</span>
              Inicio
            </Link>
            <div className="md:hidden">
              <Marca />
            </div>
          </div>

          {/* Indicador de pasos */}
          <div className="flex items-center justify-between mb-xl w-full max-w-sm mx-auto md:mx-0">
            <div className="flex flex-col items-center gap-xs">
              <div className={`w-9 h-9 rounded-full flex items-center justify-center font-label-md text-label-md font-semibold transition-all duration-300 ${
                paso >= 1
                  ? "bg-primary text-on-primary shadow-lg shadow-primary/25"
                  : "bg-surface-container-high text-on-surface-variant"
              }`}>
                {paso > 1 ? <span className="material-symbols-outlined text-sm">check</span> : "1"}
              </div>
              <span className={`font-label-sm text-label-sm transition-colors ${paso >= 1 ? "text-primary font-semibold" : "text-on-surface-variant"}`}>Cuenta</span>
            </div>
            <div className="flex-1 h-1 bg-outline-variant/40 mx-sm rounded-full relative overflow-hidden">
              <div className={`absolute top-0 left-0 h-full bg-primary rounded-full transition-all duration-500 ${paso >= 2 ? "w-full" : "w-0"}`}></div>
            </div>
            <div className="flex flex-col items-center gap-xs">
              <div className={`w-9 h-9 rounded-full flex items-center justify-center font-label-md text-label-md font-semibold transition-all duration-300 border-2 ${
                paso >= 2
                  ? "bg-primary text-on-primary border-primary shadow-lg shadow-primary/25"
                  : "bg-surface-container-high text-on-surface-variant border-outline-variant"
              }`}>
                2
              </div>
              <span className={`font-label-sm text-label-sm transition-colors ${paso >= 2 ? "text-primary font-semibold" : "text-on-surface-variant"}`}>Perfil</span>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-sm rounded-lg bg-error-container px-sm py-sm text-on-error-container mb-md">
              <span className="material-symbols-outlined" style={{ fontSize: "20px" }}>
                error
              </span>
              <span className="font-body-md text-sm">{error}</span>
            </div>
          )}

          {paso === 1 ? (
            <form className="flex flex-col gap-md" onSubmit={irPaso2}>
              <h3 className="font-headline-md text-headline-md text-on-surface">Detalles de la cuenta</h3>
              <Campo id="nombre" etiqueta="Nombre *" icono="person" valor={formulario.nombre} onChange={(v) => cambiar("nombre", v)} />
              <Campo id="apellido" etiqueta="Apellido" icono="badge" valor={formulario.apellido} onChange={(v) => cambiar("apellido", v)} />
              <Campo id="telefono" etiqueta="Teléfono" icono="call" valor={formulario.telefono} onChange={(v) => cambiar("telefono", v)} />
              <Campo id="email" etiqueta="Correo electrónico *" icono="mail" tipo="email" valor={formulario.email} onChange={(v) => cambiar("email", v)} />
              <Campo
                id="contrasena"
                etiqueta="Contraseña *"
                icono="lock"
                tipo="password"
                valor={formulario.contrasena}
                onChange={(v) => cambiar("contrasena", v)}
                ayuda="Mín. 10 caracteres, con mayúscula, número y símbolo."
              />
              <Campo
                id="confirmar"
                etiqueta="Confirmar contraseña *"
                icono="lock"
                tipo="password"
                valor={formulario.confirmar_contrasena}
                onChange={(v) => cambiar("confirmar_contrasena", v)}
              />
              <div className="mt-md flex justify-end">
                <button type="submit" className="bg-primary hover:shadow-lg hover:scale-[1.01] text-on-primary font-label-md text-label-md py-sm px-lg rounded-lg shadow-sm transition-all flex items-center gap-xs">
                  Continuar
                  <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>arrow_forward</span>
                </button>
              </div>
            </form>
          ) : (
            <form className="flex flex-col gap-lg flex-1" onSubmit={enviar}>
              <h3 className="font-headline-md text-headline-md text-on-surface">Tipo de perfil</h3>
              <div className="flex flex-col gap-sm">
                <span className="font-label-md text-label-md text-on-surface">Selecciona tu rol principal</span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-sm">
                  {ROLES_UI.map((r) => {
                    const activo = rolElegido === r.nombre;
                    return (
                      <button
                        key={r.nombre}
                        type="button"
                        onClick={() => elegirRol(r.nombre)}
                        className={`flex flex-col items-center justify-center p-md border-2 rounded-xl text-center gap-xs transition-all duration-200 hover-lift-sm ${
                          activo
                            ? "border-primary bg-primary/5 shadow-md shadow-primary/10"
                            : "border-outline-variant/40 hover:border-outline-variant hover:bg-surface-container-low"
                        }`}
                      >
                        <span className={`material-symbols-outlined text-3xl transition-colors ${activo ? "text-primary" : "text-on-surface-variant"}`}>
                          {r.icono}
                        </span>
                        <span className={`font-label-md text-label-md transition-colors ${activo ? "text-primary font-semibold" : "text-on-surface"}`}>{r.etiqueta}</span>
                        <span className="font-label-sm text-label-sm text-on-surface-variant">{r.descripcion}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {rolElegido === "donante" && (
                <div className="flex flex-col gap-sm">
                  <span className="font-label-md text-label-md text-on-surface">Subtipo de donante</span>
                  <div className="flex gap-sm">
                    {[
                      { v: "formal", t: "Formalizado (con RNC)", icono: "business" },
                      { v: "informal", t: "Especial / Agrícola", icono: "agriculture" },
                    ].map((s) => (
                      <label
                        key={s.v}
                        className={`flex-1 flex items-center gap-sm p-sm border-2 rounded-xl cursor-pointer transition-all duration-200 ${
                          formulario.subtipo_donante === s.v
                            ? "border-primary bg-primary/5 shadow-sm"
                            : "border-outline-variant/40 hover:bg-surface-container-low"
                        }`}
                      >
                        <input
                          type="radio"
                          name="subtipo"
                          value={s.v}
                          checked={formulario.subtipo_donante === s.v}
                          onChange={() => cambiar("subtipo_donante", s.v)}
                          className="text-primary focus:ring-primary"
                        />
                        <span className="material-symbols-outlined text-on-surface-variant text-sm">{s.icono}</span>
                        <span className="font-body-md text-body-md text-on-surface">{s.t}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Campos específicos por rol / 角色专属字段 */}
              {(rolElegido === "receptor" ||
                rolElegido === "banco_alimentos" ||
                (rolElegido === "donante" &&
                  formulario.subtipo_donante === "formal")) && (
                <Campo
                  id="rnc"
                  etiqueta="RNC (11 dígitos)"
                  icono="badge"
                  valor={formulario.rnc}
                  onChange={(v) => cambiar("rnc", v)}
                  ayuda="Registro Nacional de Contribuyentes."
                />
              )}

              {(rolElegido === "receptor" ||
                rolElegido === "banco_alimentos") && (
                <>
                  <Campo
                    id="direccion"
                    etiqueta="Dirección de la sede"
                    icono="location_on"
                    valor={formulario.direccion_texto}
                    onChange={(v) => cambiar("direccion_texto", v)}
                    ayuda="Coordenadas de ejemplo (Santo Domingo); puedes ajustarlas."
                  />
                  <div className="grid grid-cols-2 gap-sm">
                    <Campo
                      id="latitud"
                      etiqueta="Latitud"
                      icono="my_location"
                      valor={formulario.latitud}
                      onChange={(v) => cambiar("latitud", v)}
                    />
                    <Campo
                      id="longitud"
                      etiqueta="Longitud"
                      icono="my_location"
                      valor={formulario.longitud}
                      onChange={(v) => cambiar("longitud", v)}
                    />
                  </div>
                  <Campo
                    id="capacidad"
                    etiqueta="Capacidad diaria (kg)"
                    icono="scale"
                    tipo="number"
                    valor={formulario.capacidad_diaria_kg}
                    onChange={(v) => cambiar("capacidad_diaria_kg", v)}
                  />
                </>
              )}

              {rolElegido === "banco_alimentos" && (
                <>
                  <Campo
                    id="horario"
                    etiqueta="Horario de atención"
                    icono="schedule"
                    valor={formulario.horario_atencion}
                    onChange={(v) => cambiar("horario_atencion", v)}
                  />
                  <label className="flex items-center gap-sm cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formulario.tiene_cadena_frio}
                      onChange={(e) =>
                        cambiar("tiene_cadena_frio", e.target.checked)
                      }
                      className="text-primary focus:ring-primary"
                    />
                    <span className="font-body-md text-body-md text-on-surface">
                      Cuenta con cadena de frío (refrigeración)
                    </span>
                  </label>
                </>
              )}

              <label className="flex items-start gap-sm cursor-pointer">
                <input
                  type="checkbox"
                  checked={formulario.consentimiento_172_13}
                  onChange={(e) => cambiar("consentimiento_172_13", e.target.checked)}
                  className="mt-xs text-primary focus:ring-primary"
                />
                <span className="font-body-md text-sm text-on-surface-variant">
                  Acepto el tratamiento de mis datos personales conforme a la Ley 172-13.
                </span>
              </label>

              <div className="mt-auto pt-md flex justify-between border-t border-outline-variant/30">
                <button
                  type="button"
                  onClick={() => setPaso(1)}
                  className="text-on-surface-variant hover:text-on-surface font-label-md text-label-md py-sm px-md rounded-lg flex items-center gap-xs"
                >
                  <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>arrow_back</span>
                  Atrás
                </button>
                <button
                  type="submit"
                  disabled={enviando}
                  className="bg-primary hover:shadow-lg hover:scale-[1.01] text-on-primary font-label-md text-label-md py-sm px-lg rounded-lg shadow-sm transition-all flex items-center gap-xs disabled:opacity-60"
                >
                  {enviando ? "Creando…" : "Completar registro"}
                  <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>check</span>
                </button>
              </div>
            </form>
          )}

          <p className="mt-md text-center font-body-md text-sm text-on-surface-variant">
            ¿Ya tienes cuenta?{" "}
            <Link to="/login" className="text-primary hover:underline font-label-md text-label-md">
              Inicia sesión
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

// Campo de formulario reutilizable / 可复用输入字段
function Campo({ id, etiqueta, icono, tipo = "text", valor, onChange, ayuda }) {
  const [verClave, setVerClave] = useState(false);
  const esClave = tipo === "password";
  const tipoReal = esClave && verClave ? "text" : tipo;
  return (
    <div className="flex flex-col gap-xs">
      <label className="font-label-md text-label-md text-on-surface" htmlFor={id}>
        {etiqueta}
      </label>
      <div className="relative">
        <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">
          {icono}
        </span>
        <input
          id={id}
          type={tipoReal}
          value={valor}
          onChange={(e) => onChange(e.target.value)}
          className={`w-full pl-10 ${esClave ? "pr-10" : "pr-3"} py-sm bg-surface border border-outline-variant rounded-lg font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-shadow`}
        />
        {esClave && (
          <button
            type="button"
            onClick={() => setVerClave((v) => !v)}
            className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-primary"
            aria-label={verClave ? "Ocultar contraseña" : "Mostrar contraseña"}
          >
            {verClave ? "visibility_off" : "visibility"}
          </button>
        )}
      </div>
      {ayuda && <small className="font-label-sm text-label-sm text-on-surface-variant">{ayuda}</small>}
    </div>
  );
}

export default Registro;
