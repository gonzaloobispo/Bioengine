# cloud_sync.py - Motor de Sincronización Híbrido (Garmin + Withings Auto-Refresh)
import os
import pandas as pd
import datetime
import json
import requests
import time
from garminconnect import Garmin
import config

# ==========================================
# 🛰️ MÓDULO GARMIN
# ==========================================
def obtener_ultima_fecha_garmin():
    if os.path.exists(config.RAW_GARMIN_FILE):
        try:
            df = pd.read_csv(config.RAW_GARMIN_FILE, sep=';')
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            return df['Fecha'].max().date()
        except: pass
    return datetime.date(2023, 1, 1)

def _parse_num_es(series):
    s = series.astype(str).str.strip()
    s = s.replace('', pd.NA)
    has_comma = s.str.contains(',', na=False)
    s = s.where(~has_comma, s.str.replace('.', '', regex=False).str.replace(',', '.', regex=False))
    return pd.to_numeric(s, errors='coerce')

def _format_num_es(value, decimals=2):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        num = float(value)
    except Exception:
        return value
    if decimals == 0:
        s = f"{int(round(num)):,}"
    else:
        s = f"{num:,.{decimals}f}"
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')

def _format_columns_es(df, column_decimals):
    for col, decimals in column_decimals.items():
        if col in df.columns:
            df[col] = _parse_num_es(df[col]).map(lambda v: _format_num_es(v, decimals=decimals))
    return df

def sync_garmin_module():
    print("   [GARMIN] (1/2) Conectando a Garmin...")
    if "tu_email" in config.GARMIN_EMAIL:
        return "[WARNING] Salteado: Falta configurar email en config.py"

    try:
        client = Garmin(config.GARMIN_EMAIL, config.GARMIN_PASSWORD)
        client.login()
        
        ultima_fecha = obtener_ultima_fecha_garmin()
        hoy = datetime.date.today()
        if ultima_fecha >= hoy:
            return "[OK] Garmin al día."
            
        start_date = ultima_fecha + datetime.timedelta(days=1)
        print(f"      Descargando desde {start_date}...")
        
        activities = client.get_activities_by_date(start_date.isoformat(), hoy.isoformat())
        if not activities:
            return "[OK] Garmin: Sin datos nuevos."

        nuevos = []
        for act in activities:
            nuevos.append({
                'Fecha': act['startTimeLocal'],
                'Tipo': act.get('activityType', {}).get('typeKey', 'otros'),
                'Distancia (km)': round(act.get('distance', 0) / 1000.0, 2),
                'Duracion (min)': round(act.get('duration', 0) / 60.0, 1),
                'Calorias': act.get('calories', 0),
                'FC Media': act.get('averageHR', None),
                'FC Max': act.get('maxHR', None),
                'Elevacion (m)': act.get('totalElevationGain', None),
                'Cadencia_Media': act.get('averageRunningCadence', None) or act.get('averageBikeCadence', None),
                'Fuente': 'Garmin Cloud'
            })
            
        df_nuevo = pd.DataFrame(nuevos)
        if os.path.exists(config.RAW_GARMIN_FILE):
            df_old = pd.read_csv(config.RAW_GARMIN_FILE, sep=';')
            df_final = pd.concat([df_old, df_nuevo], ignore_index=True)
        else:
            df_final = df_nuevo
            
        df_final = df_final.drop_duplicates(subset=['Fecha', 'Tipo'], keep='last')
        df_final = _format_columns_es(df_final, {
            'Distancia (km)': 2,
            'Duracion (min)': 1,
            'Calorias': 0,
        })
        df_final.to_csv(config.RAW_GARMIN_FILE, sep=';', index=False)
        return f"[OK] Garmin: +{len(nuevos)} actividades."

    except Exception as e:
        return f"[ERROR] Error Garmin: {str(e)}"

# ==========================================
# ⚖️ MÓDULO WITHINGS (CON AUTO-RENOVACIÓN)
# ==========================================
def cargar_tokens_withings():
    if os.path.exists(config.WITHINGS_TOKEN_FILE):
        with open(config.WITHINGS_TOKEN_FILE, 'r') as f:
            return json.load(f)
    return None

def guardar_tokens_withings(token_data):
    with open(config.WITHINGS_TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)

def refrescar_token_withings(refresh_token):
    print("      [REFRESH] Renovando Token Withings caducado...")
    url = "https://wbsapi.withings.net/v2/oauth2"
    payload = {
        'action': 'requesttoken',
        'grant_type': 'refresh_token',
        'client_id': config.WITHINGS_CLIENT_ID,
        'client_secret': config.WITHINGS_CLIENT_SECRET,
        'refresh_token': refresh_token
    }
    try:
        r = requests.post(url, data=payload)
        data = r.json()
        if data['status'] == 0:
            new_tokens = {
                'access_token': data['body']['access_token'],
                'refresh_token': data['body']['refresh_token'],
                'expires_in': data['body']['expires_in']
            }
            guardar_tokens_withings(new_tokens)
            return new_tokens['access_token']
        return None
    except Exception as e:
        return None

