# audit_files.py - Radar de Archivos Crudos
import os
import config

def escanear_boveda():
    print("📂 ESCANEANDO CARPETA 'DATA_RAW'...")
    print("-" * 50)
    
    ruta_base = config.DATA_RAW
    archivos_encontrados = 0
    
    for root, dirs, files in os.walk(ruta_base):
        for name in files:
            # Ignorar archivos ocultos o de sistema
            if name.startswith('.'): continue
            
            ruta_completa = os.path.join(root, name)
            tamaño = os.path.getsize(ruta_completa) / 1024 # KB
            
            # Mostrar solo CSV, XML, JSON o TXT
            if name.lower().endswith(('.csv', '.xml', '.json', '.txt', '.xls', '.xlsx')):
                archivos_encontrados += 1
                print(f"📄 {name:<40} | {tamaño:>6.1f} KB | Ruta: {root}")

    print("-" * 50)
    if archivos_encontrados == 0:
        print("❌ La carpeta parece vacía o no tiene archivos de datos reconocibles.")
    else:
        print(f"✅ Se encontraron {archivos_encontrados} archivos potenciales.")

if __name__ == "__main__":
    escanear_boveda()