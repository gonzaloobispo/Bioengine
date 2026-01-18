import config
from garminconnect import Garmin
import csv
from datetime import datetime

def conectar_garmin():
    try:
        client = Garmin(config.GARMIN_EMAIL, config.GARMIN_PASSWORD)
        client.login()
        return client
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def exportar_historico(api):
    print("--- ⌚ Extrayendo Histórico de Actividades Garmin ---")
    
    # Pedimos las últimas 50 actividades
    # (0 es el inicio, 50 es la cantidad)
    activities = api.get_activities(0, 50) 
    
    if not activities:
        print("No se encontraron actividades.")
        return

    filename = "historial_actividades_garmin.csv"
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        # Encabezados técnicos para tu análisis
        writer.writerow(['Fecha', 'Tipo', 'Nombre', 'Distancia (km)', 'Duracion (min)', 'Calorias', 'FC Media'])
        
        for act in activities:
            # Procesamiento de datos
            fecha_dt = datetime.strptime(act['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
            fecha_fmt = fecha_dt.strftime('%d/%m/%Y')
            
            tipo = act['activityType']['typeKey']
            nombre = act['activityName']
            distancia = round(act.get('distance', 0) / 1000, 2)
            duracion = round(act.get('duration', 0) / 60, 2)
            calorias = act.get('calories', 0)
            fc_media = act.get('averageHR', 0)
            
            writer.writerow([fecha_fmt, tipo, nombre, distancia, duracion, calorias, fc_media])
            
    print(f"✅ ¡ÉXITO! Se exportaron {len(activities)} actividades a '{filename}'")

if __name__ == "__main__":
    api = conectar_garmin()
    if api:
        exportar_historico(api)