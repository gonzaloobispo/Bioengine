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
    print("INICIANDO FUSION DE DATOS DEPORTIVOS (Todas las Fuentes)...")
    fuentes = []

    ruta_garmin = os.path.join(config.DATA_PROCESSED, 'historial_garmin_raw.csv')
    if os.path.exists(ruta_garmin):
        df_g = pd.read_csv(ruta_garmin, sep=';')
        df_g['Fuente'] = df_g.get('Fuente_Origen', 'Garmin')
        fuentes.append(df_g)

    ruta_runkeeper = os.path.join(config.DATA_PROCESSED, 'historial_runkeeper_puro.csv')
    if os.path.exists(ruta_runkeeper):
        df_rk = pd.read_csv(ruta_runkeeper, sep=';')
        df_rk['Fuente'] = df_rk.get('Fuente', 'Runkeeper')
        fuentes.append(df_rk)

    ruta_apple = os.path.join(config.DATA_PROCESSED, 'historial_apple_deportes.csv')
    if os.path.exists(ruta_apple):
        df_a = pd.read_csv(ruta_apple, sep=';')
        df_a['Fuente'] = df_a.get('Fuente', 'Apple Health')
        fuentes.append(df_a)

    if not fuentes:
        print("   ?? No hay fuentes deportivas disponibles para fusionar.")
        return

    df_all = pd.concat(fuentes, ignore_index=True)
    if 'Fecha' not in df_all.columns:
        print("   ?? No se encontr¢ columna Fecha en los datos deportivos.")
        return

    df_all['Fecha'] = _parse_fecha_mixta(df_all['Fecha'])
    df_all = df_all.dropna(subset=['Fecha'])

    # Normalización de categorías y fuentes
    if 'Tipo' in df_all.columns:
        df_all['Tipo'] = _normalize_tipo_actividad(df_all['Tipo'])
    if 'Fuente' in df_all.columns:
        df_all['Fuente'] = _normalize_fuente_labels(df_all['Fuente'])

    for col in ['Tipo', 'Distancia (km)', 'Duracion (min)', 'Calorias']:
        if col not in df_all.columns:
            df_all[col] = None

    df_all = df_all.sort_values('Fecha', ascending=False)
    df_all = df_all.drop_duplicates(subset=['Fecha', 'Tipo', 'Distancia (km)'], keep='first')


    df_all = _format_columns_es(df_all, {
        'Distancia (km)': 2,
        'Duracion (min)': 1,
        'Calorias': 0,
        'FC Media': 0,
        'Elevacion (m)': 0,
        'Cadencia_Media': 0,
        'Oscilacion_Vertical': 2,
        'Tiempo_Contacto': 2,
        'FC_Max': 0,
        'Training_Effect': 2,
        'Distancia_km': 2,
        'Duracion_min': 1,
        'Average Speed (km/h)': 2,
        'Climb (m)': 0,
        'Average Heart Rate (bpm)': 0,
        'Stress_Score': 2,
    })
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



def fusionar_peso_completo():
    print("INICIANDO FUSION DE PESO (APIs + Historicos)...")
    fuentes = []

    ruta_withings = os.path.join(config.DATA_PROCESSED, 'historial_withings_raw.csv')
    if os.path.exists(ruta_withings):
        df_w = pd.read_csv(ruta_withings, sep=';')
        if 'Fuente' not in df_w.columns:
            df_w['Fuente'] = 'Withings Cloud'
        fuentes.append(df_w)

    ruta_maestro_hist = os.path.join(config.DATA_PROCESSED, 'historial_completo_peso.csv')
    if os.path.exists(ruta_maestro_hist):
        df_h = pd.read_csv(ruta_maestro_hist, sep=';')
        fuentes.append(df_h)

    if not fuentes:
        print("   ?? No hay fuentes de peso disponibles para fusionar.")
        return

    df_all = pd.concat(fuentes, ignore_index=True)
    if 'Fecha' not in df_all.columns:
        print("   ?? No se encontr¢ columna Fecha en los datos de peso.")
        return

    df_all['Fecha'] = _parse_fecha_mixta(df_all['Fecha'])
    df_all = df_all.dropna(subset=['Fecha'])

    # Normalizar columnas
    for col in ['Peso', 'Grasa_Pct', 'Masa_Muscular_Kg', 'Fuente']:
        if col not in df_all.columns:
            df_all[col] = None
    df_all['Fuente'] = df_all['Fuente'].fillna('Withings Cloud')
    df_all['Fuente'] = df_all['Fuente'].astype(str).str.strip().replace('', 'Withings Cloud')
    df_all['Fuente'] = _normalize_fuente_labels(df_all['Fuente'])

    # Dedupe por dia: preferir ultimo registro del dia
    df_all['Fecha_dia'] = df_all['Fecha'].dt.date
    df_all = df_all.sort_values('Fecha')
    df_all = df_all.drop_duplicates(subset=['Fecha_dia'], keep='last')
    df_all = df_all.drop(columns=['Fecha_dia'])
    df_all = df_all.sort_values('Fecha', ascending=False)

    df_all = _format_columns_es(df_all, {
        'Peso': 2,
        'Grasa_Pct': 2,
        'Masa_Muscular_Kg': 2,
    })
    df_all.to_csv(config.CSV_PESO_MAESTRO, sep=';', index=False)
    print(f"Fusion de peso completa. Total registros: {len(df_all)}")

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
