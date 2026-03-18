@echo off
echo ================================
echo   Tunel Seguro - FutAdmin (Pinggy)
echo ================================
echo.
echo Iniciando conexion con Pinggy...
echo Por favor, copia la URL que empieza con "https://" que aparecera abajo.
echo.
ssh -p 443 -R0:localhost:5003 a.pinggy.io
pause
