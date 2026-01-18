import os
import shutil

def limpieza_gerencial():
    base = r'C:\BioEngine_Gonzalo'
    
    # Definimos qué se queda en la raíz (Motor Principal)
    se_quedan = [
        'main.py', 'bio_engine.py', 'config.py', 
        'super_merger.py', 'report_generator.py', 'graficador.py'
    ]
    
    # Crear carpetas de destino si no existen
    legacy_dir = os.path.join(base, 'legacy')
    raw_dir = os.path.join(base, 'data_raw')
    if not os.path.exists(legacy_dir): os.makedirs(legacy_dir)
    if not os.path.exists(raw_dir): os.makedirs(raw_dir)

    for item in os.listdir(base):
        item_path = os.path.join(base, item)
        
        # Saltarse carpetas de sistema y archivos maestros
        if item in se_quedan or item in ['data_processed', 'reports', 'config', 'legacy', 'data_raw']:
            continue
            
        # Mover scripts viejos a legacy
        if item.endswith('.py'):
            shutil.move(item_path, os.path.join(legacy_dir, item))
            print(f"📦 Al archivo (legacy): {item}")
            
        # Mover restos de exportaciones a data_raw
        elif os.path.isdir(item_path) or item.endswith(('.txt', '.md', '.xml', '.zip')):
            try:
                shutil.move(item_path, os.path.join(raw_dir, item))
                print(f"📁 Al archivo (raw): {item}")
            except:
                print(f"⚠️ No se pudo mover {item} (posiblemente abierto)")

if __name__ == "__main__":
    limpieza_gerencial()