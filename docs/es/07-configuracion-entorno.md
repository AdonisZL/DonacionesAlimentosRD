# 07 — Configuración del Entorno

Guía para dejar el proyecto funcionando en una máquina nueva (para todo el equipo).

## 1. Requisitos previos

| Herramienta | Versión | Notas |
|---|---|---|
| Python | 3.11+ | Con `pip` y `venv` |
| Node.js | 18+ (probado con 22.14) | Incluye `npm` |
| PostgreSQL | 18 | Con la extensión **PostGIS** |
| Git | cualquiera | Para clonar el repositorio |

Verificar versiones:
```powershell
python --version
node --version
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --version
```

## 2. Base de datos (PostgreSQL + PostGIS)

1. Instalar **PostgreSQL 18** desde el instalador oficial.
2. Durante la instalación se define la contraseña del usuario `postgres`: **anótala**.
3. Al final, abrir **Stack Builder** e instalar **PostGIS** (categoría *Spatial Extensions*).
4. Verificar que existen las extensiones:
   ```powershell
   Test-Path 'C:\Program Files\PostgreSQL\18\share\extension\postgis.control'
   Test-Path 'C:\Program Files\PostgreSQL\18\share\extension\uuid-ossp.control'
   ```
   Ambas deben devolver `True`.

> No hace falta crear la base manualmente: el script `scripts/inicializar_bd.py` la crea.

## 3. Backend (FastAPI)

```powershell
cd backend
python -m venv venv                                   # solo la primera vez
.\venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```
Editar `backend\.env` y poner la contraseña real en `BD_CONTRASENA`.

Inicializar la base de datos (crea BD, 22 tablas y datos semilla):
```powershell
.\venv\Scripts\python.exe scripts\inicializar_bd.py
.\venv\Scripts\python.exe scripts\verificar_bd.py     # opcional: comprueba el estado
```

Crear el usuario administrador (**obligatorio tras inicializar**):
```powershell
.\venv\Scripts\python.exe scripts\crear_admin.py
```
> Admin por defecto: `admin.demo@ejemplo.com` / `AdminRD2026!`.
> En producción **cambia la contraseña**. El rol administrador no se puede auto-registrar vía API (RF-28).

(Opcional) Insertar datos de demostración para probar:
```powershell
.\venv\Scripts\python.exe scripts\datos_demo.py
```
> Requiere la API corriendo (`uvicorn`). Crea usuarios demo, productos, lotes y emparejamientos.

Arrancar la API:
```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

### Dependencias del backend
Están en `backend/requirements.txt`. Principales paquetes:
| Paquete | Propósito |
|---|---|
| fastapi, uvicorn | Framework web y servidor |
| SQLAlchemy, psycopg2-binary | ORM y driver PostgreSQL |
| GeoAlchemy2 | Soporte geoespacial PostGIS |
| Pydantic, pydantic-settings | Validación de datos y configuración |
| python-dotenv | Lectura de variables `.env` |
| bcrypt, python-jose, python-multipart | Hash de contraseñas, tokens JWT, parsing de formularios |
| email-validator | Validación de formato de email |

## 4. Frontend (React + Vite)

```powershell
cd frontend
npm install
npm run dev
```
La app queda en http://localhost:5173 y habla con la API en http://127.0.0.1:8000.

### Variables de entorno del frontend
El frontend usa la variable `VITE_URL_API` para apuntar a la API del backend (por defecto `http://127.0.0.1:8000`).
Si necesitas cambiarla, crea `frontend\.env`:
```
VITE_URL_API=http://127.0.0.1:8000
```
> Si el backend corre en otro puerto o host, modifica esta variable.

### Fuentes e iconos (dependencia de red)
El frontend carga **Google Fonts** (Hanken Grotesk + Inter) e iconos **Material Symbols**.
La primera carga requiere conexión a internet. En entornos sin red, las fuentes usarán el fallback del sistema (no afecta la funcionalidad).

> El archivo `frontend\.env.example` contiene la plantilla con la variable `VITE_URL_API` y su valor por defecto. Cópialo como `.env` si necesitas cambiarla.

## 5. Variables de entorno

### Variables del backend (`.env`)

