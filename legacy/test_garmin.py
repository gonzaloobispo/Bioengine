import config
from garminconnect import Garmin
import json
from datetime import date

def conectar_garmin():
    print("--- ⌚ Conectando con Garmin Connect ---")
    try:
        # Inicializar el cliente
        client = Garmin(config.GARMIN_EMAIL, config.GARMIN_PASSWORD)
        client.login()
        print("✅ Conexión Exitosa!")
        return client
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def explorar_datos(api):
    hoy = date.today()
    
    # 1. Resumen de Actividad del día
    print("\n📦 Resumen del día:")
    stats = api.get_stats(hoy.isoformat())
    print(f"   Pasos: {stats.get('totalSteps')}")
    print(f"   Calorías activas: {stats.get('activeCalories')}")

    # 2. Métricas de Salud (Lo que le interesa a un Runner)
    print("\n🏃 Métricas de Performance:")
    # El 965 da el VO2 Max muy preciso
    training_status = api.get_training_status(hoy.isoformat())
    vo2max = training_status.get('mostRecentVO2Max', {}).get('generic', 'N/A')
    print(f"   VO2 Max actual: {vo2max}")
    
    # 3. Listar últimas actividades (Carreras/Tenis)
    print("\n🎾 Últimas Actividades:")
    activities = api.get_activities(0, 3) # Traer las últimas 3
    for act in activities:
        fecha = act['startTimeLocal']
        tipo = act['activityType']['typeKey']
        nombre = act['activityName']
        distancia = round(act['distance'] / 1000, 2)
        print(f"   - {fecha} | {tipo}: {nombre} ({distancia} km)")

if __name__ == "__main__":
    garmin_api = conectar_garmin()
    if garmin_api:
        explorar_datos(garmin_api)