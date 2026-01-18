# cda_importer.py - Con Smart Caching
import os
import pandas as pd
import xml.etree.ElementTree as ET
import config

CACHE_CDA = os.path.join(config.DATA_PROCESSED, 'cache_cda_weight.pkl')

def es_cache_valido(carpeta_origen, archivo_cache):
    if not os.path.exists(archivo_cache): return False
    t_cache = os.path.getmtime(archivo_cache)
    
    # Si la carpeta fue modificada DESPUÉS del caché, invalidamos
    t_carpeta = os.path.getmtime(carpeta_origen)
    return t_cache > t_carpeta

def procesar_cda_peso():
    ruta_base = os.path.join(config.DATA_RAW, 'apple_health_export')
    if not os.path.exists(ruta_base): return pd.DataFrame()
    
    # Verificación de Caché
    if es_cache_valido(ruta_base, CACHE_CDA):
        # Opcional: imprimir solo si debug
        # print("   ⚡ (Apple CDA) Usando caché.") 
        return pd.read_pickle(CACHE_CDA)

    print("🏥 Iniciando extracción CDA (Escaneando XMLs)...")
    registros = []
    
    for root_dir, dirs, files in os.walk(ruta_base):
        for file in files:
            if file.endswith('.xml') and 'export' not in file:
                ruta_completa = os.path.join(root_dir, file)
                try:
                    tree = ET.parse(ruta_completa)
                    root = tree.getroot()
                    ns = {'v3': 'urn:hl7-org:v3'}
                    
                    # Buscar observaciones de peso
                    for obs in root.findall('.//v3:observation', ns):
                        code = obs.find('v3:code', ns)
                        if code is not None and code.get('code') == '3141-9': # Código LOINC Peso
                            val_node = obs.find('v3:value', ns)
                            eff_time = obs.find('v3:effectiveTime', ns)
                            
                            if val_node is not None and eff_time is not None:
                                peso = float(val_node.get('value'))
                                fecha_raw = eff_time.get('value')
                                
                                # Convertir fecha formato '20230101120000'
                                fecha = pd.to_datetime(fecha_raw, format='%Y%m%d%H%M%S', errors='coerce')
                                
                                registros.append({
                                    'Fecha': fecha,
                                    'Peso': peso,
                                    'Fuente': 'Apple CDA (Medical Doc)'
                                })
                except:
                    continue

    df = pd.DataFrame(registros)
    if not df.empty:
        df = df.drop_duplicates()
        df.to_pickle(CACHE_CDA) # Guardamos para la próxima
        print(f"   ✅ CDA procesado y cacheado: {len(df)} registros.")
    
    return df