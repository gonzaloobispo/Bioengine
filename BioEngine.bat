@echo off
title Lanzador Bio-Engine Gonzalo
cls
cd /d "C:\BioEngine_Gonzalo"

echo Iniciando Bio-Engine...
echo  Paso 1: Sincronizando datos de Nube y Calzado...
python super_merger.py

echo  Paso 2: Generando Plan Semanal Inteligente (Fase: Rehab/Construccion)...
python init_plan.py

echo  Paso 3: Lanzando Dashboard en el navegador...
start /b python -m streamlit run dashboard.py

echo ✅ Todo listo. Podes cerrar esta ventana cuando termines de usar el Dashboard.
pause