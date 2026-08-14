-- =====================================================================
-- CAMBIOS INCREMENTALES - Migración de Base de Datos
-- Fecha: 2026-08-13
-- Propósito: Actualizar BD existente sin perder datos
-- =====================================================================

-- ⚠️ HACER BACKUP ANTES DE EJECUTAR ESTE ARCHIVO
-- pg_dump -U usuario -d donaciones_alimentos -f backup_pre_migracion.sql

BEGIN TRANSACTION;

-- =====================================================================
-- 1. NUEVAS EXTENSIONES
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS h3;
-- CREATE EXTENSION IF NOT EXISTS h3_postgis;  -- Requiere postgis_raster, omitido

-- =====================================================================
-- 2. NUEVAS FUNCIONES
-- =====================================================================

CREATE OR REPLACE FUNCTION fn_bloquear_modificacion_append_only()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'Esta tabla es append-only: operación % no permitida sobre %', TG_OP, TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_bloquear_reporte_emitido()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.estado = 'emitido' THEN
    RAISE EXCEPTION 'RN-17: un reporte emitido no puede modificarse directamente; genere un reporte rectificativo (id_reporte_rectificado).';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- 3. AGREGAR COLUMNAS A TABLAS EXISTENTES
-- =====================================================================

-- Tabla: bitacora_auditoria
-- Agregamos campos para chain de hashes (Hallazgo 8)
ALTER TABLE "bitacora_auditoria"
ADD COLUMN "hash_actual" VARCHAR(128) NOT NULL DEFAULT '',
ADD COLUMN "hash_anterior" VARCHAR(128);

-- Tabla: historial_estado_lote
-- Agregamos campos para chain de hashes (Hallazgo 8)
ALTER TABLE "historial_estado_lote"
ADD COLUMN "hash_actual" VARCHAR(128) NOT NULL DEFAULT '',
ADD COLUMN "hash_anterior" VARCHAR(128);

-- Tabla: detalle_donaciones
-- Agregamos valor estimado para Ley 11-92 (deducibilidad fiscal)
ALTER TABLE "detalle_donaciones"
ADD COLUMN "valor_estimado_rd" NUMERIC(12,2) DEFAULT 0.00;

-- Tabla: emparejamientos
-- Agregamos campos para OE3 (motor FEFO + IA + aprobación manual)
ALTER TABLE "emparejamientos"
ADD COLUMN "prioridad_fefo_score" NUMERIC(5,2),
ADD COLUMN "justificacion_ia" TEXT,
ADD COLUMN "aprobado_por_operador" UUID;

-- Tabla: reportes_consolidados
-- Agregamos hash del documento para integridad (Hallazgo 8)
ALTER TABLE "reportes_consolidados"
ADD COLUMN "hash_documento" VARCHAR(128);

-- =====================================================================
-- 4. CAMBIAR ESTRUCTURA DE perfiles_legales (IMPORTANTE)
-- =====================================================================

-- Primero, crear las nuevas columnas para cifrado
ALTER TABLE "perfiles_legales"
ADD COLUMN "rnc_cifrado" BYTEA,
ADD COLUMN "rnc_hash_busqueda" VARCHAR(64) UNIQUE,
ADD COLUMN "cedula_cifrada" BYTEA,
ADD COLUMN "cedula_hash_busqueda" VARCHAR(64) UNIQUE;

-- ⚠️ NOTA: La migración de datos de rnc a rnc_cifrado debe hacerse en la aplicación
-- porque requiere cifrado AES-256-GCM. Ver servicio_admin.py para implementación.
-- Por ahora, dejaremos el campo rnc VARCHAR(255) UNIQUE existente para compatibilidad.

-- Una vez que hayas migrado los datos a rnc_cifrado, ENTONCES ejecuta:
-- ALTER TABLE "perfiles_legales" DROP COLUMN "rnc";

-- =====================================================================
-- 5. AGREGAR FOREIGN KEY
-- =====================================================================