def obtener_ultima_fecha_withings():
    ruta = config.CSV_PESO_MAESTRO  # Leer del maestro acumulado, no del raw temporal
    if os.path.exists(ruta):
        try:
            df = pd.read_csv(ruta, sep=';')
            if not df.empty and 'Fecha' in df.columns:
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
                max_fecha = df['Fecha'].max()
                if pd.notna(max_fecha):
                    return int(max_fecha.timestamp())
        except Exception as e:
            print(f"   [WARNING] Error leyendo fecha Withings: {e}")
    return 1672531200 # 01/01/2023 como fallback

def sync_withings_module():
    print("   [WITHINGS] (2/2) Conectando a Withings...")
    tokens = cargar_tokens_withings()
    if not tokens:
        return "[WARNING] Withings: Falta 'withings_tokens.json'."

    access_token = tokens['access_token']
    last_update = obtener_ultima_fecha_withings()
    # Restar 1 hora para asegurar que no se pierdan datos por timezone o precision
    last_update -= 3600  # 1 hora en segundos
    print(f"      Última fecha Withings: {last_update} ({datetime.datetime.fromtimestamp(last_update) if last_update > 0 else 'N/A'})")
    url = "https://wbsapi.withings.net/measure"
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'action': 'getmeas', 'meastype': '1,6,76', 'lastupdate': last_update}
    
    r = requests.post(url, headers=headers, data=params)
    data = r.json()
    
    print(f"      Respuesta Withings: status={data.get('status')}, body={data.get('body', {})}")
    
    if data['status'] == 401:
        nuevo_access = refrescar_token_withings(tokens['refresh_token'])
        if nuevo_access:
            headers['Authorization'] = f'Bearer {nuevo_access}'
            r = requests.post(url, headers=headers, data=params)
            data = r.json()
        else:
            return "[ERROR] Withings: Falló renovación."

    if data['status'] == 0:
        grps = data['body']['measuregrps']
        if not grps: return "[OK] Withings: Sin datos nuevos."
        nuevos = []
        for g in grps:
            fecha = datetime.datetime.fromtimestamp(g['date'])
            record = {'Fecha': fecha, 'Peso': None, 'Grasa_Pct': None, 'Masa_Muscular_Kg': None}
            for m in g['measures']:
                val = m['value'] * (10 ** m['unit'])
                if m['type'] == 1: record['Peso'] = round(val, 2)
                elif m['type'] == 6: record['Grasa_Pct'] = round(val, 2)
                elif m['type'] == 76: record['Masa_Muscular_Kg'] = round(val, 2)
            if record['Peso']: nuevos.append(record)
        
        df_new = pd.DataFrame(nuevos)
        df_new['Fuente'] = 'Withings Cloud'
        print(f"      Nuevos registros Withings: {len(nuevos)} - Fechas: {df_new['Fecha'].tolist() if not df_new.empty else 'Ninguna'}")
        ruta_out = os.path.join(config.DATA_PROCESSED, 'historial_withings_raw.csv')
        if os.path.exists(ruta_out):
            df_old = pd.read_csv(ruta_out, sep=';')
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        else: df_final = df_new
        df_final = df_final.drop_duplicates(subset=['Fecha'], keep='last')
        df_final = _format_columns_es(df_final, {
            'Peso': 2,
            'Grasa_Pct': 2,
            'Masa_Muscular_Kg': 2,
        })
        df_final.to_csv(ruta_out, sep=';', index=False)
        return f"[OK] Withings: +{len(nuevos)} pesajes."
    return f"[ERROR] Error Withings: {data['status']}"

def sincronizar_todo():
    print("\nCLOUD INICIANDO SINCRONIZACIÓN TOTAL...")
    res_garmin = sync_garmin_module()
    res_withings = sync_withings_module()
    
    # Auto-actualizar estadísticas (movido a super_merger.py para asegurar datos frescos)
    # Detectar patrones automáticamente
    try:
        from context_manager import ContextManager
        ctx_mgr = ContextManager()
        
        # Detectar patrones automáticamente
        print("   🔍 Detectando patrones...")
        from pattern_detector import PatternDetector
        detector = PatternDetector(ctx_mgr)
        patterns = detector.analyze_all_patterns()
        
        if patterns:
            print(f"   [OK] {len(patterns)} patrones encontrados")
            ctx_mgr.update_insights_from_patterns(patterns)
        else:
            print("   [INFO] No se detectaron patrones nuevos")
            
    except Exception as e:
        print(f"   [WARNING] Error en analisis automatico: {e}")
    
    return f"{res_garmin} | {res_withings}"

if __name__ == "__main__":
    print(sincronizar_todo())


