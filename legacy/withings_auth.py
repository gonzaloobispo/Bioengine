import json
import requests
import config # Importamos el archivo que acabas de crear

def cargar_tokens():
    try:
        with open(config.TOKEN_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error crítico: No se encuentra {config.TOKEN_FILE}")
        exit()

def guardar_tokens(nuevos_tokens):
    # Leemos lo viejo para no perder datos (ej. userid)
    tokens_actuales = cargar_tokens()
    tokens_actuales.update(nuevos_tokens)
    
    with open(config.TOKEN_FILE, 'w') as f:
        json.dump(tokens_actuales, f, indent=4)
    print("💾 Tokens actualizados y guardados correctamente.")

def get_valid_access_token():
    """
    Esta es la función MAESTRA.
    Devuelve un access_token válido. Si el actual venció, lo renueva solo.
    """
    tokens = cargar_tokens()
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    
    # Validamos si funciona haciendo una petición ligera (check de estado)
    # Nota: Withings no tiene un endpoint "check_token" oficial simple, 
    # así que confiamos en la gestión de errores del script principal 
    # O, proactivamente, intentamos refrescarlo si sabemos que es viejo.
    # Por eficiencia, simplemente devolvemos el token y dejamos que el script 
    # principal llame a 'renovar_token' si recibe un error 401.
    
    return access_token

def renovar_token_vencido():
    tokens = cargar_tokens()
    refresh_token = tokens['refresh_token']
    
    print("🔄 El token ha caducado. Negociando uno nuevo con Withings...")
    
    url = "https://wbsapi.withings.net/v2/oauth2"
    payload = {
        'action': 'requesttoken',
        'grant_type': 'refresh_token',
        'client_id': config.WITHINGS_CLIENT_ID,
        'client_secret': config.WITHINGS_CLIENT_SECRET,
        'refresh_token': refresh_token
    }
    
    response = requests.post(url, data=payload)
    data = response.json()
    
    if data['status'] == 0:
        nuevos_datos = data['body']
        guardar_tokens(nuevos_datos)
        return nuevos_datos['access_token']
    else:
        print(f"❌ Error fatal renovando token: {data}")
        exit()