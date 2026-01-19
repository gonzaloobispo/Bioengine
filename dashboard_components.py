import streamlit as st
import pandas as pd
import visualizations
import datetime
import config

def render_kpi_header(df_s_f, df_p_f_full, last_p, last_p_date):
    """Renderiza la sección de KPIs principales"""
    st.header("1. Resumen de Eficiencia y Estado Actual")
    
    # Cálculos
    def clean_num(v):
        if pd.isna(v): return 0
        if isinstance(v, str): return float(v.replace('.','').replace(',','.'))
        return float(v)

    km_tot = df_s_f['Distancia (km)'].apply(clean_num).sum() if not df_s_f.empty else 0
    kcal_tot = df_s_f['Calorias'].apply(clean_num).sum() if not df_s_f.empty else 0
    peso_avg = df_p_f_full['Peso'].mean() if not df_p_f_full.empty else 0
    eficiencia = kcal_tot / (km_tot * peso_avg) if (peso_avg and (km_tot * peso_avg) > 0) else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Peso Actual", f"{last_p:.1f} kg")
        st.caption(f"Última sync: {last_p_date}")
    with c2:
        st.metric("Km Totales", f"{km_tot:.1f} km")
    with c3:
        st.metric("Energía Total", f"{kcal_tot:,.0f} kcal".replace(',','.'))
    with c4:
        st.metric("Eficiencia", f"{eficiencia:.3f}", help="Kcal gastadas por cada Km por cada Kg de peso")

def render_knee_health_section(df_sport, df_p_full):
    """Sección detallada de salud de rodilla"""
    st.divider()
    st.header("📈 Auditoría de Rodilla (Carga vs Stress)")
    
    col_chart, col_info = st.columns([3, 1])
    
    with col_chart:
        fig = visualizations.create_knee_stress_chart(df_sport, df_p_full)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes para generar la auditoría de rodilla.")
            
    with col_info:
        st.markdown("""
        **Guía de Análisis:**
        - **Barras Azules**: Entrenamientos.
        - **Barras Rojas**: Competencias.
        - **Línea Puntos**: Tu peso. 
        - **Sombreado Rojo**: Stress mecánico.
        
        *Si el sombreado rojo sube pero el peso también, el riesgo de lesión en tu rodilla derecha aumenta exponencialmente.*
        """)
        
        if not df_sport.empty and 'Stress_Score' in df_sport.columns:
            def clean_stress(v):
                if isinstance(v, str): return float(v.replace(',','.'))
                return v
            max_stress = df_sport['Stress_Score'].apply(clean_stress).max()
            st.write(f"**Pico de Stress Máximo:** {max_stress:.1f}")
            if max_stress > 500:
                st.warning("Has superado el umbral de 500 puntos de stress. Recomendado: Masaje y hielo.")

def render_shoe_management(df_sport):
    """Gestión de calzado con barras de progreso"""
    st.divider()
    st.header("👟 Gestión de Activos (Calzado)")
    
    fig = visualizations.create_shoe_wear_chart(df_sport)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Inicia una actividad para ver el desgaste de zapatillas.")

def render_roi_section(df_sport):
    """ROI y eficiencia por deporte"""
    st.divider()
    st.header("📊 Inteligencia Deportiva (ROI)")
    
    c1, c2 = st.columns(2)
    with c1:
        fig = visualizations.create_roi_heat_map(df_sport)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("**Conclusiones de Eficiencia:**")
        # Aquí se podrían agregar insights automáticos dinámicos
        st.info("El Trail Running genera picos de stress 3.5x superiores al Running de calle por cada km avanzado.")

