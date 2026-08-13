-- =====================================================================
-- 03_usuarios_prueba.sql
-- Usuarios de prueba para demostración del sistema
-- Fecha: 2026-08-13
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
    -- Usuario 1: ADMINISTRADOR DEL SISTEMA
    -- =====================================================================
    -- Contraseña: Admin123!
    INSERT INTO "usuarios" 
        ("nombre", "apellido", "email", "contrasena_hash", "id_rol", "estado", "email_verificado", "telefono")
    VALUES 
        ('Admin', 'Sistema', 'admin@donacionesalimentos.com', 
         '$2b$12$zPIXNiUlObwT4uI37EZpruO2jMQQeM3EReXJIGl5lpYp7rbJqF9M.', 
         v_rol_admin, 'activo', true, '+1-809-000-0001')
    ON CONFLICT (email) DO NOTHING;

    -- =====================================================================
    -- Usuario 2: BANCO DE ALIMENTOS (Intermediario)
    -- =====================================================================
    -- Contraseña: Banco123!
    INSERT INTO "usuarios" 
        ("nombre", "apellido", "email", "contrasena_hash", "id_rol", "estado", "email_verificado", "telefono")
    VALUES 
        ('Carlos', 'Martínez', 'banco@donacionesalimentos.com', 
         '$2b$12$ptOzTDN/A2vpdaNS3Vp0V.LKnH01zMuq2o8PejgSa0KHYjU0xGxo.', 
         v_rol_banco, 'activo', true, '+1-809-000-0002')
    ON CONFLICT (email) DO NOTHING;

    -- =====================================================================
    -- Usuario 3: DONANTE (Empresa Formal - Supermercado)
    -- =====================================================================
    -- Contraseña: Donante123!
    -- RNC: 101234567 (ficticio pero sigue formato 9 dígitos)
    INSERT INTO "usuarios" 
        ("nombre", "apellido", "email", "contrasena_hash", "id_rol", "subtipo_donante", "estado", "email_verificado", "telefono")
    VALUES 
        ('Juan', 'Pérez', 'donante@supermercado.com.do', 
         '$2b$12$RMy/adfsoe5I4fiOF2rgLev/sR5nA/wk7J.KlUgr4AddDGdP3XZSm', 
         v_rol_donante, 'formal', 'activo', true, '+1-809-000-0003')
    ON CONFLICT (email) DO NOTHING;

    -- =====================================================================
    -- Usuario 4: RECEPTOR (Organización Social - Fundación)
    -- =====================================================================
    -- Contraseña: Receptor123!
    INSERT INTO "usuarios" 
        ("nombre", "apellido", "email", "contrasena_hash", "id_rol", "estado", "email_verificado", "telefono")
    VALUES 
        ('María', 'González', 'receptor@fundacion.com.do', 
         '$2b$12$jmXwt04q3EmiEsLHa3/s7e4NWQovc3uUtgC3h68p1x19pQinNZWHm', 
         v_rol_receptor, 'activo', true, '+1-809-000-0004')
    ON CONFLICT (email) DO NOTHING;

    RAISE NOTICE 'Usuarios de prueba creados exitosamente';
END $$;

-- =====================================================================
-- Datos adicionales para los usuarios (sedes/direcciones para receptores)
-- =====================================================================

-- Crear sede para el Banco de Alimentos
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

-- Crear sede para la Fundación Receptora
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
-- Crear perfil legal para el Donante (Empresa)
-- =====================================================================
INSERT INTO "perfiles_legales" 
    ("id_usuario", "telefono", "consentimiento_172_13", "fecha_consentimiento", 
     "rnc", "cedula_cifrada", "cedula_hash_busqueda")
SELECT 
    u."id_usuario",
    '+1-809-000-0003',
    true,
    now(),
    '101234567',
    NULL,
    NULL
FROM "usuarios" u
WHERE u."email" = 'donante@supermercado.com.do'
    AND NOT EXISTS (
        SELECT 1 FROM "perfiles_legales" WHERE "id_usuario" = u."id_usuario"
    );

-- =====================================================================
-- VALIDACIÓN Y VERIFICACIÓN
-- =====================================================================

-- Contar usuarios creados
SELECT 
    COUNT(*) as "Total Usuarios",
    STRING_AGG(nombre || ' ' || COALESCE(apellido, ''), ', ') as "Nombres"
FROM "usuarios"
WHERE email IN (
    'admin@donacionesalimentos.com',
    'banco@donacionesalimentos.com',
    'donante@supermercado.com.do',
    'receptor@fundacion.com.do'
);

-- Listar usuarios de prueba con roles
SELECT 
    u."email",
    u."nombre",
    r."nombre" as "rol",
    u."estado",
    u."email_verificado",
    u."telefono"
FROM "usuarios" u
JOIN "roles" r ON u."id_rol" = r."id_rol"
WHERE u."email" IN (
    'admin@donacionesalimentos.com',
    'banco@donacionesalimentos.com',
    'donante@supermercado.com.do',
    'receptor@fundacion.com.do'
)
ORDER BY r."nombre";

-- Contar sedes creadas
SELECT 
    COUNT(*) as "Total Sedes"
FROM "direcciones_sedes" ds
JOIN "usuarios" u ON ds."id_usuario" = u."id_usuario"
WHERE u."email" IN (
    'banco@donacionesalimentos.com',
    'receptor@fundacion.com.do'
);

COMMIT;

-- =====================================================================
-- CREDENCIALES DE PRUEBA PARA LA PRESENTACIÓN
-- =====================================================================
/*

USUARIO 1 - ADMINISTRADOR:
  Email:      admin@donacionesalimentos.com
  Contraseña: Admin123!
  Rol:        Administrador del Sistema
  
USUARIO 2 - BANCO DE ALIMENTOS:
  Email:      banco@donacionesalimentos.com
  Contraseña: Banco123!
  Rol:        Banco de Alimentos (Intermediario)
  Teléfono:   +1-809-000-0002
  Sede:       Avenida 27 de Febrero #123, Santo Domingo
  
USUARIO 3 - DONANTE (EMPRESA):
  Email:      donante@supermercado.com.do
  Contraseña: Donante123!
  Rol:        Donante (Formal)
  RNC:        101234567 (Ficticio)
  Teléfono:   +1-809-000-0003
  
USUARIO 4 - RECEPTOR (FUNDACIÓN):
  Email:      receptor@fundacion.com.do
  Contraseña: Receptor123!
  Rol:        Receptor (ONG/Fundación)
  Teléfono:   +1-809-000-0004
  Sede:       Calle Conde #456, Santo Domingo

*/

-- =====================================================================
-- FIN DE USUARIOS DE PRUEBA
-- =====================================================================
