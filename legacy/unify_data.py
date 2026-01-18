import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import pandas as pd

# --- CONFIGURACIÓN ---
FILE_XML = 'Gonzalo+Obispo.xml'
FILE_CSV = 'historial_peso.csv'
FILE_OUTPUT = 'historial_peso_final.csv'

def main():
    print("--- 🧹 INICIANDO LIMPIEZA Y FUSIÓN DE DATOS ---")
    data_list = []

    # 1. LEER XML (Pesobook)
    if os.path.exists(FILE_XML):
        try:
            tree = ET.parse(FILE_XML)
            root = tree.getroot()
            count_xml = 0
            # Usamos iter() para ignorar namespaces complejos
            for node in root.iter():
                if node.tag.endswith('Peso'):
                    fecha = None
                    valor = None
                    for child in node:
                        if child.tag.endswith('PesoFecha'): fecha = child.text
                        if child.tag.endswith('PesoValor'): valor = child.text
                    
                    if fecha and valor:
                        # Convertimos string YYYY-MM-DD a objeto fecha (sin hora)
                        dt = datetime.strptime(fecha, '%Y-%m-%d').date()
                        data_list.append({
                            'Fecha': dt,
                            'Peso': float(valor)
                        })
                        count_xml += 1
            print(f"📖 XML procesado: {count_xml} registros.")
        except Exception as e:
            print(f"❌ Error leyendo XML: {e}")

    # 2. LEER CSV (Withings)
    if os.path.exists(FILE_CSV):
        try:
            # Leemos con pandas para facilitar manejo de fechas variadas
            df_csv = pd.read_csv(FILE_CSV, sep=';')
            count_csv = 0
            for _, row in df_csv.iterrows():
                # Asumimos formato dd/mm/yyyy del CSV de Withings
                fecha_str = row['Fecha']
                # Extraemos solo la fecha, ignorando la hora
                dt = datetime.strptime(fecha_str, '%d/%m/%Y').date()
                peso = float(row['Peso (kg)']) # Asegúrate que el nombre de columna coincida
                
                data_list.append({
                    'Fecha': dt,
                    'Peso': peso
                })
                count_csv += 1
            print(f"☁️ CSV procesado: {count_csv} registros.")
        except Exception as e:
            print(f"❌ Error leyendo CSV: {e}")

    # 3. UNIFICAR Y LIMPIAR
    # Convertimos a DataFrame para filtrar fácil
    df_total = pd.DataFrame(data_list)
    
    # Ordenamos por fecha descendente (lo más nuevo arriba)
    df_total = df_total.sort_values(by='Fecha', ascending=False)
    
    total_original = len(df_total)
    
    # ELIMINAR DUPLICADOS EXACTOS (Misma Fecha + Mismo Peso)
    df_clean = df_total.drop_duplicates(subset=['Fecha', 'Peso'])
    
    duplicados_borrados = total_original - len(df_clean)

    # 4. GUARDAR
    # Formateamos la fecha a dd/mm/yyyy para el Excel final
    df_clean['Fecha'] = pd.to_datetime(df_clean['Fecha']).dt.strftime('%d/%m/%Y')
    
    df_clean.to_csv(FILE_OUTPUT, index=False, sep=';')
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   - Registros Totales leídos: {total_original}")
    print(f"   - Duplicados eliminados: {duplicados_borrados}")
    print(f"   - Registros Únicos finales: {len(df_clean)}")
    print(f"✅ Archivo generado: {FILE_OUTPUT}")

if __name__ == "__main__":
    main()