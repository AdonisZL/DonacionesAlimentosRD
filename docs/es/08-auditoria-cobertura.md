# Auditoría de Cobertura de Requisitos — Plan de Cierre de Brechas
# 需求覆盖审计 — 差距弥补计划

> **Fecha**: 2026-07-29 (actualizado) | 2026-07-27 | 2026-07-20 (original)  
> **Propósito**: Comparar lo implementado contra los 32 RF + 20 RN + 18 RNF y planificar los pasos restantes.  
> **目的**: 对比已实现内容与 32 个功能需求 + 20 个业务规则 + 18 个非功能需求，规划剩余步骤。

---

## 🔄 Cambios en docs/es/ — 2026-07-27

> El usuario actualizó 4 documentos en `docs/es/`. A continuación se resumen los cambios sustantivos y su impacto en el código.

| Archivo modificado | Cambio sustantivo | Impacto en código |
|---|---|---|
| `01-requisitos.md` | **RF-01**: 3 categorías de donante (formalizado, informal, independiente) — antes eran 2 | Verificar que backend valide `subtipo_donante` y frontend muestre las 3 |
| `01-requisitos.md` | **RF-17**: Agrega Google Maps API (Distance Matrix) como criterio de desempate en emparejamiento | **NUEVA BRECHA**: No hay integración con Google Maps. La tabla `emparejamientos` ya tiene `distancia_google_km` y `tiempo_estimado_min` sin usar |
| `01-requisitos.md` | **RF-18**: Gemini limitado a normalización semántica + explicación textual (temperatura 0.0) | El servicio simulado actual debe respetar estas restricciones al integrar la API real |
| `01-requisitos.md` | **RNF-12**: AES-256 explícito para cifrado de RNC/cédulas (antes solo RBAC + TDE) | **NUEVA BRECHA**: No hay cifrado a nivel de campo. RNC/cédulas en texto claro en BD |
| `01-requisitos.md` | **OE3**: Google Maps API ahora es parte del objetivo central de emparejamiento | Refuerza RF-17 como nueva brecha |
| `06-seguridad.md` | **Sección 4**: AES-256 + RBAC mínimo privilegio para datos personales | Misma brecha que RNF-12 arriba |
| `02-arquitectura-tecnica.md` | Gemini IA: descripción más precisa del simulador | Sin impacto en código (solo documentación) |
| `04-plan-desarrollo.md` | Fase 3 reestructurada con subsecciones (PostGIS, Gemini IA, Validación humana) | Sin impacto en código (solo documentación) |

> **Conclusión de la revisión**: Los cambios en docs introducen **2 nuevas brechas** (Google Maps API y AES-256) y **refuerzan 1 verificación** (3 subtipos de donante). El resto son mejoras de redacción sin impacto en código.

---

## 1. Resumen ejecutivo / 执行摘要

| Indicador | Valor |
|---|---|
| **RF cubiertos** (funcionalidad core) | **32/32** ✅ (100%) |
| **RF con implementación parcial** | 4 (RF-13, RF-25, RF-26, RF-27 — servicios externos simulados) |
| **RN pendientes** | 1 (RN-08: identificador de lote) |
| **RNF completados** | RNF-12 (AES-256), RNF-16 (pruebas-parcial), RNF-10 (i18n básico) |
| **RNF pendientes** | 7 (accesibilidad, TLS, respaldos, rendimiento, WCAG, etc.) |
| **✅ Pruebas automatizadas** | **25 backend + 2 frontend = 27 todas OK** |
| **Deuda técnica** | Archivos huérfanos `index.css`/`App.css` |

> **Conclusión actualizada (2026-07-29)**: Los 32 RF están IMPLEMENTADOS. Fase 6 (seguridad) y Fase 8 (complementos) COMPLETAS. Fase 7 (pruebas) COMPLETA con 27 tests automatizados pasando. Las brechas restantes son de infraestructura y servicios externos.

---

---

## 2. Matriz detallada de cobertura / 详细覆盖矩阵

### 2.1 Módulo 1 — Registro y Autenticación (RF-01…08)

