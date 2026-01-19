"""
Pattern Detector - Sistema de Detección Automática de Patrones
Analiza datos históricos para encontrar correlaciones y tendencias
"""

import pandas as pd
import json
from datetime import datetime, timedelta
import os
import config


class PatternDetector:
    """
    Detecta patrones automáticos en datos del usuario
    """
    
    def __init__(self, context_manager):
        self.ctx = context_manager
        self.min_observations = 10  # Mínimo de datos para calcular correlación
        self.confidence_threshold = 75  # Umbral mínimo de confianza
    
    def analyze_all_patterns(self):
        """
        Ejecuta todos los detectores de patrones
        Retorna lista de patrones encontrados
        """
        patterns = []
        
        # Detector 1: Correlación actividad-dolor
        try:
            activity_pain = self.detect_activity_pain_correlation()
            if activity_pain:
                patterns.extend(activity_pain)
        except Exception as e:
            print(f"[WARNING] Error en detector actividad-dolor: {e}")
        
        # Detector 2: Adherencia por tipo
        try:
            adherence = self.detect_adherence_patterns()
            if adherence:
                patterns.extend(adherence)
        except Exception as e:
            print(f"[WARNING] Error en detector adherencia: {e}")
        
        return patterns
    
    def detect_activity_pain_correlation(self):
        """
        Detecta correlaciones entre tipos de actividad y nivel de dolor
        Retorna patrones con confianza > threshold
        """
        patterns = []
        
        # 1. Cargar datos de actividades (últimos 60 días para tener más muestra)
        fecha_limite = datetime.now() - timedelta(days=60)
        
        if not os.path.exists(config.CSV_DEPORTE_MAESTRO):
            return patterns
        
        df_sport = pd.read_csv(config.CSV_DEPORTE_MAESTRO, sep=';')
        df_sport['Fecha'] = pd.to_datetime(df_sport['Fecha'], errors='coerce')
        df_sport = df_sport[df_sport['Fecha'] >= fecha_limite]
        
        if df_sport.empty or 'Tipo' not in df_sport.columns:
            return patterns
        
        # 2. Cargar datos de dolor
        dolor_file = os.path.join(config.BASE_DIR, 'data_cloud_sync', 'dolor_rodilla.json')
        if not os.path.exists(dolor_file):
            return patterns
        
        with open(dolor_file, 'r', encoding='utf-8') as f:
            dolor_data = json.load(f)
        
        # Crear diccionario fecha -> intensidad de dolor
        dolor_por_fecha = {}
        for registro in dolor_data.get('registros', []):
            fecha = registro['fecha']
            intensidad = registro.get('intensidad', 0)
            # Si hay múltiples registros en el día, tomar el promedio
            if fecha in dolor_por_fecha:
                dolor_por_fecha[fecha].append(intensidad)
            else:
                dolor_por_fecha[fecha] = [intensidad]
        
        # Calcular promedio por fecha
        dolor_promedio = {
            fecha: sum(valores) / len(valores) 
            for fecha, valores in dolor_por_fecha.items()
        }
        
        # 3. Analizar cada tipo de actividad
        tipos_actividad = df_sport['Tipo'].value_counts()
        
        for tipo in tipos_actividad.index:
            if tipos_actividad[tipo] < self.min_observations:
                continue  # No hay suficientes datos
            
            # Actividades de este tipo
            df_tipo = df_sport[df_sport['Tipo'] == tipo].copy()
            
            # Cruzar con dolor
            dolores = []
            for _, row in df_tipo.iterrows():
                fecha_str = row['Fecha'].strftime('%Y-%m-%d')
                if fecha_str in dolor_promedio:
                    dolores.append(dolor_promedio[fecha_str])
            
            if len(dolores) < 5:  # Necesitamos al menos 5 cruces
                continue
            
            # Calcular estadísticas
            dolor_avg = sum(dolores) / len(dolores)
            dolor_bajo_count = sum(1 for d in dolores if d <= 2)
            dolor_bajo_pct = (dolor_bajo_count / len(dolores)) * 100
            
            # Si la correlación es fuerte (>75% de veces con dolor bajo)
            if dolor_bajo_pct >= self.confidence_threshold:
                pattern = {
                    'tipo': 'actividad_dolor',
                    'description': f"{tipo} → Dolor bajo ({dolor_bajo_pct:.0f}% de las veces)",
                    'recommendation': f"Priorizar {tipo} cuando hay dolor alto",
                    'confidence': int(dolor_bajo_pct),
                    'datos': {
                        'actividad': tipo,
                        'sesiones_analizadas': len(dolores),
                        'dolor_promedio': round(dolor_avg, 1),
                        'dolor_bajo_pct': round(dolor_bajo_pct, 1)
                    }
                }
                patterns.append(pattern)
        
        return patterns
    
    def detect_adherence_patterns(self):
        """
        Detecta qué tipos de actividad se completan con mayor frecuencia
        """
        patterns = []
        
        # Cargar plan de entrenamiento
        plan_file = os.path.join(config.BASE_DIR, 'config', 'plan_entrenamiento.json')
        if not os.path.exists(plan_file):
            return patterns
        
        with open(plan_file, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        # Contar actividades planificadas por tipo
        actividades_planificadas = {}
        for dia in plan.get('semana', []):
            actividad = dia.get('actividad', '')
            if actividad and actividad != 'Descanso Total':
                actividades_planificadas[actividad] = actividades_planificadas.get(actividad, 0) + 1
        
        # Cargar actividades reales (últimos 30 días)
        if not os.path.exists(config.CSV_DEPORTE_MAESTRO):
            return patterns
        
        fecha_limite = datetime.now() - timedelta(days=30)
        df_sport = pd.read_csv(config.CSV_DEPORTE_MAESTRO, sep=';')
        df_sport['Fecha'] = pd.to_datetime(df_sport['Fecha'], errors='coerce')
        df_reciente = df_sport[df_sport['Fecha'] >= fecha_limite]
        
        if df_reciente.empty or 'Tipo' not in df_reciente.columns:
            return patterns
        
        # Contar actividades reales por tipo
        actividades_reales = df_reciente['Tipo'].value_counts().to_dict()
        
        # Calcular adherencia por tipo
        for actividad, planificado in actividades_planificadas.items():
            # Aproximar cuántas veces debió hacerse en 30 días (4 semanas)
            esperado = int(planificado * 4)
            realizado = actividades_reales.get(actividad, 0)
            
            if esperado > 0:
                adherencia_pct = min(100, (realizado / esperado) * 100)
                
                # Si adherencia es muy alta (>80%)
                if adherencia_pct >= 80:
                    pattern = {
                        'tipo': 'adherencia',
                        'description': f"Alta adherencia a {actividad} ({adherencia_pct:.0f}%)",
                        'recommendation': f"Mantener {actividad} en el plan - buena adherencia",
                        'confidence': int(adherencia_pct),
                        'datos': {
                            'actividad': actividad,
                            'esperado': esperado,
                            'realizado': realizado,
                            'adherencia_pct': round(adherencia_pct, 1)
                        }
                    }
                    patterns.append(pattern)
                
                # Si adherencia es muy baja (<40%)
                elif adherencia_pct < 40 and esperado >= 4:  # Al menos 4 sesiones esperadas
                    pattern = {
                        'tipo': 'adherencia',
                        'description': f"Baja adherencia a {actividad} ({adherencia_pct:.0f}%)",
                        'recommendation': f"Considerar reemplazar {actividad} por otra actividad",
                        'confidence': int(100 - adherencia_pct),  # Confianza inversa
                        'datos': {
                            'actividad': actividad,
                            'esperado': esperado,
                            'realizado': realizado,
                            'adherencia_pct': round(adherencia_pct, 1)
                        }
                    }
                    patterns.append(pattern)
        
        return patterns


if __name__ == "__main__":
    # Test básico
    from context_manager import ContextManager
    
    ctx = ContextManager()
    detector = PatternDetector(ctx)
    
    print("Analizando patrones...")
    patterns = detector.analyze_all_patterns()
    
    print(f"\nPatrones encontrados: {len(patterns)}")
    for p in patterns:
        print(f"\n- {p['description']}")
        print(f"  Confianza: {p['confidence']}%")
        print(f"  Recomendacion: {p['recommendation']}")
