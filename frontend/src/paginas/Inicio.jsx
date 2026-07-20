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
        <section className="relative overflow-hidden rounded-3xl bg-primary text-on-primary p-xl md:p-2xl mb-2xl">
          <div className="absolute inset-0 animar-brillo pointer-events-none" />
          <div className="relative z-10 max-w-2xl">
            <p className="font-label-sm text-label-sm uppercase tracking-widest text-on-primary/80 mb-sm">
              Panel de {usuario.estado}
            </p>
            <h1 className="font-display-lg text-display-lg leading-tight mb-md">
              Hola, {usuario.nombre}
            </h1>
            <p className="font-body-lg text-body-lg text-on-primary/85">
              Gestiona tu inventario, encuentra receptores compatibles y da seguimiento
              a tus donaciones desde un solo lugar.
            </p>
          </div>
        </section>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-lg mb-2xl">
          <AccionRapida
            a="/inventario"
            icono="inventory_2"
            titulo="Inventario"
            texto="Registra lotes, revisa el orden FEFO y atiende las alertas de vencimiento."
            color="text-primary bg-primary-container/20"
          />
          <AccionRapida
            a="/emparejamientos"
            icono="hub"
            titulo="Emparejamientos"
            texto="Busca receptores cercanos y gestiona confirmaciones y entregas."
            color="text-tertiary bg-tertiary-container/20"
          />
          <AccionRapida
            a="/reportes"
            icono="bar_chart"
            titulo="Reportes"
            texto="Genera reportes de donaciones, inventario, asignaciones y fiscal."
            color="text-primary bg-primary-container/20"
          />
          <AccionRapida
            a="/perfil"
            icono="person"
            titulo="Mi perfil"
            texto="Actualiza tus datos de contacto o gestiona tu cuenta."
            color="text-secondary bg-secondary-container/20"
          />
        </div>

        <section className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-xl">
          <h2 className="font-headline-md text-headline-md text-on-surface mb-lg">
            Datos de la cuenta
          </h2>
          <dl className="grid grid-cols-1 sm:grid-cols-3 gap-md">
            <div className="bg-surface-container-low rounded-xl p-md">
              <dt className="font-label-sm text-label-sm text-on-surface-variant">Nombre</dt>
              <dd className="font-body-md text-body-md text-on-surface">{usuario.nombre}</dd>
            </div>
            <div className="bg-surface-container-low rounded-xl p-md">
              <dt className="font-label-sm text-label-sm text-on-surface-variant">Correo</dt>
              <dd className="font-body-md text-body-md text-on-surface break-all">{usuario.email}</dd>
            </div>
            <div className="bg-surface-container-low rounded-xl p-md">
              <dt className="font-label-sm text-label-sm text-on-surface-variant">Estado</dt>
              <dd className="font-body-md text-body-md text-on-surface capitalize flex items-center gap-xs">
                <span className="w-2 h-2 rounded-full bg-primary-container inline-block" />
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
      <header className="sticky top-0 z-50 bg-surface/80 backdrop-blur-md border-b border-outline-variant/20">
        <nav className="max-w-6xl mx-auto h-16 px-margin-mobile md:px-margin-desktop flex items-center justify-between">
          <Marca />
          <div className="hidden md:flex items-center gap-lg font-body-md text-on-surface-variant">
            <a href="#problema" className="hover:text-primary transition-colors">El problema</a>
            <a href="#solucion" className="hover:text-primary transition-colors">Solución</a>
            <a href="#pasos" className="hover:text-primary transition-colors">Cómo funciona</a>
          </div>
          <div className="flex items-center gap-sm">
            <Link
              to="/login"
              className="px-md py-sm rounded-lg text-primary font-label-md text-label-md hover:bg-primary-container/10 transition-colors"
            >
              Iniciar sesión
            </Link>
            <Link
              to="/registro"
              className="px-lg py-sm rounded-lg bg-primary text-on-primary font-label-md text-label-md hover:shadow-lg transition-all"
            >
              Crear cuenta
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden bg-hero-glow">
        <div className="max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop py-2xl grid grid-cols-1 md:grid-cols-2 gap-2xl items-center">
          <div className="space-y-lg animar-aparecer">
            <div className="inline-flex items-center gap-sm bg-primary-container/20 text-on-primary-fixed-variant px-md py-1 rounded-full border border-primary/20">
              <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>verified</span>
              <span className="font-label-sm text-label-sm uppercase tracking-wider">Compromiso dominicano</span>
            </div>
            <h1 className="font-display-lg text-display-lg leading-tight">
              Alimentando la esperanza en la{" "}
              <span className="text-gradient">República Dominicana</span>
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant max-w-lg">
              Conectamos los excedentes de alimentos con quienes más los necesitan, con
              trazabilidad, optimización logística FEFO y cumplimiento legal.
            </p>
            <div className="flex flex-wrap gap-md pt-sm">
              <Link
                to="/registro"
                className="group px-xl py-md bg-primary text-on-primary rounded-xl font-label-md text-label-md hover:shadow-xl hover:scale-[1.02] transition-all flex items-center gap-sm"
              >
                Empezar ahora
                <span className="material-symbols-outlined group-hover:translate-x-1 transition-transform" style={{ fontSize: "20px" }}>
                  arrow_forward
                </span>
              </Link>
              <a
                href="#solucion"
                className="px-xl py-md border-2 border-tertiary text-tertiary rounded-xl font-label-md text-label-md hover:bg-tertiary/5 transition-all"
              >
                Saber más
              </a>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute -inset-4 bg-gradient-to-tr from-primary/20 to-secondary/20 blur-3xl opacity-60 rounded-full" />
            <div className="relative aspect-[4/5] max-w-md mx-auto rounded-3xl overflow-hidden shadow-2xl border border-white/30">
              <img src={imagenHero} alt="Voluntaria con una caja de alimentos donados" className="w-full h-full object-cover" />
            </div>
            <div className="absolute -bottom-5 -left-2 md:-left-5 glass-card p-md rounded-2xl shadow-xl flex items-center gap-md animar-flotar">
              <div className="w-12 h-12 bg-secondary rounded-full flex items-center justify-center text-on-primary">
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
              <div className="flex items-start gap-md p-md bg-surface-container rounded-xl">
                <span className="material-symbols-outlined text-error mt-1">warning</span>
                <div>
                  <h4 className="font-label-md text-label-md font-bold">Pérdida crítica</h4>
                  <p className="font-body-md text-body-md text-on-surface-variant">
                    Toneladas de alimentos frescos se pierden en la cadena de suministro.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-md p-md bg-surface-container rounded-xl">
                <span className="material-symbols-outlined text-primary mt-1">groups</span>
                <div>
                  <h4 className="font-label-md text-label-md font-bold">Hambre invisible</h4>
                  <p className="font-body-md text-body-md text-on-surface-variant">
                    Muchas comunidades enfrentan altas tasas de inseguridad alimentaria.
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div className="order-1 md:order-2 relative rounded-3xl overflow-hidden aspect-[4/3] shadow-xl">
            <img src={imagenHero} alt="Alimentos donados" className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-on-surface/80 to-transparent flex items-end p-lg">
              <p className="text-on-primary font-body-md italic leading-relaxed">
                «Cerca del 30% de los alimentos producidos terminan en desperdicio
                mientras miles sufren inseguridad alimentaria.»
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* La solución */}
      <section id="solucion" className="py-2xl">
        <div className="max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop">
          <div className="text-center max-w-2xl mx-auto mb-2xl">
            <h2 className="font-headline-lg text-headline-lg mb-md">Nuestra solución logística</h2>
            <p className="font-body-lg text-body-lg text-on-surface-variant">
              Transformamos la donación en una operación estratégica de alto impacto
              mediante tecnología.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
            {CARACTERISTICAS.map((c) => (
              <div
                key={c.titulo}
                className="hover-lift p-xl bg-surface-container-lowest rounded-3xl border border-outline-variant/40 group"
              >
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
      <section className="py-2xl bg-on-surface text-on-primary relative overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_50%_50%,_#22c55e_0%,_transparent_55%)]" />
        <div className="max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop relative z-10 grid grid-cols-1 md:grid-cols-3 gap-2xl text-center">
          {ESTADISTICAS.map((e) => (
            <div key={e.etiqueta} className="space-y-sm">
              <p className="font-display-lg text-display-lg text-primary-fixed-dim">{e.valor}</p>
              <p className="font-label-md text-label-md uppercase tracking-widest text-surface-variant">
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
            <h2 className="font-headline-lg text-headline-lg">Proceso de impacto</h2>
            <p className="font-body-lg text-body-lg text-on-surface-variant">
              Tres pasos para transformar excedentes en ayuda real.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-xl relative">
            {PASOS.map((p) => (
              <div key={p.n} className="relative space-y-md">
                <div className="w-14 h-14 bg-primary text-on-primary rounded-full flex items-center justify-center font-headline-md text-headline-md relative z-10">
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
        <div className="max-w-6xl mx-auto bg-primary rounded-[2.5rem] p-xl md:p-2xl text-center relative overflow-hidden shadow-2xl">
          <div className="absolute inset-0 animar-brillo pointer-events-none" />
          <div className="relative z-10 max-w-3xl mx-auto space-y-lg">
            <h2 className="font-display-lg text-display-lg text-on-primary">
              Únete a la red de impacto
            </h2>
            <p className="font-body-lg text-body-lg text-on-primary/85">
              Cada donación, por pequeña que sea, es un paso hacia una República
              Dominicana libre de hambre. Empieza hoy mismo.
            </p>
            <div className="pt-sm flex flex-wrap gap-md justify-center">
              <Link
                to="/registro"
                className="bg-secondary text-on-primary px-2xl py-lg rounded-2xl font-headline-md text-headline-md hover:scale-105 active:scale-95 transition-all shadow-xl"
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
