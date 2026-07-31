"""Agrega la columna 'direccion' a direcciones_sedes si no existe."""
import psycopg2

conn = psycopg2.connect(
    host='localhost', port=5432,
    dbname='donaciones_alimentos',
    user='postgres', password='9709'
)
cur = conn.cursor()

# Verificar si la columna ya existe
cur.execute(
    "SELECT column_name FROM information_schema.columns "
    "WHERE table_name = 'direcciones_sedes' AND column_name = 'direccion'"
)
exists = cur.fetchone()
print(f"Columna 'direccion' existe: {exists is not None}")

if not exists:
    print("AGREGANDO columna 'direccion'...")
    cur.execute("ALTER TABLE direcciones_sedes ADD COLUMN direccion VARCHAR(150)")
    conn.commit()
    print("HECHO - columna 'direccion' agregada exitosamente")
else:
    print("La columna ya existe, no se necesita migracion")

# Ver columnas actuales
cur.execute(
    "SELECT column_name FROM information_schema.columns "
    "WHERE table_name = 'direcciones_sedes' ORDER BY ordinal_position"
)
cols = [r[0] for r in cur.fetchall()]
print(f"Columnas actuales ({len(cols)}): {', '.join(cols)}")

cur.close()
conn.close()
