# 03 — Guía de Diseño (UI/UX)

Diseño **simple e intuitivo**. Español por defecto. Responsive desde 360 px. Accesibilidad WCAG 2.1 AA.

## 1. Paleta de colores

| Rol | Color | HEX sugerido | Uso |
|---|---|---|---|
| Primario (Verde) | Verde | `#2E7D32` / claro `#43A047` | Acciones principales, marca, éxito |
| Secundario (Amarillo/Naranja) | Ámbar/Naranja | `#F9A825` / `#FB8C00` | Alertas, destacados, avisos de vencimiento |
| Fondo base (Blanco/Gris) | Blanco/Gris | `#FFFFFF` / `#F5F5F5` / `#E0E0E0` | Fondos, tarjetas, bordes |
| Control (Azul oscuro) | Azul oscuro | `#0D47A1` / `#1A237E` | Enlaces, controles, detalles |
| Texto | Gris muy oscuro | `#212121` / secundario `#616161` | Legibilidad |
| Estados | Éxito `#2E7D32` · Aviso `#F9A825` · Error `#C62828` · Info `#0D47A1` | | Retroalimentación |

### Variables CSS (referencia para `src/styles/`)
```css
:root {
  --color-primario: #2E7D32;
  --color-primario-claro: #43A047;
  --color-secundario: #F9A825;
  --color-secundario-alt: #FB8C00;
  --color-fondo: #FFFFFF;
  --color-fondo-gris: #F5F5F5;
  --color-borde: #E0E0E0;
  --color-control: #0D47A1;
  --color-texto: #212121;
  --color-texto-suave: #616161;
  --color-exito: #2E7D32;
  --color-aviso: #F9A825;
  --color-error: #C62828;
  --radio-borde: 8px;
  --espacio: 8px;
  --sombra: 0 1px 3px rgba(0,0,0,.12);
}
```

## 2. Tipografía y espaciado
- Fuente del sistema (sans-serif): legible y rápida. Tamaño base 16 px.
- Escala de espaciado en múltiplos de 8 px.
- Bordes redondeados 8 px; sombras suaves para tarjetas.

## 3. Componentes base
- **Botones**: primario (verde relleno), secundario (borde), peligro (rojo). Estados hover/focus visibles.
- **Formularios**: etiquetas claras en español, mensajes de error debajo del campo, validación en tiempo real.
- **Tablas**: para inventario FEFO, resaltar en ámbar los lotes próximos a vencer (≤ 3 días).
- **Alertas/Notificaciones**: color según estado; ícono + texto.
- **Tarjetas (cards)**: para resúmenes del panel (kg rescatados, tasa de efectividad).

## 4. Responsive
- Mobile-first desde 360 px.
- Puntos de quiebre: móvil < 600, tablet 600–1024, escritorio > 1024.
- Menú lateral colapsable en móvil.

## 5. Accesibilidad (WCAG 2.1 AA)
- Contraste de texto ≥ 4.5:1.
- Todos los campos con `<label>`; navegación por teclado; foco visible.
- Imágenes con `alt`; íconos decorativos con `aria-hidden`.
- Validar con **axe-core** (meta ≥ 90% de pantallas).

## 6. Idioma (i18n)
- Español por defecto; textos gestionados con `react-i18next` (nada de texto "quemado" en el JSX).
- Estructura preparada para inglés (claves de traducción en `src/i18n/`).

## 7. Iconografía
- Set consistente y ligero (p. ej. lucide-react o SVG propios).
- Íconos semánticos: donación, inventario, alerta de vencimiento, mapa, reporte.
