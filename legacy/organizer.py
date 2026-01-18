import os
import shutil
import config

def organizar_profesional():
    print("📂 Organizando Bio-Engine por departamentos...")
    
    # 1. Crear carpetas si no existen
    carpetas = [config.DATA_RAW, config.DATA_PROCESSED, config.REPORTS_DIR, config.CONFIG_DIR]
    for c in carpetas:
        if not os.path.exists(c):
            os.makedirs(c)

    # 2. Mapeo de archivos específicos
    mapeo = {
        '.csv': config.DATA_PROCESSED,
        '.png': config.REPORTS_DIR,
        '.pdf': config.REPORTS_DIR,
        '.json': config.CONFIG_DIR,
        '.xml': config.DATA_RAW,
        '.zip': config.DATA_RAW
    }

    # 3. Mover archivos de la raíz a sus carpetas
    for item in os.listdir(config.BASE_DIR):
        item_path = os.path.join(config.BASE_DIR, item)
        
        # No mover carpetas ni el propio script main.py (dejar scripts en la raíz)
        if os.path.isdir(item_path) or item.endswith('.py'):
            continue
            
        ext = os.path.splitext(item)[1].lower()
        if ext in mapeo:
            dest = os.path.join(mapeo[ext], item)
            # Evitar error si el archivo ya está en el destino
            if item_path != dest:
                shutil.move(item_path, dest)
                print(f"✔️  Moviendo {item} -> {os.path.basename(mapeo[ext])}")

if __name__ == "__main__":
    organizar_profesional()