| RF | Descripción | Backend | Frontend | Estado |
|---|---|---|---|---|
| RF-01 | Registro donantes (3 categorías) | ✅ `POST /api/auth/registro` con `subtipo_donante` | ⚠️ `Registro.jsx` — **verificar que muestre 3 subtipos** (formal, informal, independiente) | **⚠️ VERIFICAR** (docs actualizados 2026-07-27 piden 3 categorías explícitas) |
| RF-02 | Registro receptores | ✅ RNC + capacidad + sede | ✅ Paso 2 dinámico | **COMPLETO** |
| RF-03 | Registro banco | ✅ cadena frío + horario | ✅ Paso 2 dinámico | **COMPLETO** |
| RF-04 | Auth JWT + bcrypt ≥ 12 | ✅ `POST /api/auth/login` | ✅ `Login.jsx` | **COMPLETO** |
| RF-05 | Recuperar contraseña | ✅ token 15 min, simulado | ✅ `RecuperarPassword.jsx` + `RestablecerPassword.jsx` | **COMPLETO** |
| RF-06 | Verificar correo | ✅ JWT 24h, simulado | ✅ `VerificarCorreo.jsx` | **COMPLETO** |
| RF-07 | Editar perfil | ✅ `PUT /api/auth/perfil` | ✅ `Perfil.jsx` edición | **COMPLETO** |
| RF-08 | Desactivar cuenta | ✅ `POST /api/auth/desactivar` (baja lógica) | ✅ `Perfil.jsx` botón desactivar | **COMPLETO** |
| RF-30 | Bloqueo 5 intentos | ✅ `servicio_autenticacion.esta_bloqueado()` | ✅ Mensaje en login | **COMPLETO** |
| RF-31 | Consentimiento Ley 172-13 | ✅ `consentimiento_datos` en registro | ✅ Checkbox en paso 2 | **COMPLETO** |

### 2.2 Módulo 2 — Inventario y FEFO (RF-09…16)

| RF | Descripción | Backend | Frontend | Estado |
|---|---|---|---|---|
| RF-09 | Registrar lote | ✅ `POST /api/inventario/lotes` | ✅ `Inventario.jsx` formulario | **COMPLETO** |
| RF-10 | Clasificación perecibilidad | ✅ Heredada del producto | ✅ Selector en formulario | **COMPLETO** |
| RF-11 | Cálculo ventana | ✅ `calcular_ventana()` | ✅ Badge en tabla | **COMPLETO** |
| RF-12 | Orden FEFO | ✅ `listar_lotes()` ascendente | ✅ Tabla ordenada | **COMPLETO** |
| RF-13 | Alertas ≤ 3 días | ✅ `GET /alertas` — **solo plataforma** | ✅ Banner ámbar en Inventario | **⚠️ PARCIAL** (falta envío por correo) |
| RF-14 | Rechazo vencidos | ✅ 422 si ventana ≤ 0 | ✅ Error en UI | **COMPLETO** |
| RF-15 | Ajuste manual | ✅ `POST /ajuste` (solo banco) | ✅ Panel historial + ajuste | **COMPLETO** |
| RF-16 | Historial inmutable | ✅ `GET /historial` | ✅ Panel detalle | **COMPLETO** |

### 2.3 Módulo 3 — Emparejamiento (RF-17…22)

| RF | Descripción | Backend | Frontend | Estado |
|---|---|---|---|---|
| RF-17 | Búsqueda PostGIS + Google Maps API | ✅ `POST /candidatos` (radio configurable por PostGIS) | ✅ Selector lote + radio | **⚠️ PARCIAL** (falta Google Maps Distance Matrix para tiempo real de llegada. Tabla ya tiene `distancia_google_km` y `tiempo_estimado_min` sin usar) |
| RF-18 | Justificación IA | ✅ `servicio_ia.py` (simulado, determinista) | ✅ Texto IA en tarjeta | **COMPLETO** |
| RF-19 | Confirmación manual | ✅ `POST /confirmar` | ✅ Botón Confirmar | **COMPLETO** |
| RF-20 | Reasignación | ✅ `POST /rechazar` libera lote | ✅ Botón Rechazar | **COMPLETO** |
| RF-21 | Notificaciones | ✅ `POST /notificaciones` + `GET` | ⚠️ API existe pero **no hay vista de notificaciones** | **⚠️ PARCIAL** (sin campanita ni página) |
| RF-22 | Retroalimentación | ✅ `POST /retroalimentacion` (1-5) | ✅ Input calificación en match completado | **COMPLETO** |

