# Bio-Engine – Informe Integral del Sistema

Este documento resume la arquitectura completa, los componentes y la operativa diaria del proyecto Bio-Engine. Reúne y organiza la información dispersa en README, arquitectura, manuales y scripts para que cualquier desarrollador o analista pueda entender la plataforma sin buscar en múltiples archivos.

## 1. Propósito y Alcance
- **Objetivo central:** consolidar datos biométricos y deportivos (Garmin, Withings, Apple Health, Runkeeper, PesoBook, calendario de carreras) en un Data Warehouse local (`data_processed/`) y transformarlos en alertas/insights para decisiones biomecánicas.
- **Usuario principal:** Gonzalo (perfil ejecutivo con foco contable). El sistema responde en términos de eficiencia, ROI deportivo y control de riesgos (inflamación rodilla derecha, amortización de calzado).

## 2. Flujo ETL completo
1. **Extract (Ingesta):**
   - `bio_engine.py`: descarga historial de Garmin (batch de 100) y guarda `data_processed/historial_garmin_raw.csv`.
   - `withings_auth.py` (vía `bio_engine.update_withings` o dashboard) y `cloud_sync.py`: sincronizan peso y métricas corporales, produciendo `historial_withings_raw.csv`.
   - Módulos legacy (`legacy_importer.py`, `cda_importer.py`, `pesobook_importer.py`, `runkeeper_extractor.py`) procesan archivos XML/CSV históricos almacenados bajo `data_raw/`.
2. **Transform:**
   - `super_merger.py` unifica todas las fuentes.
     - `fusionar_deportes()` consolida Garmin/Runkeeper/Apple en `historial_deportivo_total_full.csv`, normaliza columnas y asigna calzado/eventos cruzando `data_processed/calendario_gonzalo.*`.
     - `fusionar_peso()` y `fusionar_peso_completo()` generan los maestros `historial_completo_peso_apis.csv` y `historial_completo_peso_full.csv`, aplicando deduplicación diaria y formato regional.
   - `metrics_engine.py` y `audit_*` calculan KPIs (stress score de rodilla, ROI por deporte, análisis gerencial de peso) que luego usa el dashboard.
3. **Load / Visualize:**
   - `dashboard.py` (Streamlit) y `app_bioengine.py` ofrecen dashboards ejecutivos, exportación manual de CSV/XLSX y botones para gatillar sincronización.
   - `reports/` centraliza reportes de texto generados por `report_generator.py` y documentos forenses.

## 3. Topología de archivos
```
BioEngine_Gonzalo/
├── app_bioengine.py          # Dashboard ejecutivo con exportaciones
├── bio_engine.py             # Extracción Garmin/Withings
├── cloud_sync.py             # Orquestación de sincronización diaria
├── super_merger.py           # Motor de fusión maestro (peso + deporte)
├── dashboard.py              # Dashboard Streamlit principal
├── main.py                   # Menú CLI para operaciones manuales
├── config.py                 # Configuración de rutas, credenciales y usuarios
├── metrics_engine.py         # KPIs y lógica de riesgo
├── audit_*.py                # Herramientas de auditoría forense
├── legacy/                   # Parsers e importadores históricos
├── data_raw/                 # Fuentes sin procesar (XML/CSV)
├── data_processed/           # Data Warehouse (CSV maestros, calendario)
└── reports/, config/, ...
```

## 4. Datos y formatos
- **Almacenamiento principal:** archivos CSV dentro de `data_processed/` usando separador `;` y decimal `,`.
- **Maestros clave:**
  - `historial_deportivo_total_full.csv` → sesiones deportivas consolidadas con campos de calzado, stress score y origen.
  - `historial_completo_peso_full.csv` y `historial_completo_peso_apis.csv` → pesos diarios con fuente normalizada.
  - `calendario_gonzalo.csv/xlsx` → tabla de eventos que actúa como catálogo para reglas de calzado.
- **Configuraciones sensibles:** `config.py` define rutas absolutas, credenciales (usar variables de entorno en producción) y perfiles biomecánicos.

## 5. Operación diaria
1. Ejecutar `streamlit run dashboard.py` o doble clic en `BioEngine.bat`.
2. En el dashboard, usar el botón **"Sincronizar Nube"** para llamar a `cloud_sync.py`, que a su vez dispara `bio_engine.update_garmin()` y la actualización de Withings.
3. Al finalizar, correr `super_merger.actualizacion_rapida()` (el dashboard lo hace automáticamente) para refrescar los maestros.
4. Revisar las tarjetas de KPI; si es necesario, descargar CSV/XLSX filtrados desde los botones de exportación (peso y deporte) en `app_bioengine.py`.

## 6. Lógica de negocio esencial
- **Asignación de calzado:** default Brooks Adrenaline GTS 23; overrides por calendario o actividades (Tenis → Babolat Fury 3, otros valores hardcodeados en `super_merger.py`).
- **Alertas de inflamación:** threshold de peso vs. carga diaria evaluado mediante `metrics_engine.calcular_stress_rodilla` y reglas descritas en README/Manual.
- **ROI y eficiencia:** métricas derivadas en `metrics_engine.py` y visualizadas en `dashboard.py`.

## 7. Dependencias
- `requirements.txt` lista librerías principales: pandas, streamlit, plotly, garminconnect, openpyxl, etc.
- Scripts auxiliares (`withings_auth.py`, `withings_token` tools) requieren credenciales OAuth definidas en `config.py` o en `config/withings_tokens.json`.

## 8. Recomendaciones para retomarlo
- Mantener cerrados los CSV maestros mientras corren los procesos (evita `PermissionError`).
- Verificar periódicamente `super_merger.py` para que no elimine históricos al aplicar `drop_duplicates`.
- Versionar `data_processed/` con backups si se agregan nuevas fuentes o reglas.

Este documento puede actuar como ficha de traspaso: incluye qué hace cada módulo, cómo se acoplan y qué datos persisten. Cualquier mejora futura (nuevas fuentes, exportaciones automáticas JSON, etc.) debe respetar este flujo ETL y la carpeta `data_processed/` como repositorio maestro.
