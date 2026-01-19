
import os
import json
from google import genai
from google.genai import types
import config
from datetime import datetime

class LlmClient:
    def __init__(self):
        self.api_key = self._load_api_key()
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            # Modelo seguro que sabemos que funciona en v2/latest
            self.model_name = 'gemini-2.0-flash' 
        else:
            self.client = None

    def _load_api_key(self):
        """Intenta cargar la API KEY de secretos o variables de entorno"""
        # 1. Secrets File
        secrets_path = os.path.join(config.BASE_DIR, 'config', 'secrets.json')
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path, 'r') as f:
                    data = json.load(f)
                    return data.get('GEMINI_API_KEY')
            except: pass
        
        # 2. Env Var
        return os.environ.get('GEMINI_API_KEY')
    
    def summarize_conversation(self, user_message, assistant_response):
        """
        Resume una conversación usando el LLM, extrayendo solo puntos clave y decisiones
        Retorna un resumen conciso sin charla innecesaria
        """
        try:
            prompt = f"""
Eres un asistente que resume conversaciones médicas/deportivas.

CONVERSACIÓN:
Usuario: {user_message}
Asistente: {assistant_response}

TAREA:
Resume esta conversación en máximo 2-3 líneas, incluyendo SOLO:
1. Decisión o cambio importante (si hubo)
2. Información médica relevante (dolor, síntoma, etc.)
3. Recomendación clave dada

FORMATO DE SALIDA:
- Una sola frase por punto
- Eliminar saludos, agradecimientos, charla innecesaria
- Ser extremadamente conciso

EJEMPLO:
Usuario solicitó cambiar rutina a Ciclismo. Reportó dolor rodilla 3/10. Recomendación: reducir impacto próximos 3 días.

RESUMEN:
"""
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            
            summary = response.text.strip()
            
            # Limitar a 200 caracteres máximo
            if len(summary) > 200:
                summary = summary[:197] + "..."
            
            return summary
            
        except Exception as e:
            # Si falla el resumen, retornar versión simple
            return f"{user_message[:80]}... {assistant_response[:80]}..."

    def send_message(self, user_message, context_data=None, conversation_history=None):
        if not self.client:
            return {
                "text": "⚠️ No tengo configurada una API KEY de Gemini. Por favor configúrala en `config/secrets.json`.",
                "action": None
            }

        # Construir Prompt con Contexto e Historial
        system_instruction = self._build_system_prompt(context_data)
        
        # Agregar historial de conversación si existe
        history_text = ""
        if conversation_history:
            history_text = "\n\nCONVERSATION HISTORY:\n"
            for msg in conversation_history:
                role = "USER" if msg["role"] == "user" else "ASSISTANT"
                history_text += f"{role}: {msg['content']}\n"
        
        full_content = f"{system_instruction}{history_text}\n\nUSER MESSAGE: {user_message}"

        # Lista de modelos a probar en orden de prioridad (Fastest/Cheapest -> Standard)
        # Basado en el listado real de la API
        candidate_models = [
            'gemini-2.0-flash-lite-001',
            'gemini-flash-latest',
            'gemini-pro-latest',
            'gemini-2.5-flash'
        ]

        last_error = None

        for model_name in candidate_models:
            try:
                # Intentar generar con el modelo actual
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=full_content,
                    config=types.GenerateContentConfig(
                        max_output_tokens=1000,
                        temperature=0.7
                    )
                )
                
                # Si llegamos aquí, funcionó
                raw_text = response.text
                return self._parse_response(raw_text)

            except Exception as e:
                last_error = e
                # Si es error de Quota (429) o Not Found (404), intentamos el siguiente
                if "429" in str(e) or "404" in str(e) or "Quota" in str(e) or "not found" in str(e):
                    continue
                else:
                    # Si es otro error (ej: autenticación), fallamos rápido
                    break
        
        # Si salimos del loop sin éxito
        return {
            "text": f"Error de conexión con Gemini (Probé {len(candidate_models)} modelos). Último error: {str(last_error)}",
            "action": None
        }

    def _build_system_prompt(self, context):
        """Crea el contexto médico y deportivo"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        prompt = f"""
Eres "BioEngine Coach", un entrenador personal experto en biomecánica y rehabilitación.
Tu usuario es "Gonzalo", un atleta de 49 años post-bariátrico con Tendinosis Cuadricipital y Pie Plano.

OBJETIVO:
Guiar al usuario protegiendo su rodilla. Priorizar Fuerza/Hipertrofia sobre Cardio de impacto.

CONTEXTO ACTUAL ({today}):
"""
        if context:
            if 'medical' in context:
                prompt += f"\n[HISTORIAL MÉDICO]:\n{json.dumps(context['medical'], ensure_ascii=False)[:1000]}"
            if 'plan' in context:
                current_plan = context['plan']
                # Resumir plan para ahorrar tokens
                plan_summary = []
                if current_plan and 'semana' in current_plan:
                    for d in current_plan.get('semana', []):
                        plan_summary.append(f"{d['dia']} ({d['fecha']}): {d['actividad']} [{d['estado']}]")
                prompt += f"\n[PLAN SEMANAL]:\n" + "\n".join(plan_summary)
            if 'protocol' in context:
                 prompt += f"\n[PROTOCOLO MÉDICO VIGENTE]:\n{context['protocol'][:2000]}" # Limitamos por si acaso
            if 'inventory' in context:
                 prompt += f"\n[EQUIPO]:\n{json.dumps(context['inventory'], ensure_ascii=False)[:1000]}"
            if 'recent_activities' in context and context['recent_activities']:
                 prompt += f"\\n[ACTIVIDADES RECIENTES]:\\n{json.dumps(context['recent_activities'], ensure_ascii=False, indent=2)[:3000]}"

        prompt += """
\nINSTRUCCIONES DE RESPUESTA:
1. Sé conciso, empático y profesional.
2. Si el usuario pide CAMBIAR una fecha o una regla, debes responder con un bloque JSON al final de tu mensaje.

FORMATO DE ACCIÓN (Si es necesario):
Si detectas una intención de cambio, añade al final:
```json
{
  "action": "force_plan_regeneration",
  "params": { "start_date": "YYYY-MM-DD" } 
}
```
O si es una consulta normal, solo responde texto.
"""
        return prompt

    def _parse_response(self, text):
        """Extrae JSON de acciones si existe"""
        action = None
        params = {}
        clean_text = text

        if "```json" in text:
            try:
                # Extraer bloque
                json_part = text.split("```json")[1].split("```")[0].strip()
                data = json.loads(json_part)
                action = data.get('action')
                params = data.get('params', {})
                
                # Limpiar el texto para el usuario
                clean_text = text.split("```json")[0].strip()
            except:
                pass # Fallo el parseo, devolvemos todo como texto
        
        return {
            "text": clean_text,
            "action": action,
            "action_params": params
        }



