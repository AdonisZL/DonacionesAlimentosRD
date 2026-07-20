// Pie de página / 页脚

import { Link } from "react-router-dom";

function PieDePagina() {
  return (
    <footer className="bg-gradient-to-br from-on-surface to-[#15273d] text-surface-bright">
      <div className="max-w-6xl mx-auto px-margin-mobile md:px-margin-desktop py-2xl flex flex-col gap-xl">
        <div className="flex flex-col md:flex-row justify-between gap-xl border-b border-white/10 pb-xl">
          <div className="space-y-sm max-w-sm">
            <div className="flex items-center gap-sm">
              <span
                className="material-symbols-outlined text-primary-fixed-dim bg-white/10 p-1.5 rounded-xl"
                style={{ fontVariationSettings: "'FILL' 1", fontSize: "24px" }}
              >
                volunteer_activism
              </span>
              <span className="font-headline-md text-headline-md font-bold text-primary-fixed-dim">
                DonacionesRD
              </span>
            </div>
            <p className="font-body-md text-body-md text-surface-variant/70 leading-relaxed">
              Registramos, organizamos y distribuimos excedentes de alimentos con
              trazabilidad, optimización logística (FEFO) y cumplimiento legal en la
              República Dominicana.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-xl">
            <div className="space-y-sm">
              <p className="font-label-sm text-label-sm uppercase tracking-widest text-surface-variant/50 font-semibold">
                Plataforma
              </p>
              <ul className="space-y-xs font-body-md text-body-md text-surface-variant/70">
                <li>
                  <Link to="/inventario" className="hover:text-primary-fixed-dim transition-colors">
                    Inventario FEFO
                  </Link>
                </li>
                <li>
                  <Link to="/emparejamientos" className="hover:text-primary-fixed-dim transition-colors">
                    Emparejamientos
                  </Link>
                </li>
                <li>
                  <Link to="/registro" className="hover:text-primary-fixed-dim transition-colors">
                    Crear cuenta
                  </Link>
                </li>
              </ul>
            </div>
            <div className="space-y-sm">
              <p className="font-label-sm text-label-sm uppercase tracking-widest text-surface-variant/50 font-semibold">
                Legal
              </p>
              <ul className="space-y-xs font-body-md text-body-md text-surface-variant/70">
                <li>Ley 172-13 (datos)</li>
                <li>Norma DGII 06-2018</li>
                <li>Cadena de frío</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center gap-md">
          <p className="font-body-md text-label-sm text-surface-variant/50">
            © 2026 DonacionesRD · República Dominicana. Proyecto de tesis.
          </p>
          <div className="flex gap-md text-surface-variant/60">
            <span className="material-symbols-outlined hover:text-primary-fixed-dim transition-colors cursor-pointer">eco</span>
            <span className="material-symbols-outlined hover:text-primary-fixed-dim transition-colors cursor-pointer">public</span>
            <span className="material-symbols-outlined hover:text-primary-fixed-dim transition-colors cursor-pointer">favorite</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default PieDePagina;
