@echo off
REM ============================================================================
REM ClimAPI Pinggy Tunnel Starter
REM Inicia el tunel Pinggy.io con el comando optimizado
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║              🌐 CLIMAPI DASHBOARD - PINGGY.IO TUNNEL STARTER              ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

REM Verificar si estamos en el directorio correcto
if not exist "dashboard\app.py" (
    echo ❌ Error: dashboard\app.py no encontrado
    echo    Ejecuta este script desde la raiz del proyecto ClimAPI
    pause
    exit /b 1
)

echo 📊 OPCIONES:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   1. 🚀 Iniciar Túnel + Dashboard (2 terminales)
echo   2. 🌐 Solo Túnel Pinggy
echo   3. 📊 Solo Dashboard Streamlit
echo   4. ⚙️  Ver Comando Pinggy
echo   5. ❌ Salir
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set /p choice="Selecciona (1-5): "

if "%choice%"=="1" goto BOTH
if "%choice%"=="2" goto TUNNEL
if "%choice%"=="3" goto DASHBOARD
if "%choice%"=="4" goto COMMAND
if "%choice%"=="5" goto END
echo ❌ Opcion invalida
goto END

:BOTH
cls
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                  🌐 INICIANDO TÚNEL + DASHBOARD                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.
echo 📌 IMPORTANTE:
echo    • Este script inicia el TÚNEL en esta terminal
echo    • Abre OTRA terminal para el DASHBOARD
echo    • Mantén ambas abiertas
echo.
echo 📝 En la otra terminal, ejecuta:
echo    .venv\Scripts\streamlit.exe run dashboard/app.py
echo.
pause
echo.
echo ⏳ Iniciando túnel...
echo.
goto TUNNEL_CMD

:TUNNEL
cls
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                      🌐 INICIANDO TÚNEL PINGGY                             ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.
goto TUNNEL_CMD

:TUNNEL_CMD
echo 🔗 Token:      Fm4hH7kZ8sz+force
echo 🚪 Puerto:     8501
echo 🌐 Destino:    free.pinggy.io
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📡 Ejecutando:
echo.
echo pinggy.exe -p 443 -R0:127.0.0.1:8501 ^
echo   -o StrictHostKeyChecking=no -o ServerAliveInterval=30 ^
echo   Fm4hH7kZ8sz+force@free.pinggy.io
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ⏳ Conectando...
echo.

REM Ejecutar el comando pinggy.exe
pinggy.exe -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io

REM Si pinggy.exe no existe, ofrecer alternativa con SSH
if errorlevel 1 (
    echo.
    echo ⚠️  pinggy.exe no encontrado
    echo.
    echo 💡 Alternativa: Usando SSH
    echo    ssh -R 0:localhost:8501 a.pinggy.io
    echo.
    ssh -R 0:localhost:8501 a.pinggy.io
)

goto END

:DASHBOARD
cls
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                 🎨 INICIANDO DASHBOARD STREAMLIT                           ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.
echo 📍 URL Local: http://localhost:8501
echo.
echo ⏳ Iniciando...
echo.

call .venv\Scripts\streamlit.exe run dashboard/app.py

goto END

:COMMAND
cls
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                    📋 COMANDO PINGGY COMPLETO                              ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🔗 Token Pinggy:  Fm4hH7kZ8sz+force
echo 🌐 Host:          free.pinggy.io
echo 🚪 Puerto Local:  8501
echo.
echo 📝 Comando:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo pinggy.exe -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📖 Documentación:
echo    • START_PINGGY.md - Inicio rápido
echo    • PINGGY_COMMAND.md - Detalles del comando
echo    • PINGGY_GUIDE.md - Documentación completa
echo.
pause
goto MAIN

:MAIN
cls
python pinggy_direct.py
goto END

:END
echo.
pause
exit /b 0
