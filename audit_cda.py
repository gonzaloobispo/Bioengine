# audit_cda.py - Inspector de Contenido CDA (Apple Health)
import xml.etree.ElementTree as ET
import os
import config

# Función auxiliar para limpiar los nombres de las etiquetas (quitar {namespaces})
def clean_tag(tag):
    if '}' in tag:
        return tag.split('}')[1]
    return tag

def auditar_cda():
    print("🔬 INICIANDO AUDITORÍA FORENSE DE CDA...")
    
    # 1. Buscar el archivo
    rutas = [
        os.path.join(config.DATA_RAW, 'apple_health_export', 'export_cda.xml'),
        os.path.join(config.DATA_RAW, 'apple_health_export', 'export_cda.xml'),
        os.path.join(config.DATA_RAW, 'export_cda.xml')
    ]
    
    archivo_encontrado = None
    for ruta in rutas:
        if os.path.exists(ruta):
            archivo_encontrado = ruta
            break
            
    if not archivo_encontrado:
        print("❌ No se encontró el archivo 'export_cda.xml' en las carpetas esperadas.")
        return

    print(f"📂 Archivo encontrado: {archivo_encontrado}")
    
    try:
        # 2. Parsear XML
        tree = ET.parse(archivo_encontrado)
        root = tree.getroot()
        
        print(f"   -> Raíz del XML: <{clean_tag(root.tag)}>")
        
        # 3. Buscar Títulos de Secciones (Lo más importante)
        # El estándar CDA organiza la data en Secciones con Títulos.
        titulos = []
        for elem in root.iter():
            tag_limpio = clean_tag(elem.tag)
            if tag_limpio == 'title':
                if elem.text:
                    titulos.append(elem.text.strip())
        
        print("\n📋 TABLA DE CONTENIDOS DETECTADA:")
        if titulos:
            for i, t in enumerate(titulos, 1):
                print(f"   {i}. {t}")
        else:
            print("   (No se encontraron títulos de secciones legibles)")

        # 4. Buscar Texto Libre (Párrafos)
        print("\n📝 MUESTRA DE TEXTO (Primeros 5 hallazgos):")
        textos = []
        for elem in root.iter():
            if clean_tag(elem.tag) == 'text':
                if elem.text and len(elem.text.strip()) > 2:
                    textos.append(elem.text.strip())
        
        for t in textos[:5]:
            print(f"   - {t}")

        # 5. Buscar Datos Numéricos (Indicios de biomecánica)
        print("\n🔢 BÚSQUEDA DE VALORES NUMÉRICOS:")
        conteo_valores = 0
        for elem in root.iter():
            if 'value' in elem.attrib:
                conteo_valores += 1
        
        print(f"   -> Se detectaron {conteo_valores} atributos 'value' en el archivo.")
        
        if conteo_valores < 50:
            print("   ⚠️ CONCLUSIÓN: El volumen de datos es muy bajo. Probablemente sea solo un resumen clínico.")
        else:
            print("   ✅ CONCLUSIÓN: Hay muchos datos. Vale la pena investigar más.")

    except Exception as e:
        print(f"❌ Error leyendo el archivo: {e}")

if __name__ == "__main__":
    auditar_cda()