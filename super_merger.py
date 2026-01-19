# super_merger.py - Fusión Inteligente y Segura
import pandas as pd
import os
import config
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

def _parse_fecha_mixta(series):
    series = series.astype(str).str.strip()
    parsed = pd.to_datetime(series, format='%Y-%m-%d %H:%M:%S', errors='coerce')
    return parsed.fillna(pd.to_datetime(series, format='%Y-%m-%d', errors='coerce'))

def _normalize_fuente_labels(series):
    s = series.astype(str).str.strip()
    s = s.replace('Pesobook (Histórico)', 'Pesobook')
    s = s.replace('PesoBook (Histórico)', 'Pesobook')
    s = s.replace('Apple Health', 'Apple')
    s = s.replace('Apple Health XML', 'Apple')
    s = s.replace('Apple CDA (Medical Doc)', 'Apple')
    s = s.replace('Apple CDA (Brute Force)', 'Apple')
    s = s.replace('Apple CDA (Forensic)', 'Apple')
    s = s.replace('Apple CDA (Vacuum)', 'Apple')
    s = s.replace('Garmin Connect', 'Garmin')
    return s

def _normalize_tipo_actividad(series):
    """Unifica categorías de deportes para informes uniformes"""
    s = series.astype(str).str.strip().str.lower()
    mapping = {
        'street_running': 'Running',
        'running': 'Running',
        'trail_running': 'Trail Running',
        'trail': 'Trail Running',
        'cycling': 'Ciclismo',
        'road_cycling': 'Ciclismo',
        'mountain_biking': 'Ciclismo',
        'walking': 'Caminata',
        'hiking': 'Caminata',
        'tennis': 'Tenis',
        'tenis': 'Tenis',
        'indoor_cycling': 'Ciclismo (Indoor)',
        'treadmill_running': 'Running (Cinta)',
    }
    
    def apply_map(val):
        for k, v in mapping.items():
            if k in val:
                return v
        return val.title() if val != 'nan' else 'Otros'
        
    return s.apply(apply_map)


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
            df[col] = df[col].map(lambda v: _format_num_es(v, decimals=decimals))
    return df

