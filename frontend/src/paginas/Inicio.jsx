// Página de inicio / 首页 — landing rico + panel de sesión (solo español)

import { Link } from "react-router-dom";

import { useSesion } from "../context/ContextoSesion.jsx";
import Marca from "../componentes/Marca.jsx";
import EncabezadoApp from "../componentes/EncabezadoApp.jsx";
import PieDePagina from "../componentes/PieDePagina.jsx";
import imagenHero from "../../fotos/01.png";

const CARACTERISTICAS = [
  {
    icono: "hub",
    color: "text-primary bg-primary-container/20",
    titulo: "Red inteligente",
    texto:
      "Emparejamos donantes con las organizaciones más cercanas usando geolocalización PostGIS y reglas de compatibilidad.",
  },
  {
    icono: "ac_unit",
    color: "text-tertiary bg-tertiary-container/20",
    titulo: "Cadena de frío",
    texto:
      "Respetamos los requisitos de refrigeración de cada alimento para garantizar la seguridad alimentaria.",
  },
  {
    icono: "schedule",
    color: "text-secondary bg-secondary-container/20",
    titulo: "Lógica FEFO",
    texto:
      "Priorizamos lo que vence primero, con alertas de vencimiento y rechazo automático de lotes vencidos.",
  },
];

const PASOS = [
  {
    n: "1",
    titulo: "Regístrate",
    texto: "Crea tu perfil como donante, receptor o banco de alimentos.",
  },
  {
    n: "2",
    titulo: "Registra o busca",
    texto: "Publica tus lotes de alimentos o busca receptores compatibles cercanos.",
  },
  {
    n: "3",
    titulo: "Mide tu impacto",
    texto: "Confirma entregas, recibe notificaciones y registra la trazabilidad.",
  },
];

const ESTADISTICAS = [
  { valor: "30%", etiqueta: "Alimentos que se desperdician en RD" },
  { valor: "FEFO", etiqueta: "Optimización de vencimientos" },
  { valor: "≤ 75 km", etiqueta: "Radio de emparejamiento" },
];

