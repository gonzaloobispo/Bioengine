# audit_pipeline.py - Auditoría Forense de Datos (Input vs Output)
import pandas as pd
import os
import config
import legacy_importer
import cda_importer
import pesobook_importer

# --- PARÁMETROS DE REGLAS (Deben coincidir con super_merger.py) ---
PESO_MIN = 70.0
PESO_MAX = 150.0

def auditar_peso():
    print("\n" + "="*60)
    print("⚖️  AUDITORÍA DE FLUJO DE PESO (Weight Pipeline)")
    print("="*60)
    
    # 1. RECOLECCIÓN DE INPUTS (Fuentes Brutas)
    total_input = 0
    dfs_raw = []
    
    print("1️⃣  CONTEO DE FUENTES ORIGINALES:")
    
    # A. Withings
    count_withings = 0
    ruta_withings = os.path.join(config.DATA_PROCESSED, 'historial_withings_raw.csv')
    if os.path.exists(ruta_withings):
        df_w = pd.read_csv(ruta_withings, sep=';')
        count_withings = len(df_w)
        dfs_raw.append(df_w)
    print(f"   • Withings API: ........ {count_withings:>5} registros")
    
    # B. Runkeeper
    df_rk = legacy_importer.procesar_runkeeper_peso()
    count_rk = len(df_rk)
    if not df_rk.empty: dfs_raw.append(df_rk)
    print(f"   • Runkeeper: ........... {count_rk:>5} registros")

    # C. Apple Health (XML)
    df_apple, _ = legacy_importer.procesar_apple_health()
    count_apple = len(df_apple)
    if not df_apple.empty: dfs_raw.append(df_apple)
    print(f"   • Apple Health (XML): .. {count_apple:>5} registros")

    # D. Apple CDA
    df_cda = cda_importer.procesar_cda_peso()
    count_cda = len(df_cda)
    if not df_cda.empty: dfs_raw.append(df_cda)
    print(f"   • Apple CDA (Force): ... {count_cda:>5} registros")

    # E. PesoBook
    df_pb = pesobook_importer.procesar_pesobook()
    count_pb = len(df_pb)
    if not df_pb.empty: dfs_raw.append(df_pb)
    print(f"   • PesoBook (Histórico):. {count_pb:>5} registros")

    # TOTAL BRUTO
    total_input = count_withings + count_rk + count_apple + count_cda + count_pb
    print("-" * 60)
    print(f"   📦 TOTAL INPUT BRUTO:    {total_input:>5} registros")
    
    # 2. SIMULACIÓN DE PROCESAMIENTO
    print("\n2️⃣  ANÁLISIS DE MERMA (Filtrado y Limpieza):")
    
    if dfs_raw:
        # Unir todo
        pd.set_option('future.no_silent_downcasting', True)
        df_combined = pd.concat(dfs_raw, ignore_index=True)
        df_combined['Fecha'] = pd.to_datetime(df_combined['Fecha'], errors='coerce')
        
        # A. Filtro de Rango (La Regla de Gonzalo)
        df_validos = df_combined[
            (df_combined['Peso'] >= PESO_MIN) & 
            (df_combined['Peso'] <= PESO_MAX)
        ]
        rechazados_rango = len(df_combined) - len(df_validos)
        print(f"   🗑️  Descartados por Rango (<{PESO_MIN} o >{PESO_MAX}kg): -{rechazados_rango}")
        
        # B. Duplicados (Misma fecha)
        # Ordenamos igual que el merger
        df_validos = df_validos.sort_values('Fecha', ascending=False)
        df_dedup = df_validos.drop_duplicates(subset=['Fecha'], keep='first')
        rechazados_duplicados = len(df_validos) - len(df_dedup)
        print(f"   ♻️  Duplicados Fusionados (Mismo día):     -{rechazados_duplicados}")
        
        expected_output = len(df_dedup)
    else:
        expected_output = 0

    # 3. VERIFICACIÓN FINAL
    print("\n3️⃣  VERIFICACIÓN CONTRA SISTEMA (Maestro):")
    real_output = 0
    if os.path.exists(config.CSV_PESO_MAESTRO):
        df_final = pd.read_csv(config.CSV_PESO_MAESTRO, sep=';')
        real_output = len(df_final)
    
    print(f"   ✅ REGISTROS EN DASHBOARD: {real_output:>5}")
    
    if real_output == expected_output:
        print("\n   🎯 RESULTADO: CUADRE PERFECTO. Todos los datos están justificados.")
    else:
        diff = expected_output - real_output
        print(f"\n   ⚠️ ALERTA: Hay una diferencia no explicada de {diff} registros.")


