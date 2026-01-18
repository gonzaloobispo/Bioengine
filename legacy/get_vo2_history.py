import config
from garminconnect import Garmin
from datetime import date, timedelta

def extraer_vo2_historico():
    print("--- 🧬 Buscando Historial de VO2 Max en Garmin ---")
    try:
        api = Garmin(config.GARMIN_EMAIL, config.GARMIN_PASSWORD)
        api.login()
        
        # Definimos el rango: últimos 30 días
        hoy = date.today()
        hace_30_dias = hoy - timedelta(days=30)
        
        # Intentamos obtener las métricas máximas del usuario
        # Este endpoint suele traer el histórico de VO2 Max
        vo2_history = api.get_max_metrics(hace_30_dias.isoformat())
        
        if not vo2_history:
            print("⚠️ No se encontraron registros de VO2 Max en el periodo.")
            return

        print("\n📈 REGISTROS ENCONTRADOS:")
        # Buscamos en el JSON la entrada de VO2 Max
        for entry in vo2_history:
            if 'vo2Max' in entry:
                v_date = entry.get('calendarDate')
                v_value = entry.get('vo2Max')
                print(f"   📅 Fecha: {v_date} | 🏆 VO2 Max: {v_value}")
        
    except Exception as e:
        print(f"❌ Error al extraer métricas: {e}")

if __name__ == "__main__":
    extraer_vo2_historico()