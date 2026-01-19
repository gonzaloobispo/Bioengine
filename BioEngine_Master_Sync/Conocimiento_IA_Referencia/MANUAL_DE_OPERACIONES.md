# Manual de Operaciones: Bio-Engine v2.0 (Actualizado: 19-01-2026)

> **📊 IMPORTANTE:** Este manual refleja el estado ACTUAL del proyecto. Para ver tareas pendientes, consulta `ESTADO_ACTUAL.md`.

## 1. Visión y Objetivo del Proyecto

### Misión
Unificar todas las fuentes de datos biomecánicos y de salud (Garmin, With ings, Apple Health, Runkeeper, PesoBook, calendarios de carreras) en un único **Data Warehouse** con **Asistente IA integrado** para el análisis de rendimiento, la prevención de lesiones y la gestión de activos deportivos.

### Usuario Clave
Gonzalo, con un perfil analítico (Contador) y necesidades biomecánicas específicas (pronación severa, riesgo en rodilla derecha). El sistema debe hablar un lenguaje de eficiencia, ROI (Retorno de Inversión) y auditoría.

### Objetivo Final
Transformar datos crudos y dispersos en **inteligencia accionable** a través de un **asistente IA conversacional**. El dashboard no es un reporte, es un **consultor biomecánico** que detecta riesgos, aprende de tus patrones y ofrece recomendaciones personalizadas.

---

## 2. ✅ FUNCIONALIDADES COMPLETADAS (Fase 1 + Chat IA)

### **Core ETL System**
- ✅ Extracción automática de APIs (Garmin, Withings)
- ✅ Procesamiento de datos históricos (Apple Health, Runkeeper, PesoBook)
- ✅ Fusión inteligente de datos (`super_merger.py`)
- ✅ Dashboard interactivo con Streamlit
- ✅ Gestión de calzado y eventos deportivos
- ✅ KPIs de rendimiento y ROI deportivo

### **🤖 Asistente IA (NUEVO)**
- ✅ **Chat conversacional con Gemini API**
- ✅ **Modificación de plan vía chat** - Di "pon ciclismo hoy" y lo cambia
- ✅ **Tracking automático de dolor** - Registra cuando mencionas "rodilla bien"
- ✅ **Alertas inteligentes** - Tendinosis, sobreentrenamiento, desgaste zapatillas
- ✅ **Memoria contextual** - El asistente recuerda tus patrones y preferencias
  - Sistema aprende correlaciones (ej: "Ciclismo → No dolor")
  - Historial de conversaciones relevantes
  - Perfil biomecánico persistente

---

## 3. Arquitectura del Sistema Actualizada

### Diagrama de Flujo COMPLETO (con IA)
```
┌─────────────────┐
│  Fuentes Datos  │
│ (APIs + Legacy) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Extracción     │
│  bio_engine.py  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Transformación  │
│super_merger.py  │
└────────┬────────┘
         │
         ▼
┌──────────────────────────┐
│   Data Warehouse (CSV)   │
│   + user_context.json    │ ← NUEVO
│   + dolor_rodilla.json   │ ← NUEVO
└─────────┬────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│      Dashboard + Chat IA        │
│  ┌───────────┐  ┌────────────┐ │
│  │Visualiz.  │  │Chat Gemini │ │
│  │(Streamlit)│  │+ Memoria   │ │
│  └───────────┘  └────────────┘ │
└─────────────────────────────────┘
```

### Componentes Clave NUEVOS
- **`trainer_assistant.py`**: Motor de análisis biomecánico con alertas inteligentes
- **`llm_client.py`**: Cliente Gemini API con memoria conversacional
- **`context_manager.py`**: Gestor de memoria contextual persistente
- **`dashboard_components.py`**: Componentes UI incluyendo chat interface
- **`data_cloud_sync/`**: Carpeta para datos persistentes (contexto, dolor)

---

## 4. Manual de Operaciones y Mantenimiento

### ¿Cómo realizar una actualización diaria?
1. Abre el dashboard: `streamlit run dashboard.py`
2. En la barra lateral, presiona **"🔄 Sincronizar"**
3. El sistema:
   - Descarga datos de Garmin y Withings
   - Actualiza archivos maestros
   - Refresca el dashboard automáticamente

### ¿Cómo usar el Chat IA?
El chat está integrado en el dashboard principal. Puedes:

**Modificar el plan:**
- "Pon ciclismo hoy" → Cambia la rutina del día
- "Planifica fuerza mañana"
- "Cambia a descanso"

**Registrar dolor:**
- "Siento la rodilla bien" → Guarda 0/10 automáticamente
- "Rodilla con dolor nivel 3" → Guarda 3/10

**Análisis y consultas:**
- "¿Cómo fue la sesión de hoy?" → Analiza todos los datos de Garmin
- "¿Qué tal mi semana?"
- "Recomiéndame algo para mañana"

