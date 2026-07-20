# 06 — Seguridad

Basado en OWASP Top 10, Ley 172-13 (protección de datos) y Ley 11-92 (tributaria). Objetivo: cero vulnerabilidades altas/críticas.

## 1. Autenticación y contraseñas
- Hashing **bcrypt con coste ≥ 12** (RF-04, RNF-12). Nunca guardar contraseñas en texto plano.
- Política de contraseña (RNF-15): mínimo 10 caracteres, con mayúscula, número y símbolo.
- **JWT** firmado con expiración configurable; secreto en `.env`.
- Verificación de correo obligatoria antes de operar (RF-06).
- Recuperación de contraseña: token de un solo uso, expira en 15 min (RF-05).

## 2. Control de acceso (RBAC) — RF-28 / RN-20
- Roles: Donante, Receptor, Banco de Alimentos, Administrador.
- Restringir endpoints y vistas según rol.
- El administrador solo ve datos personales completos con justificación registrada en la bitácora.

## 3. Protección contra ataques (OWASP) — RNF-13
- **Inyección SQL**: usar SIEMPRE el ORM (SQLAlchemy) con consultas parametrizadas; nunca concatenar SQL.
- **XSS**: React escapa por defecto; no usar `dangerouslySetInnerHTML`.
- **CSRF/CORS**: configurar CORS restringido a los orígenes permitidos.
- **Fuerza bruta** (RF-30): bloquear la cuenta tras 5 intentos fallidos en 10 min.
- **Exposición de datos**: no devolver hashes ni campos sensibles en las respuestas de la API.
- Validación de entrada con Pydantic en todos los endpoints.

## 4. Datos personales (Ley 172-13) — RF-31 / RN-18 / RN-19
- Registrar **consentimiento explícito** antes de guardar datos (tabla `consentimiento_datos`).
- Atender derechos **ARCO** (acceso, rectificación, cancelación, oposición) en ≤ 15 días hábiles (tabla `solicitudes_arco`).
- RNC y cédulas: en texto claro pero protegidos por RBAC + cifrado de disco (TDE); no se exponen sin autorización.

## 5. Auditoría — RF-29 / RN-08
- Registrar en `bitacora_auditoria`: quién (id_usuario), qué (acción), cuándo (timestamp), desde dónde (IP).
- Historial de lotes inmutable (`historial_estado_lote`); todo cambio genera un nuevo movimiento.

## 6. Transporte y almacenamiento
- **TLS 1.2+** en todo el tráfico (RNF-11).
- Cifrado en reposo a nivel de disco (infraestructura de BD).
- Secretos SIEMPRE en `.env` (nunca en el código ni en el repositorio). Proveer `.env.example` sin valores reales.

## 7. Retención y respaldo
- Conservar transacciones y donaciones **10 años** (RN-15, Ley 11-92).
- Respaldos diarios cifrados; RTO ≤ 4 h, RPO ≤ 24 h (RNF-07).
- Reportes fiscales **inmutables** tras el cierre; corrección solo por reporte rectificativo (RN-16/17).

## 8. Checklist antes de cada entrega
- [ ] Sin secretos en el código ni en commits.
- [ ] Endpoints protegidos por rol.
- [ ] Validación de entrada en todos los formularios y endpoints.
- [ ] Contraseñas con bcrypt; JWT con expiración.
- [ ] Consentimiento y auditoría funcionando.
- [ ] Escaneo OWASP ZAP sin hallazgos altos/críticos.
