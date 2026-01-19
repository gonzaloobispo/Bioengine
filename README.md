# Manual de Operaciones: Bio-Engine

## 1. Visión y Objetivo del Proyecto

### Misión
Unificar todas las fuentes de datos biomecánicos y de salud (Garmin, Withings, Apple Health, Runkeeper, PesoBook, calendarios de carreras) en un único **Data Warehouse** para el análisis de rendimiento, la prevención de lesiones y la gestión de activos deportivos.

### Usuario Clave
Gonzalo, con un perfil analítico (Contador) y necesidades biomecánicas específicas (pronación severa, riesgo en rodilla derecha). El sistema debe hablar un lenguaje de eficiencia, ROI (Retorno de Inversión) y auditoría.

### Objetivo Final
Transformar datos crudos y dispersos en **inteligencia accionable**. El dashboard no es un reporte, es un **consultor biomecánico** que detecta riesgos y oportunidades de mejora.

---

## 2. Arquitectura del Sistema

El sistema sigue un flujo de datos claro y robusto (ETL: Extract, Transform, Load).

### Diagrama de Flujo de Datos
1.  **INPUTS (Fuentes Crudas)**:
    *   **APIs Nube**: `cloud_sync.py` se conecta a Garmin Connect y Withings para obtener los datos más recientes.
    *   **Archivos Históricos**: `legacy_importer.py` y otros leen los archivos estáticos (Apple Health XML, PesoBook, Runkeeper) que ya no cambian. *Nota: En modo "rápido", estos se ignoran para mayor velocidad.*
    *   **Calendario de Eventos**: El archivo `data_processed/calendario_gonzalo.csv` actúa como una base de datos de carreras y eventos especiales.

2.  **PROCESAMIENTO (Cerebro del Sistema)**:
    *   `super_merger.py`: Es el consolidador principal. Su función `actualizacion_rapida()` es el corazón del proceso diario. Se encarga de:
        *   **Limpiar datos**: Aplica reglas de negocio (ej. `PESO_MINIMO_GONZALO`).
        *   **Enriquecer datos**: Cruza la información de las APIs con el calendario para etiquetar carreras y calzado.
        *   **Unificar**: Fusiona los datos nuevos con el historial maestro, creando una única fuente de verdad.

3.  **ALMACENAMIENTO (Data Warehouse)**:
    *   La carpeta `data_processed/` contiene los archivos maestros (`historial_deportivo_maestro.csv` y `historial_peso_maestro.csv`). Estos son los activos de datos más importantes del sistema.

4.  **VISUALIZACIÓN (Panel de Mando)**:
    *   `dashboard.py`: Lee los archivos maestros y los presenta de forma interactiva y pedagógica, con métricas, gráficos y conclusiones automáticas.

### Componentes Clave
*   `config.py`: Centraliza todas las configuraciones (credenciales, rutas, umbrales). **Es el único lugar donde debes poner tus contraseñas.**
*   `cloud_sync.py`: El motor que se conecta a la nube.
*   `super_merger.py`: El motor que limpia, enriquece y fusiona los datos.
*   `dashboard.py`: La cara visible del proyecto.

---

## 3. Manual de Operaciones y Mantenimiento

### ¿Cómo realizar una actualización diaria?
Es el proceso que harás cada vez que quieras ver tus datos nuevos.
1.  Abre una terminal (PowerShell) en la carpeta del proyecto: `C:\BioEngine_Gonzalo`.
2.  Ejecuta el comando: `python -m streamlit run dashboard.py`
3.  En el dashboard que se abre en tu navegador, ve a la barra lateral izquierda y presiona el botón **"🔄 Sincronizar Nube"**.
4.  El sistema se conectará a las APIs, procesará los datos y refrescará la pantalla automáticamente.

### ¿Cómo agregar una nueva carrera?
Para que el sistema identifique una carrera futura o pasada y la etiquete correctamente:
1.  Abre el archivo `data_processed/calendario_gonzalo.csv` con Excel o un editor de texto.
2.  Añade una nueva fila con la información requerida. Las columnas son: `Fecha`, `Nombre `, `Distancia Oficial`, `Tipo`, `ZAPATOS`. (¡Ojo con el espacio en `Nombre `!).
3.  Guarda el archivo.
4.  Ejecuta una sincronización en el dashboard para que los cambios se apliquen.

### Resolución de Problemas Comunes
*   **`PermissionError: [Errno 13]`**: Este error significa que un archivo que el sistema necesita escribir (ej. `historial_peso_maestro.csv`) está abierto en otro programa, típicamente Excel. **Solución: Cierra el archivo Excel y vuelve a sincronizar.**
*   **"No veo datos antiguos" / "Faltan Kms"**: Generalmente es un problema de filtros. Asegúrate de que el campo **"Analizar desde"** en la barra lateral esté puesto en una fecha antigua (ej. 2014) para ver todo el historial. Si los filtros se "pegan", usa el botón **"🗑️ Resetear Memoria de Fechas"**.
*   **Error de Sincronización (401 o similar)**: Si falla la conexión a Garmin o Withings, puede ser por un cambio de contraseña o porque el token de Withings expiró de forma definitiva. Verifica tus credenciales en `config.py` o el archivo `withings_tokens.json`.

---

## 4. Hoja de Ruta (Roadmap) Futuro

El Bio-Engine está diseñado para crecer. Estas son las próximas fases lógicas de desarrollo:

*   **Fase Actual (Completada):**
    *   Integración de todas las fuentes de datos.
    *   Análisis de rendimiento (KPIs, ROI por deporte).
    *   Gestión de activos de calzado.
    *   Auditoría de riesgo biomecánico (inflamación de rodilla).

*   **Fase 2: Análisis de Recuperación (Próximos Pasos Sugeridos)**
    *   **Integrar Datos de Sueño**: Conectar a las APIs para obtener horas de sueño, sueño profundo/REM.
    *   **Cruzar Sueño con Carga**: Crear una métrica de "Déficit de Recuperación". Si tienes una carga de entrenamiento alta pero pocas horas de sueño, el sistema emitirá una alerta de riesgo de sobreentrenamiento.
    *   **Analizar Variabilidad Cardíaca (HRV)**: Integrar el HRV nocturno como indicador del estado de tu sistema nervioso y tu preparación para el próximo entrenamiento.

*   **Fase 3: Análisis Nutricional**
    *   **Conectar con MyFitnessPal/Similares**: Integrar la ingesta calórica y de macronutrientes.
    *   **Balance Energético**: Crear un gráfico que compare "Calorías Ingeridas" vs. "Calorías Gastadas" para una gestión precisa del peso.

*   **Fase 4: Automatización y Alertas Proactivas**
    *   **Ejecución Automática**: Configurar el sistema para que se ejecute solo todos los días en un servidor o PC.
    *   **Notificaciones por Email/WhatsApp**: Enviar un resumen diario o alertas críticas ("Riesgo de lesión alto hoy, considera descanso") directamente a tu celular.
