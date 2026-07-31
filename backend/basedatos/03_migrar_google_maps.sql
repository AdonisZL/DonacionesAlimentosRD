-- Migración: Agregar columna direccion a direcciones_sedes / 添加 direccion 字段
-- Fecha: 2026-07-29
-- Fase 8: Integración Google Maps API

-- Agregar columna direccion (nombre descriptivo de la sede)
ALTER TABLE direcciones_sedes
ADD COLUMN
IF NOT EXISTS direccion VARCHAR
(150);

-- Comentario de columna
COMMENT ON COLUMN direcciones_sedes.direccion IS 'Nombre o etiqueta descriptiva de la dirección (ej: Sede Central)';
