import pandas as pd
import os
import config
from datetime import date, datetime

def _parse_fecha_mixta(series):
    series = series.astype(str).str.strip()
    parsed = pd.to_datetime(series, format='%Y-%m-%d %H:%M:%S', errors='coerce')
    return parsed.fillna(pd.to_datetime(series, format='%Y-%m-%d', errors='coerce'))

def _parse_num_es(series):
    s = series.astype(str).str.strip()
    s = s.replace('', pd.NA)
    has_comma = s.str.contains(',', na=False)
    s = s.where(~has_comma, s.str.replace('.', '', regex=False).str.replace(',', '.', regex=False))
    return pd.to_numeric(s, errors='coerce')

print("--- DEBUG DATA LOADING ---")
path = config.CSV_PESO_MAESTRO
print(f"Loading: {path}")
if os.path.exists(path):
    df = pd.read_csv(path, sep=';')
    print(f"Raw rows: {len(df)}")
    df['Fecha_Parsed'] = _parse_fecha_mixta(df['Fecha'])
    df['Peso_Parsed'] = _parse_num_es(df['Peso'])
    
    print("\nTop 5 rows after parsing:")
    print(df[['Fecha', 'Peso', 'Fecha_Parsed', 'Peso_Parsed']].head())
    
    print(f"\nNaT in Fecha_Parsed: {df['Fecha_Parsed'].isna().sum()}")
    print(f"NaN in Peso_Parsed: {df['Peso_Parsed'].isna().sum()}")
    
    last_row = df.sort_values('Fecha_Parsed').iloc[-1]
    print(f"\nLast entry found: {last_row['Fecha_Parsed']} -> {last_row['Peso_Parsed']}")
    
    # Simulate dashboard filter
    start_date = date(2024, 1, 1)
    end_date = date.today()
    df_f = df[(df['Fecha_Parsed'].dt.date >= start_date) & (df['Fecha_Parsed'].dt.date <= end_date)]
    print(f"\nRows in range {start_date} to {end_date}: {len(df_f)}")
    if not df_f.empty:
        last_p = df_f.sort_values('Fecha_Parsed').iloc[-1]['Peso_Parsed']
        print(f"Last Peso in range: {last_p}")
else:
    print("File not found.")