def render_trainer_assistant(assistant, df_sport, df_p_full):
    """Sección del Asistente Personal (Coach)"""
    
    st.divider()
    st.header("🤖 Coach Personal: Asistente de Recuperación")
    
    advice = assistant.analyze_status(df_sport, df_p_full)
    metrics = assistant.get_adherence_metrics(df_sport)
    
    col_advice, col_metric = st.columns([2, 1])
    
    with col_advice:
        if advice['level'] == 'danger':
            st.error(f"**{advice['title']}**\n\n{advice['message']}")
            st.info(f"💡 **Acción recomendada:** {advice['action']}")
        elif advice['level'] == 'warning':
            st.warning(f"**{advice['title']}**\n\n{advice['message']}")
            st.info(f"💡 **Acción recomendada:** {advice['action']}")
        else:
            st.success(f"**{advice['title']}**\n\n{advice['message']}")
            st.info(f"💡 **Acción recomendada:** {advice['action']}")

    with col_metric:
        st.metric("Adherencia al Reposo de Impacto", f"{metrics['adherence_score']:.0f}%", 
                  delta=f"{metrics['weekly_km']:.1f} / {metrics['limit']} km", delta_color="inverse")
        st.caption("Basado en el límite de seguridad por Tendinosis Cuadricipital.")

def render_medical_profile():
    """Muestra el perfil clínico extraído"""
    import json
    import os
    import config
    
    ruta = os.path.join(config.BASE_DIR, 'config', 'historial_medico.json')
    if not os.path.exists(ruta):
        st.info("No se encontró el historial médico estructurado.")
        return

    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)

    st.divider()
    st.subheader("🏥 Perfil Clínico Integrado")
    
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Hitos Clínicos:**")
        for h in data['hitos_metabolicos']:
            st.write(f"- {h['fecha']}: {h['evento']} ({h['resultado'] if 'resultado' in h else h.get('detalle', '')})")
            
        st.write("**Condiciones Crónicas:**")
        for c in data['condiciones_cronicas']:
            st.write(f"- {c['nombre']}: {c['medicacion']} ({c['estado']})")
            
    with c2:
        st.write("**Biomecánica y Lesiones:**")
        for l in data['lesiones_y_biomecanica']:
            status_symbol = "🔴" if "Fase" in l.get('estado', '') else "🟡"
            st.write(f"{status_symbol} **{l['nombre']}** ({l.get('localizacion', 'Sistémico')})")
            st.caption(f"Recomendación: {l['recomendacion'] if 'recomendacion' in l else l.get('tratamiento', '')}")

    st.write("**⚠️ Alertas de Seguridad Configuradas:**")
    st.json(data['alertas_riesgo'])


def render_weekly_plan(assistant):
    """Muestra el calendario de entrenamiento planificado vs real"""
    st.divider()
    st.header("📅 Planificación Semanal (Closed Loop)")
    
    plan = assistant.current_plan
    if not plan:
        st.warning("No hay plan activo.")
        return

    st.caption(f"Semana del: {plan['semana_inicio']}")
    
    cols = st.columns(7)
    dias_orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    # Mapear datos por nombre de día (simple match)
    mapa_dias = {d['dia']: d for d in plan['dias']}
    
    for i, dia_nombre in enumerate(dias_orden):
        with cols[i]:
            datos = mapa_dias.get(dia_nombre)
            if datos:
                # Estilo dinámico según estado
                # Estilo dinámico según estado
                estado = datos['estado']
                actividad = datos['actividad']
                
                # Definir Icono Actividad
                icon_act = "🏃"
                if "Descanso" in actividad: icon_act = "💤"
                elif "Ciclismo" in actividad: icon_act = "🚴"
                elif "Fuerza" in actividad: icon_act = "🏋️"
                elif "Caminata" in actividad: icon_act = "🚶"
                elif "Rehab" in actividad: icon_act = "🧘"

                st.markdown(f"**{dia_nombre}**")
                # Parsear fecha YYYY-MM-DD a DD/MM/YY
                try:
                    f_obj = datetime.datetime.strptime(datos['fecha'], "%Y-%m-%d")
                    st.caption(f_obj.strftime("%d/%m/%y"))
                except:
                    st.caption(datos['fecha'])
                
                if estado == "Cumplido":
                    st.success(f"✅ {icon_act} {actividad}")
                    st.caption(f"Real: {datos.get('cumplimiento_real', '-')}")
                
                elif estado == "Fallido":
                    # Si era DESCANSO y falló (hizo algo), es ROJO.
                    # Si era ACTIVIDAD y falló (no hizo nada), es ROJO.
                    # PERO queremos diferenciar visualmente.
                    if "Descanso" in actividad:
                        st.error(f"❌ {icon_act} {actividad} (Roto)")
                    else:
                        st.error(f"❌ {icon_act} {actividad} (Saltado)")
                        
                elif estado == "Ajustado":
                     st.warning(f"⚠️ {icon_act} {actividad}")
                     st.caption(f"Motivo: {datos.get('notas', '')}")
                     
                else: # Pendiente
                    # Mostrar en AZUL/VERDE la actividad futura, NO en Rojo/Gris
                    if "Descanso" in actividad:
                         st.info(f"{icon_act} {actividad}")
                    else:
                         # Usamos success (verde) explícitamente para actividades pendientes
                         st.success(f"{icon_act} {actividad}") 
                    
                    if datos['duracion_obj_min'] > 0:
                        st.caption(f"Obj: {datos['duracion_obj_min']} min")
                
                if datos.get('equipo_sugerido') and datos['equipo_sugerido'] != "-":
                    st.caption(f"🎒 {datos['equipo_sugerido']}")


