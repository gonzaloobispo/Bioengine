import xml.etree.ElementTree as ET
import csv
from datetime import datetime
import os

def procesar_apple_health():
    xml_path = 'export.xml' # El archivo que descargaste del iPhone
    if not os.path.exists(xml_path):
        print("❌ No se encontró 'export.xml'. Expórtalo desde tu iPhone primero.")
        return

    print("--- 🍎 Procesando Histórico de Apple Watch ---")
    
    actividades = []
    try:
        # Nota: Este archivo puede ser MUY grande, usamos iterparse para no agotar la RAM
        context = ET.iterparse(xml_path, events=('end',))
        
        for event, elem in context:
            if elem.tag == 'Workout':
                # Extraemos los datos básicos de cada entrenamiento
                tipo = elem.get('workoutActivityType').replace('HKWorkoutActivityType', '')
                fecha_inicio = elem.get('startDate')
                duracion = float(elem.get('duration', 0))
                distancia = float(elem.get('totalDistance', 0))
                calorias = float(elem.get('totalEnergyBurned', 0))
                
                # Formatear fecha
                dt = datetime.strptime(fecha_inicio[:19], '%Y-%m-%d %H:%M:%S')
                
                actividades.append({
                    'Fecha': dt.strftime('%d/%m/%Y'),
                    'Tipo': tipo,
                    'Nombre': 'Apple Watch Workout',
                    'Distancia (km)': round(distancia, 2), # Apple suele exportar en km o millas según config
                    'Duracion (min)': round(duracion, 2),
                    'Calorias': int(calorias),
                    'FC Media': 0, # Apple lo guarda en nodos hijos complejos, por ahora lo dejamos en 0
                    'Elevacion (m)': 0
                })
            elem.clear() # Limpiar memoria
            
        # Guardar en un CSV temporal de Apple
        if actividades:
            with open('historial_apple_watch.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=actividades[0].keys(), delimiter=';')
                writer.writeheader()
                writer.writerows(actividades)
            print(f"✅ Se rescataron {len(actividades)} actividades de Apple Watch.")
            
    except Exception as e:
        print(f"❌ Error al procesar XML de Apple: {e}")

if __name__ == "__main__":
    procesar_apple_health()