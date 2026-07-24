# 04 — Plan de Desarrollo (por fases)

Principio: **avance por fases, en pasos pequeños y verificables**. No pasar a la siguiente fase sin validar la actual. Servicios externos **simulados** hasta tener credenciales.

## Fase 0 — Cimientos (esqueleto + base de datos)

**Meta**: frontend, backend y base de datos conectados.

- Verificar PostgreSQL + PostGIS.
- Crear base de datos y ejecutar el script SQL (22 tablas).
- Insertar datos semilla: `roles` (donante, receptor, banco_alimentos, administrador), `categorias_perecibilidad` (ventanas RN-05), `categorias_alimentos`.
- Backend: `requirements.txt`, conexión a BD, `config` con `.env`, endpoint de prueba (leer `roles`).
- Frontend: limpiar plantilla, instalar router/axios, página inicial que consuma el backend.
- **Verificación**: la página muestra datos leídos de la base de datos.

## Fase 1 — OE1 Registro y Autenticación (RF-01…08)

- Modelos y esquemas de `usuarios`, `roles`, `perfiles_legales`, `direcciones_sedes`.
- Registro (donante formal/especial, receptor, banco), hashing bcrypt ≥ 12.
- Login con JWT; verificación de correo (simulada); recuperación de contraseña (token 15 min, simulado).
- Consentimiento Ley 172-13 (RF-31) en el registro.
- Frontend: páginas Registro, Login, Perfil; guardado de sesión.
- **Verificación**: crear cuenta, iniciar sesión, editar perfil.

## Fase 2 — OE2 Inventario y FEFO (RF-09…16)

- Modelos `productos`, `lotes_inventario`, `mermas`, `historial_estado_lote`.
- Registro de lote, clasificación de perecibilidad, cálculo de ventana, rechazo si ventana ≤ 0.
- Vista de inventario ordenada FEFO; alertas ≤ 3 días; ajuste manual con motivo (banco).
- **Verificación**: registrar lotes y ver orden FEFO + alertas.

## Fase 3 — OE3 Emparejamiento (RF-17…22)

- **PostGIS**: búsqueda de receptores por radio configurable, aplicando reglas de capacidad y cadena de frío.Consulta PostGIS por radio configurable; reglas de capacidad y cadena de frío.
- **Gemini IA**: justificación narrativa simulada, sin alterar el cálculo determinista.
- **Validación humana**: confirmación manual del emparejamiento, con posibilidad de reasignación y notificaciones automáticas.
- ****Verificación**: el sistema sugiere, el operador confirma.Verificación**: sugerir emparejamiento, confirmarlo manualmente.

## Fase 4 — OE4 Reportería (RF-23…27)

- Reportes de donaciones/inventario/asignaciones con filtros.
- Exportación a Google Sheets y PDF DGII **simuladas** (archivo local).
- **Verificación**: generar y descargar reportes.

## Fase 5 — OE5 Seguridad y Administración (RF-28…32)

- RBAC en endpoints y vistas; auditoría (bitacora_auditoria); bloqueo por intentos fallidos.
- Gestión de consentimiento y solicitudes ARCO; panel administrativo (KPIs).
- **Verificación**: permisos por rol, auditoría registrada, panel funcional.

## Fases posteriores (fuera del MVP)

- Integraciones reales (Gemini, Sheets, correo SMTP, mapa Leaflet).
- Pruebas de carga (k6/JMeter), auditoría OWASP ZAP, cobertura de pruebas objetivo.

## Estado actual

- [X]  Documentación y estándares creados.
- [ ]  **Fase 0 — siguiente**.
