# bio_engine.py - Conector de Extracción de Datos (ETL - Versión Blindada)
import config
import pandas as pd
import json
import time
import os
import sys
from garminconnect import Garmin

# Intentar importar el módulo de auth de Withings si existe en la carpeta
try:
    import withings_auth
    WITHINGS_ACTIVO = True
except ImportError:
    WITHINGS_ACTIVO = False

def get_garmin_details(activity):
    """Extrae métricas biomecánicas avanzadas del JSON de Garmin"""
    detalles = {
        "Cadencia_Media": 0,
        "Oscilacion_Vertical": 0,
        "Tiempo_Contacto": 0,
        "FC_Max": 0,
        "Training_Effect": 0.0
    }
    try:
        # Uso de .get() para evitar errores si el campo no existe
        detalles["Cadencia_Media"] = activity.get('averageRunningCadenceInStepsPerMinute', 0)
        detalles["Oscilacion_Vertical"] = activity.get('avgVerticalOscillation', 0)
        detalles["Tiempo_Contacto"] = activity.get('avgGroundContactTime', 0)
        detalles["FC_Max"] = activity.get('maxHeartRate', 0)
        detalles["Training_Effect"] = activity.get('aerobicTrainingEffect', 0.0)
    except Exception:
        pass 
    return detalles

def update_garmin():
    print("⌚ CONECTANDO CON GARMIN CONNECT (MODO BLINDADO)...")
    try:
        if "TuPassword" in config.GARMIN_PASSWORD:
            print("❌ ERROR: Debes poner tu contraseña real en config.py")
            return

        api = Garmin(config.GARMIN_EMAIL, config.GARMIN_PASSWORD)
        api.login()
        
        # --- ESTRATEGIA DE PAGINACIÓN ---
        TOTAL_OBJETIVO = 2000
        BATCH_SIZE = 100
        all_activities = []
        
        print(f"   -> Iniciando descarga de historial (Objetivo: {TOTAL_OBJETIVO})...")
        
        start = 0
        while start < TOTAL_OBJETIVO:
            print(f"      ... Descargando lote {start} a {start + BATCH_SIZE} ...")
            batch = api.get_activities(start, BATCH_SIZE)
            
            if not batch:
                print("      -> Fin de los registros disponibles en el servidor.")
                break
                
            all_activities.extend(batch)
            start += BATCH_SIZE
            time.sleep(1) 
            
        print(f"   -> Descarga finalizada. Procesando {len(all_activities)} registros...")
        
        data_list = []
        for act in all_activities:
            try:
                # --- EXTRACCIÓN SEGURA (SAFE GET) ---
                # Usamos .get('campo', 0) para que si falta el dato, ponga 0 en lugar de fallar
                
                distancia_m = act.get('distance', 0) or 0  # El 'or 0' es por si viene None
                duracion_s = act.get('duration', 0) or 0
                
                fila = {
                    "Fecha": act.get('startTimeLocal', '')[:10],
                    "Tipo": act.get('activityType', {}).get('typeKey', 'unknown'),
                    "Nombre": act.get('activityName', 'Actividad Sin Nombre'),
                    "Distancia (km)": round(distancia_m / 1000, 2),
                    "Duracion (min)": round(duracion_s / 60, 2),
                    "Calorias": act.get('calories', 0),
                    "FC Media": act.get('averageHR', 0),
                    "Elevacion (m)": act.get('totalElevationGain', 0),
                    "Fuente_Origen": "Garmin"
                }
                
                # Datos Avanzados
                detalles = get_garmin_details(act)
                fila.update(detalles)
                data_list.append(fila)
            except Exception as e_fila:
                # Si una fila específica falla, la saltamos pero no paramos todo el proceso
                print(f"⚠️ Alerta menor: Saltando actividad corrupta ({e_fila})")
                continue
            
        # Guardar CSV intermedio
        df = pd.DataFrame(data_list)
        # Limpieza básica
        df = df[df['Fecha'] != ''] # Eliminar filas sin fecha
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df = df.sort_values('Fecha', ascending=False)
        
        # Guardar en data_processed
        ruta_garmin = os.path.join(config.DATA_PROCESSED, 'historial_garmin_raw.csv')
        df.to_csv(ruta_garmin, sep=';', index=False, encoding='utf-8')
        print(f"✅ ÉXITO: {len(df)} actividades procesadas y guardadas.")
        
    except Exception as e:
        print(f"❌ Error crítico general en Garmin: {e}")

def update_withings():
    print("⚖️ INTENTANDO ACTUALIZAR WITHINGS...")
    if WITHINGS_ACTIVO:
        try:
            print("   -> Ejecutando script de autenticación...")
            import subprocess
            result = subprocess.run([sys.executable, 'withings_auth.py'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Proceso de Withings finalizado.")
            else:
                print(f"❌ Error ejecutando Withings: {result.stderr}")
        except Exception as e:
            print(f"❌ Error ejecutando Withings: {e}")
    else:
        print("⚠️ No se encontró 'withings_auth.py'. Saltando actualización de peso.")

if __name__ == "__main__":
    print("\n--- INICIANDO AUDITORÍA MASIVA DE DATOS ---")
    update_garmin()
    update_withings()
    print("--- FIN DEL PROCESO ---")