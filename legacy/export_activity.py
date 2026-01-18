import requests
import json
import csv
from datetime import datetime, date, timedelta

# --- CONFIGURACIÓN ---
CLIENT_ID = "ab42901f472e68a9f8dc6503387ee3a28d9e6ce3b0c71c9a4b097550cb679ce8"
CLIENT_SECRET = "354a12c732071260c54137c5edfa8f52b991aca124a043a21921062fdd07910a"
TOKEN_FILE = 'withings_tokens.json'
CSV_FILENAME = 'historial_actividad.csv'

# Rango de fechas: Desde 01/01/2023 hasta Hoy
START_DATE = "2023-01-01" 

def cargar_tokens():
    try:
        with open(TOKEN_FILE, 'r') as f: return json.load(f)
    except FileNotFoundError: exit(f"Error: Falta {TOKEN_FILE}")

def guardar_tokens(nuevos):
    tokens = cargar_tokens()
    tokens.update(nuevos)
    with open(TOKEN_FILE, 'w') as f: json.dump(tokens, f, indent=4)
    print("💾 Tokens actualizados.")

def refrescar_token(refresh_token):
    print("🔄 Renovando token...")
    url = "https://wbsapi.withings.net/v2/oauth2"
    payload = {'action': 'requesttoken', 'grant_type': 'refresh_token',
               'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET,
               'refresh_token': refresh_token}
    resp = requests.post(url, data=payload).json()
    if resp['status'] == 0: return resp['body']
    else: exit(f"Error fatal refrescando token: {resp}")

def obtener_actividad():
    tokens = cargar_tokens()
    url = 'https://wbsapi.withings.net/v2/measure'
    
    # Calculamos la fecha de hoy
    hoy = date.today().strftime("%Y-%m-%d")
    
    # Pedimos: Pasos, Distancia, Calorías, Elevación, Calorías Totales
    payload = {
        'action': 'getactivity',
        'startdateymd': START_DATE,
        'enddateymd': hoy,
        'data_fields': 'steps,distance,calories,elevation,totalcalories' 
    }
    headers = {'Authorization': f"Bearer {tokens['access_token']}"}
    
    print(f"--- 🏃 Descargando Actividad ({START_DATE} a {hoy}) ---")
    response = requests.post(url, headers=headers, data=payload)
    data = response.json()
    
    # Auto-reparación de token
    if data['status'] == 401:
        nuevos = refrescar_token(tokens['refresh_token'])
        guardar_tokens(nuevos)
        headers = {'Authorization': f"Bearer {nuevos['access_token']}"}
        print("Reintentando descarga con token nuevo...")
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        
    return data

def procesar_y_guardar(data):
    if data['status'] != 0:
        print(f"Error API: {data}")
        return

    actividades = data['body']['activities']
    print(f"✅ Se encontraron {len(actividades)} días de registros.")
    
    with open(CSV_FILENAME, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        # Encabezados
        writer.writerow(['Fecha', 'Pasos', 'Distancia (km)', 'Calorias Activas', 'Calorias Totales'])
        
        for dia in actividades:
            fecha = dia.get('date', '') # Formato viene YYYY-MM-DD
            # Convertir formato a DD/MM/YYYY para Excel
            if fecha:
                obj_fecha = datetime.strptime(fecha, '%Y-%m-%d')
                fecha_fmt = obj_fecha.strftime('%d/%m/%Y')
            else:
                fecha_fmt = "N/A"

            steps = dia.get('steps', 0)
            dist_m = dia.get('distance', 0)
            dist_km = round(dist_m / 1000, 2) # Convertir metros a KM
            cal_active = dia.get('calories', 0)
            cal_total = dia.get('totalcalories', 0)
            
            writer.writerow([fecha_fmt, steps, dist_km, cal_active, cal_total])
            
    print(f"🎉 Archivo generado: {CSV_FILENAME}")

if __name__ == "__main__":
    datos = obtener_actividad()
    procesar_y_guardar(datos)	