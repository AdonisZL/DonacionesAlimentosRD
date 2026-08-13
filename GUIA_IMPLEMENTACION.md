# Guía de Implementación - Migración de Base de Datos

## ⚠️ IMPORTANTE: Haz un backup antes de continuar

```bash
# Backup de la base de datos actual
pg_dump -U usuario -d donaciones_alimentos -f backup_pre_migracion_2026-08-13.sql
```

## Paso 1: Aplicar el nuevo esquema SQL

Tienes dos opciones:

### Opción A: Crear una nueva BD desde cero (Recomendado para desarrollo)

```bash
# 1. Crear nueva base de datos
createdb -U usuario donaciones_alimentos_nueva

# 2. Aplicar el esquema actualizado
psql -U usuario -d donaciones_alimentos_nueva -f backend/basedatos/01_esquema.sql

# 3. Aplicar datos semilla (si es necesario)
psql -U usuario -d donaciones_alimentos_nueva -f backend/basedatos/02_datos_semilla.sql
```

### Opción B: Migrar la BD existente (Para producción - más complicado)

```bash
# 1. Hacer backup (ya hecho arriba)

# 2. Conectarse a la BD actual
psql -U usuario -d donaciones_alimentos

# 3. Ejecutar solo los cambios NUEVOS (ver archivo CAMBIOS_SQL_SOLO.sql)
psql -U usuario -d donaciones_alimentos -f backend/basedatos/CAMBIOS_INCREMENTALES.sql
```

> **Nota**: Los cambios incrementales incluyen:
> - Nuevas extensiones
> - Nuevas funciones SQL
> - Nuevas columnas en 6 tablas
> - Nuevos triggers
> - Nueva FK en emparejamientos

## Paso 2: Configurar la conexión en el backend

Actualiza el archivo `.env` en `backend/`:

```bash
# backend/.env

# Nueva BD (si la creaste con "Opción A")
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/donaciones_alimentos_nueva

# O la BD actual (si migraste con "Opción B")
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/donaciones_alimentos
```

## Paso 3: Instalar dependencias (si es necesario)

Todas las dependencias ya están en `requirements.txt`. Solo ejecuta:

```bash
cd backend
pip install -r requirements.txt
```

## Paso 4: Validar la migración

### 4A. Validar modelos SQLAlchemy

```bash
cd backend
python3 << EOF
from app.database.conexion import motor, Base
from app.models import *

# Intenta conectarse
with motor.connect() as conn:
    print("✅ Conexión a BD exitosa")
    
# Verifica que los modelos cargan
from app.models.bitacora_auditoria import BitacoraAuditoria
from app.models.emparejamiento import Emparejamiento
from app.models.perfil_legal import PerfilLegal
from app.models.detalle_donacion import DetalleDonacion
from app.models.historial_estado_lote import HistorialEstadoLote
from app.models.reporte_consolidado import ReporteConsolidado

print("✅ Todos los modelos cargados correctamente")
print(f"✅ BitacoraAuditoria tiene campos: {[c.name for c in BitacoraAuditoria.__table__.columns]}")
print(f"✅ Emparejamiento tiene campos: {[c.name for c in Emparejamiento.__table__.columns]}")
EOF
```

### 4B. Iniciar el servidor backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Debería iniciarse sin errores. Si hay errores de BD, verifica:
1. Que el DATABASE_URL sea correcto
2. Que PostgreSQL esté ejecutándose
3. Que la BD exista y tenga el schema actualizado

### 4C. Validar con un endpoint simple

```bash
# En otra terminal
curl http://localhost:8000/api/usuarios/perfil

# Debería devolver un error 401 (Unauthorized) porque no tienes token
# Pero NO debería haber errores de BD
```

## Paso 5: Migrar datos (Si usaste Opción B)

Si ya tenías datos en la BD anterior y la migraste, necesitas:

1. **Validar integridad referencial**:
   ```bash
   psql -U usuario -d donaciones_alimentos << EOF
   SELECT COUNT(*) FROM usuarios;
   SELECT COUNT(*) FROM lotes_inventario;
   SELECT COUNT(*) FROM emparejamientos;
   SELECT COUNT(*) FROM bitacora_auditoria;
   EOF
   ```

2. **Verificar que no hay registros huérfanos**:
   ```bash
   psql -U usuario -d donaciones_alimentos << EOF
   -- Verificar FKs válidas
   SELECT COUNT(*) FROM emparejamientos e
   WHERE NOT EXISTS (SELECT 1 FROM lotes_inventario l WHERE l.id_lote = e.id_lote);
   EOF
   ```

