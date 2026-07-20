// Marca del proyecto / 项目品牌
// Logo + nombre. Con `claro` para fondos oscuros.

export function Marca({ claro = false }) {
  const colorIcono = claro ? "text-primary-fixed-dim" : "text-primary";
  const colorTexto = claro ? "text-surface-bright" : "text-on-tertiary-container";
  return (
    <div className="flex items-center gap-sm">
      <span
        className={`material-symbols-outlined ${colorIcono}`}
        style={{ fontVariationSettings: "'FILL' 1", fontSize: "32px" }}
      >
        volunteer_activism
      </span>
      <span className={`font-headline-md text-headline-md font-bold ${colorTexto}`}>
        DonacionesRD
      </span>
    </div>
  );
}

export default Marca;
