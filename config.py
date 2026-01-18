# config.py - Configuración Maestra del Bio-Engine
import os
from datetime import datetime

# --- 1. RUTAS DEL SISTEMA (File System) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Hacerlo relativo

# Carpetas
DATA_RAW = os.path.join(BASE_DIR, 'data_raw')
DATA_PROCESSED = os.path.join(BASE_DIR, 'data_processed')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

# Archivos Maestros (La Verdad Contable) - Ahora solo APIs, históricos separados
CSV_PESO_MAESTRO = os.path.join(DATA_PROCESSED, 'historial_completo_peso_full.csv')
CSV_PESO_MAESTRO_APIS = os.path.join(DATA_PROCESSED, 'historial_completo_peso_apis.csv')
CSV_DEPORTE_MAESTRO = os.path.join(DATA_PROCESSED, 'historial_deportivo_total_full.csv')

# --- 2. CREDENCIALES (LLAVES DE ACCESO) ---
# Usar variables de entorno para seguridad
GARMIN_EMAIL = os.getenv('GARMIN_EMAIL', 'gonzaloobispo@hotmail.com')  # Valor por defecto para desarrollo
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD', 'Gob29041976$')

# WITHINGS (Configuración App Bio-Engine)
WITHINGS_CLIENT_ID = os.getenv('WITHINGS_CLIENT_ID', 'ab42901f472e68a9f8dc6503387ee3a28d9e6ce3b0c71c9a4b097550cb679ce8')
WITHINGS_CLIENT_SECRET = os.getenv('WITHINGS_CLIENT_SECRET', '1cce12d853f3ba00bf06c23a3d776c6666e41bad4010d19dd3045091f3b393a4')

# --- 3. PERFILES DE USUARIO ---
USUARIOS = {
    "Gonzalo": {
        "fecha_nacimiento": "1976-04-29",
        "sexo": "M",
        "altura": 1.76,
        "lesion_rodilla": True, # Activa lógica conservadora
        "umbral_dolor": 4 
    }
}

# Usuario Activo
ACTIVE_USER = "Gonzalo"

# --- 4. FUNCIONES DE SOPORTE ---
def get_edad(fecha_str):
    """Calcula edad exacta al día de hoy"""
    nacimiento = datetime.strptime(fecha_str, "%Y-%m-%d")
    hoy = datetime.now()
    return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))

def get_perfil_activo():
    return USUARIOS[ACTIVE_USER]

# --- CREDENCIALES WITHINGS (OAUTH2) ---
# Eliminadas duplicaciones, usar las de arriba
WITHINGS_REDIRECT_URI = "http://localhost:8080/" 

# Archivo donde guardaremos los tokens vivos (para que se actualicen solos)
WITHINGS_TOKEN_FILE = os.path.join(CONFIG_DIR, 'withings_tokens.json')

# Agregar rutas faltantes para cloud_sync.py
RAW_GARMIN_FILE = os.path.join(DATA_PROCESSED, 'historial_garmin_raw.csv')
