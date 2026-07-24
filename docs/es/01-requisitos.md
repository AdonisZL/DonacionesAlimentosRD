# 01 — Especificación de Requisitos / Requisitos

> Fuente original: [Descripcion.md](../../Descripcion.md). Este documento resume y estructura los requisitos.

## 1. Objetivos

### Objetivo General

Diseñar y desarrollar un sistema web para la gestión eficiente de donaciones de alimentos, que permita registrar, organizar y distribuir excedentes mediante algoritmos de optimización logística en cumplimiento con la normativa dominicana, para reducir el desperdicio y fortalecer la seguridad alimentaria.

### Objetivos Específicos

- **OE1**: Registrar y organizar donantes, receptores y bancos de alimentos en una base de datos centralizada.
- **OE2**: Implementar un módulo de inventario dinámico indexado por vida útil residual (FEFO).
- **OE3**: Emparejamiento semiautomático entre excedentes y demanda institucional mediante motor determinista (FEFO + PostGIS + restricciones + Google Maps API), asistido por IA (Gemini) para normalización y justificación, con validación humana obligatoria.Emparejamiento semiautomático (motor determinista FEFO + PostGIS + restricciones + Google MapApi) asistido por IA (Gemini) con validación humana obligatoria.
- **OE4**: Generar reportes de donaciones, inventario y distribución (transparencia y beneficios fiscales).
- **OE5**: Control de acceso (RBAC) y protección de datos (autenticación segura y gestión de roles).

## 2. Módulos del sistema


| # | Módulo                     | OE  | Requisitos     |
| - | --------------------------- | --- | -------------- |
| 1 | Registro y Autenticación   | OE1 | RF-01 … RF-08 |
| 2 | Inventario y Gestión FEFO  | OE2 | RF-09 … RF-16 |
| 3 | Emparejamiento Inteligente  | OE3 | RF-17 … RF-22 |
| 4 | Reportería                 | OE4 | RF-23 … RF-27 |
| 5 | Seguridad y Administración | OE5 | RF-28 … RF-32 |

## 3. Requisitos Funcionales (RF)

### Módulo 1 — Registro y Autenticación

- **RF-01** (Alta): **RF‑01 (Alta):** Registro de donantes en tres categorías: (a) **Formalizado**: RNC y Razón Social. (b) **Informal**: nombre del negocio y ubicación. (c) **Independiente**: Cédula o Pasaporte.Registro de donantes: (a) Formalizado (RNC, Razón Social) y (b) Especial/Agrícola (Cédula/Pasaporte). Ambos(Formalizado e independiente): correo, contraseña cifrada, dirección y coordenadas.
- **RF-02** (Alta): Registro de organizaciones receptoras (RNC, registro en Procuraduría, capacidad, población atendida).
- **RF-03** (Alta): Registro de bancos de alimentos (sedes, almacenamiento refrigerado, horarios).
- **RF-04** (Alta): Autenticación con correo/contraseña, JWT firmado, bcrypt coste ≥ 12.
- **RF-05** (Media): Recuperación de contraseña por correo (enlace válido 15 min).
- **RF-06** (Alta): Verificación de cuenta por correo antes de operar.
- **RF-07** (Media): Edición de perfil (contacto, dirección, geolocalización).
- **RF-08** (Media): Desactivación lógica de cuenta (conserva historial, Ley 11-92).

### Módulo 2 — Inventario y FEFO

- **RF-09** (Alta): Registro de lote (producto, categoría, cantidad, unidad, vencimiento, lote fabricante, almacenamiento).
- **RF-10** (Alta): Clasificación automática de perecibilidad (no perecedero, semi-perecedero, perecedero, congelado).
- **RF-11** (Alta): Cálculo de ventana `vencimiento − hoy` y validación de umbral mínimo.
- **RF-12** (Alta): Ordenamiento FEFO ascendente por fecha de vencimiento.
- **RF-13** (Alta): Alertas de vencimiento (≤ 3 días) en plataforma y correo.
- **RF-14** (Alta): Rechazo automático si `ventana ≤ 0`.
- **RF-15** (Media): Ajuste manual de inventario (solo banco) con motivo obligatorio.
- **RF-16** (Alta): Histórico inmutable de movimientos (bitácora).

### Módulo 3 — Emparejamiento

- **RF-17** (Alta): Búsqueda de receptores compatibles con PostGIS (radio configurable), complementada con Google Maps API (Distance Matrix) para calcular tiempos reales de llegada como criterio de desempate en el motor determinista.Búsqueda de receptores compatibles con PostGIS (radio configurable).
- **RF-18** (Alta): Justificación narrativa asistida por Gemini limitada a normalización semántica y generación de explicación textual (temperatura 0.0, sin alterar el resultado determinista).
- **RF-19** (Alta): Confirmación manual del emparejamiento (validación humana).
- **RF-20** (Media): Reasignación si el receptor rechaza o no retira a tiempo.
- **RF-21** (Alta): Notificación a donante y receptor al confirmar.
- **RF-22** (Baja): Retroalimentación (calificación 1–5 y comentario).

