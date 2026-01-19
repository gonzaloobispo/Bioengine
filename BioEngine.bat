@echo off
title Lanzador Bio-Engine Gonzalo
cls
cd /d "C:\BioEngine_Gonzalo"

echo ======================================================
echo          Bio-Engine: Inteligencia Biomecanica
echo ======================================================
echo.
echo 1. Abrir Dashboard en la NUBE (Recomendado)
echo 2. Abrir Dashboard LOCAL (Para mantenimiento/dev)
echo 3. Solo Sincronizar Datos (Sin abrir navegador)
echo 4. Salir
echo.
set /p choice="Selecciona una opcion (1-4): "

if "%choice%"=="1" (
    echo Lanzando Dashboard en la Nube...
    start https://bioengine-gonzalo.streamlit.app
    goto end
)

if "%choice%"=="2" (
    echo Sincronizando datos locales...
    python super_merger.py
    echo Lanzando Dashboard Local...
    start /b python -m streamlit run dashboard.py
    goto end
)

if "%choice%"=="3" (
    echo Sincronizando datos locales...
    python super_merger.py
    echo Sincronizacion completada.
    pause
    goto end
)

if "%choice%"=="4" exit

:end
echo ✅ Proceso finalizado.
timeout /t 5