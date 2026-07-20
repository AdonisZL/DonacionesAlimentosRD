# 05 — Estándares de Código

**Regla principal: el código se escribe en ESPAÑOL.** Palabras clave del lenguaje y nombres de librerías permanecen en inglés (no se traducen).

## 1. Idioma del código
- **Español**: variables, funciones, clases, métodos, rutas de API, nombres de archivos/carpetas propios, mensajes de commit, comentarios.
- **Inglés (se mantiene)**: sintaxis del lenguaje, librerías y sus APIs (`FastAPI`, `useState`, `select`, etc.).
- Comentarios en español; se permite una nota breve en chino cuando ayude al usuario.

## 2. Nomenclatura

### Backend (Python — PEP 8)
- Variables y funciones: `snake_case` en español → `crear_usuario`, `calcular_ventana_donacion`, `fecha_vencimiento`.
- Clases: `PascalCase` en español → `LoteInventario`, `ServicioEmparejamiento`.
- Constantes: `MAYUSCULAS_CON_GUION_BAJO` → `RADIO_MAXIMO_KM`.
- Archivos/módulos: `snake_case` → `servicio_inventario.py`, `router_usuarios.py`.
- Rutas de API en español y plural → `/api/usuarios`, `/api/lotes`, `/api/emparejamientos`.

### Frontend (React — JavaScript)
- Componentes: `PascalCase` en español → `FormularioRegistro.jsx`, `TablaInventario.jsx`.
- Variables/funciones: `camelCase` en español → `usuarioActual`, `cargarLotes()`.
- Hooks propios: `useSesion`, `useInventario`.
- Textos visibles al usuario: SIEMPRE vía i18n (no texto fijo en el JSX).

## 3. Estructura y estilo
- **Backend**: separar responsabilidades → `routers` (HTTP) llaman a `services` (lógica) que usan `models` (datos). `schemas` valida entrada/salida.
- Tipar con anotaciones de Python y Pydantic. Evitar lógica en los routers.
- **Frontend**: componentes pequeños y reutilizables; llamadas HTTP centralizadas en `src/api/`.
- Sin credenciales ni URLs secretas en el código: usar `.env` (backend) y variables de Vite (`import.meta.env`, frontend).

## 4. Manejo de errores
- Backend: devolver códigos HTTP correctos (400, 401, 403, 404, 409, 422, 500) con mensajes claros en español.
- Validar en los límites del sistema (entrada de la API, formularios). No sobre-validar internamente.

## 5. Commits (convencional, en español)
Formato: `tipo: descripción breve`.
- `feat: registrar donante formalizado`
- `fix: corregir cálculo de ventana FEFO`
- `docs: actualizar guía de diseño`
- `test: pruebas de autenticación`
- `refactor:`, `chore:`, `style:`.

## 6. Pruebas
- Backend: `pytest`. Frontend: `Vitest`.
- Metas (RNF-16): cobertura unitaria ≥ 80%, integración ≥ 60%.
- Nombrar pruebas en español: `test_rechaza_lote_vencido`.

## 7. Calidad
- Formateo backend: `black` + `isort`. Lint: `ruff`/`flake8`.
- Lint frontend: `oxlint` (ya presente).
- Modularidad (DDD ligero), bajo acoplamiento (RNF-17).
