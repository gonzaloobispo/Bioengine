import requests
import json
import time
import csv
from datetime import datetime

# --- CONFIGURACIÓN ---
CLIENT_ID = "ab42901f472e68a9f8dc6503387ee3a28d9e6ce3b0c71c9a4b097550cb679ce8"
CLIENT_SECRET = "354a12c732071260c54137c5edfa8f52b991aca124a043a21921062fdd07910a"
TOKEN_FILE = 'withings_tokens.json'
CSV_FILENAME = 'historial_peso.csv'

def cargar_tokens():
    try:
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: No existe {TOKEN_FILE}.")
        exit()

def guardar_tokens(nuevos_tokens):
    tokens_existentes = cargar_tokens()
    tokens_existentes.update(nuevos_tokens)
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens_existentes, f, indent=4)
    print("💾 Tokens renovados y guardados.")

def refrescar_token(refresh_token):
    print("🔄 Renovando access_token vencido...")
    url = "https://wbsapi.withings.net/v2/oauth2"
    payload = {
        'action': 'requesttoken', 'grant_type': 'refresh_token',
        'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token
    }
    resp = requests.post(url, data=payload).json()
    if resp['status'] == 0: return resp['body']
    else: exit(f"Error fatal refrescando token: {resp}")

def obtener_historial_completo():
    tokens = cargar_tokens()
    url = 'https://wbsapi.withings.net/measure'
    
    # category=1 significa "Medidas reales" (no objetivos)
    # meastype=1 es "Peso"
    payload = {'action': 'getmeas', 'category': 1, 'meastype': 1}
    headers = {'Authorization': f"Bearer {tokens['access_token']}"}
    
    print("--- Descargando historial completo de Withings ---")
    response = requests.post(url, headers=headers, data=payload)
    data = response.json()
    
    # Auto-reparación si el token venció (Error 401)
    if data['status'] == 401:
        nuevos = refrescar_token(tokens['refresh_token'])
        guardar_tokens(nuevos)
        headers = {'Authorization': f"Bearer {nuevos['access_token']}"}
        print("Reintentando descarga...")
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        
    return data

def procesar_y_guardar(data):
    if data['status'] != 0:
        print(f"Error en API: {data}")
        return

    measuregrps = data['body']['measuregrps']
    print(f"✅ Se encontraron {len(measuregrps)} registros de peso.")
    
    # Preparamos el archivo CSV
    with open(CSV_FILENAME, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';') # Uso punto y coma para que Excel lo lea fácil en español
        writer.writerow(['Fecha', 'Hora', 'Peso (kg)']) # Encabezados
        
        count = 0
        for grupo in measuregrps:
            # Timestamp a fecha legible
            fecha_dt = datetime.fromtimestamp(grupo['date'])
            fecha_str = fecha_dt.strftime('%d/%m/%Y')
            hora_str = fecha_dt.strftime('%H:%M:%S')
            
            # Buscamos la medida de peso dentro del grupo
            for medida in grupo['measures']:
                if medida['type'] == 1: # Asegurar que es peso
                    valor = medida['value']
                    unit = medida['unit']
                    peso_real = valor * (10 ** unit)
                    
                    # Escribir fila (reemplazamos punto por coma para Excel español si prefieres)
                    # Pero Python usa punto para float. Excel suele entenderlo o se cambia formato.
                    writer.writerow([fecha_str, hora_str, round(peso_real, 2)])
                    count += 1
                    
    print(f"🎉 Exportación completada: {count} filas guardadas en '{CSV_FILENAME}'")
    print("Puedes abrir este archivo directamente en Excel.")

if __name__ == "__main__":
    datos = obtener_historial_completo()
    procesar_y_guardar(datos)