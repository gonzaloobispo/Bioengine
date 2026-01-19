import pandas as pd
import os
import config

def _parse_fecha_mixta(series):
    series = series.astype(str).str.strip()
    parsed = pd.to_datetime(series, format='%Y-%m-%d %H:%M:%S', errors='coerce')
    return parsed.fillna(pd.to_datetime(series, format='%Y-%m-%d', errors='coerce'))

def fusionar_peso_completo():
    print("INICIANDO FUSION DE PESO (APIs + Historicos)...")
    fuentes = []

    ruta_withings = os.path.join(config.DATA_PROCESSED, 'historial_withings_raw.csv')
    if os.path.exists(ruta_withings):
        print(f"Loading raw withings: {ruta_withings}")
        df_w = pd.read_csv(ruta_withings, sep=';')
        print(f"Raw Withings rows: {len(df_w)}")
        if 'Fuente' not in df_w.columns:
            df_w['Fuente'] = 'Withings Cloud'
        fuentes.append(df_w)

    ruta_maestro_hist = os.path.join(config.DATA_PROCESSED, 'historial_completo_peso.csv')
    if os.path.exists(ruta_maestro_hist):
        print(f"Loading historical master: {ruta_maestro_hist}")
        df_h = pd.read_csv(ruta_maestro_hist, sep=';')
        print(f"Historical Master rows: {len(df_h)}")
        fuentes.append(df_h)

    if not fuentes:
        print("   ?? No hay fuentes de peso disponibles para fusionar.")
        return

    df_all = pd.concat(fuentes, ignore_index=True)
    print(f"Total after concat: {len(df_all)}")
    
    df_all['Fecha_Parsed'] = _parse_fecha_mixta(df_all['Fecha'])
    
    # Check if NaT
    print(f"NaT after parse: {df_all['Fecha_Parsed'].isna().sum()}")
    
    # Sort and Dedupe
    df_all['Fecha_dia'] = df_all['Fecha_Parsed'].dt.date
    df_all = df_all.sort_values('Fecha_Parsed')
    
    print("\nLast 5 before dedupe:")
    print(df_all[['Fecha', 'Peso', 'Fecha_dia']].tail())
    
    df_all = df_all.drop_duplicates(subset=['Fecha_dia'], keep='last')
    print(f"Total after dedupe: {len(df_all)}")
    
    print("\nLast 5 after dedupe:")
    print(df_all[['Fecha', 'Peso', 'Fecha_dia']].tail())

fusionar_peso_completo()
