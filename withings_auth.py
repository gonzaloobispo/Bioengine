# withings_auth.py - Conector Withings con Auto-Renovación (Persistencia)
import requests
import config
import pandas as pd
import os
import datetime
import json
import time

# Configuración de API Withings
AUTH_URL = 'https://account.withings.com/oauth2_user/authorize2'
TOKEN_URL = 'https://wbsapi.withings.net/v2/oauth2'
CALLBACK_URI = 'http://localhost'
TOKEN_FILE = os.path.join(config.CONFIG_DIR, 'withings_tokens.json') # Archivo para guardar la sesión
SCOPE = ['user.metrics']

def save_tokens(token_data):
    """Guarda las llaves en disco para no pedirlas de nuevo"""
    try:
        # Agregamos timestamp para saber cuándo se guardó
        token_data['saved_at'] = time.time()
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f)
        print("💾 Sesión guardada exitosamente (Auto-Login activado).")
    except Exception as e:
        print(f"⚠️ No se pudo guardar el archivo de tokens: {e}")

def load_tokens():
    """Carga las llaves del disco"""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def refresh_access_token(saved_tokens):
    """Usa el Refresh Token para obtener acceso nuevo sin molestar al usuario"""
    print("🔄 Token vencido o existente. Intentando renovación automática...")
    
    payload = {
        'action': 'requesttoken',
        'grant_type': 'refresh_token',
        'client_id': config.WITHINGS_CLIENT_ID,
        'client_secret': config.WITHINGS_CLIENT_SECRET,
        'refresh_token': saved_tokens.get('refresh_token')
    }
    
    try:
        response = requests.post(TOKEN_URL, data=payload)
        data = response.json()
        
        # Withings a veces devuelve la data directo o dentro de 'body'
        new_tokens = data.get('body') or data
        
        if 'access_token' in new_tokens:
            print("✅ Renovación ÉXITOSA. Tenemos acceso por 3 horas más.")
            save_tokens(new_tokens) # Guardamos los nuevos para la próxima
            return new_tokens['access_token']
        else:
            print(f"⚠️ Falló la renovación automática: {data}")
            return None
    except Exception as e:
        print(f"❌ Error conectando para renovar: {e}")
        return None

def get_new_token_manual():
    """Flujo manual (Solo se usa la primera vez o si falla todo)"""
    from requests_oauthlib import OAuth2Session
    
    # 1. Generar URL
    oauth = OAuth2Session(config.WITHINGS_CLIENT_ID, redirect_uri=CALLBACK_URI, scope=SCOPE)
    authorization_url, state = oauth.authorization_url(AUTH_URL)
    
    print("\n⚠️ AUTORIZACIÓN MANUAL REQUERIDA (Configuración Inicial)")
    print("1. Abre este Link en tu navegador:")
    print(f"{authorization_url}\n")
    print("2. Acepta y copia la URL de error (localhost).")
    
    redirect_response = input("Pegue la URL completa aquí: ")
    
    # Extraer código
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(redirect_response)
        code = parse_qs(parsed.query)['code'][0]
    except:
        print("❌ URL inválida.")
        return None

    # 2. Canjear código
    payload = {
        'action': 'requesttoken',
        'grant_type': 'authorization_code',
        'client_id': config.WITHINGS_CLIENT_ID,
        'client_secret': config.WITHINGS_CLIENT_SECRET,
        'code': code,
        'redirect_uri': CALLBACK_URI
    }
    
    try:
        response = requests.post(TOKEN_URL, data=payload)
        data = response.json()
        tokens = data.get('body') or data
        
        if 'access_token' in tokens:
            save_tokens(tokens) # <--- AQUÍ GUARDAMOS PARA EL FUTURO
            return tokens['access_token']
        else:
            print(f"❌ Error Withings: {tokens}")
            return None
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return None

def get_valid_token():
    """Cerebro principal: Decide si renovar o pedir manual"""
    # 1. Intentar cargar archivo
    saved_tokens = load_tokens()
    
    if saved_tokens and 'refresh_token' in saved_tokens:
        # 2. Si existe, intentamos renovar directamente (es más seguro que chequear tiempo)
        new_access_token = refresh_access_token(saved_tokens)
        if new_access_token:
            return new_access_token
        else:
            print("⚠️ El token guardado ya no sirve. Toca loguearse de nuevo.")
    
    # 3. Si no hay archivo o falló la renovación, vamos manual
    return get_new_token_manual()

def get_measurements():
    """Descarga Peso, Grasa y Músculo"""
    print("⚖️ Verificando credenciales Withings...")
    
    access_token = get_valid_token()
    if not access_token:
        print("❌ No se pudo obtener acceso a Withings.")
        return None
    
    print("⚖️ Descargando datos de la nube...")
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'action': 'getmeas',
        'meastypes': '1,6,76',
        'category': 1
    }
    
    try:
        response = requests.post('https://wbsapi.withings.net/measure', headers=headers, data=params)
        cuerpo = response.json()
        
        if cuerpo['status'] != 0:
            # Si da error 401 (Auth Failed), podríamos intentar borrar el token y reintentar, 
            # pero por seguridad paramos aquí.
            print(f"❌ Error API Withings: {cuerpo}")
            return None
            
        # Procesar JSON
        registros = []
        if 'measuregrps' in cuerpo['body']:
            for grupo in cuerpo['body']['measuregrps']:
                fecha = datetime.datetime.fromtimestamp(grupo['date']).strftime('%Y-%m-%d')
                fila = {"Fecha": fecha, "Peso": None, "Grasa_Pct": None, "Masa_Muscular_Kg": None}
                
                for medida in grupo['measures']:
                    valor = medida['value'] * (10 ** medida['unit'])
                    if medida['type'] == 1: fila["Peso"] = round(valor, 2)
                    if medida['type'] == 6: fila["Grasa_Pct"] = round(valor, 2)
                    if medida['type'] == 76: fila["Masa_Muscular_Kg"] = round(valor, 2)
                
                if fila["Peso"]: registros.append(fila)
        
        # Guardar CSV
        if registros:
            df = pd.DataFrame(registros).sort_values('Fecha', ascending=False)
            ruta = os.path.join(config.DATA_PROCESSED, 'historial_withings_raw.csv')
            df.to_csv(ruta, sep=';', index=False)
            print(f"✅ ÉXITO: {len(df)} registros descargados.")
            return df
        return pd.DataFrame()

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    get_measurements()