# audit_cda_deep.py - Clasificador de Activos CDA (Deep Scan)
import xml.etree.ElementTree as ET
import os
import config
from collections import Counter

# Función para limpiar namespaces molestos de XML
def clean_tag(tag):
    if '}' in tag: return tag.split('}')[1]
    return tag

def escanear_tipos_cda():
    print("🔬 INICIANDO ESCANEO PROFUNDO DE CDA (1.6 Millones de registros)...")
    print("   (Esto tomará unos segundos, procesando en streaming...)")
    
    archivo = os.path.join(config.DATA_RAW, 'apple_health_export', 'export_cda.xml')
    if not os.path.exists(archivo):
        # Intento alternativo
        archivo = os.path.join(config.DATA_RAW, 'export_cda.xml')
    
    if not os.path.exists(archivo):
        print("❌ No encuentro el archivo.")
        return

    # Contadores
    tipos_encontrados = Counter()
    
    try:
        # Usamos iterparse para no saturar la memoria RAM
        context = ET.iterparse(archivo, events=('start', 'end'))
        context = iter(context)
        event, root = next(context) # Obtener la raíz
        
        # Variables temporales para rastrear el contexto
        ultimo_code_display = "Desconocido"
        
        for event, elem in context:
            tag = clean_tag(elem.tag)
            
            if event == 'start':
                # Si encontramos una etiqueta 'code', guardamos qué es
                # (Ej: code="8867-4" displayName="Heart rate")
                if tag == 'code':
                    if 'displayName' in elem.attrib:
                        ultimo_code_display = elem.attrib['displayName']
            
            elif event == 'end':
                # Cuando cierra un elemento con 'value', contamos qué tipo era
                if 'value' in elem.attrib:
                    tipos_encontrados[ultimo_code_display] += 1
                
                # Limpiar memoria (Crítico para archivos grandes)
                if tag in ['entry', 'component', 'observation']:
                    elem.clear()
                    
    except Exception as e:
        print(f"⚠️ El proceso se interrumpió: {e}")

    print("\n📊 RESUMEN EJECUTIVO DE DATOS CDA:")
    print(f"{'TIPO DE DATO (DisplayName)':<40} | {'CANTIDAD REGISTROS'}")
    print("-" * 60)
    
    total = 0
    for tipo, cantidad in tipos_encontrados.most_common():
        print(f"{tipo:<40} | {cantidad:,.0f}")
        total += cantidad
        
    print("-" * 60)
    print(f"{'TOTAL':<40} | {total:,.0f}")

if __name__ == "__main__":
    escanear_tipos_cda()