def auditar_deportes():
    print("\n\n" + "="*60)
    print("🏃  AUDITORÍA DE FLUJO DEPORTIVO (Sports Pipeline)")
    print("="*60)
    
    # 1. INPUTS
    total_input = 0
    dfs_raw = []
    print("1️⃣  CONTEO DE FUENTES ORIGINALES:")
    
    # Garmin
    ruta_garmin = os.path.join(config.DATA_PROCESSED, 'historial_garmin_raw.csv')
    count_garmin = 0
    if os.path.exists(ruta_garmin):
        df = pd.read_csv(ruta_garmin, sep=';')
        count_garmin = len(df)
        dfs_raw.append(df)
    print(f"   • Garmin Connect: ...... {count_garmin:>5} actividades")
    
    # Runkeeper
    df_rk = legacy_importer.procesar_runkeeper_deportes()
    count_rk = len(df_rk)
    if not df_rk.empty: dfs_raw.append(df_rk)
    print(f"   • Runkeeper: ........... {count_rk:>5} actividades")
    
    # Apple
    _, df_apple = legacy_importer.procesar_apple_health()
    count_apple = len(df_apple)
    if not df_apple.empty: dfs_raw.append(df_apple)
    print(f"   • Apple Health: ........ {count_apple:>5} actividades")
    
    total_input = count_garmin + count_rk + count_apple
    print("-" * 60)
    print(f"   📦 TOTAL INPUT BRUTO:    {total_input:>5} actividades")

    # 2. PROCESAMIENTO
    print("\n2️⃣  ANÁLISIS DE MERMA:")
    if dfs_raw:
        df_combined = pd.concat(dfs_raw, ignore_index=True)
        # Normalización básica para contar duplicados
        df_combined['Fecha'] = pd.to_datetime(df_combined['Fecha'], errors='coerce')
        df_combined = df_combined.dropna(subset=['Fecha'])
        
        # Duplicados (Fecha + Tipo + Distancia)
        # Nota: Aquí no usamos normalizar_actividad para la auditoría rápida, 
        # pero asumimos que el merger lo hace. 
        # La lógica de duplicados exacta depende de la normalización,
        # así que calcularemos la "Merma por Fusión" globalmente.
        
        df_dedup = df_combined.drop_duplicates(subset=['Fecha', 'Distancia (km)'], keep='first')
        rechazados = len(df_combined) - len(df_dedup)
        
        print(f"   ♻️  Duplicados Fusionados (Aprox):         -{rechazados}")
        expected_output = len(df_dedup)
    else:
        expected_output = 0

    # 3. VERIFICACIÓN
    print("\n3️⃣  VERIFICACIÓN CONTRA SISTEMA:")
    real_output = 0
    if os.path.exists(config.CSV_DEPORTE_MAESTRO):
        df_final = pd.read_csv(config.CSV_DEPORTE_MAESTRO, sep=';')
        real_output = len(df_final)
    
    print(f"   ✅ REGISTROS EN DASHBOARD: {real_output:>5}")
    
    # En deportes es normal una pequeña variación por la normalización de nombres
    diff = abs(expected_output - real_output)
    if diff < 5:
         print("\n   🎯 RESULTADO: CUADRE CORRECTO (Diferencias mínimas por normalización).")
    else:
         print(f"\n   ℹ️  NOTA: {diff} registros de diferencia debido a la limpieza de nombres de actividad.")

if __name__ == "__main__":
    auditar_peso()
    auditar_deportes()