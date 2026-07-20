CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE "roles" (
  "id_rol" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "nombre" VARCHAR(50) UNIQUE NOT NULL,
  "descripcion" VARCHAR(255)
);

CREATE TABLE "usuarios" (
  "id_usuario" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "nombre" VARCHAR(100) NOT NULL,
  "apellido" VARCHAR(100),
  "telefono" VARCHAR(20),
  "foto_perfil" VARCHAR(255),
  "ultimo_acceso" TIMESTAMPTZ,
  "email" VARCHAR(255) UNIQUE,
  "email_verificado" BOOLEAN DEFAULT false,
  "contrasena_hash" VARCHAR(255),
  "id_rol" UUID NOT NULL,
  "subtipo_donante" VARCHAR(20) CHECK (subtipo_donante IN ('formal', 'informal', 'independiente') OR subtipo_donante IS NULL),
  "id_usuario_registrador" UUID,
  "intentos_fallidos" SMALLINT DEFAULT 0,
  "bloqueado_hasta" TIMESTAMPTZ,
  "estado" VARCHAR(20) CHECK (estado IN ('activo', 'inactivo', 'suspendido')) DEFAULT 'activo',
  "creado_en" TIMESTAMPTZ NOT NULL DEFAULT (now())
);

CREATE TABLE "direcciones_sedes" (
  "id_sede" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_usuario" UUID NOT NULL,
  "nombre_sede" VARCHAR(150),
  "direccion_texto" VARCHAR(255),
  "correo_contacto" VARCHAR(255),
  "telefono_contacto" VARCHAR(20),
  "horario_atencion" VARCHAR(255),
  "estado" VARCHAR(20) DEFAULT 'activa',
  "coordenadas" GEOGRAPHY(POINT,4326) NOT NULL,
  "capacidad_diaria_kg" NUMERIC(10,2),
  "tiene_cadena_frio" BOOLEAN DEFAULT false,
  "rnc" VARCHAR(11),
  "creado_en" TIMESTAMPTZ NOT NULL DEFAULT (now())
);

CREATE TABLE "categorias_alimentos" (
  "id_categoria_alimento" SERIAL PRIMARY KEY,
  "nombre_categoria" VARCHAR(100) NOT NULL,
  "requiere_cadena_frio" BOOLEAN DEFAULT false
);

CREATE TABLE "categorias_perecibilidad" (
  "id_perecibilidad" SERIAL PRIMARY KEY,
  "nombre" VARCHAR(50) NOT NULL,
  "dias_minimos_ventana" INT NOT NULL
);

CREATE TABLE "productos" (
  "id_producto" SERIAL PRIMARY KEY,
  "id_categoria_alimento" INT NOT NULL,
  "id_perecibilidad" INT NOT NULL,
  "nombre_producto" VARCHAR(150) NOT NULL,
  "codigo_barra" VARCHAR(50),
  "descripcion" VARCHAR(255),
  "marca" VARCHAR(100),
  "imagen_url" VARCHAR(255),
  "unidad_predeterminada" VARCHAR(20)
);

CREATE TABLE "lotes_inventario" (
  "id_lote" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_usuario" UUID NOT NULL,
  "id_producto" INT NOT NULL,
  "id_sede" UUID,
  "cantidad_disponible" NUMERIC(10,2) NOT NULL,
  "unidad_medida" VARCHAR(10),
  "peso_total" NUMERIC(10,2),
  "peso_disponible" NUMERIC(10,2),
  "fecha_produccion" DATE,
  "fecha_vencimiento" DATE NOT NULL,
  "temperatura_requerida" VARCHAR(30),
  "estado" VARCHAR(20) NOT NULL CHECK (estado IN ('disponible', 'reservado', 'asignado', 'entregado', 'vencido', 'retirado')) DEFAULT 'disponible',
  "creado_en" TIMESTAMPTZ NOT NULL DEFAULT (now()),
  CONSTRAINT "chk_fecha_vencimiento_futura" CHECK (fecha_vencimiento > fecha_produccion)
);

CREATE TABLE "mermas" (
  "id_merma" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_lote" UUID NOT NULL,
  "id_usuario_responsable" UUID NOT NULL,
  "motivo" VARCHAR(30) NOT NULL CHECK (motivo IN ('vencimiento', 'dano_fisico', 'contaminacion', 'rechazo_en_destino', 'otro')),
  "detalle" TEXT,
  "cantidad_afectada" NUMERIC(10,2) NOT NULL,
  "unidad_medida" VARCHAR(10),
  "fecha_registro" TIMESTAMPTZ NOT NULL DEFAULT (now())
);

CREATE TABLE "emparejamientos" (
  "id_emparejamiento" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_lote" UUID NOT NULL,
  "id_sede" UUID NOT NULL,
  "distancia_km" NUMERIC(6,2) NOT NULL,
  "distancia_google_km" NUMERIC(6,2),
  "tiempo_estimado_min" NUMERIC(6,2),
  "estado_tramite" VARCHAR(20) NOT NULL CHECK (estado_tramite IN ('sugerido', 'confirmado', 'rechazado', 'expirado', 'completado')) DEFAULT 'sugerido',
  "fecha_limite_retiro" TIMESTAMPTZ,
  "creado_en" TIMESTAMPTZ NOT NULL DEFAULT (now()),
  CONSTRAINT "chk_radio_maximo" CHECK (distancia_km <= 75)
);

CREATE TABLE "ia_ejecuciones" (
  "id_ejecucion" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_emparejamiento" UUID,
  "tipo_ejecucion" VARCHAR(30) NOT NULL CHECK (tipo_ejecucion IN ('normalizacion_ner', 'justificacion_narrativa')),
  "prompt" TEXT,
  "respuesta" TEXT,
  "modelo" VARCHAR(50),
  "tokens_usados" INT,
  "confianza" NUMERIC(4,2),
  "creado_en" TIMESTAMPTZ NOT NULL DEFAULT (now())
);

CREATE TABLE "entregas_transacciones" (
  "id_entrega" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_emparejamiento" UUID NOT NULL,
  "estado_entrega" VARCHAR(20) NOT NULL CHECK (estado_entrega IN ('pendiente', 'completada', 'rechazada')) DEFAULT 'pendiente',
  "fecha_completado" TIMESTAMPTZ,
  "hash_fiscal_dgii" VARCHAR(128),
  "hash_anterior" VARCHAR(128),
  "nombre_receptor" VARCHAR(150),
  "firma_url" VARCHAR(255),
  "documento_firmado_url" VARCHAR(255),
  "creado_en" TIMESTAMPTZ NOT NULL DEFAULT (now())
);

CREATE TABLE "evidencia_entrega" (
  "id_evidencia" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_entrega" UUID NOT NULL,
  "tipo_archivo" VARCHAR(20),
  "archivo_url" VARCHAR(255) NOT NULL,
  "subido_en" TIMESTAMPTZ NOT NULL DEFAULT (now())
);

CREATE TABLE "perfiles_legales" (
  "id_usuario" UUID PRIMARY KEY,
  "rnc" VARCHAR(11) UNIQUE,
  "telefono" VARCHAR(20),
  "consentimiento_172_13" BOOLEAN NOT NULL DEFAULT false,
  "fecha_consentimiento" TIMESTAMPTZ,
  CONSTRAINT "chk_rnc_formal" CHECK (rnc IS NULL OR length(rnc) = 11)
);

CREATE TABLE "donaciones" (
  "id_donacion" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_usuario" UUID NOT NULL,
  "fecha_donacion" TIMESTAMPTZ NOT NULL DEFAULT (now()),
  "comprobante_url" VARCHAR(255),
  "observaciones" TEXT,
  "creado_en" TIMESTAMPTZ NOT NULL DEFAULT (now())
);

CREATE TABLE "detalle_donaciones" (
  "id_detalle_donacion" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_donacion" UUID NOT NULL,
  "id_producto" INT NOT NULL,
  "cantidad" NUMERIC(10,2) NOT NULL,
  "unidad_medida" VARCHAR(20),
  "fecha_vencimiento" DATE
);

CREATE TABLE "reportes_consolidados" (
  "id_reporte" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "creado_por" UUID NOT NULL,
  "tipo_reporte" VARCHAR(30) NOT NULL,
  "url_archivo" VARCHAR(255),
  "parametros_busqueda" JSONB,
  "version" INT NOT NULL DEFAULT 1,
  "id_reporte_rectificado" UUID,
  "estado" VARCHAR(20) NOT NULL CHECK (estado IN ('borrador', 'emitido', 'rectificado')) DEFAULT 'emitido',
  "fecha_generacion" TIMESTAMPTZ NOT NULL DEFAULT (now())
);

CREATE TABLE "notificaciones" (
  "id_notificacion" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_usuario" UUID NOT NULL,
  "titulo" VARCHAR(150),
  "mensaje" TEXT,
  "leido" BOOLEAN DEFAULT false,
  "creado_en" TIMESTAMPTZ NOT NULL DEFAULT (now())
);

CREATE TABLE "historial_estado_lote" (
  "id_historial" BIGSERIAL PRIMARY KEY,
  "id_usuario" UUID NOT NULL,
  "id_lote" UUID NOT NULL,
  "estado_anterior" VARCHAR(20),
  "estado_nuevo" VARCHAR(20) NOT NULL,
  "motivo" TEXT,
  "fecha" TIMESTAMPTZ NOT NULL DEFAULT (now())
);