def render_coach_chat(assistant):
    """Interfaz de chat simulada con el Coach"""
    st.divider()
    st.header("💬 Chat con tu Coach")
    
    # Simulación de estado de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        # Verificar si ya respondió sobre dolor hoy
        from datetime import datetime
        import json
        import os
        
        dolor_file = os.path.join(config.BASE_DIR, 'data_cloud_sync', 'dolor_rodilla.json')
        ya_respondio_hoy = False
        
        try:
            if os.path.exists(dolor_file):
                with open(dolor_file, 'r', encoding='utf-8') as f:
                    dolor_data = json.load(f)
                    hoy = datetime.now().strftime('%Y-%m-%d')
                    for registro in dolor_data.get('registros', []):
                        if registro.get('fecha') == hoy:
                            ya_respondio_hoy = True
                            break
        except Exception:
            pass
        
        # Mensaje inicial adaptado
        if ya_respondio_hoy:
            mensaje_inicial = "Hola Gonzalo. ¿En qué puedo ayudarte hoy?"
        else:
            mensaje_inicial = "Hola Gonzalo. He revisado tu carga de hoy. ¿Cómo sientes la rodilla después del esfuerzo?"
        
        st.session_state.messages.append({"role": "assistant", "content": mensaje_inicial})

    # Mostrar historia
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input usuario
    if prompt := st.chat_input("Escribe a tu coach..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Motor de INTELIGENCIA REAL (Gemini)
        # Preparamos contexto con actividades recientes
        from datetime import datetime, timedelta
        import pandas as pd
        
        # Obtener actividades de los últimos 7 días si existen
        recent_activities = []
        try:
            df_sport = pd.read_csv(config.CSV_DEPORTE_MAESTRO, sep=';')
            if not df_sport.empty and 'Fecha' in df_sport.columns:
                df_sport['Fecha'] = pd.to_datetime(df_sport['Fecha'])
                fecha_limite = datetime.now() - timedelta(days=7)
                df_reciente = df_sport[df_sport['Fecha'] >= fecha_limite].sort_values('Fecha', ascending=False)
                
                # Pasar TODOS los datos disponibles para análisis profundo
                for _, row in df_reciente.head(10).iterrows():
                    actividad = {
                        'fecha': row['Fecha'].strftime('%Y-%m-%d %H:%M'),
                        'actividad': row.get('Actividad', 'Desconocida'),
                        'duracion_min': row.get('Duración (min)', 0),
                        'distancia_km': row.get('Distancia (km)', 0)
                    }
                    
                    # Agregar todos los campos adicionales disponibles
                    campos_opcionales = [
                        'Calorías', 'FC_Prom (bpm)', 'FC_Max (bpm)', 
                        'Cadencia_Prom', 'Elevación (m)', 'Velocidad_Prom (km/h)',
                        'Stress_Score', 'Temperatura (°C)', 'Potencia_Prom (W)',
                        'Training_Effect', 'VO2Max_Estimado'
                    ]
                    
                    for campo in campos_opcionales:
                        if campo in row and pd.notna(row[campo]):
                            actividad[campo] = row[campo]
                    
                    recent_activities.append(actividad)
        except Exception:
            pass
        
        context = {
            "medical": assistant.medical_history,
            "inventory": assistant.inventory,
            "plan": assistant.current_plan,
            "protocol": assistant.protocol,
            "recent_activities": recent_activities  # Nuevas actividades
        }
        
        # Agregar contexto persistente del usuario
        try:
            from context_manager import ContextManager
            ctx_mgr = ContextManager()
            context['user_context'] = ctx_mgr.get_context_summary()
        except Exception:
            pass  # Continuar sin contexto persistente si falla
        
        with st.spinner("Pensando..."):
            # Pasar historial de conversación para memoria
            conversation_history = [{"role": msg["role"], "content": msg["content"]} 
                                   for msg in st.session_state.messages[-5:]]  # Últimos 5 mensajes
            response_data = assistant.brain.send_message(prompt, context, conversation_history)
        
        reply_text = response_data['text']
        action = response_data['action']
        params = response_data.get('action_params', {})
        
        # Bandera para saber si se modificó el plan
        plan_modificado = False
        
        # Ejecutar acción si existe
        if action == "force_plan_regeneration":
            start_date = params.get('start_date')
            assistant.force_plan_regeneration(start_date)
            reply_text += f"\n\n✅ *He actualizado el plan comenzando el {start_date or 'hoy'}."
            plan_modificado = True
        
        # Nueva acción: modificar plan de hoy (con lógica corregida)
        # Detectar keywords de modificación
        keywords_modificacion = ["planifica", "agrega", "cambia", "modifica", "pon", "haz", "programa"]
        keywords_actividad = {
            "ciclismo": ("Ciclismo Recuperación", 45),
            "bicicleta": ("Ciclismo Recuperación", 45),
            "fuerza": ("Fuerza Hipertrofia Fase 1", 45),
            "hipertrofia": ("Fuerza Hipertrofia Fase 1", 45),
            "descanso": ("Descanso Total", 0)
        }
        
        # Verificar si hay intención de modificar
        tiene_intencion = any(kw in prompt.lower() for kw in keywords_modificacion)
        
        if tiene_intencion or action == "modify_today_plan":
            # Detectar qué actividad quiere
            actividad_nueva = None
            duracion = 0
            
            for keyword, (actividad, mins) in keywords_actividad.items():
                if keyword in prompt.lower():
                    actividad_nueva = actividad
                    duracion = mins
                    break
            
            if actividad_nueva:
                # Modificar plan de hoy
                from datetime import datetime
                hoy = datetime.now().strftime("%Y-%m-%d")
                
                # Buscar y modificar el día de hoy en el plan
                dia_encontrado = False
                for dia in assistant.current_plan['semana']:
                    if dia['fecha'] == hoy:
                        dia['actividad'] = actividad_nueva
                        dia['duracion_obj_min'] = duracion
                        dia['estado'] = 'Pendiente'
                        dia_encontrado = True
                        break
                
                if dia_encontrado:
                    # Guardar plan modificado
                    import json
                    with open(assistant.plan_file, 'w', encoding='utf-8') as f:
                        json.dump(assistant.plan, f, indent=2, ensure_ascii=False)
                    
                    reply_text += f"\n\n✅ **Plan modificado:** Hoy ({hoy}) tienes **{actividad_nueva}** ({duracion} min)."
                    st.success(f"✅ Plan actualizado: {actividad_nueva}")
                    plan_modificado = True
        
        # Si se modificó el plan, forzar recarga en próximo refresh
        if plan_modificado:
            st.session_state['plan_modified'] = True
        
        # Detectar y registrar estado de rodilla
        keywords_dolor = ["rodilla", "dolor", "siento", "molestia"]
        keywords_bien = ["bien", "ok", "sin dolor", "genial", "perfecto", "normal"]
        
        if any(kw in prompt.lower() for kw in keywords_dolor):
            # Usuario mencionó la rodilla
            intensidad = None
            
            # Buscar intensidad numérica (1-10)
            import re
            numeros = re.findall(r'\b([1-9]|10)\b', prompt)
            if numeros:
                intensidad = int(numeros[0])
            elif any(kw in prompt.lower() for kw in keywords_bien):
                intensidad = 0
            
            if intensidad is not None:
                # Guardar registro
                from datetime import datetime
                import json
                import os
                
                dolor_file = os.path.join(config.BASE_DIR, 'data_cloud_sync', 'dolor_rodilla.json')
                
                try:
                    if os.path.exists(dolor_file):
                        with open(dolor_file, 'r', encoding='utf-8') as f:
                            dolor_data = json.load(f)
                    else:
                        dolor_data = {"registros": []}
                    
                    # Agregar nuevo registro
                    dolor_data['registros'].append({
                        "fecha": datetime.now().strftime('%Y-%m-%d'),
                        "hora": datetime.now().strftime('%H:%M'),
                        "intensidad": intensidad,
                        "nota": prompt[:100],  # Primeros 100 caracteres
                        "registrado_via": "chat"
                    })
                    
                    # Guardar
                    with open(dolor_file, 'w', encoding='utf-8') as f:
                        json.dump(dolor_data, f, indent=2, ensure_ascii=False)
                    
                    st.success(f"✅ Estado de rodilla registrado: {intensidad}/10")
                except Exception as e:
                    pass  # Fallar silenciosamente
            
        with st.chat_message("assistant"):
            st.markdown(reply_text)
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        
        # NUEVO: Logging automático de conversaciones importantes
        try:
            from context_manager import ContextManager
            from llm_client import LLMClient
            
            # Detectar si la conversación es importante para guardar
            es_importante = False
            tipo_conversacion = ""
            
            # Criterios de importancia:
            if plan_modificado:
                es_importante = True
                tipo_conversacion = "modificacion_plan"
            
            elif any(kw in prompt.lower() for kw in keywords_dolor):
                es_importante = True
                tipo_conversacion = "reporte_medico"
            
            elif any(palabra in prompt.lower() for palabra in ["recomienda", "debería", "consejo", "qué hacer", "cómo"]):
                # Consultas que requieren recomendación personalizada
                if len(reply_text) > 100:  # Solo si la respuesta es sustancial
                    es_importante = True
                    tipo_conversacion = "consulta_personalizada"
            
            elif "correlación" in reply_text.lower() or "patrón" in reply_text.lower():
                # El asistente detectó un patrón o correlación
                es_importante = True
                tipo_conversacion = "insight_patron"
            
            # Guardar si es importante
            if es_importante:
                # RESUMIR con LLM antes de guardar
                llm = LLMClient()
                resumen = llm.summarize_conversation(prompt, reply_text)
                
                ctx = ContextManager()
                ctx.log_conversation_learning(
                    summary=resumen,  # Resumen generado por LLM
                    learning=f"[{tipo_conversacion}] {resumen[:100]}",
                    context_note=""  # Ya no guardamos el contexto completo
                )
                print(f"[CONV] Guardado: {resumen}")
                
        except Exception as e:
            # No fallar si hay error en logging
            print(f"[WARNING] Error guardando conversacion: {e}")
        
        # Forzar recarga si hubo acción crítica
        if action:
            st.rerun()


def render_bio_timeline_section(df_sport, assistant):
    """Renderiza el gráfico maestro de línea de tiempo"""
    st.divider()
    st.header("⏳ Línea de Tiempo Bio-Integrada")
    st.caption("Visualiza la relación Causa-Efecto entre tu Carga de Entrenamiento y Eventos Médicos.")
    
    fig = visualizations.create_bio_timeline(df_sport, assistant.medical_history)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos para construir la línea de tiempo.")



def add_chat_css():
    import streamlit as st
    st.markdown("""<style>
/* Mejorar UX del chat */
.stChatFloatingInputContainer {
    position: sticky !important;
    bottom: 0 !important;
    background: white;
    z-index: 999;
    padding-top: 1rem;
    border-top: 1px solid #e0e0e0;
}
/* Auto-scroll */
.stChatMessage {
    scroll-margin-bottom: 100px;
}
</style>""", unsafe_allow_html=True)