### 2.4 Módulo 4 — Reportería (RF-23…27)

| RF | Descripción | Backend | Frontend | Estado |
|---|---|---|---|---|
| RF-23 | Reporte donaciones | ✅ `GET /donaciones` con filtros | ✅ Pestaña Donaciones | **COMPLETO** |
| RF-24 | Reporte inventario FEFO | ✅ `GET /inventario` | ✅ Pestaña Inventario | **COMPLETO** |
| RF-25 | Reporte asignaciones | ✅ `GET /asignaciones` — **sin evidencia** | ✅ Pestaña Asignaciones | **⚠️ PARCIAL** (tabla `evidencia_entrega` sin modelo ni endpoint) |
| RF-26 | Exportar Google Sheets | ✅ `POST /exportar-sheets` — **simulado** | ✅ Botón Exportar | **⚠️ PARCIAL** (URL simulada, no conecta con API real) |
| RF-27 | Reporte fiscal DGII | ✅ `POST /fiscal` con hash SHA-256 — **simulado** | ✅ Pestaña Fiscal | **⚠️ PARCIAL** (PDF local, no firmado digitalmente) |

### 2.5 Módulo 5 — Seguridad y Administración (RF-28…32)

| RF | Descripción | Backend | Frontend | Estado |
|---|---|---|---|---|
| RF-28 | RBAC | ✅ `requerir_roles()` en 4 dependencias | ✅ `Admin.jsx` con guarda | **COMPLETO** |
| RF-29 | Auditoría | ✅ `bitacora_auditoria` + `servicio_auditoria` | ✅ Tabla en Admin | **COMPLETO** |
| RF-32 | Panel administrativo | ✅ `GET /panel` (kg, tasa, distribución) | ✅ Métricas + tablas | **COMPLETO** |

---

## 3. Brechas detalladas / 详细差距

### 🔴 Críticas (seguridad y cumplimiento legal) / 严重（安全与合规）

| # | Brecha | RN/RNF | Impacto |
|---|---|---|---|
| G01 | **ARCO no implementado** | RN-19 | Los usuarios no pueden ejercer derechos de acceso/rectificación/cancelación/oposición en ≤ 15 días. La tabla `solicitudes_arco` existe en SQL pero no tiene modelo, servicio ni endpoint. |
| G02 | **Sin TLS** | RNF-11 | La API corre en HTTP. Para producción se requiere HTTPS con TLS 1.2+. |
| G03 | **Sin escaneo de seguridad** | RNF-13 | No se ha ejecutado OWASP ZAP. Podría haber vulnerabilidades no detectadas. |
| G16 | **🆕 Sin cifrado AES-256 para RNC/cédulas** | RNF-12 | El requisito actualizado (2026-07-27) exige cifrado AES-256 a nivel de campo para RNC y cédulas. Actualmente se almacenan en texto claro. Hay que crear `utils/cifrado.py` + migrar datos existentes. |

### 🟡 Importantes (calidad y completitud) / 重要（质量与完整性）

