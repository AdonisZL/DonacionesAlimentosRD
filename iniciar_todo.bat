@echo off
REM ============================================
REM Iniciar TODO el proyecto / 启动全部
REM ============================================
echo.
echo    🚀 Donaciones de Alimentos RD
echo    Iniciando Backend + Frontend...
echo.
echo    Backend : http://127.0.0.1:8000
echo    Frontend: http://localhost:5173
echo.

REM Iniciar backend en ventana separada / 在新窗口启动后端
start "Backend FastAPI" cmd /c "cd /d %~dp0backend && echo Iniciando backend... && C:/Users/Adonl/AppData/Local/Programs/Python/Python311/python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 && pause"

REM Esperar 3 segundos a que el backend levante / 等3秒后端启动
timeout /t 3 /nobreak >nul

REM Iniciar frontend en ventana separada / 在新窗口启动前端
start "Frontend Vite" cmd /c "cd /d %~dp0frontend && echo Iniciando frontend... && echo Abrir: http://localhost:5173 && call npm run dev && pause"

echo.
echo    ✅ Todo iniciado. Abre http://localhost:5173 en el navegador.
echo.
pause
