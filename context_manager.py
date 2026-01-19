import json
import os
from datetime import datetime
import config

class ContextManager:
    """
    Gestiona el contexto persistente del usuario para personalización del chatbot
    """
    
    def __init__(self):
        self.context_file = config.USER_CONTEXT_FILE
        self.context = self._load_context()
    
    def _load_context(self):
        """Carga el contexto desde el archivo JSON"""
        try:
            if os.path.exists(self.context_file):
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._create_default_context()
        except Exception as e:
            print(f"Error loading context: {e}")
            return self._create_default_context()
    
    def _create_default_context(self):
        """Crea contexto por defecto si no existe"""
        return {
            "metadata": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "context_window_summary": "Nuevo usuario"
            },
            "perfil_usuario": {},
            "estadisticas_ultimos_30d": {},
            "insights_aprendidos": [],
            "conversaciones_relevantes": []
        }
    
    def _save_context(self):
        """Guarda el contexto en el archivo JSON"""
        try:
            self.context['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self.context_file), exist_ok=True)
            
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(self.context, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving context: {e}")
            return False
    
    def get_context_summary(self):
        """Devuelve resumen optimizado para incluir en prompts del LLM"""
        summary = {
            "perfil": self.context.get('perfil_usuario', {}),
            "medico": self.context.get('historial_medico_resumido', {}),
            "stats_recientes": self.context.get('estadisticas_ultimos_30d', {}),
            "insights": self.context.get('insights_aprendidos', [])[:5],  # Top 5 insights
            "conversaciones": self.context.get('conversaciones_relevantes', [])[-3:]  # Últimas 3
        }
        return summary
    
    def update_stats_from_activity(self, new_activity):
        """
        Actualiza estadísticas cuando hay nueva actividad
        """
        stats = self.context.setdefault('estadisticas_ultimos_30d', {
            'km_totales': 0,
            'actividades_completadas': 0,
            'peso_promedio_kg': 0,
            'adherencia_plan': 0,
            'dolor_rodilla_dias': 0
        })
        
        # Actualizar km totales
        if 'Distancia (km)' in new_activity or 'distancia_km' in new_activity:
            km = new_activity.get('Distancia (km)', new_activity.get('distancia_km', 0))
            stats['km_totales'] += km
        
        # Incrementar contador
        stats['actividades_completadas'] += 1
        
        self._save_context()
        return True
    
    def add_insight(self, pattern, action, confidence):
        """
        Agrega nuevo insight aprendido por el sistema
        """
        new_insight = {
            "fecha_deteccion": datetime.now().strftime('%Y-%m-%d'),
            "patron": pattern,
            "accion": action,
            "confianza": confidence
        }
        
        insights = self.context.setdefault('insights_aprendidos', [])
        insights.append(new_insight)
        
        # Mantener solo los últimos 10 insights más importantes
        self.context['insights_aprendidos'] = sorted(
            insights,
            key=lambda x: x.get('confianza', 0),
            reverse=True
        )[:10]
        
        self._save_context()
        return True
    
    def update_insights_from_patterns(self, detected_patterns):
        """
        Actualiza insights desde patrones detectados automáticamente
        Solo guarda patrones con confianza > 75%
        """
        if not detected_patterns:
            return False
        
        saved_count = 0
        for pattern in detected_patterns:
            confidence = pattern.get('confidence', 0)
            
            # Solo guardar si confianza es suficiente
            if confidence >= 75:
                # Verificar que no exista ya (evitar duplicados)
                existing = self.context.get('insights_aprendidos', [])
                pattern_desc = pattern.get('description', '')
                
                # Buscar si ya existe este patrón
                already_exists = any(
                    insight.get('patron', '') == pattern_desc 
                    for insight in existing
                )
                
                if not already_exists:
                    self.add_insight(
                        pattern=pattern.get('description', ''),
                        action=pattern.get('recommendation', ''),
                        confidence=confidence
                    )
                    saved_count += 1
        
        if saved_count > 0:
            print(f"[OK] {saved_count} nuevos insights guardados")
        
        return saved_count > 0
    
    def log_conversation_learning(self, summary, learning, context_note=""):
        """
        Registra aprendizajes de conversaciones
        """
        conv_log = {
            "fecha": datetime.now().strftime('%Y-%m-%d'),
            "aprendizaje": learning,
            "contexto": context_note or summary
        }
        
        conversations = self.context.setdefault('conversaciones_relevantes', [])
        conversations.append(conv_log)
        
        # Mantener últimas 20 conversaciones
        self.context['conversaciones_relevantes'] = conversations[-20:]
        
        self._save_context()
        return True
    
    def update_pain_level(self, level, note=""):
        """
        Actualiza el nivel de dolor actual en el contexto
        """
        if 'historial_medico_resumido' in self.context:
            if 'lesiones_activas' in self.context['historial_medico_resumido']:
                for lesion in self.context['historial_medico_resumido']['lesiones_activas']:
                    if 'rodilla' in lesion.get('nombre', '').lower():
                        lesion['nivel_dolor_actual'] = level
                        if note:
                            lesion['nota_reciente'] = note
                        break
        
        self._save_context()
        return True
    
    def get_formatted_context_for_llm(self):
        """
        Formatea el contexto para incluir en el system prompt del LLM
        """
        ctx = self.context
        
        formatted = f"""
## CONOCIMIENTO PROFUNDO DEL USUARIO

### Perfil
- Nombre: {ctx['perfil_usuario'].get('nombre', 'Usuario')}
- Edad: {ctx['perfil_usuario'].get('edad', 'N/A')} años
- Nivel deportivo: {ctx['perfil_usuario'].get('experiencia_deportiva', {}).get('nivel_actual', 'N/A')}

### Condición Médica
"""
        
        if 'historial_medico_resumido' in ctx:
            for lesion in ctx['historial_medico_resumido'].get('lesiones_activas', []):
                formatted += f"""
- Lesión: {lesion.get('nombre', 'N/A')}
- Dolor actual: {lesion.get('nivel_dolor_actual', 'N/A')}/10
- Restricciones: {', '.join(lesion.get('restricciones', []))}
"""
        
        formatted += f"""
### Rendimiento Reciente (30 días)
- Actividades completadas: {ctx.get('estadisticas_ultimos_30d', {}).get('actividades_completadas', 0)}
- Kilómetros totales: {ctx.get('estadisticas_ultimos_30d', {}).get('km_totales', 0)} km
- Adherencia al plan: {ctx.get('estadisticas_ultimos_30d', {}).get('adherencia_plan', 0)}%

### Patrones Aprendidos
"""
        
        for insight in ctx.get('insights_aprendidos', [])[:3]:
            formatted += f"- {insight.get('patron', '')} → {insight.get('accion', '')}\n"
        
        return formatted
    
    def recalculate_stats_from_csv(self):
        """
        Recalcula TODAS las estadísticas desde los archivos maestros
        Llamar después de sincronización con Garmin/Withings
        """
        from datetime import datetime, timedelta
        import pandas as pd
        
        try:
            # Fecha límite: últimos 30 días
            fecha_limite = datetime.now() - timedelta(days=30)
            
            stats = {
                'km_totales': 0,
                'actividades_completadas': 0,
                'peso_promedio_kg': 0,
                'adherencia_plan': 0,
                'dolor_rodilla_dias': 0,
                'ultimo_calculo': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            
            # 1. CALCULAR ACTIVIDADES (desde CSV maestro)
            csv_deporte = config.CSV_DEPORTE_MAESTRO
            if os.path.exists(csv_deporte):
                df_sport = pd.read_csv(csv_deporte, sep=';')
                if not df_sport.empty and 'Fecha' in df_sport.columns:
                    # Parsear fecha
                    df_sport['Fecha'] = pd.to_datetime(df_sport['Fecha'], errors='coerce')
                    
                    # Filtrar últimos 30 días
                    df_reciente = df_sport[df_sport['Fecha'] >= fecha_limite]
                    
                    # Contar actividades
                    stats['actividades_completadas'] = len(df_reciente)
                    
                    # Sumar kilómetros
                    if 'Distancia (km)' in df_reciente.columns:
                        # Parsear números con formato español (coma decimal)
                        km_series = df_reciente['Distancia (km)'].astype(str).str.replace(',', '.')
                        km_numericos = pd.to_numeric(km_series, errors='coerce').fillna(0)
                        stats['km_totales'] = round(km_numericos.sum(), 2)
            
            # 2. CALCULAR PESO PROMEDIO (desde CSV maestro)
            csv_peso = config.CSV_PESO_MAESTRO
            if os.path.exists(csv_peso):
                df_peso = pd.read_csv(csv_peso, sep=';')
                if not df_peso.empty and 'Fecha' in df_peso.columns and 'Peso' in df_peso.columns:
                    df_peso['Fecha'] = pd.to_datetime(df_peso['Fecha'], errors='coerce')
                    df_peso_reciente = df_peso[df_peso['Fecha'] >= fecha_limite]
                    
                    if not df_peso_reciente.empty:
                        # Parsear pesos
                        peso_series = df_peso_reciente['Peso'].astype(str).str.replace(',', '.')
                        pesos = pd.to_numeric(peso_series, errors='coerce').dropna()
                        if len(pesos) > 0:
                            stats['peso_promedio_kg'] = round(pesos.mean(), 1)
            
            # 3. CALCULAR DÍAS CON DOLOR (desde dolor_rodilla.json)
            dolor_file = config.DOLOR_RODILLA_FILE
            if os.path.exists(dolor_file):
                with open(dolor_file, 'r', encoding='utf-8') as f:
                    dolor_data = json.load(f)
                    
                registros_recientes = [
                    r for r in dolor_data.get('registros', [])
                    if datetime.strptime(r['fecha'], '%Y-%m-%d') >= fecha_limite
                ]
                
                # Contar días únicos con dolor > 0
                dias_con_dolor = set()
                for r in registros_recientes:
                    if r.get('intensidad', 0) > 0:
                        dias_con_dolor.add(r['fecha'])
                
                stats['dolor_rodilla_dias'] = len(dias_con_dolor)
            
            # 4. CALCULAR ADHERENCIA AL PLAN (aproximada)
            # Si hay plan_entrenamiento.json, comparar días con actividad vs días planificados
            plan_file = config.PLAN_ENTRENAMIENTO_FILE
            if os.path.exists(plan_file):
                with open(plan_file, 'r', encoding='utf-8') as f:
                    plan = json.load(f)
                    
                # Contar días en el plan que NO son "Descanso Total"
                dias_planificados = sum(
                    1 for dia in plan.get('semana', []) 
                    if dia.get('actividad', '') != 'Descanso Total'
                )
                
                # Aproximar adherencia diviendo semanas
                if dias_planificados > 0:
                    semanas_en_30d = 30 / 7
                    dias_esperados = int(dias_planificados * semanas_en_30d)
                    if dias_esperados > 0:
                        stats['adherencia_plan'] = min(100, int((stats['actividades_completadas'] / dias_esperados) * 100))
            
            # Guardar en contexto
            self.context['estadisticas_ultimos_30d'] = stats
            self._save_context()
            
            print(f"[OK] Estadisticas recalculadas: {stats['actividades_completadas']} actividades, {stats['km_totales']} km")
            return True
            
        except Exception as e:
            print(f"[WARNING] Error recalculando stats: {e}")
            return False
