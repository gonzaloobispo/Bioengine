
import zipfile
import re

def get_docx_xml(path):
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml').decode('utf-8')
    document.close()
    return xml_content

try:
    path = r'c:\BioEngine_Gonzalo\data_raw\dieta 1ª etapa original.doc'
    print(f"--- Processing: {path} ---")
    # Note: .doc is harder than .docx, but often contains raw text if it's an old format
    with open(path, 'rb') as f:
        content = f.read().decode('latin-1', errors='ignore')
    
    # Simple search for years or surgery keywords
    print("Muestra de texto:")
    print(content[:2000])
    
    import re
    years = re.findall(r'20\d{2}', content)
    print("\nAños encontrados:", set(years))
    
except Exception as e:
    print(f"Error: {e}")