def fusionar_deportes():
    print("INICIANDO FUSION DE DATOS DEPORTIVOS (Normalización Completa)...")
    fuentes = []

    # Schema unificado basado en Garmin API
    COLUMNAS_MAESTRAS = [
        'Fecha', 'Tipo', 'Distancia (km)', 'Duracion (min)', 'Calorias', 
        'FC Media', 'FC Max', 'Elevacion (m)', 'Cadencia_Media', 'Fuente'
    ]

    # 1. Garmin
    ruta_garmin = os.path.join(config.DATA_PROCESSED, 'historial_garmin_raw.csv')
    if os.path.exists(ruta_garmin):
        df_g = pd.read_csv(ruta_garmin, sep=';')
        df_g['Fuente'] = df_g.get('Fuente', 'Garmin Cloud')
        fuentes.append(df_g)

    # 2. Runkeeper
    ruta_runkeeper = os.path.join(config.DATA_PROCESSED, 'historial_runkeeper_puro.csv')
    if os.path.exists(ruta_runkeeper):
        df_rk = pd.read_csv(ruta_runkeeper, sep=';')
        df_rk['Fuente'] = 'Runkeeper'
        # No tiene mas que Distancia, Duracion, Tipo.
        fuentes.append(df_rk)

    # 3. Apple
    ruta_apple = os.path.join(config.DATA_PROCESSED, 'historial_apple_deportes.csv')
    if os.path.exists(ruta_apple):
        df_a = pd.read_csv(ruta_apple, sep=';')
        # Mapeo de columnas Apple -> Garmin Schema
        mapping_apple = {
            'Distancia_km': 'Distancia (km)',
            'Duracion_min': 'Duracion (min)',
            'Fuente': 'Fuente'
        }
        df_a = df_a.rename(columns=mapping_apple)
        df_a['Fuente'] = 'Apple'
        fuentes.append(df_a)

    if not fuentes:
        print("   ?? No hay fuentes deportivas disponibles para fusionar.")
        return

    df_all = pd.concat(fuentes, ignore_index=True)
    if 'Fecha' not in df_all.columns:
        print("   ?? No se encontró columna Fecha en los datos deportivos.")
        return

    # Normalización de Fechas
    df_all['Fecha'] = _parse_fecha_mixta(df_all['Fecha'])
    df_all = df_all.dropna(subset=['Fecha'])

    # Normalización de Categorías y Fuentes
    if 'Tipo' in df_all.columns:
        df_all['Tipo'] = _normalize_tipo_actividad(df_all['Tipo'])
    if 'Fuente' in df_all.columns:
        df_all['Fuente'] = _normalize_fuente_labels(df_all['Fuente'])

    # Mapeo de columnas alternativas que puedan haber quedado
    alt_mappings = {
        'Average Heart Rate (bpm)': 'FC Media',
        'Average Heart Rate': 'FC Media',
        'Average HR': 'FC Media',
        'Climb (m)': 'Elevacion (m)',
        'Elevation Gain': 'Elevacion (m)',
        'Max HR': 'FC Max',
        'Average Speed (km/h)': 'Velocidad Media' # Opcional, pero Garmin lo da
    }
    df_all = df_all.rename(columns=alt_mappings)

    # Asegurar que existan todas las columnas maestras
    for col in COLUMNAS_MAESTRAS:
        if col not in df_all.columns:
            df_all[col] = None

    # Eliminar información innecesaria (columnas que no están en el schema maestro o calculado posteriormente)
    # Mantener columnas que usará el proceso de calzado/stress después
    columnas_a_mantener = COLUMNAS_MAESTRAS + ['Calzado', 'Evento_Nombre', 'Stress_Score']
    
    # Filtrar solo columnas existentes que queremos
    cols_presentes = [c for c in df_all.columns if c in columnas_a_mantener]
    df_all = df_all[cols_presentes]

    # Ordenar y deduplicar
    df_all = df_all.sort_values('Fecha', ascending=False)
    # Dedupe por fecha, tipo y distancia (para evitar solapamientos entre fuentes)
    df_all = df_all.drop_duplicates(subset=['Fecha', 'Tipo', 'Distancia (km)'], keep='first')

    # Formateo final
    df_all = _format_columns_es(df_all, {
        'Distancia (km)': 2,
        'Duracion (min)': 1,
        'Calorias': 0,
        'FC Media': 0,
        'FC Max': 0,
        'Elevacion (m)': 0,
        'Cadencia_Media': 0,
        'Stress_Score': 2
    })
    
    # Reordenar columnas para que se vea limpio
    final_cols = [c for c in COLUMNAS_MAESTRAS if c in df_all.columns]
    df_all = df_all[final_cols]

    df_all.to_csv(config.CSV_DEPORTE_MAESTRO, sep=';', index=False)
    print(f"Fusion deportiva completada. Total registros: {len(df_all)}")


