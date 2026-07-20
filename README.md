# Donaciones de Alimentos RD

Sistema web para la gestión y optimización de donaciones de alimentos en la República Dominicana: registro de donantes/receptores/bancos, inventario con FEFO, emparejamiento geoespacial (PostGIS) y reportes, cumpliendo la normativa dominicana.

## Stack

- **Frontend**: React 19 + Vite + Tailwind CSS
- **Backend**: Python 3.11 + FastAPI
- **Base de datos**: PostgreSQL 18 + PostGIS

## Requisitos previos

| Herramienta | Versión | Notas |
|---|---|---|
| Python | 3.11+ | Con `pip` y `venv` |
| Node.js | 18+ (probado con 22) | Incluye `npm` |
| PostgreSQL | 18 | Con la extensión **PostGIS** (instalable con Stack Builder) |

## Puesta en marcha rápida (Windows / PowerShell)

### 1. Base de datos
1. Instala **PostgreSQL 18** y, mediante *Stack Builder*, la extensión **PostGIS**.
2. Anota la contraseña del usuario `postgres` (la pedirá el paso siguiente).

### 2. Backend
```powershell
cd backend
python -m venv venv                                   # solo la primera vez
.\venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env                           # crea tu .env
# Edita backend\.env y coloca tu contraseña en BD_CONTRASENA
.\venv\Scripts\python.exe scripts\inicializar_bd.py   # crea BD, tablas y datos base
.\venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```
API en http://127.0.0.1:8000 (documentación interactiva en `/docs`).

### 3. Frontend
```powershell
cd frontend
npm install
npm run dev
```
Aplicación en http://localhost:5173

## Documentación

Ver [docs/](docs/README.md): requisitos, arquitectura, guía de diseño, plan de desarrollo, estándares de código, seguridad y **configuración de entorno** ([es](docs/es/07-configuracion-entorno.md) · [zh](docs/zh/07-环境配置.md)).

Guía de trabajo del proyecto: [CLAUDE.md](CLAUDE.md). Bitácora diaria: [bitacora-desarrollo/](bitacora-desarrollo/).

## Seguridad

La contraseña de la base de datos y las claves se colocan en `backend/.env`, que **no se sube al repositorio** (está en `.gitignore`). Usa `backend/.env.example` como plantilla.
