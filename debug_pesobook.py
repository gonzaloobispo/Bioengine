# debug_pesobook.py - Análisis de Estructura de PesoBook
import pandas as pd
import config
import os

def escanear():
    print("🔬 INSPECCIÓN DE PESOBOOK")
    print("-" * 50)
    
    # Ruta exacta detectada en el escaneo anterior
    ruta = os.path.join(config.DATA_RAW, 'bio-engine', 'data', 'staging', 'pesobook_history.csv')
    
    if not os.path.exists(ruta):
        print("❌ No encuentro el archivo en la ruta esperada.")
        return

    try:
        # Intento 1: Lectura estándar con coma
        print("➡️ Intento de lectura (separador = COMA)...")
        df = pd.read_csv(ruta, nrows=5)
        print(f"   Columnas detectadas: {list(df.columns)}")
        print(df.head(3))
        
        # Validación rápida de fecha
        if len(df) > 0:
            col_fecha = df.columns[0] # Asumimos la primera
            ejemplo = df.iloc[0][col_fecha]
            print(f"\n📅 Ejemplo de fecha cruda: '{ejemplo}'")

    except Exception as e:
        print(f"❌ Error leyendo: {e}")
        
        try:
            # Intento 2: Punto y coma
            print("\n➡️ Intento de lectura (separador = PUNTO Y COMA)...")
            df = pd.read_csv(ruta, sep=';', nrows=5)
            print(f"   Columnas detectadas: {list(df.columns)}")
            print(df.head(3))
        except:
            pass

if __name__ == "__main__":
    escanear()