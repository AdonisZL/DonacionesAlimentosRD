# 📖 Diccionario de Datos — DonacionesAlimentosRD

> **Base de datos**: PostgreSQL + PostGIS  
> **Fecha de elaboración**: 2026-07-31  
> **Versión**: 1.0  
> **Idioma**: Español  

---

## Tabla de Contenidos

1. [Visión General](#1-visión-general)
2. [Tablas del Sistema](#2-tablas-del-sistema)
   - [roles](#21-roles)
   - [usuarios](#22-usuarios)
   - [direcciones_sedes](#23-direcciones_sedes)
   - [categorias_alimentos](#24-categorias_alimentos)
   - [categorias_perecibilidad](#25-categorias_perecibilidad)
   - [productos](#26-productos)
   - [lotes_inventario](#27-lotes_inventario)
   - [mermas](#28-mermas)
   - [emparejamientos](#29-emparejamientos)
   - [ia_ejecuciones](#210-ia_ejecuciones)
   - [entregas_transacciones](#211-entregas_transacciones)
   - [evidencia_entrega](#212-evidencia_entrega)
   - [perfiles_legales](#213-perfiles_legales)
   - [donaciones](#214-donaciones)
   - [detalle_donaciones](#215-detalle_donaciones)
   - [reportes_consolidados](#216-reportes_consolidados)
   - [notificaciones](#217-notificaciones)
   - [historial_estado_lote](#218-historial_estado_lote)
   - [bitacora_auditoria](#219-bitacora_auditoria)
   - [consentimiento_datos](#220-consentimiento_datos)
   - [solicitudes_arco](#221-solicitudes_arco)
   - [retroalimentacion](#222-retroalimentacion)
   - [tokens_recuperacion_password](#223-tokens_recuperacion_password)
3. [Diagrama de Relaciones](#3-diagrama-de-relaciones)
4. [Reglas de Negocio Referenciadas](#4-reglas-de-negocio-referenciadas)

---

## 1. Visión General

El sistema **DonacionesAlimentosRD** gestiona la cadena de donación de alimentos en República Dominicana. La base de datos está compuesta por **23 tablas** que cubren los siguientes dominios:

| Dominio | Tablas |
|---|---|
| **Usuarios y roles** | `roles`, `usuarios`, `perfiles_legales`, `consentimiento_datos`, `solicitudes_arco` |
| **Ubicaciones** | `direcciones_sedes` |
| **Catálogos** | `categorias_alimentos`, `categorias_perecibilidad`, `productos` |
| **Inventario** | `lotes_inventario`, `historial_estado_lote`, `mermas` |
| **Logística** | `emparejamientos`, `entregas_transacciones`, `evidencia_entrega`, `retroalimentacion` |
| **Donaciones** | `donaciones`, `detalle_donaciones` |
| **IA** | `ia_ejecuciones` |
| **Reportes** | `reportes_consolidados` |
| **Comunicación** | `notificaciones` |
| **Seguridad** | `tokens_recuperacion_password` |
| **Auditoría** | `bitacora_auditoria` |

### Tipos de datos frecuentes

| Tipo SQL | Descripción |
|---|---|
| `UUID` | Identificador único universal generado con `uuid_generate_v4()` |
| `SERIAL` / `BIGSERIAL` | Entero auto-incremental |
| `VARCHAR(N)` | Texto de longitud variable, máximo N caracteres |
| `TEXT` | Texto de longitud ilimitada |
| `BOOLEAN` | Verdadero / falso |
| `SMALLINT` | Entero pequeño (-32,768 a 32,767) |
| `INT` | Entero estándar |
| `NUMERIC(P,S)` | Número decimal con precisión P y escala S |
| `DATE` | Fecha (sin hora) |
| `TIMESTAMPTZ` | Fecha y hora con zona horaria |
| `JSONB` | Objeto JSON en formato binario |
| `INET` | Dirección IP (IPv4 o IPv6) |
| `GEOGRAPHY(POINT,4326)` | Punto geográfico (latitud/longitud, sistema WGS 84) |

---

## 2. Tablas del Sistema

---

### 2.1 roles

> **Descripción**: Catálogo de roles del sistema. Cada usuario posee un único rol principal (RN-03).

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_rol` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único del rol |
| 2 | `nombre` | `VARCHAR(50)` | **UNIQUE**, **NOT NULL** | Nombre del rol (ej. `donante`, `receptor`, `banco_alimentos`, `administrador`) |
| 3 | `descripcion` | `VARCHAR(255)` | — | Descripción detallada de las funciones del rol |

**Índices**: (PK implícito sobre `id_rol`)  
**Referenciado por**: [`usuarios.id_rol`](#22-usuarios)

---

### 2.2 usuarios

> **Descripción**: Registro de todos los usuarios del sistema. Soporta múltiples roles y subtipos de donante.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_usuario` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único del usuario |
| 2 | `nombre` | `VARCHAR(100)` | **NOT NULL** | Nombre del usuario |
| 3 | `apellido` | `VARCHAR(100)` | — | Apellido del usuario |
| 4 | `telefono` | `VARCHAR(20)` | — | Número de teléfono de contacto |
| 5 | `foto_perfil` | `VARCHAR(255)` | — | URL de la foto de perfil |
| 6 | `ultimo_acceso` | `TIMESTAMPTZ` | — | Fecha y hora del último inicio de sesión |
| 7 | `email` | `VARCHAR(255)` | **UNIQUE** | Correo electrónico (único en el sistema) |
| 8 | `email_verificado` | `BOOLEAN` | DEFAULT `false` | Indica si el correo fue verificado |
| 9 | `contrasena_hash` | `VARCHAR(255)` | — | Hash bcrypt de la contraseña (coste ≥ 12) |
| 10 | `id_rol` | `UUID` | **NOT NULL**, **FK** → `roles.id_rol` | Rol principal del usuario |
| 11 | `subtipo_donante` | `VARCHAR(20)` | CHECK: `'formal'`, `'informal'`, `'independiente'` o NULL | Subtipo cuando el rol es donante |
| 12 | `id_usuario_registrador` | `UUID` | **FK** → `usuarios.id_usuario` | Operador que registró al donante independiente (RF-01) |
| 13 | `intentos_fallidos` | `SMALLINT` | DEFAULT `0` | Contador de intentos fallidos de inicio de sesión |
| 14 | `bloqueado_hasta` | `TIMESTAMPTZ` | — | Fecha/hora hasta la que el usuario está bloqueado |
| 15 | `estado` | `VARCHAR(20)` | CHECK: `'activo'`, `'inactivo'`, `'suspendido'`, DEFAULT `'activo'` | Estado actual de la cuenta |
| 16 | `creado_en` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de creación del registro |

**Índices**:
- `idx_usuarios_rol` sobre `id_rol`
- `idx_usuarios_email` sobre `email`

**Referencias**:
- `id_rol` → [`roles.id_rol`](#21-roles)
- `id_usuario_registrador` → [`usuarios.id_usuario`](#22-usuarios) (auto-referencia)

---

### 2.3 direcciones_sedes

> **Descripción**: Sedes físicas (centros de acopio, almacenes, comedores) asociadas a cada usuario. Incluye coordenadas geográficas para cálculo de distancias.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_sede` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único de la sede |
| 2 | `id_usuario` | `UUID` | **NOT NULL**, **FK** → `usuarios.id_usuario` | Usuario propietario de la sede |
| 3 | `nombre_sede` | `VARCHAR(150)` | — | Nombre descriptivo de la sede |
| 4 | `direccion_texto` | `VARCHAR(255)` | — | Dirección en formato texto legible |
| 5 | `correo_contacto` | `VARCHAR(255)` | — | Correo de contacto de la sede |
| 6 | `telefono_contacto` | `VARCHAR(20)` | — | Teléfono de contacto de la sede |
| 7 | `horario_atencion` | `VARCHAR(255)` | — | Horario de atención al público |
| 8 | `estado` | `VARCHAR(20)` | DEFAULT `'activa'` | Estado de la sede (activa, inactiva, etc.) |
| 9 | `coordenadas` | `GEOGRAPHY(POINT,4326)` | **NOT NULL** | Ubicación geográfica (lat/lon) para operaciones PostGIS |
| 10 | `capacidad_diaria_kg` | `NUMERIC(10,2)` | — | Capacidad máxima diaria en kilogramos |
| 11 | `tiene_cadena_frio` | `BOOLEAN` | DEFAULT `false` | Indica si la sede dispone de cadena de frío |
| 12 | `rnc` | `VARCHAR(11)` | — | Registro Nacional de Contribuyente (RD) |
| 13 | `creado_en` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de creación del registro |

**Índices**:
- `idx_sedes_coordenadas` (GiST) sobre `coordenadas` — aceleración de consultas geoespaciales
- `idx_sedes_usuario` sobre `id_usuario`

**Referencia**: `id_usuario` → [`usuarios.id_usuario`](#22-usuarios)

---

### 2.4 categorias_alimentos

> **Descripción**: Catálogo de categorías de alimentos (lácteos, carnes, enlatados, etc.).

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_categoria_alimento` | `SERIAL` | **PK** | Identificador auto-incremental |
| 2 | `nombre_categoria` | `VARCHAR(100)` | **NOT NULL** | Nombre de la categoría |
| 3 | `requiere_cadena_frio` | `BOOLEAN` | DEFAULT `false` | Si los alimentos de esta categoría requieren refrigeración |

**Índices**: (PK implícito sobre `id_categoria_alimento`)  
**Referenciado por**: [`productos.id_categoria_alimento`](#26-productos)

---

### 2.5 categorias_perecibilidad

> **Descripción**: Clasificación de productos según su velocidad de caducidad. Define la ventana mínima de días antes del vencimiento para aceptar un lote (RN-05).

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_perecibilidad` | `SERIAL` | **PK** | Identificador auto-incremental |
| 2 | `nombre` | `VARCHAR(50)` | **NOT NULL** | Nombre de la categoría (ej. `perecedero`, `no_perecedero`, `semanal`) |
| 3 | `dias_minimos_ventana` | `INT` | **NOT NULL** | Días mínimos antes del vencimiento requeridos para aceptar el lote. Editable por `banco_alimentos` y `administrador` (RN-05) |

**Índices**: (PK implícito sobre `id_perecibilidad`)  
**Referenciado por**: [`productos.id_perecibilidad`](#26-productos)

---

### 2.6 productos

> **Descripción**: Catálogo maestro de productos alimenticios.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_producto` | `SERIAL` | **PK** | Identificador auto-incremental |
| 2 | `id_categoria_alimento` | `INT` | **NOT NULL**, **FK** → `categorias_alimentos.id_categoria_alimento` | Categoría del alimento |
| 3 | `id_perecibilidad` | `INT` | **NOT NULL**, **FK** → `categorias_perecibilidad.id_perecibilidad` | Nivel de perecibilidad |
| 4 | `nombre_producto` | `VARCHAR(150)` | **NOT NULL** | Nombre del producto |
| 5 | `codigo_barra` | `VARCHAR(50)` | — | Código de barras (EAN/UPC) |
| 6 | `descripcion` | `VARCHAR(255)` | — | Descripción breve del producto |
| 7 | `marca` | `VARCHAR(100)` | — | Marca comercial |
| 8 | `imagen_url` | `VARCHAR(255)` | — | URL de la imagen del producto |
| 9 | `unidad_predeterminada` | `VARCHAR(20)` | — | Unidad de medida por defecto (kg, L, unidad, etc.) |

**Índices**: (PK implícito sobre `id_producto`)  
**Referencias**:
- `id_categoria_alimento` → [`categorias_alimentos.id_categoria_alimento`](#24-categorias_alimentos)
- `id_perecibilidad` → [`categorias_perecibilidad.id_perecibilidad`](#25-categorias_perecibilidad)

---

### 2.7 lotes_inventario

> **Descripción**: Lotes de alimentos registrados en el inventario. Cada lote pertenece a un usuario, contiene un producto específico y puede estar asociado a una sede. Se gestiona con lógica FEFO (primero en vencer, primero en salir).

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_lote` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único del lote |
| 2 | `id_usuario` | `UUID` | **NOT NULL**, **FK** → `usuarios.id_usuario` | Usuario propietario del lote |
| 3 | `id_producto` | `INT` | **NOT NULL**, **FK** → `productos.id_producto` | Producto contenido en el lote |
| 4 | `id_sede` | `UUID` | **FK** → `direcciones_sedes.id_sede` | Sede donde se almacena el lote |
| 5 | `cantidad_disponible` | `NUMERIC(10,2)` | **NOT NULL** | Cantidad aún disponible para donación |
| 6 | `unidad_medida` | `VARCHAR(10)` | — | Unidad de medida (kg, L, caja, etc.) |
| 7 | `peso_total` | `NUMERIC(10,2)` | — | Peso total original del lote |
| 8 | `peso_disponible` | `NUMERIC(10,2)` | — | Peso aún disponible para donación |
| 9 | `fecha_produccion` | `DATE` | — | Fecha de producción o elaboración |
| 10 | `fecha_vencimiento` | `DATE` | **NOT NULL** | Fecha de vencimiento del lote |
| 11 | `temperatura_requerida` | `VARCHAR(30)` | — | Temperatura de conservación requerida (ej. `-18°C`, `2-8°C`) |
| 12 | `estado` | `VARCHAR(20)` | **NOT NULL**, CHECK: `'disponible'`, `'reservado'`, `'asignado'`, `'entregado'`, `'vencido'`, `'retirado'`, DEFAULT `'disponible'` | Estado actual del lote en el flujo logístico |
| 13 | `creado_en` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de creación del registro |

**Checks**:
- `chk_fecha_vencimiento_futura`: `fecha_vencimiento > fecha_produccion`

**Índices**:
- `idx_lotes_fecha_vencimiento` sobre `fecha_vencimiento` — optimización FEFO
- `idx_lotes_estado` sobre `estado`
- `idx_lotes_sede` sobre `id_sede`

**Referencias**:
- `id_usuario` → [`usuarios.id_usuario`](#22-usuarios)
- `id_producto` → [`productos.id_producto`](#26-productos)
- `id_sede` → [`direcciones_sedes.id_sede`](#23-direcciones_sedes)

---

### 2.8 mermas

> **Descripción**: Registro de pérdidas de alimentos por vencimiento, daño, contaminación u otros motivos (RN-09).

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_merma` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único de la merma |
| 2 | `id_lote` | `UUID` | **NOT NULL**, **FK** → `lotes_inventario.id_lote` | Lote afectado |
| 3 | `id_usuario_responsable` | `UUID` | **NOT NULL**, **FK** → `usuarios.id_usuario` | Usuario que reporta la merma |
| 4 | `motivo` | `VARCHAR(30)` | **NOT NULL**, CHECK: `'vencimiento'`, `'dano_fisico'`, `'contaminacion'`, `'rechazo_en_destino'`, `'otro'` | Causa de la merma |
| 5 | `detalle` | `TEXT` | — | Descripción detallada de lo ocurrido |
| 6 | `cantidad_afectada` | `NUMERIC(10,2)` | **NOT NULL** | Cantidad de alimento perdido |
| 7 | `unidad_medida` | `VARCHAR(10)` | — | Unidad de la cantidad afectada |
| 8 | `fecha_registro` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha y hora del registro de la merma |

**Nota**: RN-09 — Toda merma requiere motivo categorizado + responsable identificado.

**Índices**:
- `idx_mermas_motivo` sobre `motivo`
- `idx_mermas_lote` sobre `id_lote`

**Referencias**:
- `id_lote` → [`lotes_inventario.id_lote`](#27-lotes_inventario)
- `id_usuario_responsable` → [`usuarios.id_usuario`](#22-usuarios)

---

### 2.9 emparejamientos

> **Descripción**: Motor determinista de emparejamiento entre lotes disponibles y sedes receptoras (OE3). Usa FEFO + PostGIS con restricciones de capacidad, distancia (≤ 75 km) y cadena de frío.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_emparejamiento` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único del emparejamiento |
| 2 | `id_lote` | `UUID` | **NOT NULL**, **FK** → `lotes_inventario.id_lote` | Lote a donar |
| 3 | `id_sede` | `UUID` | **NOT NULL**, **FK** → `direcciones_sedes.id_sede` | Sede receptora sugerida |
| 4 | `distancia_km` | `NUMERIC(6,2)` | **NOT NULL** | Distancia calculada en kilómetros (PostGIS) |
| 5 | `distancia_google_km` | `NUMERIC(6,2)` | — | Distancia en ruta real (Google Maps, simulado) |
| 6 | `tiempo_estimado_min` | `NUMERIC(6,2)` | — | Tiempo estimado de viaje en minutos |
| 7 | `estado_tramite` | `VARCHAR(20)` | **NOT NULL**, CHECK: `'sugerido'`, `'confirmado'`, `'rechazado'`, `'expirado'`, `'completado'`, DEFAULT `'sugerido'` | Estado del trámite de emparejamiento |
| 8 | `fecha_limite_retiro` | `TIMESTAMPTZ` | — | Fecha límite para retirar el lote |
| 9 | `creado_en` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de creación del emparejamiento |

**Checks**:
- `chk_radio_maximo`: `distancia_km <= 75` — radio máximo de cobertura

**Índices**:
- `idx_emparejamientos_lote` sobre `id_lote`
- `idx_emparejamientos_sede` sobre `id_sede`
- `idx_emparejamientos_estado` sobre `estado_tramite`

**Nota**: OE3 — Motor determinista (FEFO + PostGIS + restricciones de capacidad/cadena de frío).

**Referencias**:
- `id_lote` → [`lotes_inventario.id_lote`](#27-lotes_inventario)
- `id_sede` → [`direcciones_sedes.id_sede`](#23-direcciones_sedes)

---

### 2.10 ia_ejecuciones

> **Descripción**: Registro de ejecuciones del servicio de IA (Gemini) para normalización NER y justificación narrativa de emparejamientos.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_ejecucion` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único de la ejecución |
| 2 | `id_emparejamiento` | `UUID` | **FK** → `emparejamientos.id_emparejamiento` | Emparejamiento relacionado (opcional) |
| 3 | `tipo_ejecucion` | `VARCHAR(30)` | **NOT NULL**, CHECK: `'normalizacion_ner'`, `'justificacion_narrativa'` | Tipo de tarea de IA ejecutada |
| 4 | `prompt` | `TEXT` | — | Texto del prompt enviado al modelo |
| 5 | `respuesta` | `TEXT` | — | Respuesta recibida del modelo |
| 6 | `modelo` | `VARCHAR(50)` | — | Nombre/versión del modelo utilizado |
| 7 | `tokens_usados` | `INT` | — | Cantidad de tokens consumidos |
| 8 | `confianza` | `NUMERIC(4,2)` | — | Nivel de confianza del resultado (0.00 a 1.00) |
| 9 | `creado_en` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de ejecución |

**Referencia**: `id_emparejamiento` → [`emparejamientos.id_emparejamiento`](#29-emparejamientos)

---

### 2.11 entregas_transacciones

> **Descripción**: Registro de transacciones de entrega una vez confirmado un emparejamiento. Incluye firma digital y trazabilidad fiscal con hash encadenado (DGII).

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_entrega` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único de la entrega |
| 2 | `id_emparejamiento` | `UUID` | **NOT NULL**, **FK** → `emparejamientos.id_emparejamiento` | Emparejamiento que originó la entrega |
| 3 | `estado_entrega` | `VARCHAR(20)` | **NOT NULL**, CHECK: `'pendiente'`, `'completada'`, `'rechazada'`, DEFAULT `'pendiente'` | Estado de la entrega |
| 4 | `fecha_completado` | `TIMESTAMPTZ` | — | Fecha en que se completó la entrega |
| 5 | `hash_fiscal_dgii` | `VARCHAR(128)` | — | Hash fiscal para la DGII (cadena de custodia) |
| 6 | `hash_anterior` | `VARCHAR(128)` | — | Hash de la transacción anterior (cadena de bloques fiscal) |
| 7 | `nombre_receptor` | `VARCHAR(150)` | — | Nombre de la persona que recibe físicamente |
| 8 | `firma_url` | `VARCHAR(255)` | — | URL de la imagen de la firma digital |
| 9 | `documento_firmado_url` | `VARCHAR(255)` | — | URL del documento de entrega firmado |
| 10 | `creado_en` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de creación del registro |

**Referencia**: `id_emparejamiento` → [`emparejamientos.id_emparejamiento`](#29-emparejamientos)

---

### 2.12 evidencia_entrega

> **Descripción**: Archivos adjuntos (fotos, documentos) que evidencian una entrega realizada.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_evidencia` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único de la evidencia |
| 2 | `id_entrega` | `UUID` | **NOT NULL**, **FK** → `entregas_transacciones.id_entrega` | Entrega a la que pertenece la evidencia |
| 3 | `tipo_archivo` | `VARCHAR(20)` | — | Tipo MIME o categoría del archivo |
| 4 | `archivo_url` | `VARCHAR(255)` | **NOT NULL** | URL del archivo de evidencia |
| 5 | `subido_en` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de subida del archivo |

**Referencia**: `id_entrega` → [`entregas_transacciones.id_entrega`](#211-entregas_transacciones)

---

### 2.13 perfiles_legales

> **Descripción**: Información legal complementaria del usuario, como RNC y consentimiento según Ley 172-13.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_usuario` | `UUID` | **PK**, **FK** → `usuarios.id_usuario` | Usuario al que pertenece el perfil legal |
| 2 | `rnc` | `VARCHAR(11)` | **UNIQUE** | Registro Nacional de Contribuyente |
| 3 | `telefono` | `VARCHAR(20)` | — | Teléfono de contacto legal |
| 4 | `consentimiento_172_13` | `BOOLEAN` | **NOT NULL**, DEFAULT `false` | Aceptación del tratamiento de datos según Ley 172-13 |
| 5 | `fecha_consentimiento` | `TIMESTAMPTZ` | — | Fecha en que se otorgó el consentimiento |

**Checks**:
- `chk_rnc_formal`: `rnc IS NULL OR length(rnc) = 11` — el RNC debe tener exactamente 11 caracteres si se proporciona

**Referencia**: `id_usuario` → [`usuarios.id_usuario`](#22-usuarios)

---

### 2.14 donaciones

> **Descripción**: Registro principal de cada acto de donación realizado por un usuario.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_donacion` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único de la donación |
| 2 | `id_usuario` | `UUID` | **NOT NULL**, **FK** → `usuarios.id_usuario` | Usuario que realizó la donación |
| 3 | `fecha_donacion` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha y hora de la donación |
| 4 | `comprobante_url` | `VARCHAR(255)` | — | URL del comprobante de donación |
| 5 | `observaciones` | `TEXT` | — | Notas u observaciones adicionales |
| 6 | `creado_en` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de creación del registro |

**Referencia**: `id_usuario` → [`usuarios.id_usuario`](#22-usuarios)

---

### 2.15 detalle_donaciones

> **Descripción**: Líneas de detalle de cada donación, especificando los productos donados y sus cantidades.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_detalle_donacion` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único del detalle |
| 2 | `id_donacion` | `UUID` | **NOT NULL**, **FK** → `donaciones.id_donacion` | Donación a la que pertenece esta línea |
| 3 | `id_producto` | `INT` | **NOT NULL**, **FK** → `productos.id_producto` | Producto donado |
| 4 | `cantidad` | `NUMERIC(10,2)` | **NOT NULL** | Cantidad donada |
| 5 | `unidad_medida` | `VARCHAR(20)` | — | Unidad de medida de la cantidad |
| 6 | `fecha_vencimiento` | `DATE` | — | Fecha de vencimiento del producto donado |

**Referencias**:
- `id_donacion` → [`donaciones.id_donacion`](#214-donaciones)
- `id_producto` → [`productos.id_producto`](#26-productos)

---

### 2.16 reportes_consolidados

> **Descripción**: Reportes generados por el sistema. Soporta versionado y rectificación de reportes previos.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_reporte` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único del reporte |
| 2 | `creado_por` | `UUID` | **NOT NULL**, **FK** → `usuarios.id_usuario` | Usuario que generó el reporte |
| 3 | `tipo_reporte` | `VARCHAR(30)` | **NOT NULL** | Tipo de reporte (inventario, donaciones, mermas, etc.) |
| 4 | `url_archivo` | `VARCHAR(255)` | — | URL del archivo generado (PDF, Excel, etc.) |
| 5 | `parametros_busqueda` | `JSONB` | — | Filtros y parámetros usados para generar el reporte |
| 6 | `version` | `INT` | **NOT NULL**, DEFAULT `1` | Número de versión del reporte |
| 7 | `id_reporte_rectificado` | `UUID` | **FK** → `reportes_consolidados.id_reporte` | Reporte anterior que este rectifica (auto-referencia) |
| 8 | `estado` | `VARCHAR(20)` | **NOT NULL**, CHECK: `'borrador'`, `'emitido'`, `'rectificado'`, DEFAULT `'emitido'` | Estado del reporte |
| 9 | `fecha_generacion` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de generación del reporte |

**Referencias**:
- `creado_por` → [`usuarios.id_usuario`](#22-usuarios)
- `id_reporte_rectificado` → [`reportes_consolidados.id_reporte`](#216-reportes_consolidados) (auto-referencia)

---

### 2.17 notificaciones

> **Descripción**: Notificaciones push/in-app para los usuarios del sistema.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_notificacion` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único de la notificación |
| 2 | `id_usuario` | `UUID` | **NOT NULL**, **FK** → `usuarios.id_usuario` | Usuario destinatario |
| 3 | `titulo` | `VARCHAR(150)` | — | Título de la notificación |
| 4 | `mensaje` | `TEXT` | — | Contenido del mensaje |
| 5 | `leido` | `BOOLEAN` | DEFAULT `false` | Si el usuario ya leyó la notificación |
| 6 | `creado_en` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de creación de la notificación |

**Índices**:
- `idx_notificaciones_fecha` sobre `creado_en`
- `idx_notificaciones_usuario` sobre `id_usuario`

**Referencia**: `id_usuario` → [`usuarios.id_usuario`](#22-usuarios)

---

### 2.18 historial_estado_lote

> **Descripción**: Trazabilidad de cada cambio de estado de un lote de inventario.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_historial` | `BIGSERIAL` | **PK** | Identificador auto-incremental |
| 2 | `id_usuario` | `UUID` | **NOT NULL**, **FK** → `usuarios.id_usuario` | Usuario que realizó el cambio |
| 3 | `id_lote` | `UUID` | **NOT NULL**, **FK** → `lotes_inventario.id_lote` | Lote cuyo estado cambió |
| 4 | `estado_anterior` | `VARCHAR(20)` | — | Estado antes del cambio |
| 5 | `estado_nuevo` | `VARCHAR(20)` | **NOT NULL** | Estado después del cambio |
| 6 | `motivo` | `TEXT` | — | Razón del cambio de estado |
| 7 | `fecha` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha y hora del cambio |

**Referencias**:
- `id_usuario` → [`usuarios.id_usuario`](#22-usuarios)
- `id_lote` → [`lotes_inventario.id_lote`](#27-lotes_inventario)

---

### 2.19 bitacora_auditoria

> **Descripción**: Registro de auditoría de todas las acciones relevantes en el sistema.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_bitacora` | `BIGSERIAL` | **PK** | Identificador auto-incremental |
| 2 | `id_usuario` | `UUID` | **FK** → `usuarios.id_usuario` | Usuario que realizó la acción (puede ser NULL para acciones del sistema) |
| 3 | `accion` | `VARCHAR(50)` | **NOT NULL** | Tipo de acción (CREAR, ACTUALIZAR, ELIMINAR, etc.) |
| 4 | `entidad_afectada` | `VARCHAR(50)` | — | Tabla o entidad sobre la que se actuó |
| 5 | `id_entidad_afectada` | `VARCHAR(100)` | — | ID del registro afectado |
| 6 | `detalles_antes_despues` | `JSONB` | — | Valores antes y después del cambio (formato JSON) |
| 7 | `ip_origen` | `INET` | — | Dirección IP desde la que se realizó la acción |
| 8 | `creado_en` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha y hora de la acción |

**Índices**:
- `idx_bitacora_usuario` sobre `id_usuario`
- `idx_bitacora_fecha` sobre `creado_en`

**Referencia**: `id_usuario` → [`usuarios.id_usuario`](#22-usuarios)

---

### 2.20 consentimiento_datos

> **Descripción**: Registro de consentimientos otorgados por los usuarios para el tratamiento de sus datos personales, según la Ley 172-13 (RN-18 / RF-31). Aplicable a cualquier usuario, no solo a perfiles legales.

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_consentimiento` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único del consentimiento |
| 2 | `id_usuario` | `UUID` | **NOT NULL**, **FK** → `usuarios.id_usuario` | Usuario que otorga el consentimiento |
| 3 | `tipo_consentimiento` | `VARCHAR(40)` | **NOT NULL**, CHECK: `'tratamiento_datos_172_13'`, `'terminos_uso'`, `'politica_privacidad'` | Tipo de consentimiento |
| 4 | `version_documento` | `VARCHAR(20)` | **NOT NULL** | Versión del documento aceptado |
| 5 | `aceptado` | `BOOLEAN` | **NOT NULL**, DEFAULT `false` | Si el usuario aceptó o no |
| 6 | `ip_origen` | `INET` | — | Dirección IP desde la que se aceptó |
| 7 | `fecha_consentimiento` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de aceptación |
| 8 | `fecha_revocacion` | `TIMESTAMPTZ` | — | Fecha de revocación (si aplica) |

**Índices**:
- `idx_consentimiento_usuario` sobre `id_usuario`

**Nota**: RN-18 / RF-31 — Consentimiento aplicable a cualquier usuario, previo a cualquier procesamiento de sus datos personales.

**Referencia**: `id_usuario` → [`usuarios.id_usuario`](#22-usuarios)

---

### 2.21 solicitudes_arco

> **Descripción**: Solicitudes ARCO (Acceso, Rectificación, Cancelación, Oposición) bajo la Ley 172-13. Traza el cumplimiento del plazo de 15 días hábiles (RN-19).

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_solicitud` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único de la solicitud |
| 2 | `id_usuario` | `UUID` | **NOT NULL**, **FK** → `usuarios.id_usuario` | Usuario que presenta la solicitud |
| 3 | `tipo_solicitud` | `VARCHAR(20)` | **NOT NULL**, CHECK: `'acceso'`, `'rectificacion'`, `'cancelacion'`, `'oposicion'` | Tipo de derecho ARCO ejercido |
| 4 | `descripcion` | `TEXT` | — | Descripción de la solicitud |
| 5 | `estado` | `VARCHAR(20)` | **NOT NULL**, CHECK: `'recibida'`, `'en_proceso'`, `'resuelta'`, `'rechazada'`, `'vencida'`, DEFAULT `'recibida'` | Estado del trámite |
| 6 | `fecha_solicitud` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de recepción de la solicitud |
| 7 | `fecha_limite_respuesta` | `DATE` | **NOT NULL** | Fecha límite para responder (15 días hábiles) |
| 8 | `fecha_resolucion` | `TIMESTAMPTZ` | — | Fecha en que se resolvió |
| 9 | `atendido_por` | `UUID` | **FK** → `usuarios.id_usuario` | Administrador que atendió la solicitud |
| 10 | `respuesta` | `TEXT` | — | Respuesta emitida por la organización |

**Índices**:
- `idx_arco_usuario` sobre `id_usuario`
- `idx_arco_estado` sobre `estado`

**Nota**: RN-19 — Traza el cumplimiento del plazo de 15 días hábiles para responder solicitudes ARCO, Ley 172-13.

**Referencias**:
- `id_usuario` → [`usuarios.id_usuario`](#22-usuarios)
- `atendido_por` → [`usuarios.id_usuario`](#22-usuarios)

---

### 2.22 retroalimentacion

> **Descripción**: Calificación y comentarios del receptor sobre la transacción logística completada (RF-22).

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_retroalimentacion` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único de la retroalimentación |
| 2 | `id_entrega` | `UUID` | **NOT NULL**, **FK** → `entregas_transacciones.id_entrega` | Entrega evaluada |
| 3 | `id_usuario` | `UUID` | **NOT NULL**, **FK** → `usuarios.id_usuario` | Usuario que emite la retroalimentación |
| 4 | `calificacion` | `SMALLINT` | **NOT NULL**, CHECK: `BETWEEN 1 AND 5` | Calificación de 1 a 5 estrellas |
| 5 | `comentario` | `TEXT` | — | Comentario cualitativo (opcional) |
| 6 | `creado_en` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de la retroalimentación |

**Índices**:
- `idx_retroalimentacion_entrega` sobre `id_entrega`

**Nota**: RF-22 — Calificación 1-5 y comentario cualitativo opcional sobre la transacción logística completada.

**Referencias**:
- `id_entrega` → [`entregas_transacciones.id_entrega`](#211-entregas_transacciones)
- `id_usuario` → [`usuarios.id_usuario`](#22-usuarios)

---

### 2.23 tokens_recuperacion_password

> **Descripción**: Enlaces temporales para restablecimiento de contraseña con expiración estricta de 15 minutos (RF-05).

| # | Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|---|
| 1 | `id_token` | `UUID` | **PK**, DEFAULT `uuid_generate_v4()` | Identificador único del token |
| 2 | `id_usuario` | `UUID` | **NOT NULL**, **FK** → `usuarios.id_usuario` | Usuario que solicitó el restablecimiento |
| 3 | `token_hash` | `VARCHAR(255)` | **NOT NULL** | Hash del token enviado al usuario |
| 4 | `usado` | `BOOLEAN` | **NOT NULL**, DEFAULT `false` | Si el token ya fue utilizado |
| 5 | `creado_en` | `TIMESTAMPTZ` | **NOT NULL**, DEFAULT `now()` | Fecha de creación del token |
| 6 | `expira_en` | `TIMESTAMPTZ` | **NOT NULL** | Fecha de expiración (creado_en + 15 min) |

**Índices**:
- `idx_tokens_recuperacion_usuario` sobre `id_usuario`

**Nota**: RF-05 — Enlaces temporales de restablecimiento de contraseña con expiración estricta de 15 minutos.

**Referencia**: `id_usuario` → [`usuarios.id_usuario`](#22-usuarios)

---

## 3. Diagrama de Relaciones

```
roles ─────────────────────────────────────────────────────┐
  │                                                        │
  └── id_rol (PK) ◄──── usuarios.id_rol (FK)              │
                          │                                │
                          ├── id_usuario (PK) ◄── usuarios.id_usuario_registrador (FK, auto-ref)
                          │                                │
                          ├── id_usuario (PK) ◄── direcciones_sedes.id_usuario (FK)
                          │                                │
                          ├── id_usuario (PK) ◄── lotes_inventario.id_usuario (FK)
                          │                                │
                          ├── id_usuario (PK) ◄── mermas.id_usuario_responsable (FK)
                          │                                │
                          ├── id_usuario (PK) ◄── perfiles_legales.id_usuario (FK)
                          │                                │
                          ├── id_usuario (PK) ◄── donaciones.id_usuario (FK)
                          │                                │
                          ├── id_usuario (PK) ◄── reportes_consolidados.creado_por (FK)
                          │                                │
                          ├── id_usuario (PK) ◄── notificaciones.id_usuario (FK)
                          │                                │
                          ├── id_usuario (PK) ◄── historial_estado_lote.id_usuario (FK)
                          │                                │
                          ├── id_usuario (PK) ◄── bitacora_auditoria.id_usuario (FK)
                          │                                │
                          ├── id_usuario (PK) ◄── consentimiento_datos.id_usuario (FK)
                          │                                │
                          ├── id_usuario (PK) ◄── solicitudes_arco.id_usuario (FK)
                          │                                │
                          ├── id_usuario (PK) ◄── solicitudes_arco.atendido_por (FK)
                          │                                │
                          ├── id_usuario (PK) ◄── retroalimentacion.id_usuario (FK)
                          │                                │
                          └── id_usuario (PK) ◄── tokens_recuperacion_password.id_usuario (FK)

categorias_alimentos ──────────────────────────────────────┐
  │                                                        │
  └── id_categoria_alimento (PK) ◄── productos.id_categoria_alimento (FK)

categorias_perecibilidad ──────────────────────────────────┐
  │                                                        │
  └── id_perecibilidad (PK) ◄── productos.id_perecibilidad (FK)

productos ─────────────────────────────────────────────────┐
  │                                                        │
  ├── id_producto (PK) ◄── lotes_inventario.id_producto (FK)
  │                        │
  └── id_producto (PK) ◄── detalle_donaciones.id_producto (FK)

direcciones_sedes ─────────────────────────────────────────┐
  │                                                        │
  ├── id_sede (PK) ◄── lotes_inventario.id_sede (FK)
  │                        │
  └── id_sede (PK) ◄── emparejamientos.id_sede (FK)

lotes_inventario ──────────────────────────────────────────┐
  │                                                        │
  ├── id_lote (PK) ◄── mermas.id_lote (FK)
  │                        │
  ├── id_lote (PK) ◄── emparejamientos.id_lote (FK)
  │                        │
  └── id_lote (PK) ◄── historial_estado_lote.id_lote (FK)

emparejamientos ───────────────────────────────────────────┐
  │                                                        │
  ├── id_emparejamiento (PK) ◄── ia_ejecuciones.id_emparejamiento (FK)
  │                        │
  └── id_emparejamiento (PK) ◄── entregas_transacciones.id_emparejamiento (FK)
                                   │
                                   └── id_entrega (PK) ◄── evidencia_entrega.id_entrega (FK)
                                   │
                                   └── id_entrega (PK) ◄── retroalimentacion.id_entrega (FK)

donaciones ────────────────────────────────────────────────┐
  │                                                        │
  └── id_donacion (PK) ◄── detalle_donaciones.id_donacion (FK)

reportes_consolidados ─────────────────────────────────────┐
  │                                                        │
  └── id_reporte (PK) ◄── reportes_consolidados.id_reporte_rectificado (FK, auto-ref)
```

---

## 4. Reglas de Negocio Referenciadas

| Código | Descripción | Tablas relacionadas |
|---|---|---|
| **RN-03** | Cada usuario posee un único rol principal | `roles`, `usuarios` |
| **RN-05** | Umbral mínimo de días antes de vencimiento para aceptar el lote, editable por banco_alimentos/administrador | `categorias_perecibilidad` |
| **RN-09** | Toda merma requiere motivo categorizado + responsable identificado | `mermas` |
| **RN-18** | Consentimiento aplicable a cualquier usuario previo al procesamiento de datos personales (Ley 172-13) | `consentimiento_datos` |
| **RN-19** | Plazo de 15 días hábiles para responder solicitudes ARCO (Ley 172-13) | `solicitudes_arco` |
| **RF-01** | Flujo de donante independiente dado de alta por operador de centro de acopio | `usuarios` |
| **RF-05** | Enlaces temporales de restablecimiento de contraseña con expiración de 15 minutos | `tokens_recuperacion_password` |
| **RF-22** | Calificación 1-5 y comentario cualitativo sobre la transacción logística completada | `retroalimentacion` |
| **RF-31** | Registro de consentimiento de tratamiento de datos personales | `consentimiento_datos` |
| **OE3** | Motor determinista de emparejamiento (FEFO + PostGIS + capacidad/cadena de frío) | `emparejamientos` |

---

> **Fin del Diccionario de Datos**  
> Para consultas o actualizaciones, referirse a `CLAUDE.md` y al plan de desarrollo en `docs/es/04-plan-desarrollo.md`.