def actualizacion_rapida():
    print("INICIANDO INTEGRACION DE CALZADO Y CARRERAS...")
    
    # 1. Cargar el Calendario de Carreras
    ruta_cal_csv = os.path.join(config.DATA_PROCESSED, 'calendario_gonzalo.csv')
    ruta_cal_xlsx = os.path.join(config.DATA_PROCESSED, 'calendario_gonzalo.xlsx')
    if os.path.exists(ruta_cal_xlsx):
        df_cal = pd.read_excel(ruta_cal_xlsx)
    elif os.path.exists(ruta_cal_csv):
        df_cal = pd.read_csv(ruta_cal_csv)
    else:
        df_cal = pd.DataFrame()
    if not df_cal.empty:
        df_cal['Fecha'] = pd.to_datetime(df_cal['Fecha'])

    # 2. Fusionar deportes (todas las fuentes)
    fusionar_deportes()

    # 3. Cargar el Maestro de Deportes
    if os.path.exists(config.CSV_DEPORTE_MAESTRO):
        df_m = pd.read_csv(config.CSV_DEPORTE_MAESTRO, sep=';')
        df_m['Fecha'] = pd.to_datetime(df_m['Fecha'])
        
        conteo_inicial = len(df_m)

        def asignar_calzado(row):
            # Regla 1: Carrera del calendario
            if not df_cal.empty and 'Fecha' in row and pd.notna(row['Fecha']):
                match = df_cal[df_cal['Fecha'].dt.date == row['Fecha'].date()]
                if not match.empty:
                    return match.iloc[0].get('ZAPATOS', 'Brooks Adrenaline GTS 23'), match.iloc[0].get('Nombre ', 'Carrera')
            
            # Regla 2: Tenis
            tipo = str(row.get('Tipo', '')).lower()
            if (('tenis' in tipo or 'tennis' in tipo) and tipo != 'nan'):
                return "Babolat Fury 3", "Tenis"
            
            # Regla 3: Default para el resto
            return "Brooks Adrenaline GTS 23", "Entrenamiento"

        res = df_m.apply(asignar_calzado, axis=1)
        df_m['Calzado'], df_m['Evento_Nombre'] = zip(*res)

        # 2b. Calcular Stress Score (Auditoría de Rodilla)
        import metrics_engine
        # Necesitamos el peso para el stress score. Cargamos el maestro de peso.
        df_p = pd.read_csv(config.CSV_PESO_MAESTRO, sep=';') if os.path.exists(config.CSV_PESO_MAESTRO) else pd.DataFrame()
        if not df_p.empty:
            df_p['Fecha'] = _parse_fecha_mixta(df_p['Fecha']).dt.date
            # Mapear peso a cada actividad por fecha (usar el último del día o el más cercano anterior)
            # Para simplificar ahora, usamos match exacto por día
            df_p_map = df_p.drop_duplicates('Fecha', keep='first').set_index('Fecha')['Peso']
            
            def calculate_row_stress(row):
                fecha_cal = row['Fecha'].date()
                peso = df_p_map.get(fecha_cal, 76.0) # Default si no hay dato
                # Limpiar valores numéricos
                def clean_num(v):
                    if pd.isna(v): return 0
                    if isinstance(v, str): return float(v.replace('.','').replace(',','.'))
                    return float(v)
                
                return metrics_engine.calcular_stress_rodilla(
                    actividad_tipo=row.get('Tipo', 'otros'),
                    duracion_min=clean_num(row.get('Duracion (min)', 0)),
                    elevacion_m=clean_num(row.get('Elevacion (m)', 0)),
                    peso_actual=clean_num(peso)
                )
            
            df_m['Stress_Score'] = df_m.apply(calculate_row_stress, axis=1)

        # Unificar nombres equivalentes de calzado

        df_m['Calzado'] = df_m['Calzado'].replace({
            'Brooks GTS 23': 'Brooks Adrenaline GTS 23',
        })
        
        df_m = df_m.sort_values('Fecha', ascending=False)
        df_m.to_csv(config.CSV_DEPORTE_MAESTRO, sep=';', index=False)
        
        print(f"Proceso terminado. Registros procesados: {len(df_m)} (Originales: {conteo_inicial})")

    # 4. Fusionar datos de peso: APIs y maestro completo (APIs + historicos)
    fusionar_peso()
    fusionar_peso_completo()
    
    # 5. Recalcular estadísticas contextuales (ahora que los CSVs están actualizados)
    try:
        from context_manager import ContextManager
        ctx = ContextManager()
        ctx.recalculate_stats_from_csv()
        print("   [OK] Estadísticas contextuales recalculadas.")
    except Exception as e:
        print(f"   [WARNING] No se pudo actualizar el contexto: {e}")



