@echo off
REM ============================================
REM Iniciar Frontend Vite / 启动前端
REM Doble clic para arrancar / 双击启动
REM ============================================
cd /d "%~dp0frontend"

echo ========================================
echo   Limpiando puerto 5173...
echo ========================================
REM Matar proceso viejo si existe / 杀掉旧进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173.*LISTENING" 2^>nul') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

echo ========================================
echo   Iniciando Frontend (Vite + React)
echo   Abrir: http://localhost:5173
echo ========================================
echo.

call npm run dev

pause
