import pandas as pd
import matplotlib.pyplot as plt

# Configuración
FILE_CSV = 'historial_peso_final.csv'
FILE_IMG = 'evolucion_peso_10_anios.png'

def main():
    print("--- 📈 GENERANDO GRÁFICO DE EVOLUCIÓN ---")
    
    # 1. Leer datos y configurar fechas
    try:
        # Leemos el CSV (formato dd/mm/yyyy)
        df = pd.read_csv(FILE_CSV, sep=';')
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
        df = df.sort_values('Fecha')
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return

    print(f"Procesando {len(df)} registros para el gráfico...")

    # 2. Configurar el lienzo
    plt.figure(figsize=(12, 6)) # Ancho x Alto en pulgadas
    
    # A) Datos reales (puntos grises claros para ver el "ruido" diario)
    plt.plot(df['Fecha'], df['Peso'], color='gray', marker='.', linestyle='None', 
             markersize=3, label='Pesaje Diario', alpha=0.3)
    
    # B) Línea de Tendencia (Media Móvil de 30 días)
    # Esto ayuda a ver si la tendencia real sube o baja, ignorando picos aislados
    df['Tendencia'] = df['Peso'].rolling(window=30, center=True).mean()
    plt.plot(df['Fecha'], df['Tendencia'], color='#007acc', linewidth=2, 
             label='Tendencia (Media 30 días)')

    # 3. Decoración del gráfico
    plt.title(f'Evolución de Peso - Gonzalo Obispo ({df["Fecha"].dt.year.min()} - {df["Fecha"].dt.year.max()})', fontsize=14)
    plt.ylabel('Peso (kg)')
    plt.xlabel('Año')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    
    # Anotación del último peso registrado
    ultimo = df.iloc[-1]
    plt.annotate(f"Actual: {ultimo['Peso']} kg", 
                 xy=(ultimo['Fecha'], ultimo['Peso']),
                 xytext=(-60, 20), textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", color='red', lw=1.5),
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", alpha=0.8))

    # 4. Guardar imagen
    plt.savefig(FILE_IMG, dpi=100, bbox_inches='tight')
    print(f"✅ Gráfico guardado exitosamente: {FILE_IMG}")
    print("👉 Búscalo en tu carpeta BioEngine_Gonzalo y ábrelo.")

if __name__ == "__main__":
    main()