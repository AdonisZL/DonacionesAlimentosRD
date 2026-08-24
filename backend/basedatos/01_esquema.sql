-- =====================================================================
-- 01 — Esquema de la base de datos / 数据库表结构
-- Actualizado / 更新日期: 2026-08-13
-- Versión mejorada con validación fiscal, cifrado, auditoría inmutable
-- 22 tablas + extensiones PostGIS avanzadas
-- =====================================================================

-- Extensiones principales / 主要扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- Extensiones complementarias para geolocalización y seguridad
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS h3;
CREATE EXTENSION IF NOT EXISTS h3_postgis;

-- =====================================================================
-- Funciones de control / 控制函数
-- =====================================================================

-- Función para bloquear modificaciones en tablas append-only
CREATE OR REPLACE FUNCTION fn_bloquear_modificacion_append_only()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'Esta tabla es append-only: operación % no permitida sobre %', TG_OP, TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

-- Función para bloquear modificación de reportes emitidos (RN-17)
-- Permite únicamente la transición emitido -> rectificado (sin alterar el
-- contenido fiscal ya emitido); cualquier otro cambio o un DELETE se bloquea.
CREATE OR REPLACE FUNCTION fn_bloquear_reporte_emitido()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF OLD.estado = 'emitido' THEN
      RAISE EXCEPTION 'RN-17: un reporte emitido no puede eliminarse.';
    END IF;
    RETURN OLD;
  END IF;

  IF OLD.estado = 'emitido' THEN
    IF NEW.estado = 'rectificado'
       AND NEW.url_archivo IS NOT DISTINCT FROM OLD.url_archivo
       AND NEW.parametros_busqueda IS NOT DISTINCT FROM OLD.parametros_busqueda
       AND NEW.hash_documento IS NOT DISTINCT FROM OLD.hash_documento THEN
      RETURN NEW;
    END IF;
    RAISE EXCEPTION 'RN-17: un reporte emitido no puede modificarse directamente; genere un reporte rectificativo (id_reporte_rectificado).';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
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
  "codigo_lote_fabricante" VARCHAR(50),
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
  "prioridad_fefo_score" NUMERIC(5,2),
  "justificacion_ia" TEXT,
  "aprobado_por_operador" UUID,
  -- RN-10: radio máximo del piloto de Santo Domingo Oeste.
  CONSTRAINT "chk_radio_maximo" CHECK (distancia_km <= 15)
);
-- Nota: OE3 motor determinista (FEFO + PostGIS + restricciones)
--       prioridad_fefo_score: peso de ordenamiento por cercanía a vencimiento
--       justificacion_ia: explicación generada por LLM (OE3)
--       aprobado_por_operador: RN-07, operador central que aprueba manualmente

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
  "telefono" VARCHAR(20),
  "consentimiento_172_13" BOOLEAN NOT NULL DEFAULT false,
  "fecha_consentimiento" TIMESTAMPTZ,
  "rnc_cifrado" BYTEA,
  "rnc_hash_busqueda" VARCHAR(64) UNIQUE,
  "cedula_cifrada" BYTEA,
  "cedula_hash_busqueda" VARCHAR(64) UNIQUE
);
-- Nota: RNC y cédula se cifran con AES-256-GCM (RNF-12), se almacenan como BYTEA
-- rnc_hash_busqueda y cedula_hash_busqueda son HMAC-SHA256 determinista (blind indexing)
-- para validar sin exponer los valores en texto claro.
-- 注意：RNC 和 身份证使用 AES-256-GCM 加密存储为 BYTEA
-- rnc_hash_busqueda 和 cedula_hash_busqueda 是 HMAC-SHA256 盲索引
-- 用于验证而无需暴露明文值。

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
  "fecha_vencimiento" DATE,
  "valor_estimado_rd" NUMERIC(12,2) DEFAULT 0.00
);
-- Nota: Ley 11-92 Incentivo a Donaciones - valoración en RD indispensable para deducibilidad fiscal
-- 注意：Ley 11-92 捐赠激励 - 多米尼加比索估价对税收可扣除性至关重要

