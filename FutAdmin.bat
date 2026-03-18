@echo off
title FutAdmin - Servidor y Tunel
cd /d C:\futadmin

echo ====================================
echo   FutAdmin - Iniciando servicios...
echo ====================================

:: 1. Detener cualquier instancia anterior en el puerto 5003
echo [1/3] Limpiando puerto 5003...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5003 " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak >nul

:: 2. Iniciar el tunel en una ventana separada
echo [2/3] Iniciando Tunel Telegram (LHR)...
start "Tunel Telegram" cmd /k "C:\futadmin\iniciar_tunel_lhr.bat"

timeout /t 2 /nobreak >nul

:: 3. Iniciar el servidor Flask
echo [3/3] Iniciando Servidor Flask en puerto 5003...
echo.
echo Presiona CTRL+C para detener el servidor.
echo.
python app.py
pause