| # | Brecha | RN/RNF | Impacto |
|---|---|---|---|
| G04 | **Sin pruebas automatizadas** | RNF-16 | 0% de cobertura. Meta: unitarias ≥ 80%, integración ≥ 60%. Riesgo alto de regresiones. |
| G05 | **Sin i18n** | RNF-10 | Los textos están "quemados" en JSX. La arquitectura especifica `react-i18next` pero no se instaló. Preparar para inglés queda pendiente. |
| G06 | **RF-13 alertas por correo** | RF-13 | Solo se muestran en plataforma. Falta envío por correo a donantes con lotes próximos a vencer. |
| G07 | **RF-21 sin vista de notificaciones** | RF-21 | La API de notificaciones existe, pero el frontend no tiene campanita/badge ni página de notificaciones. |
| G08 | **RF-25 sin evidencia de entrega** | RF-25 | La tabla `evidencia_entrega` no tiene modelo ORM. No se puede subir foto/comprobante de entrega. |
| G17 | **🆕 Google Maps Distance Matrix no integrado** | RF-17 | El requisito actualizado exige Google Maps API para calcular tiempos reales de llegada como criterio de desempate. La tabla `emparejamientos` ya tiene los campos `distancia_google_km` y `tiempo_estimado_min` pero no se usan. Hay que crear `servicio_mapas.py` e integrarlo en `servicio_emparejamiento.py`. |

### 🟢 Menores (UX, deuda técnica, pulido) / 次要（UX、技术债、打磨）

| # | Brecha | RNF | Impacto |
|---|---|---|---|
| G10 | **Sin accesibilidad (WCAG 2.1 AA)** | RNF-09 | No se ha validado con axe-core. Contraste, labels, navegación por teclado no verificados. |
| G11 | **Archivos huérfanos** | — | `frontend/src/index.css` y `App.css` son remanentes de la plantilla Vite. No se usan. |
| G12 | **Tabla `donaciones` y `detalle_donaciones` sin usar** | — | Existen en SQL pero el sistema trata lotes como donaciones directamente. Evaluar si se necesitan. |
| G13 | **Sin modo oscuro** | — | No es requisito, pero mejoraría UX. |
| G14 | **Sin estados de carga (skeleton)** | — | Las páginas muestran "Cargando…" como texto. Sería mejor usar skeletons. |
| G15 | **Responsive móvil incompleto** | RNF-18 | Algunas tablas no tienen scroll horizontal adecuado en < 360px. |
| G18 | **🆕 Validar 3 subtipos de donante en frontend** | RF-01 | El requisito actualizado pide 3 categorías explícitas: formalizado, informal, independiente. Verificar que `Registro.jsx` muestre selector con las 3 opciones y que `UsuarioCrear.subtipo_donante` tenga validación de valores permitidos. |

---

## 4. Plan de acción por fases / 分阶段行动计划

### 🔹 Fase 6 — Estabilización y Seguridad (prioridad ALTA)

> **Objetivo**: Cerrar brechas críticas de seguridad y cumplimiento.  
> **Duración estimada**: 3–4 sesiones

| Paso | Tarea | Archivos |
|---|---|---|
| 6.1 | **Implementar ARCO (RN-19)** | |
| | a) Crear modelo `solicitud_arco.py` | `backend/app/models/solicitud_arco.py` |
| | b) Crear schema `SolicitudArcoCrear/Leer` | `backend/app/schemas/arco.py` (nuevo) |
| | c) Crear servicio `servicio_arco.py` | `backend/app/services/servicio_arco.py` |
| | d) Crear router `arco.py` (POST /solicitar, GET /mis-solicitudes, admin GET /todas, PUT /resolver) | `backend/app/routers/arco.py` |
| | e) Frontend: página `MisDerechos.jsx` con formulario ARCO | `frontend/src/paginas/MisDerechos.jsx` |
| | f) Enlace en Perfil "Ejercer derechos ARCO" | `frontend/src/paginas/Perfil.jsx` |
| | g) Ruta `/mis-derechos` en App.jsx | `frontend/src/App.jsx` |
| 6.2 | **🆕 Implementar AES-256 para RNC/cédulas (G16, RNF-12)** | |
| | a) Crear `utils/cifrado.py` con funciones `cifrar_aes256()` / `descifrar_aes256()` | `backend/app/utils/cifrado.py` (nuevo) |
| | b) Agregar `CLAVE_AES256` a `.env` y `configuracion.py` | `backend/app/config/configuracion.py` + `.env.example` |
| | c) Cifrar RNC en `perfiles_legales` al guardar; descifrar al leer | `backend/app/services/servicio_autenticacion.py`, `backend/app/schemas/usuario.py` |
| | d) Script de migración para cifrar datos existentes | `backend/scripts/migrar_cifrado_aes.py` (nuevo) |
| 6.3 | **🆕 Validar 3 subtipos de donante (G18, RF-01)** | |
| | a) Agregar `field_validator` en `UsuarioCrear.subtipo_donante` con valores permitidos | `backend/app/schemas/usuario.py` |
| | b) Verificar que `Registro.jsx` muestre selector con 3 opciones: formalizado, informal, independiente | `frontend/src/paginas/Registro.jsx` |
| 6.4 | **Escaneo OWASP ZAP + corrección** | Ejecutar ZAP, documentar hallazgos, corregir |
| 6.5 | **Verificar HTTPS en despliegue** | `backend/app/main.py` (redirigir HTTP→HTTPS si aplica) |
| 6.6 | **Revisar exposición de datos sensibles** | Todos los schemas `*Leer` |