CREATE TABLE "reportes_consolidados" (
  "id_reporte" UUID PRIMARY KEY DEFAULT (uuid_generate_v4()),
  "creado_por" UUID NOT NULL,
  "tipo_reporte" VARCHAR(30) NOT NULL,
  "url_archivo" VARCHAR(255),
  "parametros_busqueda" JSONB,
  "version" INT NOT NULL DEFAULT 1,
  "id_reporte_rectificado" UUID,
  "estado" VARCHAR(20) NOT NULL CHECK (estado IN ('borrador', 'emitido', 'rectificado')) DEFAULT 'emitido',
  "fecha_generacion" TIMESTAMPTZ NOT NULL DEFAULT (now()),
  "hash_documento" VARCHAR(128)
);
-- Nota: Tabla append-only con trigger, estado='emitido' no se puede modificar
--       hash_documento = SHA-256 del PDF generado (RF-27), calculado al emitir
--       Hallazgo 8: integridad y no-repudio de reportes
--       RN-15: conservar por un mínimo de 5 años (Ley 11-92, prescripción fiscal)
-- 注意：仅追加表，estado='emitido' 无法修改，hash_documento 是 PDF 签名

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
  "fecha" TIMESTAMPTZ NOT NULL DEFAULT (now()),
  "hash_actual" VARCHAR(128) NOT NULL DEFAULT '',
  "hash_anterior" VARCHAR(128)
);
-- Nota: Tabla append-only, con trigger que bloquea UPDATE/DELETE
--       hash_actual = SHA-256(id_usuario||id_lote||estado_nuevo||hash_anterior)
--       Hallazgo 8: cadena de hashes para integridad del historial
--       RN-15: conservar por un mínimo de 5 años (Ley 11-92)
-- 注意：仅追加表，触发器阻止 UPDATE/DELETE，带有哈希链

CREATE TABLE "bitacora_auditoria" (
  "id_bitacora" BIGSERIAL PRIMARY KEY,
  "id_usuario" UUID,
  "accion" VARCHAR(50) NOT NULL,
  "entidad_afectada" VARCHAR(50),
  "id_entidad_afectada" VARCHAR(100),
  "detalles_antes_despues" JSONB,
  "ip_origen" INET,
  "creado_en" TIMESTAMPTZ NOT NULL DEFAULT (now()),
  "hash_actual" VARCHAR(128) NOT NULL DEFAULT '',
  "hash_anterior" VARCHAR(128)
);
-- Nota: hash_actual = SHA-256(id_usuario||accion||entidad_afectada||detalles_antes_despues||hash_anterior)
--       Hallazgo 8: cadena de hashes para integridad de auditoría
-- 注意：hash_actual = SHA-256 链式哈希，hash_anterior 指向前一条记录

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

-- =====================================================================
-- Triggers / 触发器
-- =====================================================================

-- Trigger: Bloquea modificaciones en bitacora_auditoria (append-only)
CREATE TRIGGER trg_bitacora_inmutable
BEFORE DELETE OR UPDATE ON bitacora_auditoria
FOR EACH ROW
EXECUTE FUNCTION fn_bloquear_modificacion_append_only();

-- Trigger: Bloquea modificaciones en historial_estado_lote (append-only)
CREATE TRIGGER trg_historial_lote_inmutable
BEFORE DELETE OR UPDATE ON historial_estado_lote
FOR EACH ROW
EXECUTE FUNCTION fn_bloquear_modificacion_append_only();

-- Trigger: Bloquea modificación de reportes que ya fueron emitidos (RN-17)
CREATE TRIGGER trg_reporte_inmutable
BEFORE DELETE OR UPDATE ON reportes_consolidados
FOR EACH ROW
EXECUTE FUNCTION fn_bloquear_reporte_emitido();

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
ALTER TABLE "emparejamientos" ADD FOREIGN KEY ("aprobado_por_operador") REFERENCES "usuarios" ("id_usuario") DEFERRABLE INITIALLY IMMEDIATE;
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