def fusionar_peso_completo():
    print("INICIANDO FUSION DE PESO (Integración y Limpieza)...")
    fuentes = []
    
    COLUMNAS_PESO = ['Fecha', 'Peso', 'Grasa_Pct', 'Masa_Muscular_Kg', 'Fuente']

    # 1. Withings (Prioridad como estándar)
    ruta_withings = os.path.join(config.DATA_PROCESSED, 'historial_withings_raw.csv')
    if os.path.exists(ruta_withings):
        df_w = pd.read_csv(ruta_withings, sep=';')
        if 'Fuente' not in df_w.columns:
            df_w['Fuente'] = 'Withings Cloud'
        fuentes.append(df_w)

    # 2. Histórico (PesoBook, Apple, etc.)
    ruta_maestro_hist = os.path.join(config.DATA_PROCESSED, 'historial_completo_peso.csv')
    if os.path.exists(ruta_maestro_hist):
        df_h = pd.read_csv(ruta_maestro_hist, sep=';')
        fuentes.append(df_h)

    if not fuentes:
        print("   ?? No hay fuentes de peso disponibles para fusionar.")
        return

    df_all = pd.concat(fuentes, ignore_index=True)
    if 'Fecha' not in df_all.columns:
        print("   ?? No se encontró columna Fecha en los datos de peso.")
        return

    # Normalización de Fechas
    df_all['Fecha'] = _parse_fecha_mixta(df_all['Fecha'])
    df_all = df_all.dropna(subset=['Fecha'])

    # Asegurar columnas estándar
    for col in COLUMNAS_PESO:
        if col not in df_all.columns:
            df_all[col] = None

    # Normalización de Fuente
    df_all['Fuente'] = df_all['Fuente'].fillna('Withings Cloud')
    df_all['Fuente'] = df_all['Fuente'].astype(str).str.strip().replace(['', 'nan'], 'Withings Cloud')
    df_all['Fuente'] = _normalize_fuente_labels(df_all['Fuente'])

    # Eliminar información redundante (mantener solo schema básico)
    df_all = df_all[COLUMNAS_PESO]

    # Dedupe por día: preferir el último registro del día (el más reciente)
    df_all['Fecha_dia'] = df_all['Fecha'].dt.date
    df_all = df_all.sort_values('Fecha')
    df_all = df_all.drop_duplicates(subset=['Fecha_dia'], keep='last')
    df_all = df_all.drop(columns=['Fecha_dia'])
    
    # Ordenar cronológicamente descendente
    df_all = df_all.sort_values('Fecha', ascending=False)

    # Formateo numérico
    df_all = _format_columns_es(df_all, {
        'Peso': 2,
        'Grasa_Pct': 2,
        'Masa_Muscular_Kg': 2,
    })

    df_all.to_csv(config.CSV_PESO_MAESTRO, sep=';', index=False)
    print(f"Fusion de peso completa. Registros finales: {len(df_all)}")

def fusionar_peso():
    print("INICIANDO FUSION DE DATOS DE PESO (Solo APIs)...")
    
    ruta_raw = os.path.join(config.DATA_PROCESSED, 'historial_withings_raw.csv')
    if not os.path.exists(ruta_raw):
        print("   ⚠️ No hay datos raw de Withings para fusionar.")
        return
    
    df_raw = pd.read_csv(ruta_raw, sep=';')
    if df_raw.empty:
        print("   ⚠️ Datos raw de Withings están vacíos.")
        return
    
    print(f"   -> Datos raw: {len(df_raw)} registros")
    df_raw['Fecha'] = _parse_fecha_mixta(df_raw['Fecha'])
    
    # No concatenar con maestro existente, solo usar datos de APIs
    df_final = df_raw
    
    # Normalizar fechas a date para eliminar duplicados por día (dentro de APIs)
    df_final['Fecha_dia'] = df_final['Fecha'].dt.date
    fechas_unicas = df_final['Fecha_dia'].nunique()
    print(f"   -> Fechas unicas antes drop: {fechas_unicas}")
    df_final = df_final.sort_values('Fecha').drop_duplicates(subset=['Fecha_dia'], keep='last')
    print(f"   -> Después drop_duplicates: {len(df_final)} registros")
    df_final = df_final.drop(columns=['Fecha_dia'])
    df_final = df_final.sort_values('Fecha', ascending=False)
    
    df_final = _format_columns_es(df_final, {
        'Peso': 2,
        'Grasa_Pct': 2,
        'Masa_Muscular_Kg': 2,
    })
    df_final.to_csv(config.CSV_PESO_MAESTRO_APIS, sep=';', index=False)
    print(f"Fusión de peso completada. Total registros en maestro APIs: {len(df_final)}, fecha máxima: {df_final['Fecha'].max()}")


if __name__ == "__main__":
    actualizacion_rapida()