function AccionRapida({ a, icono, titulo, texto, color }) {
  return (
    <Link
      to={a}
      className="hover-lift group flex flex-col gap-sm p-lg rounded-2xl border border-outline-variant/40 bg-surface-container-lowest"
    >
      <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${color}`}>
        <span className="material-symbols-outlined" style={{ fontSize: "28px" }}>
          {icono}
        </span>
      </div>
      <h3 className="font-headline-md text-headline-md text-on-surface">{titulo}</h3>
      <p className="font-body-md text-body-md text-on-surface-variant">{texto}</p>
      <span className="mt-auto inline-flex items-center gap-xs text-primary font-label-md text-label-md">
        Abrir
        <span className="material-symbols-outlined group-hover:translate-x-1 transition-transform" style={{ fontSize: "18px" }}>
          arrow_forward
        </span>
      </span>
    </Link>
  );
}

function PanelSesion({ usuario }) {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <EncabezadoApp />
      <main className="flex-1 max-w-6xl w-full mx-auto px-margin-mobile md:px-margin-desktop py-2xl">
        {/* Banner de bienvenida */}
        <section className="relative overflow-hidden rounded-[2rem] bg-gradient-to-br from-primary via-primary to-[#004b1e] text-on-primary p-xl md:p-2xl mb-2xl shadow-xl">
          <div className="absolute inset-0 animar-brillo pointer-events-none" />
          {/* Decorative circles */}
          <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full bg-white/5" />
          <div className="absolute -bottom-10 right-32 w-32 h-32 rounded-full bg-white/5" />
          <div className="relative z-10 max-w-2xl">
            <div className="inline-flex items-center gap-sm bg-white/15 text-surface-bright px-md py-1 rounded-full border border-white/20 mb-md">
              <span className="w-2 h-2 rounded-full bg-primary-fixed-dim animar-pulso" />
              <span className="font-label-sm text-label-sm uppercase tracking-widest">
                Panel de {usuario.estado}
              </span>
            </div>
            <h1 className="font-display-lg text-display-lg leading-tight mb-md">
              ¡Hola, {usuario.nombre}! 👋
            </h1>
            <p className="font-body-lg text-body-lg text-on-primary/85 max-w-lg">
              Gestiona tu inventario, encuentra receptores compatibles y da seguimiento
              a tus donaciones desde un solo lugar.
            </p>
          </div>
        </section>

        {/* Acciones rápidas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-lg mb-2xl animar-lista">
          <AccionRapida
            a="/inventario"
            icono="inventory_2"
            titulo="Inventario"
            texto="Registra lotes, revisa el orden FEFO y atiende las alertas de vencimiento."
            color="text-primary bg-primary/10"
          />
          <AccionRapida
            a="/emparejamientos"
            icono="hub"
            titulo="Emparejamientos"
            texto="Busca receptores cercanos y gestiona confirmaciones y entregas."
            color="text-tertiary bg-tertiary/10"
          />
          <AccionRapida
            a="/reportes"
            icono="bar_chart"
            titulo="Reportes"
            texto="Genera reportes de donaciones, inventario, asignaciones y fiscal."
            color="text-primary bg-primary/10"
          />
          <AccionRapida
            a="/perfil"
            icono="person"
            titulo="Mi perfil"
            texto="Actualiza tus datos de contacto o gestiona tu cuenta."
            color="text-secondary bg-secondary/10"
          />
        </div>

        {/* Datos de cuenta */}
        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl shadow-sm hover-lift-sm">
          <div className="flex items-center gap-sm mb-lg">
            <span className="material-symbols-outlined text-primary">account_circle</span>
            <h2 className="font-headline-md text-headline-md text-on-surface">
              Datos de la cuenta
            </h2>
          </div>
          <dl className="grid grid-cols-1 sm:grid-cols-3 gap-md">
            <div className="bg-surface-container-low rounded-xl p-md border border-outline-variant/20">
              <dt className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-xs mb-1">
                <span className="material-symbols-outlined text-sm">badge</span>
                Nombre
              </dt>
              <dd className="font-body-md text-body-md text-on-surface font-semibold">{usuario.nombre}</dd>
            </div>
            <div className="bg-surface-container-low rounded-xl p-md border border-outline-variant/20">
              <dt className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-xs mb-1">
                <span className="material-symbols-outlined text-sm">mail</span>
                Correo
              </dt>
              <dd className="font-body-md text-body-md text-on-surface break-all">{usuario.email}</dd>
            </div>
            <div className="bg-surface-container-low rounded-xl p-md border border-outline-variant/20">
              <dt className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-xs mb-1">
                <span className="material-symbols-outlined text-sm">toggle_on</span>
                Estado
              </dt>
              <dd className="font-body-md text-body-md text-on-surface capitalize flex items-center gap-xs font-semibold">
                <span className="w-2.5 h-2.5 rounded-full bg-primary shadow-[0_0_8px_rgba(34,197,94,0.5)] inline-block" />
                {usuario.estado}
              </dd>
            </div>
          </dl>
        </section>
      </main>
      <PieDePagina />
    </div>
  );
}

function Inicio() {
  const { usuario } = useSesion();

  if (usuario) return <PanelSesion usuario={usuario} />;

  return (
    <div className="bg-surface text-on-surface">
      <header className="sticky top-0 z-50 bg-surface/85 backdrop-blur-md border-b border-outline-variant/20 shadow-[0_1px_12px_rgba(11,28,48,0.04)]">
        <nav className="max-w-6xl mx-auto h-16 px-margin-mobile md:px-margin-desktop flex items-center justify-between">
          <Marca />
          <div className="hidden md:flex items-center gap-lg font-body-md text-on-surface-variant">
            <a href="#problema" className="hover:text-primary transition-colors font-medium">El problema</a>
            <a href="#solucion" className="hover:text-primary transition-colors font-medium">Solución</a>
            <a href="#pasos" className="hover:text-primary transition-colors font-medium">Cómo funciona</a>
          </div>
          <div className="flex items-center gap-sm">
            <Link
              to="/login"
              className="px-md py-sm rounded-lg text-primary font-label-md text-label-md font-semibold hover:bg-primary/5 transition-all"
            >
              Iniciar sesión
            </Link>
            <Link
              to="/registro"
              className="px-lg py-sm rounded-lg bg-primary text-on-primary font-label-md text-label-md font-semibold hover:shadow-lg hover:shadow-primary/25 hover:scale-[1.02] transition-all"
            >
              Crear cuenta
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden bg-hero-glow">
        {/* Decorative blobs */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-tertiary/5 rounded-full blur-3xl" />
        <div className="max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop py-2xl grid grid-cols-1 md:grid-cols-2 gap-2xl items-center">
          <div className="space-y-lg animar-aparecer">
            <div className="inline-flex items-center gap-sm bg-primary/10 text-on-primary-fixed-variant px-md py-1.5 rounded-full border border-primary/20">
              <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>verified</span>
              <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold">Compromiso dominicano</span>
            </div>
            <h1 className="font-display-lg text-display-lg leading-tight">
              Alimentando la esperanza en la{" "}
              <span className="text-gradient">República Dominicana</span>
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant max-w-lg leading-relaxed">
              Conectamos los excedentes de alimentos con quienes más los necesitan, con
              trazabilidad, optimización logística FEFO y cumplimiento legal.
            </p>
            <div className="flex flex-wrap gap-md pt-sm">
              <Link
                to="/registro"
                className="group px-xl py-md bg-primary text-on-primary rounded-xl font-label-md text-label-md font-semibold hover:shadow-xl hover:scale-[1.02] transition-all flex items-center gap-sm shadow-lg shadow-primary/25"
              >
                Empezar ahora
                <span className="material-symbols-outlined group-hover:translate-x-1 transition-transform" style={{ fontSize: "20px" }}>
                  arrow_forward
                </span>
              </Link>
              <a
                href="#solucion"
                className="px-xl py-md border-2 border-tertiary text-tertiary rounded-xl font-label-md text-label-md font-semibold hover:bg-tertiary/5 transition-all"
              >
                Saber más
              </a>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute -inset-4 bg-gradient-to-tr from-primary/20 to-secondary/20 blur-3xl opacity-60 rounded-full animar-pulso" />
            <div className="relative aspect-[4/5] max-w-md mx-auto rounded-3xl overflow-hidden shadow-2xl border border-white/30 ring-1 ring-black/5">
              <img src={imagenHero} alt="Voluntaria con una caja de alimentos donados" className="w-full h-full object-cover" />
            </div>
            <div className="absolute -bottom-5 -left-2 md:-left-5 glass-card p-md rounded-2xl shadow-xl flex items-center gap-md animar-flotar">
              <div className="w-12 h-12 bg-gradient-to-br from-secondary to-secondary-fixed-dim rounded-full flex items-center justify-center text-on-primary shadow-lg">
                <span className="material-symbols-outlined">volunteer_activism</span>
              </div>
              <div>
                <p className="font-headline-md text-headline-md font-bold text-on-surface">FEFO</p>
                <p className="font-label-sm text-label-sm text-on-surface-variant">Cero desperdicio</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* El problema */}
      <section id="problema" className="bg-surface-container-lowest py-2xl">
        <div className="max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop grid grid-cols-1 md:grid-cols-2 gap-2xl items-center">
          <div className="space-y-lg order-2 md:order-1">
            <div className="inline-flex items-center gap-sm bg-error/10 text-error px-md py-1 rounded-full border border-error/20">
              <span className="material-symbols-outlined text-sm">priority_high</span>
              <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold">El desafío</span>
            </div>
            <h2 className="font-headline-lg text-headline-lg">
              Un desafío de eficiencia,{" "}
              <span className="text-error">no de escasez</span>
            </h2>
            <p className="font-body-lg text-body-lg text-on-surface-variant">
              La República Dominicana produce suficiente para todos, pero la brecha
              logística impide que el alimento llegue a tiempo a los sectores más
              vulnerables.
            </p>
            <div className="space-y-md">
              <div className="flex items-start gap-md p-md bg-surface-container rounded-xl border border-outline-variant/20 hover-lift-sm">
                <span className="material-symbols-outlined text-error mt-1 p-2 bg-error/10 rounded-lg">warning</span>
                <div>
                  <h4 className="font-label-md text-label-md font-bold text-on-surface">Pérdida crítica</h4>
                  <p className="font-body-md text-body-md text-on-surface-variant">
                    Toneladas de alimentos frescos se pierden en la cadena de suministro.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-md p-md bg-surface-container rounded-xl border border-outline-variant/20 hover-lift-sm">
                <span className="material-symbols-outlined text-primary mt-1 p-2 bg-primary/10 rounded-lg">groups</span>
                <div>
                  <h4 className="font-label-md text-label-md font-bold text-on-surface">Hambre invisible</h4>
                  <p className="font-body-md text-body-md text-on-surface-variant">
                    Muchas comunidades enfrentan altas tasas de inseguridad alimentaria.
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div className="order-1 md:order-2 relative rounded-3xl overflow-hidden aspect-[4/3] shadow-xl ring-1 ring-black/5">
            <img src={imagenHero} alt="Alimentos donados" className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-on-surface/85 via-on-surface/20 to-transparent flex items-end p-lg">
              <p className="text-surface-bright font-body-md italic leading-relaxed">
                «Cerca del 30% de los alimentos producidos terminan en desperdicio
                mientras miles sufren inseguridad alimentaria.»
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* La solución */}
      <section id="solucion" className="py-2xl bg-glow-subtle">
        <div className="max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop">
          <div className="text-center max-w-2xl mx-auto mb-2xl">
            <div className="inline-flex items-center gap-sm bg-primary/10 text-primary px-md py-1 rounded-full border border-primary/20 mb-md">
              <span className="material-symbols-outlined text-sm">lightbulb</span>
              <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold">Tecnología con propósito</span>
            </div>
            <h2 className="font-headline-lg text-headline-lg mb-md">Nuestra solución logística</h2>
            <p className="font-body-lg text-body-lg text-on-surface-variant">
              Transformamos la donación en una operación estratégica de alto impacto
              mediante tecnología.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-lg animar-lista">
            {CARACTERISTICAS.map((c) => (
              <div
                key={c.titulo}
                className="hover-lift p-xl bg-surface-container-lowest rounded-3xl border border-outline-variant/40 group relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl from-current/5 to-transparent rounded-bl-3xl -mr-4 -mt-4" />
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-lg group-hover:scale-110 transition-transform ${c.color}`}>
                  <span className="material-symbols-outlined" style={{ fontSize: "32px" }}>{c.icono}</span>
                </div>
                <h3 className="font-headline-md text-headline-md mb-sm">{c.titulo}</h3>
                <p className="font-body-md text-body-md text-on-surface-variant">{c.texto}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Estadísticas */}
      <section className="py-2xl bg-gradient-to-br from-on-surface to-[#15273d] text-on-primary relative overflow-hidden">
        <div className="absolute inset-0 opacity-[0.07] bg-[radial-gradient(circle_at_50%_50%,_#22c55e_0%,_transparent_55%)]" />
        {/* Grid pattern */}
        <div className="absolute inset-0 opacity-[0.03]" style={{
          backgroundImage: "linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
        }} />
        <div className="max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop relative z-10 grid grid-cols-1 md:grid-cols-3 gap-2xl text-center">
          {ESTADISTICAS.map((e) => (
            <div key={e.etiqueta} className="space-y-sm group">
              <p className="font-display-lg text-display-lg text-primary-fixed-dim group-hover:scale-110 transition-transform duration-300">{e.valor}</p>
              <p className="font-label-md text-label-md uppercase tracking-widest text-surface-variant/80">
                {e.etiqueta}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Cómo funciona */}
      <section id="pasos" className="py-2xl bg-surface-container-lowest">
        <div className="max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop">
          <div className="mb-2xl">
            <div className="inline-flex items-center gap-sm bg-tertiary/10 text-tertiary px-md py-1 rounded-full border border-tertiary/20 mb-md">
              <span className="material-symbols-outlined text-sm">rocket_launch</span>
              <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold">3 pasos</span>
            </div>
            <h2 className="font-headline-lg text-headline-lg">Proceso de impacto</h2>
            <p className="font-body-lg text-body-lg text-on-surface-variant">
              Tres pasos para transformar excedentes en ayuda real.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-xl relative">
            {/* Connecting line desktop */}
            <div className="hidden md:block absolute top-7 left-[calc(16%+28px)] right-[calc(16%+28px)] h-0.5 bg-gradient-to-r from-primary/20 via-primary/40 to-primary/20" />
            {PASOS.map((p) => (
              <div key={p.n} className="relative space-y-md text-center md:text-left">
                <div className="w-14 h-14 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-full flex items-center justify-center font-headline-md text-headline-md relative z-10 shadow-lg shadow-primary/25 mx-auto md:mx-0">
                  {p.n}
                </div>
                <h4 className="font-headline-md text-headline-md">{p.titulo}</h4>
                <p className="font-body-md text-body-md text-on-surface-variant">{p.texto}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA final */}
      <section className="py-2xl px-margin-mobile">
        <div className="max-w-6xl mx-auto bg-gradient-to-br from-primary via-primary to-[#004b1e] rounded-[2.5rem] p-xl md:p-2xl text-center relative overflow-hidden shadow-2xl shadow-primary/20">
          <div className="absolute inset-0 animar-brillo pointer-events-none" />
          {/* Decorative circles */}
          <div className="absolute top-10 right-10 w-40 h-40 rounded-full bg-white/5" />
          <div className="absolute -bottom-10 -left-10 w-56 h-56 rounded-full bg-white/5" />
          <div className="relative z-10 max-w-3xl mx-auto space-y-lg">
            <div className="inline-flex items-center gap-sm bg-white/15 text-surface-bright px-md py-1 rounded-full border border-white/20">
              <span className="material-symbols-outlined text-sm">favorite</span>
              <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold">Haz la diferencia</span>
            </div>
            <h2 className="font-display-lg text-display-lg text-on-primary">
              Únete a la red de impacto
            </h2>
            <p className="font-body-lg text-body-lg text-on-primary/85 max-w-xl mx-auto">
              Cada donación, por pequeña que sea, es un paso hacia una República
              Dominicana libre de hambre. Empieza hoy mismo.
            </p>
            <div className="pt-sm flex flex-wrap gap-md justify-center">
              <Link
                to="/registro"
                className="bg-secondary text-on-primary px-2xl py-lg rounded-2xl font-headline-md text-headline-md hover:scale-105 active:scale-95 transition-all shadow-xl shadow-secondary/30"
              >
                Registrarse ahora
              </Link>
              <Link
                to="/login"
                className="border-2 border-on-primary/60 text-on-primary px-2xl py-lg rounded-2xl font-headline-md text-headline-md hover:bg-on-primary/10 transition-all"
              >
                Iniciar sesión
              </Link>
            </div>
          </div>
        </div>
      </section>

      <PieDePagina />
    </div>
  );
}

export default Inicio;
