import os
import bio_engine
import report_generator
import super_merger
import graficador # <--- Nuevo
from datetime import datetime

def ver_estado():
    print("\n🔍 ESTADO DE SINCRONIZACIÓN:")
    archivos = {
        "Withings (Peso)": "historial_peso.csv",
        "Garmin (Actividades)": "historial_garmin_completo.csv",
        "Apple (Histórico)": "historial_apple_deportes.csv",
        "Runkeeper (Histórico)": "historial_runkeeper_puro.csv",
        "MAESTRO DEPORTIVO": "historial_deportivo_total.csv",
        "MAESTRO DE PESO": "historial_completo_peso.csv"
    }
    for nombre, ruta in archivos.items():
        if os.path.exists(ruta):
            mtime = os.path.getmtime(ruta)
            fecha = datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M')
            print(f"   ✅ {nombre.ljust(22)}: Última actualización {fecha}")
        else:
            print(f"   ❌ {nombre.ljust(22)}: No encontrado.")

def menu():
    while True:
        print("\n" + "="*40)
        print("      🧬 BIO-ENGINE: PANEL DE CONTROL")
        print("="*40)
        print("1. 🔄 Actualizar Todo (Cloud + Fusión)")
        print("2. 📊 Generar Reporte de Texto")
        print("3. 📈 Generar Dashboard Visual (Gráficos)")
        print("4. 📋 Ver Estado de Sincronización")
        print("5. 🚪 Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            print("\n📡 Conectando con servicios en la nube...")
            bio_engine.update_withings()
            bio_engine.update_garmin()
            print("\n🔗 Consolidando bases de datos locales...")
            super_merger.unificar_actividades()
            print("\n✅ PROCESO COMPLETADO EXITOSAMENTE.")
        elif opcion == "2":
            report_generator.generar_resumen()
        elif opcion == "3":
            graficador.generar_dashboard()
        elif opcion == "4":
            ver_estado()
        elif opcion == "5":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()