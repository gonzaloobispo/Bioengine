import config
from garminconnect import Garmin
import csv
import os
from datetime import datetime, timedelta

def get_last_date_garmin(filename):
    if not os.path.exists(filename): return None
    with open(filename, 'r', encoding='utf-8') as f:
        rows = list(csv.reader(f, delimiter=';'))
        if len(rows) <= 1: return None
        # La última fecha está en la segunda fila (ya que ordenamos desc o asc)
        # Vamos a buscar la fecha más reciente de la columna 0
        fechas = [datetime.strptime(row[0], '%d/%m/%Y') for row in rows[1:]]
        return max(fechas)

def update_garmin_delta():
    filename = "historial_garmin_completo.csv"
    last_date = get_last_date_garmin(filename)
    
    api = Garmin(config.GARMIN_EMAIL, config.GARMIN_PASSWORD)
    api.login()
    
    # Si tenemos fecha, pedimos desde el día siguiente. Si no, pedimos los últimos 20 por seguridad.
    search_start = last_date + timedelta(days=1) if last_date else datetime(2023,1,1)
    print(f"--- ⌚ Buscando actividades Garmin desde: {search_start.strftime('%d/%m/%Y')} ---")
    
    # Garmin API no filtra directo por fecha en get_activities, 
    # así que bajamos las últimas y filtramos nosotros.
    activities = api.get_activities(0, 20) 
    nuevas = []
    
    for act in activities:
        act_date = datetime.strptime(act['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
        if act_date > search_start:
            nuevas.append(act)
    
    if nuevas:
        print(f"   ✅ Encontradas {len(nuevas)} actividades nuevas.")
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            for act in nuevas:
                dt = datetime.strptime(act['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
                writer.writerow([
                    dt.strftime('%d/%m/%Y'),
                    act['activityType']['typeKey'],
                    act['activityName'],
                    round(act.get('distance', 0) / 1000, 2),
                    round(act.get('duration', 0) / 60, 2),
                    act.get('calories', 0),
                    act.get('averageHR', 0),
                    round(act.get('elevationGain', 0), 0)
                ])
    else:
        print("   🙌 Todo está al día en Garmin.")

if __name__ == "__main__":
    update_garmin_delta()