import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

def create_knee_stress_chart(df_sport, df_p_full):
    """
    Crea una gráfica interactiva de Stress de Rodilla vs Peso Corporal.
    """
    if df_sport.empty or df_p_full.empty:
        return None

    # Asegurar orden cronológico para Plotly
    df_s = df_sport.sort_values('Fecha')
    df_p = df_p_full.sort_values('Fecha')
    
    # Crear figura con ejes y secundarios
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. Carga de Entrenamiento (Barras)
    fig.add_trace(
        go.Bar(
            x=df_s['Fecha'],
            y=df_s['Distancia (km)'],
            name="Distancia (km)",
            marker_color='rgba(52, 152, 219, 0.6)',
            hovertemplate="<b>%{x|%d/%m/%y}</b><br>" +
                          "Distancia: %{y:.2f} km<br>" +
                          "Evento: %{customdata[0]}<br>" +
                          "Calzado: %{customdata[1]}<extra></extra>",
            customdata=df_s[['Evento_Nombre', 'Calzado']].values
        ),
        secondary_y=False,
    )

    # 2. Stress Score (Línea de Área)
    if 'Stress_Score' in df_s.columns:
        # Limpiar stress score si viene como string con coma
        def clean_stress(v):
            if isinstance(v, str): return float(v.replace(',','.'))
            return v
        
        y_stress = df_s['Stress_Score'].apply(clean_stress)
        
        fig.add_trace(
            go.Scatter(
                x=df_s['Fecha'],
                y=y_stress,
                name="Knee Stress Score",
                line=dict(color='rgba(231, 76, 60, 0.8)', width=2),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.1)',
                hovertemplate="Stress Score: %{y:.1f}<extra></extra>"
            ),
            secondary_y=False,
        )

    # 3. Peso Corporal (Línea de Puntos)
    fig.add_trace(
        go.Scatter(
            x=df_p['Fecha'],
            y=df_p['Peso'],
            name="Peso (kg)",
            line=dict(color='#2c3e50', width=3, dash='dot'),
            hovertemplate="Peso: %{y:.1f} kg<extra></extra>"
        ),
        secondary_y=True,
    )

    # Configuración de diseño
    fig.update_layout(
        title="<b>Evolución de Carga vs Peso (Auditoría de Rodilla)</b>",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=80, b=0),
        height=500
    )

    fig.update_yaxes(title_text="<b>Carga / Stress</b>", secondary_y=False, gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(title_text="<b>Peso (kg)</b>", secondary_y=True, showgrid=False)
    
    return fig

def create_shoe_wear_chart(df_sport):
    """
    Gráfica de desgaste de calzado con barras de progreso.
    """
    if df_sport.empty or 'Calzado' not in df_sport.columns:
        return None
    
    # Calcular kms por calzado
    def clean_dist(v):
        if isinstance(v, str): return float(v.replace('.','').replace(',','.'))
        return float(v)
    
    df_temp = df_sport.copy()
    df_temp['Km'] = df_temp['Distancia (km)'].apply(clean_dist)
    
    wear = df_temp.groupby('Calzado')['Km'].sum().reset_index()
    wear.columns = ['Calzado', 'Km_Totales']
    
    # Definir límite (800km por defecto)
    wear['Life_Limit'] = 800
    wear['Wear_Pct'] = (wear['Km_Totales'] / wear['Life_Limit'] * 100).clip(upper=100)
    
    # Color según desgaste
    def get_color(pct):
        if pct < 70: return '#27ae60' # Verde
        if pct < 90: return '#f1c40f' # Amarillo
        return '#e74c3c' # Rojo

    wear['Color'] = wear['Wear_Pct'].apply(get_color)
    
    fig = go.Figure()
    
    for _, row in wear.sort_values('Km_Totales', ascending=True).iterrows():
        # Barra de fondo (gris)
        fig.add_trace(go.Bar(
            y=[row['Calzado']],
            x=[800],
            orientation='h',
            marker_color='rgba(0,0,0,0.05)',
            showlegend=False,
            hoverinfo='none'
        ))
        # Barra de progreso
        fig.add_trace(go.Bar(
            y=[row['Calzado']],
            x=[row['Km_Totales']],
            orientation='h',
            name=row['Calzado'],
            marker_color=row['Color'],
            hovertemplate=f"Km: {row['Km_Totales']:.1f} / 800<extra></extra>",
            showlegend=False
        ))

    fig.update_layout(
        barmode='overlay',
        title="<b>Estado de Vida ÚTIL de Calzado</b>",
        height=300 + (len(wear) * 30),
        margin=dict(l=0, r=0, t=50, b=0),
        xaxis=dict(title="Kilómetros Recorridos", range=[0, 850])
    )
    
    return fig

def create_roi_heat_map(df_sport):
    """
    Heatmap de Eficiencia por Deporte.
    """
    if df_sport.empty:
        return None
        
    def clean_val(v):
        if isinstance(v, str): return float(v.replace('.','').replace(',','.'))
        return float(v)

    df_temp = df_sport.copy()
    df_temp['Km'] = df_temp['Distancia (km)'].apply(clean_val)
    df_temp['Kcal'] = df_temp['Calorias'].apply(clean_val)
    
    roi = df_temp.groupby('Tipo').agg({
        'Km': 'sum',
        'Kcal': 'sum',
        'Fecha': 'count'
    }).reset_index()
    roi['Kcal/Km'] = roi['Kcal'] / roi['Km']
    roi = roi[roi['Km'] > 0].sort_values('Kcal/Km', ascending=False)
    
    fig = px.bar(
        roi, 
        x='Tipo', 
        y='Kcal/Km', 
        color='Kcal/Km',
        text_auto='.1f',
        title="<b>Retorno de Inversión Energética (Kcal/Km)</b>",
        color_continuous_scale='RdYlGn_r'
    )
    
    fig.update_layout(height=400, coloraxis_showscale=False)
    return fig

def create_bio_timeline(df_sport, medical_history):
    """
    Gráfico Maestro: Línea de Tiempo Bio-Integrada (Entrenamiento + Eventos Médicos + Fases)
    """
    if df_sport is None or df_sport.empty:
        return None
        
    df = df_sport.copy()
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df = df.sort_values('Fecha')
    
    # 1. Base: Stress Score Diario (Barras)
    fig = go.Figure()
    
    # Check metric
    y_metric = df['Distancia (km)']
    y_name = "Carga (km)"
    if 'Stress_Score' in df.columns:
        # Clean stress
        def clean_s(x): 
             if isinstance(x, str): return float(x.replace(',','.'))
             return x
        y_metric = df['Stress_Score'].apply(clean_s)
        y_name = "Stress Mecánico"
        
    fig.add_trace(go.Bar(
        x=df['Fecha'],
        y=y_metric,
        name=y_name,
        marker_color='rgba(41, 128, 185, 0.4)',
        hovertemplate="%{x|%d/%m/%Y}<br>" + f"{y_name}: %{{y:.1f}}<extra></extra>"
    ))

    # 2. Eventos Médicos (Marcadores)
    events = []
    # Parsear hitos
    if medical_history:
        # Hitos metabólicos
        for hito in medical_history.get('hitos_metabolicos', []):
            try:
                # Intentar parsear YYYY-MM o YYYY-MM-DD
                d_str = hito['fecha']
                if len(d_str) == 7: d_str += "-01"
                d_date = pd.to_datetime(d_str)
                events.append({'date': d_date, 'label': hito['evento'], 'color': '#e74c3c'})
            except: pass
            
        # Lesiones
        for les in medical_history.get('lesiones_y_biomecanica', []):
            if 'fecha_diagnostico' in les:
                try:
                    d_str = les['fecha_diagnostico']
                    if len(d_str) == 7: d_str += "-01"
                    d_date = pd.to_datetime(d_str)
                    events.append({'date': d_date, 'label': f"Dx: {les['nombre']}", 'color': '#c0392b'})
                except: pass

    # Plotear eventos
    for evt in events:
        fig.add_annotation(
            x=evt['date'],
            y=y_metric.max() * 0.9, # Altura relativa
            text="🏥",
            hovertext=evt['label'],
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=evt['color'],
            bgcolor="white",
            bordercolor=evt['color']
        )
        # Línea vertical
        fig.add_vline(x=evt['date'].timestamp() * 1000, line_width=1, line_dash="dash", line_color=evt['color'])

    # 3. Zonas de Fase (Simplificado basándose en fechas clave conocidas)
    # Por ahora hardzodeado dinámico: Si hoy es > 2025-01 -> Fase Rehab
    # Esto se podría hacer más inteligente leyendo un historial de fases
    
    # Highlight Today
    fig.add_vline(x=pd.Timestamp.now().timestamp() * 1000, line_width=2, line_color="#2c3e50", annotation_text="HOY")

    fig.update_layout(
        title="<b>Línea de Tiempo Bio-Integrada</b> (Carga vs Eventos Clínicos)",
        xaxis_title="Tiempo",
        yaxis_title=y_name,
        height=450,
        hovermode="x unified",
        margin=dict(t=50)
    )
    
    return fig
