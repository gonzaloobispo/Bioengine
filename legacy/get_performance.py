import config
from garminconnect import Garmin
import pandas as pd
from datetime import date

def extraer_metricas_fisiologicas():
    print("--- 🧬 Extrayendo Métricas de Performance (VO2 Max) ---")
    try:
        api = Garmin(config.GARMIN_EMAIL, config.GARMIN_PASSWORD)
        api.login()
        
        # 1. Obtener el estado de entrenamiento actual
        # Esto incluye VO2 Max, Carga de entrenamiento y Estado (Productivo, etc.)
        status = api.get_training_status(date.today().isoformat())
        
        # Extraer VO2 Max (Genérico y de Carrera si existe)
        vo2_data = status.get('mostRecentVO2Max', {})
        vo2_valor = vo2_data.get('generic', 'N/A')
        
        # Extraer Carga Aguda (Acute Load)
        carga = status.get('acuteTrainingLoad', 'N/A')
        
        # Extraer Estado de Entrenamiento
        estado = status.get('trainingStatus', 'Sin Estado')

        print(f"\n✅ DATOS FISIOLÓGICOS DETECTADOS:")
        print(f"   🏆 VO2 Max Actual: {vo2_valor}")
        print(f"   🔥 Carga Aguda: {carga}")
        print(f"   📈 Estado: {estado}")

        # 2. Intentar obtener el histórico de VO2 Max (Últimos 30 días)
        # Nota: Este endpoint puede variar según la versión de la API
        print("\n⏳ Buscando tendencia de VO2 Max...")
        # (Garmin a veces limita el histórico de VO2Max a través de esta librería, 
        # pero el valor más reciente siempre es accesible).

    except Exception as e:
        print(f"❌ Error al extraer métricas: {e}")

if __name__ == "__main__":
    extraer_metricas_fisiologicas()