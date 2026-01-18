# legacy_importer.py - Con Smart Caching (Velocidad Extrema)
import pandas as pd
import xml.etree.ElementTree as ET
import os
import datetime
import config

# Archivos de caché para no releer XMLs gigantes si no han cambiado
CACHE_APPLE_SPORT = os.path.join(config.DATA_PROCESSED, 'cache_apple_sport.pkl')
CACHE_APPLE_WEIGHT = os.path.join(config.DATA_PROCESSED, 'cache_apple_weight.pkl')
CACHE_RK_SPORT = os.path.join(config.DATA_PROCESSED, 'cache_rk_sport.pkl')
CACHE_RK_WEIGHT = os.path.join(config.DATA_PROCESSED, 'cache_rk_weight.pkl')

def es_cache_valido(archivo_origen, archivo_cache):
    """Devuelve True si el caché existe y es más nuevo que el archivo origen"""
    if not os.path.exists(archivo_origen): return False
    if not os.path.exists(archivo_cache): return False
    
    t_origen = os.path.getmtime(archivo_origen)
    t_cache = os.path.getmtime(archivo_cache)
    
    return t_cache > t_origen

def procesar_runkeeper_deportes():
    # 1. Rutas
    ruta_rk = os.path.join(config.DATA_RAW, 'runkeeper_export', 'cardioActivities.csv')
    if not os.path.exists(ruta_rk): return pd.DataFrame()
    
    # 2. Chequeo Caché
    if es_cache_valido(ruta_rk, CACHE_RK_SPORT):
        print("   ⚡ (Runkeeper) Cargando desde caché rápido...")
        return pd.read_pickle(CACHE_RK_SPORT)
        
    print("📂 Buscando DEPORTES en Runkeeper (Procesando CSV)...")
    try:
        df = pd.read_csv(ruta_rk)
        df = df.rename(columns={
            'Date': 'Fecha',
            'Type': 'Tipo',
            'Distance (km)': 'Distancia (km)',
            'Duration (min)': 'Duracion (min)',
            'Calories Burned': 'Calorias'
        })
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Fuente'] = 'Runkeeper'
        
        # Guardar Caché
        df.to_pickle(CACHE_RK_SPORT)
        return df
    except Exception as e:
        print(f"❌ Error RK Sport: {e}")
        return pd.DataFrame()

def procesar_runkeeper_peso():
    ruta_rk = os.path.join(config.DATA_RAW, 'runkeeper_export', 'measurements.csv')
    if not os.path.exists(ruta_rk): return pd.DataFrame()
    
    if es_cache_valido(ruta_rk, CACHE_RK_WEIGHT):
        return pd.read_pickle(CACHE_RK_WEIGHT)
        
    try:
        df = pd.read_csv(ruta_rk)
        df = df.rename(columns={'Date': 'Fecha', 'Weight (kg)': 'Peso'})
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Fuente'] = 'Runkeeper'
        
        # Filtro básico
        df = df[df['Peso'] > 0]
        
        df.to_pickle(CACHE_RK_WEIGHT)
        return df
    except: return pd.DataFrame()

def procesar_apple_health():
    # Rutas
    ruta_xml = os.path.join(config.DATA_RAW, 'apple_health_export', 'exportar.xml')
    if not os.path.exists(ruta_xml): 
        print("❌ No se encuentra exportar.xml")
        return pd.DataFrame(), pd.DataFrame()
    
    # 2. Chequeo Caché (Si existe AMBOS caches y son válidos)
    if es_cache_valido(ruta_xml, CACHE_APPLE_WEIGHT) and es_cache_valido(ruta_xml, CACHE_APPLE_SPORT):
        print("   ⚡ (Apple Health) XML sin cambios. Usando caché instantáneo.")
        return pd.read_pickle(CACHE_APPLE_WEIGHT), pd.read_pickle(CACHE_APPLE_SPORT)

    print("🍎 Procesando Apple Health XML (Esto tardará solo si el archivo cambió)...")
    try:
        # Parseo XML (Lento)
        tree = ET.parse(ruta_xml)
        root = tree.getroot()
        
        # --- A. PESO ---
        data_peso = []
        for record in root.findall('Record'):
            if record.get('type') == "HKQuantityTypeIdentifierBodyMass":
                try:
                    fecha = record.get('startDate')
                    valor = float(record.get('value'))
                    data_peso.append({'Fecha': fecha, 'Peso': valor, 'Fuente': 'Apple Health XML'})
                except: pass
        df_peso = pd.DataFrame(data_peso)
        if not df_peso.empty:
            df_peso['Fecha'] = pd.to_datetime(df_peso['Fecha'])
            # Guardar Caché
            df_peso.to_pickle(CACHE_APPLE_WEIGHT)

        # --- B. DEPORTES ---
        data_sport = []
        for workout in root.findall('Workout'):
            try:
                activity_type = workout.get('workoutActivityType').replace('HKWorkoutActivityType', '')
                fecha = workout.get('startDate')
                duration = float(workout.get('duration', 0))
                
                dist = 0.0
                kcal = 0.0
                
                for stat in workout.findall('WorkoutStatistics'):
                    type_stat = stat.get('type')
                    if type_stat == "HKQuantityTypeIdentifierDistanceWalkingRunning":
                        dist = float(stat.get('sum', 0))
                    elif type_stat == "HKQuantityTypeIdentifierActiveEnergyBurned":
                        kcal = float(stat.get('sum', 0))
                
                data_sport.append({
                    'Fecha': fecha,
                    'Tipo': activity_type,
                    'Duracion (min)': round(duration, 2),
                    'Distancia (km)': round(dist, 2),
                    'Calorias': round(kcal, 0),
                    'Fuente': 'Apple Health XML'
                })
            except: pass
            
        df_sport = pd.DataFrame(data_sport)
        if not df_sport.empty:
            df_sport['Fecha'] = pd.to_datetime(df_sport['Fecha'])
            # Guardar Caché
            df_sport.to_pickle(CACHE_APPLE_SPORT)
            
        return df_peso, df_sport

    except Exception as e:
        print(f"❌ Error crítico leyendo XML Apple: {e}")
        return pd.DataFrame(), pd.DataFrame()