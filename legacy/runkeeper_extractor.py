import pandas as pd
import os

def procesar_runkeeper():
    path = r'C:\BioEngine_Gonzalo\runkeeper_export\cardioActivities.csv'
    
    if not os.path.exists(path):
        print(f"❌ No se encontró el archivo en: {path}")
        return

    print("--- 🏃 PROCESANDO HISTÓRICO DE RUNKEEPER ---")
    
    # Leer el CSV de Runkeeper (suelen usar coma como separador)
    df = pd.read_csv(path)
    
    # Seleccionar y renombrar columnas para que coincidan con nuestro Bio-Engine
    # Columnas típicas de Runkeeper: 'Date', 'Type', 'Distance (km)', 'Duration', 'Calories Burned'
    df_clean = df[['Date', 'Type', 'Distance (km)', 'Duration', 'Calories Burned']].copy()
    
    # Convertir fecha al formato estándar del Bio-Engine (dd/mm/yyyy)
    df_clean['Date'] = pd.to_datetime(df_clean['Date']).dt.strftime('%d/%m/%Y')
    
    # Renombrar para consistencia
    df_clean.columns = ['Fecha', 'Tipo', 'Nombre', 'Distancia (km)', 'Duracion (min)']
    # (Ajustamos 'Nombre' para que guarde el tipo original)
    df_clean['Nombre'] = "Runkeeper: " + df_clean['Tipo']
    
    output = 'historial_runkeeper_puro.csv'
    df_clean.to_csv(output, sep=';', index=False, encoding='utf-8')
    
    print(f"✅ ÉXITO: Se procesaron {len(df_clean)} actividades de Runkeeper.")
    print(f"📂 Archivo generado: {output}")

if __name__ == "__main__":
    procesar_runkeeper()