CREATE TABLE "bitacora_auditoria" (
  "id_bitacora" BIGSERIAL PRIMARY KEY,
  "id_usuario" UUID,
  "accion" VARCHAR(50) NOT NULL,
  "entidad_afectada" VARCHAR(50),
  "id_entidad_afectada" VARCHAR(100),
  "detalles_antes_despues" JSONB,
  "ip_origen" INET,
  "creado_en" TIMESTAMPTZ NOT NULL DEFAULT (now())
);

CREATE TABLE "consentimiento_datos" (
  "id_consentimiento" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_usuario" UUID NOT NULL,
  "tipo_consentimiento" VARCHAR(40) NOT NULL CHECK (tipo_consentimiento IN ('tratamiento_datos_172_13', 'terminos_uso', 'politica_privacidad')),
  "version_documento" VARCHAR(20) NOT NULL,
  "aceptado" BOOLEAN NOT NULL DEFAULT false,
  "ip_origen" INET,
  "fecha_consentimiento" TIMESTAMPTZ NOT NULL DEFAULT (now()),
  "fecha_revocacion" TIMESTAMPTZ
);

CREATE TABLE "solicitudes_arco" (
  "id_solicitud" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_usuario" UUID NOT NULL,
  "tipo_solicitud" VARCHAR(20) NOT NULL CHECK (tipo_solicitud IN ('acceso', 'rectificacion', 'cancelacion', 'oposicion')),
  "descripcion" TEXT,
  "estado" VARCHAR(20) NOT NULL CHECK (estado IN ('recibida', 'en_proceso', 'resuelta', 'rechazada', 'vencida')) DEFAULT 'recibida',
  "fecha_solicitud" TIMESTAMPTZ NOT NULL DEFAULT (now()),
  "fecha_limite_respuesta" DATE NOT NULL,
  "fecha_resolucion" TIMESTAMPTZ,
  "atendido_por" UUID,
  "respuesta" TEXT
);

CREATE TABLE "retroalimentacion" (
  "id_retroalimentacion" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_entrega" UUID NOT NULL,
  "id_usuario" UUID NOT NULL,
  "calificacion" SMALLINT NOT NULL CHECK (calificacion BETWEEN 1 AND 5),
  "comentario" TEXT,
  "creado_en" TIMESTAMPTZ NOT NULL DEFAULT (now())
);

CREATE TABLE "tokens_recuperacion_password" (
  "id_token" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "id_usuario" UUID NOT NULL,
  "token_hash" VARCHAR(255) NOT NULL,
  "usado" BOOLEAN NOT NULL DEFAULT false,
  "creado_en" TIMESTAMPTZ NOT NULL DEFAULT (now()),
  "expira_en" TIMESTAMPTZ NOT NULL
);

CREATE INDEX "idx_usuarios_rol" ON "usuarios" ("id_rol");

CREATE INDEX "idx_usuarios_email" ON "usuarios" ("email");

CREATE INDEX "idx_sedes_coordenadas" ON "direcciones_sedes" USING GIST ("coordenadas");

CREATE INDEX "idx_sedes_usuario" ON "direcciones_sedes" ("id_usuario");

CREATE INDEX "idx_lotes_fecha_vencimiento" ON "lotes_inventario" ("fecha_vencimiento");

CREATE INDEX "idx_lotes_estado" ON "lotes_inventario" ("estado");

CREATE INDEX "idx_lotes_sede" ON "lotes_inventario" ("id_sede");

CREATE INDEX "idx_mermas_motivo" ON "mermas" ("motivo");

CREATE INDEX "idx_mermas_lote" ON "mermas" ("id_lote");

CREATE INDEX "idx_emparejamientos_lote" ON "emparejamientos" ("id_lote");

CREATE INDEX "idx_emparejamientos_sede" ON "emparejamientos" ("id_sede");

CREATE INDEX "idx_emparejamientos_estado" ON "emparejamientos" ("estado_tramite");

CREATE INDEX "idx_notificaciones_fecha" ON "notificaciones" ("creado_en");

CREATE INDEX "idx_notificaciones_usuario" ON "notificaciones" ("id_usuario");

CREATE INDEX "idx_bitacora_usuario" ON "bitacora_auditoria" ("id_usuario");

CREATE INDEX "idx_bitacora_fecha" ON "bitacora_auditoria" ("creado_en");

CREATE INDEX "idx_consentimiento_usuario" ON "consentimiento_datos" ("id_usuario");

CREATE INDEX "idx_arco_usuario" ON "solicitudes_arco" ("id_usuario");

CREATE INDEX "idx_arco_estado" ON "solicitudes_arco" ("estado");

CREATE INDEX "idx_retroalimentacion_entrega" ON "retroalimentacion" ("id_entrega");

CREATE INDEX "idx_tokens_recuperacion_usuario" ON "tokens_recuperacion_password" ("id_usuario");

