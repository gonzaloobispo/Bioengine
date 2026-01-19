import json
import os
import pandas as pd
import config
import config
from datetime import datetime, timedelta
from llm_client import LlmClient

class TrainerAssistant:
    def __init__(self):
        self.medical_history = self._load_medical_history()
        self.inventory = self._load_inventory()
        self.plan_file = config.PLAN_ENTRENAMIENTO_FILE
        self.protocol_file = os.path.join(config.BASE_DIR, 'config', 'protocolo_medico.md')
        self.current_plan = self._load_current_plan()
        self.protocol = self._load_protocol()
        self.data_processed = config.SYNC_DATA
        self.brain = LlmClient() # Cerebro Gemini
    
    def _load_medical_history(self):
        ruta = config.HISTORIAL_MEDICO_FILE
        if os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _load_inventory(self):
        ruta = config.INVENTARIO_FILE
        if os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _load_protocol(self):
        if os.path.exists(self.protocol_file):
            with open(self.protocol_file, 'r', encoding='utf-8') as f:
                return f.read()
        return "No protocol found."

    def _load_current_plan(self):
        if os.path.exists(self.plan_file):
            with open(self.plan_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.generate_smart_plan()

    def generate_smart_plan(self, df_sport=None):
        """Genera un plan PROGRESIVO y personalizado (Fase: Rehabilitación)"""
        # 1. Determinar Fase de Entrenamiento
        tendinosis = self._get_lesion("Tendinosis")
        
        # Si hay lesión activa, la fase es REHABILITACIÓN CONSERVADORA
        if tendinosis:
            fase = "Rehabilitación (Fase 1)"
            frequency = 3 # Máximo 3 días de actividad a la semana
            duration_base = 30 # Minutos iniciales conservadores
            allowed_high_impact = False
        else:
            fase = "Construcción Base"
            frequency = 4
            duration_base = 45
            allowed_high_impact = True

        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        
        plan = {
            "semana_inicio": start_of_week.strftime("%Y-%m-%d"), 
            "fase_actual": fase,
            "dias": []
        }
        
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        # Helpers de Inventario
        bike = "Bici Estática/Rodillo" 
        if self.inventory and self.inventory.get("bicicletas"):
            bike = self.inventory["bicicletas"][0]["modelo"] # Trek FX
            
        shoe_trail = "Zapatillas Trail"
        if self.inventory and self.inventory.get("calzado"):
            shoe_trail = f"{self.inventory['calzado']['trail'][0]['modelo']} + Plantillas"

        shoe_street = "Zapatillas Estables"
        if self.inventory and self.inventory.get("calzado"):
            shoe_street = f"{self.inventory['calzado']['running_calle'][0]['modelo']} + Plantillas" # Kayano

        # Distribución de Carga para Lesionados (L-X-V o M-J-S)
        # Priorizamos descanso intercalado OBLIGATORIO
        active_days = ["Martes", "Jueves", "Sábado"] if tendinosis else ["Martes", "Jueves", "Sábado", "Domingo"]

        for i, nombre_dia in enumerate(dias_semana):
            dia_date = (start_of_week + timedelta(days=i)).strftime("%Y-%m-%d")
            
            activity = "Descanso Total"
            dur = 0
            inte = "-"
            equip = "-"
            note = "Permite que la inflamación baje."
            
            if nombre_dia in active_days:
                if tendinosis:
                    if nombre_dia in ["Martes", "Jueves", "Sábado"]:
                        activity = "Fuerza / Hipertrofia (Prot. Articular)"
                        dur = 45 
                        inte = "Carga Media Controlada"
                        equip = "Mancuernas 5kg + Colchoneta"
                        
                        # Rutina detallada A/B para variar
                        if nombre_dia == "Jueves":
                             note = "**Rutina B (Tracción/Cadena Posterior):**\n1. Peso Muerto Rumano c/mancuernas (4x12)\n2. Remo Unilateral (4x12)\n3. Puente Glúteo Isométrico (4x45s)\n4. Curl Bíceps (3x15)\n5. Plancha Lateral (3x30s)"
                        else: # Martes y Sábado (Empuje/Dominante Rodilla Seguro)
                             note = "**Rutina A (Empuje/Cuádriceps Seguro):**\n1. Sentadilla Isométrica en Pared (4x45s)\n2. Press de Hombros Sentado (4x12)\n3. Floor Press (Pecho) (4x12)\n4. Elevación Talones (Gemelos) (4x20)\n5. Deadbug (Core) (3x15)"
                    
                    # Cardio complementario solo si sobra energía, pero la base es Fuerza ahora.
                    if nombre_dia == "Sábado":
                        # Añadir un poco de cardio al final del Sábado
                        note += " + 20 min Caminata (Opcional)"

                else:
                    activity = "Running"
                    dur = duration_base
                    inte = "Zona 2"
                    equip = "Zapatillas Running"

            # Agregamos trabajo de Mobilidad / Ciclismo suave en días intermedios (Miércoles)
            if nombre_dia in ["Miércoles"] and tendinosis:
                activity = "Ciclismo Reg. / Movilidad"
                dur = 25
                # Cálculo: 25min a ritmo suave (~20km/h) = 8-9km
                inte = "Z1 | 85-90 RPM"
                equip = f"{bike}"
                note = "Meta: ~8.5km. Cadencia alta vital para lubricar rodilla sin carga." # Detalle específico

            plan["dias"].append({
                "fecha": dia_date,
                "dia": nombre_dia,
                "actividad": activity,
                "duracion_obj_min": dur,
                "intensidad": inte,
                "equipo_sugerido": equip,
                "notas": note,
                "estado": "Pendiente",
                "cumplimiento_real": None
            })
            
        return plan

    def save_plan(self):
        with open(self.plan_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_plan, f, indent=4, ensure_ascii=False)

    def reconcile_and_adjust(self, df_sport):
        """El cerebro del ciclo cerrado: Compara realidad vs plan y ajusta"""
        if df_sport.empty: return self.current_plan
        
        updated = False
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        for dia_plan in self.current_plan['dias']:
            if dia_plan['estado'] in ['Pendiente', 'Ajustado'] and dia_plan['fecha'] < today_str:
                # Buscar si se hizo algo ese día
                fecha_obj = datetime.strptime(dia_plan['fecha'], "%Y-%m-%d").date()
                match = df_sport[df_sport['Fecha'].dt.date == fecha_obj]
                
                if not match.empty:
                    # Se hizo actividad - Verificar si coincide el TIPO
                    # Normalizamos strings para comparar
                    planned_type = dia_plan['actividad'].lower()
                    actual_types = match['Tipo'].astype(str).str.lower().tolist()
                    
                    is_match = False
                    if "descanso" in planned_type:
                        is_match = False # Si era descanso y hubo algo, es match negativo (castigo)
                    elif "ciclis" in planned_type and any("cicl" in t or "bic" in t or "cycl" in t for t in actual_types):
                        is_match = True
                    elif "run" in planned_type and any("run" in t or "carr" in t for t in actual_types):
                        is_match = True
                    elif "camin" in planned_type and any("walk" in t or "sender" in t or "camin" in t for t in actual_types):
                        is_match = True
                    elif "fuerza" in planned_type and any("fuerza" in t or "strength" in t or "pesa" in t for t in actual_types):
                        is_match = True
                    else:
                        # Si es algo genérico o no detectado, asumimos OK por ahora para no frustrar
                        # pero podríamos marcarlo distinto
                        is_match = True 

                    real_km = match['Distancia (km)'].sum()
                    real_min = match['Duracion (min)'].sum()
                    
                    dia_plan['cumplimiento_real'] = f"{real_km:.1f} km / {real_min:.0f} min"

                    if is_match:
                         dia_plan['estado'] = "Cumplido"
                    elif dia_plan['actividad'] == "Descanso":
                         # Violación de descanso
                         self._trigger_punishment_adjustment(dia_plan['fecha'])
                         dia_plan['estado'] = "Fallido (Descanso Roto)"
                         updated = True
                    else:
                         # Hizo otra cosa (ej: Tenis en vez de Correr)
                         dia_plan['estado'] = "Ajustado (Act. Diferente)"
                         dia_plan['notas'] = f"Se detectó actividad distinta a la planeada ({actual_types[0]})."
                         
                else:
                    # No se hizo nada
                    if dia_plan['actividad'] != "Descanso":
                        dia_plan['estado'] = "Fallido"
                        updated = True
                    else:
                        dia_plan['estado'] = "Cumplido" # Descansó como debía
        
        if updated:
            self.save_plan()
            
        return self.current_plan

    def _trigger_punishment_adjustment(self, trigger_date):
        """Ajusta días futuros reduciendo carga por exceso previo"""
        trigger_dt = datetime.strptime(trigger_date, "%Y-%m-%d")
        for dia in self.current_plan['dias']:
            d_dt = datetime.strptime(dia['fecha'], "%Y-%m-%d")
            if d_dt > trigger_dt and dia['estado'] == 'Pendiente':
                # Convertir próximo entreno en descanso o muy suave
                if dia['duracion_obj_min'] > 30:
                    dia['actividad'] = "Recuperación Forzada (Ajuste)"
                    dia['duracion_obj_min'] = 20
                    dia['intensidad'] = "Muy Baja"
                    dia['notas'] = "Ajuste automático por exceso de carga previo."
                    dia['notas'] = "Ajuste automático por exceso de carga previo."
                    dia['estado'] = "Ajustado"

    def force_plan_regeneration(self, start_date=None):
        """Regenera el plan forzando una fecha de inicio (Módulo Chat)"""
        # Hack simple para la demo
        plan = self.generate_smart_plan()
        if start_date:
            plan['semana_inicio'] = start_date
            
            # Recalcular las fechas de los días subsiguientes
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            for i, dia in enumerate(plan['dias']):
                real_dt = start_dt + timedelta(days=i)
                dia['fecha'] = real_dt.strftime("%Y-%m-%d")
                
        self.current_plan = plan
        self.save_plan()
        return True

    def analyze_status(self, df_sport, df_weight):
        # Primero reconciliar
        self.reconcile_and_adjust(df_sport)
        
        """Analiza el estado actual basado en los últimos datos y el historial médico"""
        if df_sport.empty:
            return {"status": "info", "message": "No hay datos deportivos recientes para analizar."}
        
        # 1. Obtener contexto de los últimos 7 días
        last_7_days = df_sport[df_sport['Fecha'] >= (datetime.now() - timedelta(days=7))]
        total_km_7d = last_7_days['Distancia (km)'].sum()
        
        # 2. Verificar la Alerta de Tendinosis vs Carga actual
        # Solo contar actividades de IMPACTO (NO ciclismo, NO natación)
        tendinosis = self._get_lesion("Tendinosis") # Busca genérico
        impact_warning = False
        
        if tendinosis:
            # Filtrar solo actividades de impacto
            actividades_impacto = ['Carrera', 'Running', 'Correr', 'Trail', 'Tenis', 'Trekking', 'Caminata']
            if 'Actividad' in last_7_days.columns:
                df_impacto = last_7_days[last_7_days['Actividad'].str.contains('|'.join(actividades_impacto), case=False, na=False)]
                km_impacto_7d = df_impacto['Distancia (km)'].sum()
                
                if km_impacto_7d > 5:  # Más de 5km de actividades de impacto
                    impact_warning = True
                    total_km_7d = km_impacto_7d  # Actualizar para mostrar solo km de impacto

        # 3. Verificar Stress Score (Stress Crónico)
        high_stress_days = last_7_days[last_7_days['Stress_Score'] > 400] if 'Stress_Score' in last_7_days.columns else pd.DataFrame()
        
        # 4. Obtener peso actual y calcular IMC
        latest_weight = 76.0 # Default
        if not df_weight.empty:
            latest_weight = df_weight.sort_values('Fecha').iloc[-1]['Peso']
            
        # 5. Generar el Consejo del Día
        advice = self._generate_advice(total_km_7d, impact_warning, high_stress_days, last_7_days, latest_weight)
        
        return advice

    def _get_lesion(self, name):
        if not self.medical_history: return None
        for lesion in self.medical_history.get('lesiones_y_biomecanica', []):
            if name in lesion['nombre']:
                return lesion
        return None

    def _generate_advice(self, km_7d, impact_warning, high_stress_days, last_7_days, current_weight):
        if impact_warning:
            # Check if bike is available for alternative
            bike_suggestion = "ciclismo"
            if self.inventory and self.inventory.get("bicicletas"):
                bike_suggestion = f"bicicleta ({self.inventory['bicicletas'][0]['modelo']})"
            
            return {
                "level": "danger",
                "title": "🔴 ALERTA DE RIESGO: TENDINOSIS",
                "message": f"Has corrido {km_7d:.1f}km esta semana. Tu diagnóstico médico (2025) recomienda suspender impacto. Estás cronificando la lesión de rodilla.",
                "action": f"Prioriza {bike_suggestion} por 10 días."
            }
        
        if not high_stress_days.empty:
            return {
                "level": "warning",
                "title": "🟡 RECUPERACIÓN NECESARIA",
                "message": f"Detectamos {len(high_stress_days)} sesiones de alto stress mecánico. Tu pie plano/pronación está sufriendo.",
                "action": "Usa las plantillas hoy y haz ejercicios excéntricos de cuádriceps."
            }
        
        # Estado Óptimo Calculado
        height_cm = 176
        if self.medical_history and 'metadata' in self.medical_history:
             height_cm = self.medical_history['metadata'].get('altura_cm', 176)
        
        imc = current_weight / ((height_cm/100)**2)
        
        # Conclusion ejercicio
        sessions_count = len(last_7_days)
        exercise_summary = f"Has completado {sessions_count} sesiones ({km_7d:.1f} km total)." 
        if sessions_count == 0:
            exercise_summary = "Semana de descanso o inicio."

        return {
            "level": "success",
            "title": "🟢 ESTADO ÓPTIMO",
            "message": f"**IMC Actual: {imc:.1f}** (Peso: {current_weight:.1f}kg).\n\n{exercise_summary} Mantienes una excelente relación peso-potencia post-bariátrica.",
            "action": "Continúa con el plan de fuerza e hipertrofia."
        }

    def get_adherence_metrics(self, df_sport):
        """Calcula métricas de adherencia al reposo o entrenamiento"""
        # Por ahora simplificamos: km acumulados vs límite seguro (ej 15km para su estado actual)
        weekly_km = df_sport[df_sport['Fecha'] >= (datetime.now() - timedelta(days=7))]['Distancia (km)'].sum()
        limit = 15.0 # Límite "seguro" propuesto
        adherence = max(0, 100 - ((weekly_km / limit) * 100)) if weekly_km > limit else 100
        
        return {
            "weekly_km": weekly_km,
            "limit": limit,
            "adherence_score": adherence
        }
