#!/usr/bin/env python3
# test_suite.py - Suite de Pruebas para Bio-Engine

import os
import sys
import pandas as pd
import config

def test_config():
    """Prueba configuración básica"""
    print("🧪 Probando configuración...")
    assert os.path.exists(config.DATA_PROCESSED), "DATA_PROCESSED no existe"
    assert config.GARMIN_EMAIL, "GARMIN_EMAIL no configurado"
    print("✅ Configuración OK")

def test_data_loading():
    """Prueba carga de datos"""
    print("🧪 Probando carga de datos...")
    try:
        df_p = pd.read_csv(config.CSV_PESO_MAESTRO, sep=';') if os.path.exists(config.CSV_PESO_MAESTRO) else pd.DataFrame()
        df_s = pd.read_csv(config.CSV_DEPORTE_MAESTRO, sep=';') if os.path.exists(config.CSV_DEPORTE_MAESTRO) else pd.DataFrame()
        print(f"✅ Datos cargados: {len(df_p)} peso, {len(df_s)} deporte")
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")

def test_imports():
    """Prueba imports de módulos principales"""
    print("🧪 Probando imports...")
    try:
        import bio_engine
        import super_merger
        import cloud_sync
        print("✅ Imports OK")
    except ImportError as e:
        print(f"❌ Import error: {e}")

def run_tests():
    """Ejecuta todas las pruebas"""
    print("🚀 INICIANDO SUITE DE PRUEBAS BIO-ENGINE\n")
    tests = [test_config, test_data_loading, test_imports]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test {test.__name__} falló: {e}")
        print()

    print("🏁 Suite de pruebas completada")

if __name__ == "__main__":
    run_tests()