COMMENT ON TABLE "roles" IS 'RN-03: cada usuario posee un único rol principal.';

COMMENT ON COLUMN "usuarios"."id_usuario_registrador" IS 'RF-01: soporta el flujo de donante independiente, dado de alta por un operador de centro de acopio.';

COMMENT ON COLUMN "categorias_perecibilidad"."dias_minimos_ventana" IS 'RN-05: umbral mínimo de días antes de vencimiento requerido para aceptar el lote, editable por rol banco_alimentos/administrador.';

COMMENT ON TABLE "mermas" IS 'RN-09: toda merma requiere motivo categorizado + responsable identificado.';

COMMENT ON TABLE "emparejamientos" IS 'OE3: motor determinista (FEFO + PostGIS + restricciones de capacidad/cadena de frío).';

COMMENT ON TABLE "consentimiento_datos" IS 'RN-18/RF-31: registro de consentimiento aplicable a cualquier usuario (no solo perfiles_legales), previo a cualquier procesamiento de sus datos personales, según Ley 172-13.';

COMMENT ON TABLE "solicitudes_arco" IS 'RN-19: traza el cumplimiento del plazo de 15 días hábiles para responder solicitudes ARCO, Ley 172-13.';

COMMENT ON TABLE "retroalimentacion" IS 'RF-22: calificación 1-5 y comentario cualitativo opcional sobre la transacción logística completada.';

COMMENT ON TABLE "tokens_recuperacion_password" IS 'RF-05: enlaces temporales de restablecimiento de contraseña con expiración estricta de 15 minutos.';

ALTER TABLE "usuarios" ADD FOREIGN KEY ("id_rol") REFERENCES "roles" ("id_rol") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "usuarios" ADD FOREIGN KEY ("id_usuario_registrador") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "direcciones_sedes" ADD FOREIGN KEY ("id_usuario") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "productos" ADD FOREIGN KEY ("id_categoria_alimento") REFERENCES "categorias_alimentos" ("id_categoria_alimento") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "productos" ADD FOREIGN KEY ("id_perecibilidad") REFERENCES "categorias_perecibilidad" ("id_perecibilidad") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "lotes_inventario" ADD FOREIGN KEY ("id_usuario") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "lotes_inventario" ADD FOREIGN KEY ("id_producto") REFERENCES "productos" ("id_producto") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "lotes_inventario" ADD FOREIGN KEY ("id_sede") REFERENCES "direcciones_sedes" ("id_sede") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "mermas" ADD FOREIGN KEY ("id_lote") REFERENCES "lotes_inventario" ("id_lote") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "mermas" ADD FOREIGN KEY ("id_usuario_responsable") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "emparejamientos" ADD FOREIGN KEY ("id_lote") REFERENCES "lotes_inventario" ("id_lote") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "emparejamientos" ADD FOREIGN KEY ("id_sede") REFERENCES "direcciones_sedes" ("id_sede") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "ia_ejecuciones" ADD FOREIGN KEY ("id_emparejamiento") REFERENCES "emparejamientos" ("id_emparejamiento") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "entregas_transacciones" ADD FOREIGN KEY ("id_emparejamiento") REFERENCES "emparejamientos" ("id_emparejamiento") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "evidencia_entrega" ADD FOREIGN KEY ("id_entrega") REFERENCES "entregas_transacciones" ("id_entrega") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "perfiles_legales" ADD FOREIGN KEY ("id_usuario") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "donaciones" ADD FOREIGN KEY ("id_usuario") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "detalle_donaciones" ADD FOREIGN KEY ("id_donacion") REFERENCES "donaciones" ("id_donacion") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "detalle_donaciones" ADD FOREIGN KEY ("id_producto") REFERENCES "productos" ("id_producto") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "reportes_consolidados" ADD FOREIGN KEY ("creado_por") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "reportes_consolidados" ADD FOREIGN KEY ("id_reporte_rectificado") REFERENCES "reportes_consolidados" ("id_reporte") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "notificaciones" ADD FOREIGN KEY ("id_usuario") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "historial_estado_lote" ADD FOREIGN KEY ("id_usuario") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "historial_estado_lote" ADD FOREIGN KEY ("id_lote") REFERENCES "lotes_inventario" ("id_lote") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "bitacora_auditoria" ADD FOREIGN KEY ("id_usuario") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "consentimiento_datos" ADD FOREIGN KEY ("id_usuario") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "solicitudes_arco" ADD FOREIGN KEY ("id_usuario") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "solicitudes_arco" ADD FOREIGN KEY ("atendido_por") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "retroalimentacion" ADD FOREIGN KEY ("id_entrega") REFERENCES "entregas_transacciones" ("id_entrega") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "retroalimentacion" ADD FOREIGN KEY ("id_usuario") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "tokens_recuperacion_password" ADD FOREIGN KEY ("id_usuario") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;