## Paso 6: Próximos pasos

Una vez validado, debes implementar:

### 6A. Cifrado de RNC/Cédula (RNF-12)

Actualiza `servicio_admin.py` para:
```python
# Ejemplo pseudocódigo
from app.utils.cifrado import cifrar_aes256gcm, crear_hash_busqueda

rnc_cifrado = cifrar_aes256gcm(rnc)
rnc_hash = crear_hash_busqueda(rnc)
perfil.rnc_cifrado = rnc_cifrado
perfil.rnc_hash_busqueda = rnc_hash
```

### 6B. Cálculo de Hash en Auditoría (Hallazgo 8)

Actualiza `servicio_auditoria.py` para:
```python
import hashlib

def calcular_hash(id_usuario, accion, entidad, detalles, hash_anterior):
    contenido = f"{id_usuario}||{accion}||{entidad}||{detalles}||{hash_anterior}"
    return hashlib.sha256(contenido.encode()).hexdigest()
```

### 6C. FEFO Scoring (OE3)

Implementa en `servicio_emparejamiento.py`:
```python
# prioridad_fefo_score = basado en days_to_expiration
dias_faltantes = (lote.fecha_vencimiento - datetime.now().date()).days
prioridad_fefo_score = 100 - max(0, min(100, dias_faltantes * 2))
```

### 6D. Hash de Reportes (RF-27)

Calcula cuando generas PDF:
```python
import hashlib
hash_documento = hashlib.sha256(pdf_bytes).hexdigest()
reporte.hash_documento = hash_documento
```

## Troubleshooting

### Error: "relation \"bitacora_auditoria\" does not exist"

**Causa**: El schema SQL no se aplicó correctamente

**Solución**:
```bash
# Verifica que las tablas existen
psql -U usuario -d donaciones_alimentos -c "\\dt"

# Si no existen, ejecuta el schema
psql -U usuario -d donaciones_alimentos -f backend/basedatos/01_esquema.sql
```

### Error: "column \"hash_actual\" does not exist"

**Causa**: Ejecutaste el código con la BD antigua

**Solución**:
1. Verifica el DATABASE_URL en `.env`
2. Aplica los cambios incrementales
3. Reinicia el servidor

### Error: "cannot execute UPDATE in a read-only transaction"

**Causa**: Los triggers en `bitacora_auditoria` están bloqueando updates

**Solución**: Esto es correcto, la tabla es append-only. Solo usa INSERT.

### Error de migración de datos con FK a `aprobado_por_operador`

**Causa**: Registros viejos pueden tener valores NULL

**Solución**: Eso está bien, la FK es nullable. Solo tienes que asegurar que si el campo tiene valor, que sea un UUID válido en la tabla usuarios.

## Verificación Final

Ejecuta este script para verificar que todo está bien:

```bash
cd backend
python3 << EOF
from sqlalchemy import inspect
from app.database.conexion import motor
from app.models.bitacora_auditoria import BitacoraAuditoria
from app.models.emparejamiento import Emparejamiento
from app.models.perfil_legal import PerfilLegal
from app.models.reporte_consolidado import ReporteConsolidado

inspector = inspect(motor)

def verificar_tabla(tabla_model, tabla_sql):
    print(f"\n📋 Verificando: {tabla_sql}")
    columnas_esperadas = {c.name for c in tabla_model.__table__.columns}
    columnas_reales = {c['name'] for c in inspector.get_columns(tabla_sql)}
    
    faltantes = columnas_esperadas - columnas_reales
    if faltantes:
        print(f"  ❌ Faltan columnas: {faltantes}")
    else:
        print(f"  ✅ Todas las columnas presentes")
    
    return not faltantes

# Verificar
ok = True
ok &= verificar_tabla(BitacoraAuditoria, "bitacora_auditoria")
ok &= verificar_tabla(Emparejamiento, "emparejamientos")
ok &= verificar_tabla(PerfilLegal, "perfiles_legales")
ok &= verificar_tabla(ReporteConsolidado, "reportes_consolidados")

if ok:
    print("\n✅ MIGRACION EXITOSA")
else:
    print("\n❌ ERRORES EN MIGRACION")
EOF
```

## Rollback (Si algo sale mal)

```bash
# Restaurar desde backup
psql -U usuario -d donaciones_alimentos < backup_pre_migracion_2026-08-13.sql

# Verificar
psql -U usuario -d donaciones_alimentos -c "SELECT COUNT(*) FROM usuarios;"
```

---

**Documentación**: Ver `MIGRACION_BD_RESUMEN.md` para detalles técnicos completos.
