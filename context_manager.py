import json
import os
from datetime import datetime
import config

class ContextManager:
    """
    Gestiona el contexto persistente del usuario para personalización del chatbot
    """
    
    def __init__(self):
        self.context_file = os.path.join(config.BASE_DIR, 'data_cloud_sync', 'user_context.json')
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