`backend/.env` (a partir de `.env.example`):

| Variable | Descripción | Ejemplo |
|---|---|---|
| `BD_HOST` | Host de PostgreSQL | `localhost` |
| `BD_PUERTO` | Puerto de PostgreSQL | `5432` |
| `BD_NOMBRE` | Nombre de la base de datos | `donaciones_alimentos` |
| `BD_USUARIO` | Usuario de la BD | `postgres` |
| `BD_CONTRASENA` | Contraseña de la BD | `tu_contraseña_de_postgres` |
| `JWT_SECRETO` | Clave secreta para firmar JWT | `una_clave_larga_aleatoria_y_secreta` |
| `JWT_ALGORITMO` | Algoritmo de firma JWT | `HS256` |
| `JWT_MINUTOS_EXPIRACION` | Expiración de tokens (minutos) | `60` |

⚠️ **Advertencias de seguridad**:
- **`JWT_SECRETO`** en producción **debe** ser una cadena larga y aleatoria (generar con `openssl rand -hex 32`).
- Nunca subas `.env` al repositorio (ya está en `.gitignore`).
- La contraseña del admin por defecto (`AdminRD2026!`) **debe cambiarse** en producción.

### Variables del frontend (`frontend/.env`)

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `VITE_URL_API` | URL base de la API backend | `http://127.0.0.1:8000` |

### Variables hardcodeadas (migración pendiente a `.env`)
| Variable | Valor actual | Ubicación | Nota |
|---|---|---|---|
| `URL_FRONTEND` | `http://localhost:5173` | `app/services/servicio_autenticacion.py` | URL del frontend para enlaces de correo. **Próximamente se moverá a `.env`** |

## 6. Servicios externos (todos simulados, sin configuración)

En la fase actual, todos los servicios externos funcionan en modo **simulado**, **sin necesidad de API Keys**:

| Servicio | Estado | Descripción |
|---|---|---|
| Gemini IA | 🧪 Simulado | `servicio_ia.py` genera justificaciones deterministas, sin llamar a Google |
| Google Sheets | 🧪 Simulado | Aún no integrado, los reportes solo devuelven JSON |
| Correo (SMTP) | 🧪 Simulado | `servicio_correo.py` imprime los correos en la consola del backend |
| Mapas | 🧪 Simulado | Se usa PostGIS para cálculos geográficos, sin API externa de mapas |

> Cuando se integren los servicios reales, las API Keys irán en `.env` y se actualizará este documento.

## 7. Gestión del servicio PostgreSQL

PostgreSQL se ejecuta como servicio de Windows. Para verificar su estado:
```powershell
Get-Service -Name "postgresql-x64-18" | Select-Object Status,StartType
```
Si no está corriendo, iniciarlo:
```powershell
Start-Service -Name "postgresql-x64-18"
```
> Se requieren **permisos de administrador** para iniciar/detener el servicio. Se recomienda configurarlo como inicio automático: `Set-Service -Name "postgresql-x64-18" -StartupType Automatic`.

## 8. Problemas comunes

| Problema | Causa / Solución |
|---|---|
| `python` abre la Microsoft Store | El alias de Windows. Usa el Python del venv: `.\venv\Scripts\python.exe`. |
| `psql` no se reconoce | No está en el PATH. Usa la ruta completa `C:\Program Files\PostgreSQL\18\bin\psql.exe`. |
| Error de conexión a la BD | Revisa `BD_CONTRASENA` en `.env` y que el servicio `postgresql-x64-18` esté *Running*. |
| `CREATE EXTENSION postgis` falla | PostGIS no está instalado. Instálalo con Stack Builder. |
| Puerto 8000/5173 ocupado | Cierra el proceso previo o cambia el puerto (`--port` / `vite --port`). |
| CORS en el navegador | El backend permite `http://localhost:5173` y `http://127.0.0.1:5173` (ver `app/main.py`). |
| Fuentes o iconos no se ven | Requiere conexión a internet para Google Fonts + Material Symbols; una vez en caché funciona offline. |
| No se puede iniciar sesión como admin | Confirma que ejecutaste `crear_admin.py`. La contraseña distingue mayúsculas/minúsculas. |