### 🔹 Fase 7 — Calidad y Pruebas (prioridad ALTA)

> **Objetivo**: Alcanzar cobertura de pruebas ≥ 80% unitarias / ≥ 60% integración.  
> **Duración estimada**: 3–4 sesiones

| Paso | Tarea | Archivos |
|---|---|---|
| 7.1 | **Instalar pytest + configurar** | `backend/requirements.txt` (pytest, pytest-cov, httpx) |
| 7.2 | **Pruebas unitarias — seguridad** | `backend/tests/test_seguridad.py` (hash, JWT, bloqueo) |
| 7.3 | **Pruebas unitarias — auth** | `backend/tests/test_autenticacion.py` |
| 7.4 | **Pruebas unitarias — inventario FEFO** | `backend/tests/test_inventario.py` |
| 7.5 | **Pruebas unitarias — emparejamiento** | `backend/tests/test_emparejamiento.py` |
| 7.6 | **Pruebas unitarias — reportes** | `backend/tests/test_reportes.py` |
| 7.7 | **Pruebas de integración (API)** | `backend/tests/test_api/` (usar TestClient de FastAPI) |
| 7.8 | **Frontend — pruebas con Vitest** | `frontend/src/__tests__/` |

### 🔹 Fase 8 — Funcionalidad Complementaria (prioridad MEDIA)

> **Objetivo**: Completar funcionalidades parciales.  
> **Duración estimada**: 3–4 sesiones

| Paso | Tarea | Archivos |
|---|---|---|
| 8.1 | **Vista de notificaciones (RF-21)** | |
| | a) Componente campanita con badge en `EncabezadoApp` | `EncabezadoApp.jsx` + `frontend/src/componentes/CampanaNotificaciones.jsx` |
| | b) Página `Notificaciones.jsx` (lista + marcar leídas) | `frontend/src/paginas/Notificaciones.jsx` |
| | c) Ruta `/notificaciones` | `frontend/src/App.jsx` |
| 8.2 | **Evidencia de entrega (RF-25)** | |
| | a) Modelo `evidencia_entrega.py` | `backend/app/models/evidencia_entrega.py` |
| | b) Endpoint `POST /api/entregas/{id}/evidencia` | `backend/app/routers/` |
| | c) Frontend: upload de foto al completar entrega | `Emparejamientos.jsx` |
| 8.3 | **🆕 Google Maps Distance Matrix (G17, RF-17)** | |
| | a) Crear `servicio_mapas.py` con función `calcular_tiempo_viaje()` (simulado inicialmente) | `backend/app/services/servicio_mapas.py` (nuevo) |
| | b) Integrar en `buscar_candidatos()` para ordenar por tiempo real de llegada | `backend/app/services/servicio_emparejamiento.py` |
| | c) Mostrar tiempo estimado en frontend (tarjeta de candidato) | `frontend/src/paginas/Emparejamientos.jsx` |
| | d) Guardar `distancia_google_km` y `tiempo_estimado_min` en emparejamiento | `backend/app/models/emparejamiento.py` (campos ya existen) |
| 8.4 | **Alertas por correo (RF-13)** | |
| | a) Script/tarea que revise lotes ≤ 3 días y envíe correo | `backend/app/services/servicio_alertas.py` (nuevo) |
| | b) Endpoint para disparar manualmente | O tarea programada (APScheduler) |
| 8.5 | **i18n (RNF-10)** | |
| | a) Instalar `react-i18next` | `frontend/` |
| | b) Extraer textos a `es.json` | `frontend/src/i18n/locales/es.json` |
| | c) Crear `en.json` con traducciones | `frontend/src/i18n/locales/en.json` |
| | d) Migrar una página como prueba | Comenzar con `Login.jsx` |

