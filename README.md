# Bio-Engine: Inteligencia Biomecánica Personalizada

## Descripción

Bio-Engine es un sistema ETL (Extract, Transform, Load) diseñado para unificar datos biométricos de múltiples fuentes (Garmin, Withings, Apple Health, Runkeeper, etc.) en un data warehouse centralizado. Transforma datos crudos en inteligencia accionable para análisis de rendimiento deportivo, prevención de lesiones y gestión de activos biomecánicos.

### Características Principales
- Integración automática con APIs de Garmin Connect y Withings
- Procesamiento de datos históricos de Apple Health, Runkeeper y PesoBook
- Dashboard interactivo con Streamlit para visualización de KPIs
- Auditoría forense de datos para validar integridad
- Gestión inteligente de calzado y eventos deportivos
- Análisis de eficiencia energética y ROI deportivo

## Instalación

### Prerrequisitos
- Python 3.8 o superior
- Credenciales válidas para Garmin Connect y Withings

### Pasos de Instalación
1. Clona o descarga el repositorio:
   ```bash
   git clone <url-del-repo>
   cd BioEngine_Gonzalo
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura las credenciales en `config.py`:
   - Reemplaza `GARMIN_EMAIL` y `GARMIN_PASSWORD` con tus credenciales reales
   - Configura `WITHINGS_CLIENT_ID` y `WITHINGS_CLIENT_SECRET` (obténlos de la app Withings)
   - Asegúrate de que las rutas en `config.py` apunten a tu directorio local

## Configuración

### Credenciales Seguras
Para mayor seguridad, considera usar variables de entorno:
```python
import os
GARMIN_EMAIL = os.getenv('GARMIN_EMAIL')
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD')
```

### Archivos de Datos
- `data_raw/`: Contiene datos crudos de fuentes externas
- `data_processed/`: Almacena archivos maestros procesados
- `config/`: Configuraciones adicionales (perfiles clínicos, tokens)

### Calendario de Carreras
Edita `data_processed/calendario_gonzalo.csv` para agregar carreras futuras o pasadas con formato:
```
Fecha,Nombre ,Distancia Oficial,Tipo,ZAPATOS
2025-01-15,Media Maraton Sevilla,21.1,Carrera,Modelo de Zapatillas
```

## Uso

### Dashboard Interactivo
Ejecuta el dashboard principal:
```bash
streamlit run dashboard.py
```
Accede a `http://localhost:8501` para ver el dashboard con sincronización automática.

### Operaciones Manuales
Usa el panel de control CLI:
```bash
python main.py
```
Opciones disponibles:
1. Actualizar Todo (Cloud + Fusión)
2. Generar Reporte de Texto
3. Generar Dashboard Visual
4. Ver Estado de Sincronización

### Sincronización Diaria
Para actualizar datos automáticamente:
1. Abre el dashboard
2. En la barra lateral, presiona "🔄 Sincronizar Nube"
3. El sistema conectará con APIs y procesará datos

## Arquitectura

### Flujo de Datos ETL
1. **Extract**: `bio_engine.py` y módulos legacy obtienen datos de APIs y archivos
2. **Transform**: `super_merger.py` limpia, enriquece y fusiona datos
3. **Load**: Archivos maestros en `data_processed/`
4. **Visualize**: `dashboard.py` presenta resultados interactivos

### Componentes Clave
- `config.py`: Configuraciones centrales
- `cloud_sync.py`: Coordinador de sincronización
- `audit_pipeline.py`: Validador de integridad
- `super_merger.py`: Motor de fusión inteligente

## Resolución de Problemas

### Errores Comunes
- **PermissionError**: Cierra archivos Excel abiertos antes de sincronizar
- **Errores de autenticación**: Verifica credenciales en `config.py`
- **Datos faltantes**: Asegura que las fechas de filtro incluyan el historial completo

### Logs y Depuración
Los scripts imprimen logs detallados en consola. Para auditorías profundas, ejecuta:
```bash
python audit_pipeline.py
```

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Guías de Desarrollo
- Sigue PEP 8 para estilo de código
- Agrega docstrings a funciones nuevas
- Incluye manejo de errores robusto
- Actualiza `MANUAL_DE_OPERACIONES.md` para cambios operativos

## Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Contacto

Para preguntas o soporte, contacta al desarrollador principal.

---

Ver `MANUAL_DE_OPERACIONES.md` para documentación técnica detallada y procedimientos avanzados.