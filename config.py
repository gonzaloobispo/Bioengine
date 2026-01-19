# config.py - Configuración Maestra del Bio-Engine
import os
from datetime import datetime

# --- 1. RUTAS DEL SISTEMA (File System) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Hacerlo relativo

# Carpetas de Trabajo Locales
DATA_RAW = os.path.join(BASE_DIR, 'data_raw')
DATA_PROCESSED = os.path.join(BASE_DIR, 'data_processed')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

# --- CARPETA MAESTRA DE SINCRONIZACION (Cloud Sync Folder) ---
SYNC_DATA = os.path.join(BASE_DIR, 'BioEngine_Master_Sync')

# Subcarpetas por competencia del usuario
SYNC_BASE_MAESTRA = os.path.join(SYNC_DATA, 'Base_Maestra_Depurada')
SYNC_MEDICA = os.path.join(SYNC_DATA, 'Competencia_Medica')
SYNC_TRAINING = os.path.join(SYNC_DATA, 'Competencia_Entrenamiento')
SYNC_KNOWLEDGE = os.path.join(SYNC_DATA, 'Conocimiento_IA_Referencia')
SYNC_CEREBRO = os.path.join(SYNC_DATA, 'Cerebro_y_Contexto')
SYNC_SISTEMA = os.path.join(SYNC_DATA, 'Sistema_y_APIs')
SYNC_DOCS = os.path.join(SYNC_DATA, 'Documentacion_Original')

# --- ARCHIVOS MAESTROS (La Verdad Contable) ---
CSV_PESO_MAESTRO = os.path.join(SYNC_BASE_MAESTRA, 'historial_completo_peso_full.csv')
CSV_PESO_MAESTRO_HIST = os.path.join(SYNC_BASE_MAESTRA, 'historial_completo_peso.csv')
CSV_PESO_MAESTRO_APIS = os.path.join(SYNC_BASE_MAESTRA, 'historial_completo_peso_apis.csv')
CSV_DEPORTE_MAESTRO = os.path.join(SYNC_BASE_MAESTRA, 'historial_deportivo_total_full.csv')
CSV_RUNKEEPER_LEGACY = os.path.join(SYNC_BASE_MAESTRA, 'historial_runkeeper_puro.csv')
CSV_APPLE_LEGACY = os.path.join(SYNC_BASE_MAESTRA, 'historial_apple_deportes.csv')

# --- CARRERAS ---
SYNC_CARRERAS = os.path.join(SYNC_DATA, 'Historial_Carreras')
CSV_CALENDARIO = os.path.join(SYNC_CARRERAS, 'calendario_gonzalo.csv')
XLSX_CALENDARIO = os.path.join(SYNC_CARRERAS, 'calendario_gonzalo.xlsx')
HISTORIAL_MEDICO_FILE = os.path.join(SYNC_MEDICA, 'historial_medico.json')
DOLOR_RODILLA_FILE = os.path.join(SYNC_MEDICA, 'dolor_rodilla.json')

# --- COMPETENCIA ENTRENAMIENTO ---
PLAN_ENTRENAMIENTO_FILE = os.path.join(SYNC_TRAINING, 'plan_entrenamiento.json')
INVENTARIO_FILE = os.path.join(SYNC_TRAINING, 'inventario.json')

# --- CEREBRO Y CONTEXTO ---
USER_CONTEXT_FILE = os.path.join(SYNC_CEREBRO, 'user_context.json')

# --- SISTEMA Y TOKENS ---
SECRETS_FILE = os.path.join(SYNC_SISTEMA, 'secrets.json')
WITHINGS_TOKEN_FILE = os.path.join(SYNC_SISTEMA, 'withings_tokens.json')
RAW_GARMIN_FILE = os.path.join(SYNC_SISTEMA, 'historial_garmin_raw.csv')
RAW_WITHINGS_FILE = os.path.join(SYNC_SISTEMA, 'historial_withings_raw.csv')

# --- 2. CREDENCIALES (LLAVES DE ACCESO) ---
GARMIN_EMAIL = os.getenv('GARMIN_EMAIL', 'gonzaloobispo@hotmail.com')
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD', 'Gob29041976$')

# WITHINGS (Configuración App Bio-Engine)
WITHINGS_CLIENT_ID = os.getenv('WITHINGS_CLIENT_ID', 'ab42901f472e68a9f8dc6503387ee3a28d9e6ce3b0c71c9a4b097550cb679ce8')
WITHINGS_CLIENT_SECRET = os.getenv('WITHINGS_CLIENT_SECRET', '1cce12d853f3ba00bf06c23a3d776c6666e41bad4010d19dd3045091f3b393a4')
WITHINGS_REDIRECT_URI = "http://localhost:8080/" 

# --- 3. PERFILES DE USUARIO ---
USUARIOS = {
    "Gonzalo": {
        "fecha_nacimiento": "1976-04-29",
        "sexo": "M",
        "altura": 1.76,
        "lesion_rodilla": True, 
        "umbral_dolor": 4 
    }
}

ACTIVE_USER = "Gonzalo"

# --- 4. FUNCIONES DE SOPORTE ---
def get_edad(fecha_str):
    nacimiento = datetime.strptime(fecha_str, "%Y-%m-%d")
    hoy = datetime.now()
    return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))

def get_perfil_activo():
    return USUARIOS[ACTIVE_USER]
