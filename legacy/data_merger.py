import xml.etree.ElementTree as ET
from datetime import datetime
import os
import pandas as pd
import config

# Archivo de salida final (La "Verdad Única")
FILE_MASTER_OUTPUT = 'historial_completo_peso.csv'

def unificar_datos():
    print("\n🔄 [MERGER] Iniciando fusión de datos (Legado + Withings)...")
    data_list = []

    # 1. LEER XML LEGADO (Pesobook) - DATOS ESTÁTICOS
    # Asumimos que este archivo nunca cambia, es tu base histórica.
    file_xml = 'Gonzalo+Obispo.xml'
    if os.path.exists(file_xml):
        try:
            tree = ET.parse(file_xml)
            root = tree.getroot()
            count_xml = 0
            for node in root.iter():
                if node.tag.endswith('Peso'):
                    fecha = None
                    valor = None
                    for child in node:
                        if child.tag.endswith('PesoFecha'): fecha = child.text
                        if child.tag.endswith('PesoValor'): valor = child.text
                    
                    if fecha and valor:
                        dt = datetime.strptime(fecha, '%Y-%m-%d').date()
                        data_list.append({'Fecha': dt, 'Peso': float(valor), 'Fuente': 'Pesobook'})
                        count_xml += 1
            print(f"   -> XML Legado cargado: {count_xml} registros.")
        except Exception as e:
            print(f"   ❌ Error leyendo XML: {e}")
    else:
        print("   ⚠️ Advertencia: No se encontró el XML de respaldo.")

    # 2. LEER CSV ACTUALIZADO (Withings) - DATOS DINÁMICOS
    # Este es el archivo que 'bio_engine.py' acaba de descargar fresco.
    file_csv = config.CSV_PESO
    if os.path.exists(file_csv):
        try:
            df_csv = pd.read_csv(file_csv, sep=';')
            count_csv = 0
            for _, row in df_csv.iterrows():
                # El CSV de Withings viene como dd/mm/yyyy
                fecha_str = row['Fecha']
                dt = datetime.strptime(fecha_str, '%d/%m/%Y').date()
                peso = float(row['Peso (kg)'])
                
                data_list.append({'Fecha': dt, 'Peso': peso, 'Fuente': 'Withings'})
                count_csv += 1
            print(f"   -> Withings (Reciente) cargado: {count_csv} registros.")
        except Exception as e:
            print(f"   ❌ Error leyendo CSV Withings: {e}")

    # 3. UNIFICAR Y LIMPIAR
    if not data_list:
        print("   ❌ No hay datos para procesar.")
        return

    df_total = pd.DataFrame(data_list)
    
    # Ordenar: Lo más nuevo arriba
    df_total = df_total.sort_values(by='Fecha', ascending=False)
    
    # Eliminar duplicados exactos (Fecha y Peso idénticos)
    # Si hay conflicto, preferimos mantener el dato de 'Withings' si es reciente
    df_clean = df_total.drop_duplicates(subset=['Fecha', 'Peso'])
    
    # 4. GUARDAR MAESTRO
    # Formato final limpio: Fecha;Peso (sin hora, sin fuente, simple para Excel)
    df_clean['Fecha'] = pd.to_datetime(df_clean['Fecha']).dt.strftime('%d/%m/%Y')
    
    # Seleccionamos solo las columnas que importan
    df_final = df_clean[['Fecha', 'Peso']]
    
    df_final.to_csv(FILE_MASTER_OUTPUT, index=False, sep=';')
    
    print(f"   ✅ FUSIÓN COMPLETADA. Archivo Maestro: {FILE_MASTER_OUTPUT}")
    print(f"   📊 Total Registros Históricos: {len(df_final)}")

if __name__ == "__main__":
    unificar_datos()