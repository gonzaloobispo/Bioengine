# check_oldest.py - Auditoría de Antigüedad
import pandas as pd
import config
import os

def check():
    print("🕰️ AUDITORÍA DE ANTIGÜEDAD DE DATOS")
    print("-" * 50)

    # 1. DEPORTES
    if os.path.exists(config.CSV_DEPORTE_MAESTRO):
        df = pd.read_csv(config.CSV_DEPORTE_MAESTRO, sep=';')
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        
        oldest = df['Fecha'].min()
        newest = df['Fecha'].max()
        count_pre_2015 = len(df[df['Fecha'].dt.year < 2015])
        
        print(f"🏃 DEPORTES:")
        print(f"   -> Registro más antiguo: {oldest.strftime('%d/%m/%Y')}")
        print(f"   -> Registro más reciente: {newest.strftime('%d/%m/%Y')}")
        print(f"   -> Cantidad de registros antes de 2015: {count_pre_2015}")
        
        if count_pre_2015 > 0:
            print("\n   🔍 Muestra de datos viejos (Pre-2015):")
            print(df[df['Fecha'].dt.year < 2015][['Fecha', 'Tipo', 'Distancia (km)']].head())
    else:
        print("❌ No existe base de datos deportiva.")

    print("-" * 50)

    # 2. PESO
    if os.path.exists(config.CSV_PESO_MAESTRO):
        df = pd.read_csv(config.CSV_PESO_MAESTRO, sep=';')
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        
        oldest = df['Fecha'].min()
        count_pre_2015 = len(df[df['Fecha'].dt.year < 2015])
        
        print(f"⚖️ PESO:")
        print(f"   -> Registro más antiguo: {oldest.strftime('%d/%m/%Y')}")
        print(f"   -> Registros antes de 2015: {count_pre_2015}")
    else:
        print("❌ No existe base de datos de peso.")

if __name__ == "__main__":
    check()