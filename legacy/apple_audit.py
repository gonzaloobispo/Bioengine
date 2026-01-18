import xml.etree.ElementTree as ET
import csv
import os
from datetime import datetime

def auditar_todo_apple():
    base_path = r'C:\BioEngine_Gonzalo\apple_health_export'
    file_exportar = os.path.join(base_path, 'exportar.xml')
    file_cda = os.path.join(base_path, 'export_cda.xml')
    
    fuentes_externas = ['Garmin', 'Connect', 'Withings', 'HealthMate', 'Strava']

    # --- 1. PROCESAR EXPORTAR.XML (Actividad y Deporte) ---
    print("\n--- 🍎 AUDITANDO EXPORTAR.XML (Deporte y Salud Diaria) ---")
    if os.path.exists(file_exportar):
        conteo_fuentes = {}
        datos_unicos = []
        
        # Usamos iterparse para eficiencia de memoria
        context = ET.iterparse(file_exportar, events=('end',))
        for event, elem in context:
            if elem.tag in ['Workout', 'Record']:
                source = elem.get('sourceName', 'Desconocido')
                conteo_fuentes[source] = conteo_fuentes.get(source, 0) + 1
                
                if elem.tag == 'Workout':
                    # Solo extraer si no es de Garmin/Withings
                    if not any(ext.lower() in source.lower() for ext in fuentes_externas):
                        tipo = elem.get('workoutActivityType', '').replace('HKWorkoutActivityType', '')
                        datos_unicos.append({
                            'Fecha': elem.get('startDate', '')[:19],
                            'Fuente': source,
                            'Tipo': tipo.replace('Tennis', 'Tenis').replace('Running', 'Carrera'),
                            'Duracion_min': round(float(elem.get('duration', 0)), 2),
                            'Distancia_km': round(float(elem.get('totalDistance', 0)), 2)
                        })
            elem.clear()
        
        print(f"✅ Auditoría completada.")
        print("Fuentes principales detectadas (Top 5):")
        for f, c in sorted(conteo_fuentes.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - {f}: {c} registros")

        if datos_unicos:
            with open('historial_apple_deportes.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=datos_unicos[0].keys(), delimiter=';')
                writer.writeheader()
                writer.writerows(datos_unicos)
            print(f"📂 Guardadas {len(datos_unicos)} actividades únicas en 'historial_apple_deportes.csv'")
    else:
        print(f"❌ No se encontró: {file_exportar}")

    # --- 2. PROCESAR EXPORT_CDA.XML (Documentos Clínicos) ---
    print("\n--- 🩺 AUDITANDO EXPORT_CDA.XML (Registros Médicos) ---")
    if os.path.exists(file_cda):
        try:
            tree = ET.parse(file_cda)
            root = tree.getroot()
            ns = {'n': 'urn:hl7-org:v3'}
            
            titulo = root.find('.//n:title', ns)
            print(f"📄 Documento: {titulo.text if titulo is not None else 'Sin título'}")
            
            secciones = root.findall('.//n:section/n:title', ns)
            if secciones:
                print("📍 Secciones médicas detectadas:")
                for s in secciones:
                    print(f"   - {s.text}")
            else:
                print("ℹ️ El archivo CDA no contiene secciones de texto.")
        except Exception as e:
            print(f"⚠️ Nota: El archivo CDA no pudo ser procesado o está vacío ({e})")
    else:
        print(f"❌ No se encontró: {file_cda}")

if __name__ == "__main__":
    auditar_todo_apple() # Aquí estaba el error de los dos puntos