import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.ticker import FixedLocator

def generar_dashboard():
    print("\n📊 GENERANDO DASHBOARD ESTRATÉGICO...")
    
    if not os.path.exists('historial_deportivo_total.csv') or not os.path.exists('historial_completo_peso.csv'):
        print("❌ Faltan archivos maestros.")
        return

    # Carga de datos
    df_p = pd.read_csv('historial_completo_peso.csv', sep=';')
    df_p['Fecha'] = pd.to_datetime(df_p['Fecha'], dayfirst=True)
    
    df_d = pd.read_csv('historial_deportivo_total.csv', sep=';')
    df_d['Fecha'] = pd.to_datetime(df_d['Fecha'], dayfirst=True)
    df_d['Mes'] = df_d['Fecha'].dt.month
    df_d['Año'] = df_d['Fecha'].dt.year

    # Configuración de estilo profesional
    sns.set_theme(style="whitegrid")
    fig, axs = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('BIO-ENGINE: DASHBOARD DE RENDIMIENTO Y SALUD', fontsize=20, fontweight='bold', y=0.98)

    # 1. FOCO EN EL PESO (Últimos 12 meses - Zoom Operativo)
    # Para ver la tendencia real de este último año de Trail
    df_p_1y = df_p[df_p['Fecha'] > (df_p['Fecha'].max() - pd.Timedelta(days=365))].sort_values('Fecha')
    axs[0, 0].plot(df_p_1y['Fecha'], df_p_1y['Peso'], color='#e74c3c', marker='.', linestyle='-', alpha=0.6)
    axs[0, 0].axhline(76, color='green', linestyle='--', label='Objetivo (76kg)')
    axs[0, 0].set_title('TENDENCIA DE PESO (Último Año)', fontweight='bold')
    axs[0, 0].legend()

    # 2. INTENSIDAD: FC MEDIA POR DEPORTE
    # Vital para cuidar tu rodilla: ¿Cuál es el deporte con mayor carga cardiovascular?
    df_fc = df_d[df_d['FC Media'] > 0]
    sns.barplot(x='Tipo', y='FC Media', data=df_fc, ax=axs[0, 1], palette='viridis', hue='Tipo', legend=False)
    axs[0, 1].set_title('CARGA CARDIOVASCULAR POR DEPORTE (FC Media)', fontweight='bold')

    # 3. VOLUMEN MENSUAL (Últimos 2 años)
    # Comparativa de tu constancia en Running/Trail
    df_d_2y = df_d[df_d['Fecha'] > (df_d['Fecha'].max() - pd.Timedelta(days=730))]
    resumen_mes = df_d_2y.groupby(['Mes']).agg({'Distancia (km)': 'sum'}).reset_index()
    sns.barplot(x='Mes', y='Distancia (km)', data=resumen_mes, ax=axs[1, 0], color='#3498db')
    axs[1, 0].set_title('KILOMETRAJE MENSUAL (Consolidado 24m)', fontweight='bold')
    axs[1, 0].xaxis.set_major_locator(FixedLocator(range(12)))
    axs[1, 0].set_xticklabels(['E','F','M','A','M','J','J','A','S','O','N','D'])

    # 4. COMPOSICIÓN DEL ENTRENAMIENTO (Horas invertidas)
    # ¿A qué le dedicas más tiempo realmente?
    horas_tipo = df_d.groupby('Tipo')['Duracion (min)'].sum() / 60
    axs[1, 1].pie(horas_tipo, labels=horas_tipo.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'), startangle=90)
    axs[1, 1].set_title('DISTRIBUCIÓN DE TIEMPO TOTAL', fontweight='bold')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('dashboard_bioengine.png', dpi=300)
    print("✅ Dashboard operativo actualizado: 'dashboard_bioengine.png'")

if __name__ == "__main__":
    generar_dashboard()