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

Arrancar la API:
```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

### Dependencias del backend
Están en `backend/requirements.txt` (FastAPI, Uvicorn, SQLAlchemy, psycopg2-binary, Pydantic, pydantic-settings, python-dotenv, bcrypt, python-jose, python-multipart, email-validator).

## 4. Frontend (React + Vite)

```powershell
cd frontend
npm install
npm run dev
```
La app queda en http://localhost:5173 y habla con la API en http://127.0.0.1:8000.

## 5. Variables de entorno

`backend/.env` (a partir de `.env.example`):
```
BD_HOST=localhost
BD_PUERTO=5432
BD_NOMBRE=donaciones_alimentos
BD_USUARIO=postgres
BD_CONTRASENA=tu_contraseña
JWT_SECRETO=una_clave_larga_y_secreta
JWT_ALGORITMO=HS256
JWT_MINUTOS_EXPIRACION=60
```
Nunca subas `.env` al repositorio.

## 6. Problemas comunes

| Problema | Causa / Solución |
|---|---|
| `python` abre la Microsoft Store | El alias de Windows. Usa el Python del venv: `.\venv\Scripts\python.exe`. |
| `psql` no se reconoce | No está en el PATH. Usa la ruta completa `C:\Program Files\PostgreSQL\18\bin\psql.exe`. |
| Error de conexión a la BD | Revisa `BD_CONTRASENA` en `.env` y que el servicio `postgresql-x64-18` esté *Running*. |
| `CREATE EXTENSION postgis` falla | PostGIS no está instalado. Instálalo con Stack Builder. |
| Puerto 8000/5173 ocupado | Cierra el proceso previo o cambia el puerto (`--port` / `vite --port`). |
| CORS en el navegador | El backend permite `http://localhost:5173` y `http://127.0.0.1:5173` (ver `app/main.py`). |
