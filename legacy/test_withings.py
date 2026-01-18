import requests
import json
import time

# --- CONFIGURACIÓN (Tus Credenciales) ---
CLIENT_ID = "ab42901f472e68a9f8dc6503387ee3a28d9e6ce3b0c71c9a4b097550cb679ce8"
CLIENT_SECRET = "354a12c732071260c54137c5edfa8f52b991aca124a043a21921062fdd07910a"
TOKEN_FILE = 'withings_tokens.json'

def cargar_tokens():
    try:
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: No existe {TOKEN_FILE}. Ejecuta el paso de autenticación manual primero.")
        exit()

def guardar_tokens(nuevos_tokens):
    # Actualizamos solo los campos necesarios conservando el userid
    tokens_existentes = cargar_tokens()
    tokens_existentes.update(nuevos_tokens) # Mezclamos datos viejos con nuevos
    
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens_existentes, f, indent=4)
    print("💾 Tokens actualizados y guardados en disco.")

def refrescar_access_token(refresh_token):
    print("🔄 El token venció. Solicitando uno nuevo...")
    url = "https://wbsapi.withings.net/v2/oauth2"
    payload = {
        'action': 'requesttoken',
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token
    }
    
    response = requests.post(url, data=payload)
    data = response.json()
    
    if data['status'] == 0:
        # Withings devuelve 'access_token', 'refresh_token', etc. en 'body'
        return data['body']
    else:
        print(f"❌ Error fatal refrescando token: {data}")
        exit()

def obtener_peso():
    tokens = cargar_tokens()
    url = 'https://wbsapi.withings.net/measure'
    
    # 1. Intentamos la petición normal
    headers = {'Authorization': f"Bearer {tokens['access_token']}"}
    payload = {'action': 'getmeas', 'meastype': 1} # 1 = Peso
    
    print(f"--- Consultando Withings (Usuario: {tokens.get('userid')}) ---")
    response = requests.post(url, headers=headers, data=payload)
    data = response.json()
    
    # 2. Verificamos si falló por Token Vencido (Status 401)
    if data['status'] == 401: 
        # Lógica de auto-reparación
        nuevos_datos = refrescar_access_token(tokens['refresh_token'])
        guardar_tokens(nuevos_datos)
        
        # 3. Reintentamos con el token nuevo
        print("Reintentando petición con token fresco...")
        headers = {'Authorization': f"Bearer {nuevos_datos['access_token']}"}
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()

    return data

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    resultado = obtener_peso()
    
    if resultado['status'] == 0:
        print("¡ÉXITO! ✅")
        grps = resultado['body']['measuregrps']
        if grps:
            # Procesar el dato más reciente
            ultimo = grps[0]
            peso_raw = ultimo['measures'][0]['value']
            unidad = ultimo['measures'][0]['unit']
            peso_real = peso_raw * (10 ** unidad)
            fecha = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ultimo['date']))
            
            print(f"📅 Fecha: {fecha}")
            print(f"⚖️  Peso: {peso_real:.2f} kg")
        else:
            print("No hay datos recientes.")
    else:
        print(f"Error final: {resultado}")