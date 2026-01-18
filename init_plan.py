from trainer_assistant import TrainerAssistant

print("Inicializando Motor de Planificación...")
assistant = TrainerAssistant()

# FORZAR regeneración con lógica nueva (Smart Plan)
assistant.current_plan = assistant.generate_smart_plan()
assistant.save_plan()

print(f"Plan de entrenamiento guardado en: {assistant.plan_file}")
print("Semana generada:")
for dia in assistant.current_plan['dias']:
    equipo = dia.get('equipo_sugerido', '-')
    print(f" - {dia['dia']}: {dia['actividad']} ({dia['duracion_obj_min']} min) | Equipo: {equipo}")
