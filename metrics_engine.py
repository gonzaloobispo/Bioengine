# metrics_engine.py - Motor de Lógica y KPIs
import config

def calcular_grasa_corporal(peso, altura, edad, sexo, grasa_medida=None):
    """Calcula grasa: Usa dato real si existe, sino estima por Deurenberg"""
    if grasa_medida is not None and grasa_medida > 0:
        return {
            "Metodo": "Medición Sensor (BIA)",
            "Valor_Porcentaje": grasa_medida,
            "Masa_Grasa_Kg": round(peso * (grasa_medida / 100), 2)
        }

    # Estimación
    imc = peso / (altura ** 2)
    sexo_factor = 1 if sexo == "M" else 0
    grasa_estimada = (1.20 * imc) + (0.23 * edad) - (10.8 * sexo_factor) - 5.4
    
    return {
        "Metodo": "Estimación Deurenberg (Teórico)",
        "Valor_Porcentaje": round(grasa_estimada, 2),
        "Masa_Grasa_Kg": round(peso * (grasa_estimada / 100), 2),
        "Nota": "Dato estimado. Falta medición real."
    }

def calcular_stress_rodilla(actividad_tipo, duracion_min, elevacion_m, peso_actual):
    """
    Calcula el índice de carga mecánica (ICMA).
    Formula: (Tiempo * Coeficiente) * (Factor Peso) + (Elevación * 0.1)
    """
    perfil = config.get_perfil_activo()
    
    # 1. Coeficientes de Impacto (Basados en tu historial)
    coeficientes = {
        "running": 2.5,
        "trail_running": 3.0,
        "tenis": 4.5,      # Impacto lateral alto
        "caminata": 1.0,
        "ciclismo": 0.5
    }
    
    tipo_key = actividad_tipo.lower().replace(" ", "_")
    factor_actividad = coeficientes.get(tipo_key, 1.5) # Default 1.5
    
    # 2. Factor de Penalización por Peso
    # Peso base saludable aprox 76kg. Cada kg extra suma 4% de carga
    sobrepeso = max(0, peso_actual - 76)
    factor_peso = 1 + (sobrepeso * 0.04)
    
    # 3. Cálculo final
    carga_base = duracion_min * factor_actividad
    carga_ajustada = carga_base * factor_peso
    carga_elevacion = elevacion_m * 0.1 # 10 puntos por cada 100m desnivel
    
    total_score = round(carga_ajustada + carga_elevacion, 1)
    
    return total_score

def analisis_gerencial_salud(peso_actual):
    perfil = config.get_perfil_activo()
    edad = config.get_edad(perfil["fecha_nacimiento"])
    altura = perfil["altura"]
    
    imc = peso_actual / (altura ** 2)
    
    # Lógica Adulto
    techo_lesion = 22.5 if perfil["lesion_rodilla"] else 24.9
    ajuste_sexo = 1.0 if perfil["sexo"] == "M" else 0
    limite_seguro = techo_lesion + ajuste_sexo
    
    peso_max = limite_seguro * (altura ** 2)
    desvio = peso_actual - peso_max
    
    status = "🟢 Óptimo"
    if desvio > 0:
        status = f"🔴 Sobrecarga (+{round(desvio, 1)} kg)"
        
    return {
        "IMC": round(imc, 2),
        "Status": status,
        "Peso_Limite_Rodilla": round(peso_max, 2)
    }