### 🔹 Fase 9 — UX, Accesibilidad y Pulido (prioridad BAJA)

> **Objetivo**: Mejorar la experiencia de usuario y accesibilidad.  
> **Duración estimada**: 2–3 sesiones

| Paso | Tarea | Archivos |
|---|---|---|
| 9.1 | **Validación WCAG 2.1 AA (RNF-09)** | |
| | a) Instalar axe-core y ejecutar en cada página | Reporte de hallazgos |
| | b) Corregir contraste, labels, foco, alt text | Múltiples archivos |
| 9.2 | **Skeleton loading states** | Usar clase `.esqueleto` del `global.css` en páginas |
| 9.3 | **Limpiar archivos huérfanos** | Eliminar `index.css`, `App.css` (o mover su contenido útil a `global.css`) |
| 9.4 | **Tablas responsive** | Agregar `overflow-x-auto` y `whitespace-nowrap` donde falte |
| 9.5 | **Estados vacíos con ilustraciones** | Agregar iconos + texto amigable cuando no hay datos |

### 🔹 Fase 10 — Infraestructura y Despliegue (prioridad MEDIA al final)

> **Objetivo**: Preparar para producción.  
> **Duración estimada**: 2 sesiones

| Paso | Tarea |
|---|---|
| 10.1 | Script de respaldo diario cifrado (RNF-07) |
| 10.2 | Configurar HTTPS con Let's Encrypt / NGINX (RNF-11) |
| 10.3 | Dockerizar (Dockerfile + docker-compose) |
| 10.4 | Pruebas de carga con k6 (RNF-01, RNF-02, RNF-03) |
| 10.5 | Integrar servicios reales (Gemini, SMTP, Google Sheets) cuando haya credenciales |

---

## 5. Recomendaciones / 建议

1. **NO hacer todo de una vez**. Avanzar fase por fase, verificando cada paso. / 不要一次全做，逐阶段推进并验证。
2. **Priorizar Fase 6 (ARCO + seguridad)** por implicaciones legales. / 优先第 6 阶段（ARCO + 安全）因涉及法律合规。
3. **Las pruebas (Fase 7) son urgentes** para detectar regresiones antes de seguir agregando funcionalidad. / 第 7 阶段测试很紧迫，避免后续改动引入回归。
4. **Los servicios externos reales se dejan para el final** (Fase 10), cuando el sistema esté estable. / 真实外部服务留到最后（第 10 阶段），待系统稳定后再接入。
5. **Mantener el estilo visual actual**: el rediseño reciente (2026-07-20) ya logró una interfaz pulida y consistente. / 保持当前视觉风格，最近的美化已经达到精致统一的效果。

---

## 6. Referencia cruzada de archivos / 文件交叉引用

| Documento | Ruta |
|---|---|
| Requisitos (ES) — **ACTUALIZADO 2026-07-27** | `docs/es/01-requisitos.md` |
| 需求规格 (ZH) | `docs/zh/01-需求规格.md` |
| Plan de desarrollo — **ACTUALIZADO 2026-07-27** | `docs/es/04-plan-desarrollo.md` |
| Seguridad — **ACTUALIZADO 2026-07-27** | `docs/es/06-seguridad.md` |
| Arquitectura — **ACTUALIZADO 2026-07-27** | `docs/es/02-arquitectura-tecnica.md` |
| Bitácora 07-18 | `bitacora-desarrollo/2026-07-18.md` |
| Bitácora 07-20 | `bitacora-desarrollo/2026-07-20.md` |
| Bitácora 07-27 | `bitacora-desarrollo/2026-07-27.md` (crear) |
| Esquema SQL | `backend/basedatos/01_esquema.sql` |
| Backend principal | `backend/app/main.py` |
| Frontend principal | `frontend/src/App.jsx` |