### Módulo 4 — Reportería

- **RF-23** (Alta): Reporte de donaciones por período (filtros: fecha, donante, categoría, estado).
- **RF-24** (Alta): Reporte de inventario actual (orden FEFO).
- **RF-25** (Alta): Reporte de asignaciones completadas (con evidencia).
- **RF-26** (Alta): Exportación a Google Sheets (API v4).
- **RF-27** (Alta): Reporte fiscal DGII en PDF inmutable firmado (Norma 04-2014, Art. 287 Ley 11-92).

### Módulo 5 — Seguridad y Administración

- **RF-28** (Alta): RBAC (Donante, Receptor, Banco, Administrador).
- **RF-29** (Alta): Auditoría (quién, qué, cuándo, IP).
- **RF-30** (Alta): Bloqueo por 5 intentos fallidos en 10 min.
- **RF-31** (Alta): Consentimiento de datos (Ley 172-13) antes de guardar.
- **RF-32** (Media): Panel administrativo (kg rescatados, tasa de efectividad, distribución por perecibilidad).

## 4. Reglas de Negocio (RN) — resumen

- **RN-01/02/03**: RNC obligatorio para donantes jurídicos; receptores con personería jurídica; un único rol por usuario/correo.
- **RN-04/05/06**: rechazo de lotes vencidos; ventana mínima por categoría (No perecedero 30–90, Semi 15–30, Perecedero 1–5, Congelado 30–60 días); prioridad FEFO.
- **RN-07/08/09**: cadena de frío; identificador de lote único e inmutable; merma con motivo + responsable.
- **RN-10/11/12/13/14**: radio inicial 25 km (máx. piloto 35 km, tope 75 km); no exceder capacidad del receptor; retiro máx. 48 h; no discriminación; entrega confirmada por el receptor.
- **RN-15/16/17**: conservación 10 años; anexo fiscal mensual (Norma 06-2018); reportes fiscales inmutables (rectificación explícita).
- **RN-18/19/20**: consentimiento previo (Ley 172-13); derechos ARCO en ≤ 15 días hábiles; RBAC con justificación registrada.

## 5. Requisitos No Funcionales (RNF) — métricas clave


| RNF    | Métrica                                                                                                                       |
| ------ | ------------------------------------------------------------------------------------------------------------------------------ |
| RNF-01 | 95% de GET ≤ 1.5 s (100 usuarios concurrentes)                                                                                |
| RNF-02 | Registro de lote ≤ 2 s                                                                                                        |
| RNF-03 | ≥ 500,000 lotes sin degradar > 10% el orden FEFO                                                                              |
| RNF-04 | Timeout IA ≤ 12 s; motor determinista independiente                                                                           |
| RNF-05 | Exportar ≤ 10,000 filas a Sheets en ≤ 10 s                                                                                   |
| RNF-06 | Disponibilidad ≥ 99.5% mensual                                                                                                |
| RNF-07 | RTO ≤ 4 h, RPO ≤ 24 h; respaldos diarios cifrados                                                                            |
| RNF-08 | Primera donación ≤ 5 min; SUS ≥ 70                                                                                          |
| RNF-09 | WCAG 2.1 AA en ≥ 90% de pantallas (axe-core)                                                                                  |
| RNF-10 | Español por defecto; preparado para inglés (i18n)                                                                            |
| RNF-11 | TLS 1.2+ (calificación A en SSL Labs)                                                                                         |
| RNF-12 | bcrypt coste ≥ 12; RNC/cédulas con AES-256 RBAC + cifrado de disco(TDE) + acceso controlado con RBAC de mínimo privilegio. |
| RNF-13 | Cero vulnerabilidades altas/críticas (OWASP ZAP)                                                                              |
| RNF-14 | Cumplimiento Ley 172-13 (consentimiento + ARCO)                                                                                |
| RNF-15 | Contraseña ≥ 10 caracteres (mayúscula, número, símbolo)                                                                   |
| RNF-16 | Cobertura pruebas unitarias ≥ 80%, integración ≥ 60%                                                                        |
| RNF-17 | Modularidad (DDD ligero); SonarQube categoría A                                                                               |
| RNF-18 | Multinavegador; responsive desde 360 px                                                                                        |

## 6. Alcance

**Incluye**: registro/auth, inventario FEFO, emparejamiento por reglas, reportes, seguridad/AES-256/RBAC.
**Excluye**: logística física/transporte, transacciones monetarias, integración con ERP externos, predicción de demanda (SARIMA/LSTM/Random Forest — solo análisis conceptual, no implementación).
