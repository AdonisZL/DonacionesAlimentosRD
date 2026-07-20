-- =====================================================================
-- 02 — Datos semilla / 种子数据
-- Idempotente: solo inserta si la tabla está vacía. / 幂等：表为空时才插入。
-- =====================================================================

-- Roles del sistema (RN-03) / 系统角色
INSERT INTO "roles"
    ("nombre", "descripcion")
SELECT *
FROM (VALUES
        ('donante', 'Persona u organización que aporta excedentes de alimentos'),
        ('receptor', 'Organización que recibe donaciones (fundación, comedor, ONG)'),
        ('banco_alimentos', 'Entidad intermediaria que gestiona y redistribuye alimentos'),
        ('administrador', 'Administrador del sistema con acceso completo')
) AS v(nombre, descripcion)
WHERE NOT EXISTS (SELECT 1
FROM "roles");

-- Categorías de perecibilidad (RN-05) / 易腐性分类
-- dias_minimos_ventana = umbral mínimo de días antes del vencimiento.
INSERT INTO "categorias_perecibilidad"
    ("nombre", "dias_minimos_ventana")
SELECT *
FROM (VALUES
        ('No perecedero', 30),
        ('Semi-perecedero', 15),
        ('Perecedero', 1),
        ('Congelado', 30)
) AS v(nombre, dias)
WHERE NOT EXISTS (SELECT 1
FROM "categorias_perecibilidad");

-- Categorías de alimentos / 食物分类
INSERT INTO "categorias_alimentos"
    ("nombre_categoria", "requiere_cadena_frio")
SELECT *
FROM (VALUES
        ('Granos y cereales', false),
        ('Enlatados y conservas', false),
        ('Panadería y repostería', false),
        ('Frutas y vegetales', false),
        ('Bebidas', false),
        ('Lácteos y huevos', true),
        ('Carnes y aves', true),
        ('Pescados y mariscos', true),
        ('Alimentos congelados', true),
        ('Comida preparada', true)
) AS v(nombre_categoria, requiere_cadena_frio)
WHERE NOT EXISTS (SELECT 1
FROM "categorias_alimentos");
