@echo off
REM ============================================
REM Iniciar Backend FastAPI / 启动后端
REM Doble clic para arrancar / 双击启动
REM ============================================
cd /d "%~dp0backend"

echo ========================================
echo   Limpiando puerto 8000...
echo ========================================
REM Matar proceso viejo si existe / 杀掉旧进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING" 2^>nul') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

echo ========================================
echo   Iniciando Backend (FastAPI)
echo   Puerto: 8000
echo ========================================
echo.

:: Usar Python del sistema (NO "python" porque apunta a Windows Store stub sin uvicorn)
:: 使用系统 Python（不用 "python" 因为指向无 uvicorn 的 Windows Store 存根）
C:/Users/Adonl/AppData/Local/Programs/Python/Python311/python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause
