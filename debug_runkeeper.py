# debug_runkeeper.py - Diagnóstico de Fechas
import pandas as pd
import config
import os

def diagnosticar():
    print("🔍 INSPECCIÓN DE ARCHIVO RAW RUNKEEPER")
    print("-" * 50)
    
    ruta = os.path.join(config.DATA_RAW, 'runkeeper_export', 'cardioActivities.csv')
    
    if not os.path.exists(ruta):
        print(f"❌ ERROR CRÍTICO: No encuentro el archivo en: {ruta}")
        return

    try:
        # Leemos el archivo tal cual es, sin tocar nada
        df = pd.read_csv(ruta)
        print(f"✅ Archivo cargado. Total de filas crudas: {len(df)}")
        print("\n--- MUESTRA DE LAS PRIMERAS 3 FILAS ---")
        print(df[['Date', 'Type', 'Distance (km)']].head(3))
        
        print("\n--- MUESTRA DE LAS ÚLTIMAS 3 FILAS (Las más antiguas) ---")
        print(df[['Date', 'Type', 'Distance (km)']].tail(3))
        
        print("-" * 50)
        print("PRUEBA DE INTERPRETACIÓN DE FECHA:")
        # Tomamos la primera fecha y probamos si pandas la entiende
        primera_fecha = df.iloc[0]['Date']
        print(f"Fecha cruda ejemplo: '{primera_fecha}'")
        
        try:
            fechita = pd.to_datetime(primera_fecha)
            print(f"✅ Pandas la interpreta como: {fechita}")
        except:
            print("❌ Pandas NO puede leer este formato automáticamente.")

    except Exception as e:
        print(f"⚠️ Error leyendo el CSV: {e}")

if __name__ == "__main__":
    diagnosticar()