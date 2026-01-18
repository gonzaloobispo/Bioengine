import config
from garminconnect import Garmin
import csv
from datetime import datetime
import time

def conectar_garmin():
    try:
        client = Garmin(config.GARMIN_EMAIL, config.GARMIN_PASSWORD)
        client.login()
        return client
    except Exception as e:
        print(f"❌ Error de login: {e}")
        return None

def exportar_todo(api):
    print("--- ⌚ Iniciando Extracción Masiva de Garmin ---")
    
    todas_las_actividades = []
    inicio = 0
    lote = 100 # Pedimos de a 100 para no saturar la conexión
    
    while True:
        print(f"   Descargando lote desde el registro {inicio}...")
        batch = api.get_activities(inicio, lote)
        
        if not batch: # Si no hay más datos, salimos del bucle
            break
            
        todas_las_actividades.extend(batch)
        inicio += lote
        # Pequeña pausa de cortesía para el servidor
        time.sleep(1) 

    if not todas_las_actividades:
        print("No se encontraron actividades.")
        return

    filename = "historial_garmin_completo.csv"
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Fecha', 'Tipo', 'Nombre', 'Distancia (km)', 'Duracion (min)', 'Calorias', 'FC Media', 'Elevacion (m)'])
        
        for act in todas_las_actividades:
            fecha_dt = datetime.strptime(act['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
            
            writer.writerow([
                fecha_dt.strftime('%d/%m/%Y'),
                act['activityType']['typeKey'],
                act['activityName'],
                round(act.get('distance', 0) / 1000, 2),
                round(act.get('duration', 0) / 60, 2),
                act.get('calories', 0),
                act.get('averageHR', 0),
                round(act.get('elevationGain', 0), 0) # Dato clave para Trail Running
            ])
            
    print(f"\n✅ ¡MISIÓN CUMPLIDA!")
    print(f"📊 Se han procesado {len(todas_las_actividades)} actividades totales.")
    print(f"📁 Archivo generado: {filename}")

if __name__ == "__main__":
    api = conectar_garmin()
    if api:
        exportar_todo(api)