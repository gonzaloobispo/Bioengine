# pesobook_importer.py - Rescatista de Datos Históricos (Corregido)
import pandas as pd
import os
import config

def procesar_pesobook():
    print("📜 Procesando archivo histórico PESOBOOK...")
    
    # Ruta específica detectada en la auditoría
    ruta = os.path.join(config.DATA_RAW, 'bio-engine', 'data', 'staging', 'pesobook_history.csv')
    
    if not os.path.exists(ruta):
        print("   ⚠️ No se encontró el archivo pesobook_history.csv")
        return pd.DataFrame()

    try:
        # Lectura directa
        df = pd.read_csv(ruta)
        
        # Renombrar columnas al estándar del Bio-Engine
        df = df.rename(columns={
            'fecha': 'Fecha',
            'peso_kg': 'Peso'
        })
        
        # Agregar columnas faltantes para compatibilidad
        df['Grasa_Pct'] = None
        df['Masa_Muscular_Kg'] = None
        df['Fuente'] = 'PesoBook (Histórico)'
        
        # Asegurar formato de fecha
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        
        print(f"   ✅ PESOBOOK: {len(df)} registros históricos recuperados (2014 era).")
        return df

    except Exception as e:
        print(f"   ❌ Error leyendo PesoBook: {e}")
        return pd.DataFrame()