**El asistente recuerda:**
- Tus correlaciones (ej: "Ciclismo te viene bien")
- Conversaciones importantes
- Patrones de entrenamiento

### ¿Cómo agregar una nueva carrera?
1. Abre `data_processed/calendario_gonzalo.csv`
2. Añade una fila: `Fecha,Nombre ,Distancia Oficial,Tipo,ZAPATOS`
3. Guarda y sincroniza

### Resolución de Problemas Comunes
- **`PermissionError`**: Cierra archivos Excel abiertos
- **"No veo datos antiguos"**: Ajusta filtro "Analizar desde"
- **Error de autenticación API**: Verifica credenciales en `.streamlit/secrets.toml`
- **Chat no responde**: Verifica `GEMINI_API_KEY` en secrets

---

## 5. Hoja de Ruta (Roadmap)

### ✅ **Fase 1: COMPLETADA** (100%)
- ✅ Integración de todas las fuentes de datos
- ✅ Análisis de rendimiento (KPIs, ROI por deporte)
- ✅ Gestión de activos de calzado
- ✅ Auditoría de riesgo biomecánico
- ✅ **Chat IA con Gemini (NUEVO)**
- ✅ **Memoria contextual persistente (NUEVO)**
- ✅ **Modificación de plan vía chat (NUEVO)**
- ✅ **Tracking automático dolor rodilla (NUEVO)**

### 🚧 **Fase 1.5: Refinamiento IA** (En progreso - 80%)
- ✅ Estructura de memoria contextual
- ✅ Integración con LLM
- ⏳ Auto-actualización de estadísticas al sincronizar
- ⏳ Detección automática de patrones (ML)
- ⏳ Logging de conversaciones importantes

### 📋 **Fase 2: Análisis de Recuperación** (Pendiente)
- [ ] **Integrar Datos de Sueño**: Garmin/Withings
- [ ] **Analizar HRV**: Variabilidad Cardíaca
- [ ] **Métrica "Déficit de Recuperación"**
- [ ] **Alertas de sobreentrenamiento** (carga + sueño)

### 📋 **Fase 3: Cloud Sync** (Pendiente - Proyecto Grande)
- [ ] Migración CSV → JSON → Google Sheets
- [ ] Google Drive API
- [ ] Sincronización bidireccional
- [ ] Funciones móviles (dolor, edición rutinas)

### 📋 **Fase 4: Análisis Nutricional** (Roadmap futuro)
- [ ] Conectar MyFitnessPal
- [ ] Balance energético (calorías in/out)
- [ ] Macronutrientes

### 📋 **Fase 5: Automatización** (Roadmap futuro)
- [ ] Ejecución automática diaria
- [ ] Notificaciones Email/WhatsApp
- [ ] Resúmenes automáticos

---

## 6. Nuevos Archivos de Datos

### Datos Persistentes (`data_cloud_sync/`)
- **`user_context.json`**: Contexto del usuario
  - Perfil biomecánico
  - Estadísticas últimos 30 días
  - Insights aprendidos (patrones detectados)
  - Conversaciones relevantes

- **`dolor_rodilla.json`**: Historial de dolor
  - Fecha, hora, intensidad (0-10)
  - Nota textual
  - Vía de registro (chat/manual)

---

## 7. Configuración de Secrets (Streamlit Cloud)

En `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "tu-api-key-de-google"

[passwords]
gonzalo = "$2b$12$hash_generado..."
```

---

## 8. Acceso Móvil

La app está desplegada en **Streamlit Cloud** y es accesible desde cualquier dispositivo.

**Para mejor experiencia en iPhone:**
1. Abre la app en Safari
2. Tap en "Compartir"
3. Selecciona "Agregar a pantalla de inicio"
4. La app se comportará como nativa y mantendrá mejor la sesión

⚠️ **Nota:** Debido a limitaciones de Streamlit Cloud, las cookies no persisten perfectamente. Puede requerir re-login al refrescar (en móvil funciona mejor).

---

## 9. Para Desarrolladores

### Estructura de Módulos
- `dashboard.py`: Entry point, UI principal
- `trainer_assistant.py`: Lógica biomecánica + alertas
- `llm_client.py`: Cliente Gemini con prompts especializados
- `context_manager.py`: CRUD de memoria contextual
- `cloud_sync.py`: Orquestador de sincronización
- `super_merger.py`: Motor de fusión de datos

### Testing
```bash
python -m pytest tests/
```

### Deployment
Ver `DEPLOYMENT_GUIDE.md` para instrucciones completas.

---

**Última actualización:** 19 de Enero de 2026  
**Versión:** 2.0 (con Chat IA y Memoria Contextual)

---

📋 **Ver también:**
- `ESTADO_ACTUAL.md` - Estado completo y tareas pendientes
- `README.md` - Instalación y setup
- `DEPLOYMENT_GUIDE.md` - Deployment a Streamlit Cloud
