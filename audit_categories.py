# audit_categories.py - Inventario de Tipos de Deporte
import pandas as pd
import config
import os

def auditar():
    print("📋 AUDITORÍA DE CATEGORÍAS DEPORTIVAS")
    print("-" * 40)
    
    if os.path.exists(config.CSV_DEPORTE_MAESTRO):
        df = pd.read_csv(config.CSV_DEPORTE_MAESTRO, sep=';')
        
        # Contar frecuencia de cada tipo
        conteo = df['Tipo'].value_counts()
        
        print(f"{'CATEGORÍA ACTUAL':<30} | {'CANTIDAD'}")
        print("-" * 45)
        
        for categoria, cantidad in conteo.items():
            print(f"{categoria:<30} | {cantidad}")
            
        print("-" * 45)
        print(f"TOTAL REGISTROS: {len(df)}")
    else:
        print("❌ No se encontró la base de datos maestra.")

if __name__ == "__main__":
    auditar()