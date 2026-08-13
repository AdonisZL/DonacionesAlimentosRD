-- =====================================================================
-- 03_usuarios_prueba_simple.sql
-- Usuarios de prueba para demostración (sin cifrado en SQL)
-- =====================================================================

BEGIN TRANSACTION;

-- Obtener IDs de roles
DO $$
DECLARE
    v_rol_admin UUID;
    v_rol_banco UUID;
    v_rol_donante UUID;
    v_rol_receptor UUID;
BEGIN
    SELECT "id_rol" INTO v_rol_admin FROM "roles" WHERE "nombre" = 'administrador' LIMIT 1;
    SELECT "id_rol" INTO v_rol_banco FROM "roles" WHERE "nombre" = 'banco_alimentos' LIMIT 1;
    SELECT "id_rol" INTO v_rol_donante FROM "roles" WHERE "nombre" = 'donante' LIMIT 1;
    SELECT "id_rol" INTO v_rol_receptor FROM "roles" WHERE "nombre" = 'receptor' LIMIT 1;

    -- =====================================================================
    -- Usuario 1: ADMINISTRADOR
    -- Contraseña: Admin123!
    -- =====================================================================
    INSERT INTO "usuarios" 
        ("nombre", "apellido", "email", "contrasena_hash", "id_rol", "estado", "email_verificado", "telefono")
    VALUES 
        ('Admin', 'Sistema', 'admin@donacionesalimentos.com', 
         '$2b$12$zPIXNiUlObwT4uI37EZpruO2jMQQeM3EReXJIGl5lpYp7rbJqF9M.', 
         v_rol_admin, 'activo', true, '+1-809-000-0001')
    ON CONFLICT (email) DO NOTHING;

    -- =====================================================================
    -- Usuario 2: BANCO DE ALIMENTOS
    -- Contraseña: Banco123!
    -- =====================================================================
    INSERT INTO "usuarios" 
        ("nombre", "apellido", "email", "contrasena_hash", "id_rol", "estado", "email_verificado", "telefono")
    VALUES 
        ('Carlos', 'Martínez', 'banco@donacionesalimentos.com', 
         '$2b$12$ptOzTDN/A2vpdaNS3Vp0V.LKnH01zMuq2o8PejgSa0KHYjU0xGxo.', 
         v_rol_banco, 'activo', true, '+1-809-000-0002')
    ON CONFLICT (email) DO NOTHING;

    -- =====================================================================
    -- Usuario 3: DONANTE (Empresa)
    -- Contraseña: Donante123!
    -- =====================================================================
    INSERT INTO "usuarios" 
        ("nombre", "apellido", "email", "contrasena_hash", "id_rol", "subtipo_donante", "estado", "email_verificado", "telefono")
    VALUES 
        ('Juan', 'Pérez', 'donante@supermercado.com.do', 
         '$2b$12$RMy/adfsoe5I4fiOF2rgLev/sR5nA/wk7J.KlUgr4AddDGdP3XZSm', 
         v_rol_donante, 'formal', 'activo', true, '+1-809-000-0003')
    ON CONFLICT (email) DO NOTHING;

    -- =====================================================================
    -- Usuario 4: RECEPTOR (Fundación)
    -- Contraseña: Receptor123!
    -- =====================================================================
    INSERT INTO "usuarios" 
        ("nombre", "apellido", "email", "contrasena_hash", "id_rol", "estado", "email_verificado", "telefono")
    VALUES 
        ('María', 'González', 'receptor@fundacion.com.do', 
         '$2b$12$jmXwt04q3EmiEsLHa3/s7e4NWQovc3uUtgC3h68p1x19pQinNZWHm', 
         v_rol_receptor, 'activo', true, '+1-809-000-0004')
    ON CONFLICT (email) DO NOTHING;

    RAISE NOTICE 'Usuarios creados exitosamente';
END $$;

-- =====================================================================
-- Crear sedes para Banco de Alimentos
-- =====================================================================
INSERT INTO "direcciones_sedes" 
    ("id_usuario", "nombre_sede", "direccion_texto", "correo_contacto", "telefono_contacto", 
     "coordenadas", "capacidad_diaria_kg", "tiene_cadena_frio", "estado")
SELECT 
    u."id_usuario",
    'Sede Central Banco de Alimentos',
    'Avenida 27 de Febrero #123, Santo Domingo, República Dominicana',
    'banco@donacionesalimentos.com',
    '+1-809-000-0002',
    ST_GeogFromText('POINT(-69.9312 18.4861)'),
    5000.00,
    true,
    'activa'
FROM "usuarios" u
WHERE u."email" = 'banco@donacionesalimentos.com'
    AND NOT EXISTS (
        SELECT 1 FROM "direcciones_sedes" WHERE "id_usuario" = u."id_usuario"
    );

-- =====================================================================
-- Crear sedes para Receptor
-- =====================================================================
INSERT INTO "direcciones_sedes" 
    ("id_usuario", "nombre_sede", "direccion_texto", "correo_contacto", "telefono_contacto", 
     "coordenadas", "capacidad_diaria_kg", "tiene_cadena_frio", "estado")
SELECT 
    u."id_usuario",
    'Centro de Distribución Fundación',
    'Calle Conde #456, Santo Domingo, República Dominicana',
    'receptor@fundacion.com.do',
    '+1-809-000-0004',
    ST_GeogFromText('POINT(-69.9288 18.4898)'),
    2000.00,
    false,
    'activa'
FROM "usuarios" u
WHERE u."email" = 'receptor@fundacion.com.do'
    AND NOT EXISTS (
        SELECT 1 FROM "direcciones_sedes" WHERE "id_usuario" = u."id_usuario"
    );

-- =====================================================================
-- VERIFICACIÓN
-- =====================================================================
SELECT 
    u."email",
    u."nombre",
    r."nombre" as "rol",
    u."estado",
    u."email_verificado"
FROM "usuarios" u
JOIN "roles" r ON u."id_rol" = r."id_rol"
WHERE u."email" IN (
    'admin@donacionesalimentos.com',
    'banco@donacionesalimentos.com',
    'donante@supermercado.com.do',
    'receptor@fundacion.com.do'
)
ORDER BY r."nombre";

COMMIT;
