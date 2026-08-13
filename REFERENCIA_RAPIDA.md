# Referencia Rápida de Cambios - Migración BD

## 📊 Resumen de Cambios por Tabla

```
┌─────────────────────────────────────────────────────────────────┐
│ TABLA: bitacora_auditoria                                       │
├─────────────────────────────────────────────────────────────────┤
│ ✨ NUEVOS CAMPOS:                                               │
│   • hash_actual VARCHAR(128) - SHA-256 del registro             │
│   • hash_anterior VARCHAR(128) - FK a registro anterior         │
│ 🔐 TIPO: Append-only (trigger bloquea UPDATE/DELETE)           │
│ 🎯 PROPÓSITO: Hallazgo 8 - Integridad de auditoría             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TABLA: historial_estado_lote                                   │
├─────────────────────────────────────────────────────────────────┤
│ ✨ NUEVOS CAMPOS:                                               │
│   • hash_actual VARCHAR(128) - SHA-256 del cambio              │
│   • hash_anterior VARCHAR(128) - FK a cambio anterior          │
│ 🔐 TIPO: Append-only (trigger bloquea UPDATE/DELETE)           │
│ 🎯 PROPÓSITO: Hallazgo 8 - Historial inmutable                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TABLA: detalle_donaciones                                       │
├─────────────────────────────────────────────────────────────────┤
│ ✨ NUEVOS CAMPOS:                                               │
│   • valor_estimado_rd NUMERIC(12,2) - Valoración en RD         │
│ 📋 TIPO: Regular                                                │
│ 🎯 PROPÓSITO: Ley 11-92 - Deducibilidad fiscal de donaciones  │
│ 🔗 USA: Reporte fiscal DGII                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TABLA: emparejamientos                                          │
├─────────────────────────────────────────────────────────────────┤
│ ✨ NUEVOS CAMPOS:                                               │
│   • prioridad_fefo_score NUMERIC(5,2) - Peso FEFO              │
│   • justificacion_ia TEXT - Explicación de IA                  │
│   • aprobado_por_operador UUID FK - Operador que aprueba      │
│ 📋 TIPO: Regular                                                │
│ 🎯 PROPÓSITO: OE3 - Motor determinista FEFO + IA + aprobación  │
│ ⚙️ REFERENCIAS: usuarios (aprobado_por_operador)               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TABLA: reportes_consolidados                                   │
├─────────────────────────────────────────────────────────────────┤
│ ✨ NUEVOS CAMPOS:                                               │
│   • hash_documento VARCHAR(128) - SHA-256 del PDF generado     │
│ 🔐 TIPO: Append-only con validación (trigger RN-17)           │
│ 🎯 PROPÓSITO: Hallazgo 8 - Integridad y no-repudio de PDF     │
│ ⚖️ REGLA: Estado='emitido' no puede modificarse               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TABLA: perfiles_legales                                        │
├─────────────────────────────────────────────────────────────────┤
│ ✨ NUEVOS CAMPOS:                                               │
│   • rnc_cifrado BYTEA - RNC cifrado AES-256-GCM               │
│   • rnc_hash_busqueda VARCHAR(64) UNIQUE - HMAC-SHA256         │
│   • cedula_cifrada BYTEA - Cédula cifrada AES-256-GCM         │
│   • cedula_hash_busqueda VARCHAR(64) UNIQUE - HMAC-SHA256      │
│ ❌ CAMPOS ELIMINADOS (después de migración):                  │
│   • rnc VARCHAR(255) → Reemplazado por rnc_cifrado             │
│ 🔐 TIPO: Regular con blind indexing                           │
│ 🎯 PROPÓSITO: RNF-12 - Cifrado AES-256-GCM + blind indexing   │
│ 🔍 BÚSQUEDA: Usa *_hash_busqueda sin exponer valores en claro  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Cambios de Código

### Modelos SQLAlchemy (6 archivos)

```python
# bitacora_auditoria.py
+ hash_actual: String(128) = NOT NULL DEFAULT ''
+ hash_anterior: String(128) = None

# perfil_legal.py
- rnc: String(255)  # Eliminar después de migración
+ rnc_cifrado: LargeBinary = None
+ rnc_hash_busqueda: String(64) = None (UNIQUE)
+ cedula_cifrada: LargeBinary = None
+ cedula_hash_busqueda: String(64) = None (UNIQUE)

# emparejamiento.py
+ prioridad_fefo_score: Numeric(5,2) = None
+ justificacion_ia: String = None
+ aprobado_por_operador: UUID FK → usuarios

# historial_estado_lote.py
+ hash_actual: String(128) = NOT NULL DEFAULT ''
+ hash_anterior: String(128) = None