-- FK en emparejamientos para aprobado_por_operador
ALTER TABLE "emparejamientos"
ADD CONSTRAINT "fk_emparejamientos_aprobado_por_operador"
FOREIGN KEY ("aprobado_por_operador") 
REFERENCES "usuarios" ("id_usuario") 
DEFERRABLE INITIALLY IMMEDIATE;

-- =====================================================================
-- 6. AGREGAR TRIGGERS PARA TABLAS APPEND-ONLY
-- =====================================================================

-- Trigger para bitacora_auditoria (inmutable)
DROP TRIGGER IF EXISTS "trg_bitacora_inmutable" ON "bitacora_auditoria";
CREATE TRIGGER "trg_bitacora_inmutable"
BEFORE DELETE OR UPDATE ON "bitacora_auditoria"
FOR EACH ROW
EXECUTE FUNCTION fn_bloquear_modificacion_append_only();

-- Trigger para historial_estado_lote (inmutable)
DROP TRIGGER IF EXISTS "trg_historial_lote_inmutable" ON "historial_estado_lote";
CREATE TRIGGER "trg_historial_lote_inmutable"
BEFORE DELETE OR UPDATE ON "historial_estado_lote"
FOR EACH ROW
EXECUTE FUNCTION fn_bloquear_modificacion_append_only();

-- Trigger para reportes_consolidados (RN-17: No modificar si está emitido)
DROP TRIGGER IF EXISTS "trg_reporte_inmutable" ON "reportes_consolidados";
CREATE TRIGGER "trg_reporte_inmutable"
BEFORE UPDATE ON "reportes_consolidados"
FOR EACH ROW
EXECUTE FUNCTION fn_bloquear_reporte_emitido();

-- =====================================================================
-- 7. VALIDACION Y DIAGNOSTICO
-- =====================================================================

-- Verificar que todas las columnas existen
SELECT 
  table_name,
  COUNT(*) as total_columnas
FROM information_schema.columns
WHERE table_name IN (
  'bitacora_auditoria', 'historial_estado_lote', 'detalle_donaciones',
  'emparejamientos', 'reportes_consolidados', 'perfiles_legales'
)
GROUP BY table_name;

-- Verificar que los triggers están activos
SELECT trigger_name, event_object_table FROM information_schema.triggers
WHERE trigger_name LIKE 'trg_%';

-- Verificar que la FK está creada
SELECT constraint_name, table_name 
FROM information_schema.key_column_usage
WHERE constraint_name LIKE '%aprobado_por%';

-- =====================================================================
-- 8. RN-10: RADIO MÁXIMO DEL PILOTO SDO (10 km inicial / 15 km máximo)
-- =====================================================================

ALTER TABLE "emparejamientos" DROP CONSTRAINT IF EXISTS "chk_radio_maximo";
ALTER TABLE "emparejamientos"
ADD CONSTRAINT "chk_radio_maximo" CHECK (distancia_km <= 15);

-- =====================================================================
-- COMMIT TRANSACTION
-- =====================================================================

COMMIT;

-- =====================================================================
-- PASOS SIGUIENTES (MANUALES EN LA APLICACION)
-- =====================================================================

-- 1. Implementar cifrado de RNC/Cédula en servicio_admin.py
--    - Leer datos de rnc (VARCHAR)
--    - Cifrar con AES-256-GCM
--    - Almacenar en rnc_cifrado (BYTEA)
--    - Calcular HMAC-SHA256 y almacenar en rnc_hash_busqueda

-- 2. Una vez completada la migración de datos, ejecutar:
--    ALTER TABLE "perfiles_legales" DROP COLUMN "rnc";

-- 3. Implementar cálculo de hash en:
--    - bitacora_auditoria: hash_actual, hash_anterior (SHA-256 chaining)
--    - historial_estado_lote: hash_actual, hash_anterior (SHA-256 chaining)
--    - reportes_consolidados: hash_documento (SHA-256 del PDF)

-- 4. Implementar scoring FEFO en emparejamientos:
--    - prioridad_fefo_score basado en días faltantes para vencimiento
--    - justificacion_ia generada por LLM
--    - aprobado_por_operador asignado en aprobación manual

-- =====================================================================
-- FIN DE CAMBIOS INCREMENTALES
-- =====================================================================