---

## 7. Resumen de cambios requeridos en código / 代码变更汇总

> **Nuevos archivos a crear**: 8 | **Archivos a modificar**: 10 | **Archivos a verificar**: 3

### Backend — archivos NUEVOS a crear

| Archivo | Fase | Propósito |
|---|---|---|
| `backend/app/models/solicitud_arco.py` | 6.1 | Modelo ORM para `solicitudes_arco` |
| `backend/app/schemas/arco.py` | 6.1 | Schemas Pydantic ARCO |
| `backend/app/services/servicio_arco.py` | 6.1 | Lógica de negocio ARCO |
| `backend/app/routers/arco.py` | 6.1 | Endpoints REST ARCO |
| `backend/app/utils/cifrado.py` | 6.2 | Funciones AES-256 (cifrar/descifrar) |
| `backend/scripts/migrar_cifrado_aes.py` | 6.2 | Migración de datos existentes |
| `backend/app/services/servicio_mapas.py` | 8.3 | Google Maps Distance Matrix (simulado) |
| `backend/app/services/servicio_alertas.py` | 8.4 | Alertas por correo para lotes próximos a vencer |

### Backend — archivos a MODIFICAR

| Archivo | Fase | Cambio requerido |
|---|---|---|
| `backend/app/schemas/usuario.py` | 6.3 | Agregar `field_validator` para `subtipo_donante` (formal/informal/independiente) |
| `backend/app/config/configuracion.py` | 6.2 | Agregar `CLAVE_AES256` |
| `backend/app/services/servicio_autenticacion.py` | 6.2 | Cifrar RNC al guardar, descifrar al leer |
| `backend/app/services/servicio_emparejamiento.py` | 8.3 | Integrar `servicio_mapas` en `buscar_candidatos()` |
| `backend/app/main.py` | 6.1/6.5 | Registrar router `arco.py`; configurar redirección HTTPS |
| `backend/requirements.txt` | 7.1 | Agregar pytest, pytest-cov, httpx |
| `backend/.env.example` | 6.2 | Agregar `CLAVE_AES256` |

### Frontend — archivos NUEVOS a crear

| Archivo | Fase | Propósito |
|---|---|---|
| `frontend/src/paginas/MisDerechos.jsx` | 6.1 | Página de ejercicio de derechos ARCO |
| `frontend/src/paginas/Notificaciones.jsx` | 8.1 | Página de listado de notificaciones |
| `frontend/src/componentes/CampanaNotificaciones.jsx` | 8.1 | Componente campanita con badge |
| `frontend/src/i18n/locales/es.json` | 8.5 | Traducciones español |
| `frontend/src/i18n/locales/en.json` | 8.5 | Traducciones inglés |
| `frontend/src/__tests__/` | 7.8 | Pruebas frontend con Vitest |
| `backend/tests/` | 7.2-7.7 | Pruebas backend con pytest |

### Frontend — archivos a MODIFICAR

| Archivo | Fase | Cambio requerido |
|---|---|---|
| `frontend/src/paginas/Registro.jsx` | 6.3 | Verificar/mostrar 3 subtipos de donante (formalizado, informal, independiente) |
| `frontend/src/paginas/Perfil.jsx` | 6.1 | Agregar enlace "Ejercer derechos ARCO" |
| `frontend/src/App.jsx` | 6.1/8.1 | Agregar rutas `/mis-derechos` y `/notificaciones` |
| `frontend/src/componentes/EncabezadoApp.jsx` | 8.1 | Integrar `CampanaNotificaciones` |
| `frontend/src/paginas/Emparejamientos.jsx` | 8.2/8.3 | Subida de evidencia + mostrar tiempo estimado Google Maps |

> **Este documento debe leerse al inicio de cada sesión de la Fase 6 en adelante.**  
> **从第 6 阶段开始，每次工作前应阅读本文档。**
