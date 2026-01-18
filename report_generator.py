import pandas as pd
import os
from datetime import datetime

def generar_resumen():
    print("\n" + "="*50)
    print("📊 REPORTE DE RENDIMIENTO BIO-ENGINE (HISTÓRICO TOTAL)")
    print("="*50)
    
    # 1. ANÁLISIS DE PESO (Maestro de 10 años)
    if os.path.exists('historial_completo_peso.csv'):
        df_p = pd.read_csv('historial_completo_peso.csv', sep=';')
        df_p['Fecha'] = pd.to_datetime(df_p['Fecha'], format='%d/%m/%Y')
        ultimo_peso = df_p.iloc[0]['Peso']
        media_semana = df_p.head(7)['Peso'].mean()
        print(f"⚖️  PESO ACTUAL: {ultimo_peso} kg (Media 7 días: {round(media_semana, 2)} kg)")
    
    # 2. ANÁLISIS DEPORTIVO UNIFICADO (Garmin + Apple + Runkeeper)
    if os.path.exists('historial_deportivo_total.csv'):
        df_d = pd.read_csv('historial_deportivo_total.csv', sep=';')
        
        # Totales Históricos
        km_totales = df_d['Distancia (km)'].sum()
        horas_totales = df_d['Duracion (min)'].sum() / 60
        cal_totales = df_d['Calorias'].sum()
        
        print(f"\n🌍 RESUMEN ATLÉTICO DE POR VIDA:")
        print(f"   🏃 Distancia Total: {round(km_totales, 1)} km")
        print(f"   ⏱️  Tiempo Invertido: {int(horas_totales)} horas")
        print(f"   🔥 Energía Quemada: {int(cal_totales):,} kcal")
        
        # Desglose por disciplina (Top 3)
        print("\n🏆 DISCIPLINAS PRINCIPALES:")
        resumen_tipo = df_d.groupby('Tipo')['Distancia (km)'].sum().sort_values(ascending=False).head(3)
        for tipo, km in resumen_tipo.items():
            print(f"   🔹 {tipo.capitalize().ljust(12)}: {round(km, 1)} km")

    print("\n" + "="*50)

if __name__ == "__main__":
    generar_resumen()