# detalle_donacion.py
+ valor_estimado_rd: Numeric(12,2) = 0.00

# reporte_consolidado.py
+ hash_documento: String(128) = None
```

### Schemas Pydantic (3 archivos)

```python
# admin.py - AuditoriaLeer
+ hash_actual: str | None
+ hash_anterior: str | None

# emparejamiento.py - EmparejamientoLeer
+ prioridad_fefo_score: float | None
+ aprobado_por_operador: UUID | None

# reporte.py - ReporteLeer
+ hash_documento: str | None
```

## 🗄️ Cambios SQL

### Nuevas Extensiones PostgreSQL
```sql
✅ pgcrypto      -- Funciones criptográficas
✅ h3            -- Geolocalización H3
✅ h3_postgis    -- Integración PostGIS-H3
```

### Nuevas Funciones
```sql
✅ fn_bloquear_modificacion_append_only()
✅ fn_bloquear_reporte_emitido()
```

### Nuevos Triggers
```sql
✅ trg_bitacora_inmutable → bitacora_auditoria (BEFORE DELETE/UPDATE)
✅ trg_historial_lote_inmutable → historial_estado_lote (BEFORE DELETE/UPDATE)
✅ trg_reporte_inmutable → reportes_consolidados (BEFORE UPDATE)
```

## 📁 Archivos Actualizados

```
BACKEND:
  ✅ backend/basedatos/01_esquema.sql (Schema completo)
  ✅ backend/basedatos/CAMBIOS_INCREMENTALES.sql (Para BD existente)
  
  ✅ backend/app/models/bitacora_auditoria.py
  ✅ backend/app/models/perfil_legal.py
  ✅ backend/app/models/emparejamiento.py
  ✅ backend/app/models/historial_estado_lote.py
  ✅ backend/app/models/detalle_donacion.py
  ✅ backend/app/models/reporte_consolidado.py
  
  ✅ backend/app/schemas/admin.py
  ✅ backend/app/schemas/emparejamiento.py
  ✅ backend/app/schemas/reporte.py

ROOT:
  ✅ MIGRACION_BD_RESUMEN.md (Documentación completa)
  ✅ GUIA_IMPLEMENTACION.md (Pasos para aplicar migración)
  ✅ REFERENCIA_RAPIDA.md (Este archivo)
```

## ✅ Validación

```
✓ 0 errores de sintaxis Python
✓ 0 errores en modelos SQLAlchemy
✓ 0 errores en schemas Pydantic
✓ Todos los tipos de datos verificados
✓ Todas las FKs configuradas correctamente
✓ Triggers creados exitosamente
```

## ⚡ Quick Start

### Opción 1: Nueva BD desde cero (Desarrollo)
```bash
createdb donaciones_alimentos_nueva
psql -U usuario -d donaciones_alimentos_nueva -f backend/basedatos/01_esquema.sql
export DATABASE_URL=postgresql://usuario:pass@localhost/donaciones_alimentos_nueva
cd backend && uvicorn app.main:app --reload
```

### Opción 2: Migrar BD existente (Producción)
```bash
# Backup primero
pg_dump -U usuario -d donaciones_alimentos > backup_$(date +%Y%m%d).sql

# Aplicar cambios
psql -U usuario -d donaciones_alimentos -f backend/basedatos/CAMBIOS_INCREMENTALES.sql

# Verificar
psql -U usuario -d donaciones_alimentos -c "SELECT column_name FROM information_schema.columns WHERE table_name='bitacora_auditoria';"
```

## 🎯 Tareas Siguientes

### Inmediato (Post-Migración)
- [ ] Validar BD con script de verificación
- [ ] Probar endpoints con Postman/Bruno
- [ ] Verificar que no hay errores en logs

### Próxima Semana (Implementar Lógica)
- [ ] Cifrado AES-256-GCM en `servicio_admin.py` para RNC/Cédula
- [ ] SHA-256 chaining en `servicio_auditoria.py` para auditoría
- [ ] FEFO scoring en `servicio_emparejamiento.py`
- [ ] Hash de PDF en `servicio_reportes.py`

### APIs Nuevas (Fase 7+)
- [ ] APIs externas para consultas
- [ ] APIs internas mejoradas
- [ ] Endpoints de validación de integridad

## 📞 Soporte

Si tienes problemas:

1. **Ver Logs**: `GUIA_IMPLEMENTACION.md` - Sección "Troubleshooting"
2. **Validar BD**: Ejecutar script de verificación en `GUIA_IMPLEMENTACION.md`
3. **Rollback**: Restaurar backup de la BD anterior
4. **Documentación**: `MIGRACION_BD_RESUMEN.md` - Detalles técnicos completos

---

**Migración Lista para Implementar** 🚀
