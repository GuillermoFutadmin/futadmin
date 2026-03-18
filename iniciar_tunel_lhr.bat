@echo off
echo ==============================================
echo   Tunel Permanente - FutAdmin (Localhost.Run)
echo ==============================================
echo.
echo Iniciando conexion segura...
echo Espera unos segundos y copia la URL que termina en ".lhr.life"
echo.
ssh -o StrictHostKeyChecking=no -R 80:localhost:5003 nokey@localhost.run
pause
