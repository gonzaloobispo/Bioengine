# app_bioengine.py - Dashboard Gerencial con Exportación Excel (.xlsx)
import streamlit as st
import pandas as pd
import plotly.express as px
import config
import metrics_engine
import os
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Bio-Engine Manager",
    page_icon="🧬",
    layout="wide"
)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    # Cargar csvs maestros
    if os.path.exists(config.CSV_PESO_MAESTRO):
        df_peso = pd.read_csv(config.CSV_PESO_MAESTRO, sep=';', decimal=',', thousands='.')
        df_peso['Fecha'] = pd.to_datetime(df_peso['Fecha'], dayfirst=True, format='mixed')
        df_peso = df_peso.sort_values('Fecha', ascending=False)
    else:
        df_peso = pd.DataFrame()

    if os.path.exists(config.CSV_DEPORTE_MAESTRO):
        df_deporte = pd.read_csv(config.CSV_DEPORTE_MAESTRO, sep=';', decimal=',', thousands='.')
        df_deporte['Fecha'] = pd.to_datetime(df_deporte['Fecha'], dayfirst=True, format='mixed')
        df_deporte = df_deporte.sort_values('Fecha', ascending=False)
    else:
        df_deporte = pd.DataFrame()
        
    return df_peso, df_deporte

def convert_df_to_excel(df):
    """Convierte dataframe a archivo Excel en memoria"""
    output = io.BytesIO()
    # Usamos el motor openpyxl para escribir .xlsx
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos_Auditoria')
    processed_data = output.getvalue()
    return processed_data

def convert_df_to_csv(df):
    """Convierte dataframe a CSV con separador ';' y decimal ','."""
    return df.to_csv(index=False, sep=';', decimal=',').encode('utf-8')

def main():
    # Sidebar: Selector de Perfil
    st.sidebar.title("🧬 Bio-Engine 2.0")
    
    nombres_usuarios = list(config.USUARIOS.keys())
    usuario_activo = st.sidebar.selectbox("Perfil Activo:", nombres_usuarios, index=0)
    
    config.ACTIVE_USER = usuario_activo
    perfil = config.get_perfil_activo()
    
    # Cargar Datos
    df_peso, df_deporte = load_data()
    
    # --- ENCABEZADO ---
    st.title(f"Panel de Control: {usuario_activo}")
    try:
        edad = config.get_edad(perfil['fecha_nacimiento'])
    except:
        edad = "N/A"
    st.markdown(f"**Edad:** {edad} años | **Altura:** {perfil['altura']}m")
    
    if df_peso.empty or df_deporte.empty:
        st.error("❌ No se encontraron datos. Ejecuta bio_engine.py y super_merger.py primero.")
        return

    # ==============================================================================
    # KPI 1: ANÁLISIS DE PESO Y ESTRUCTURA (CON EXPORTACIÓN EXCEL)
    # ==============================================================================
    st.subheader("1. Auditoría de Estructura Corporal")
    
    # --- ZONA DE FILTROS PESO ---
    if not df_peso.empty:
        max_date_w = df_peso['Fecha'].max().date()
        min_date_w = df_peso['Fecha'].min().date()
        # Por defecto mostramos últimos 6 meses
        default_start_w = max_date_w - pd.Timedelta(days=180)
        if default_start_w < min_date_w: default_start_w = min_date_w

        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1:
            date_start_w = st.date_input("Desde (Peso):", value=default_start_w, min_value=min_date_w, max_value=max_date_w)
        with col_f2:
            date_end_w = st.date_input("Hasta (Peso):", value=max_date_w, min_value=min_date_w, max_value=max_date_w)
        
        # Filtrar Dataframe
        mask_w = (df_peso['Fecha'].dt.date >= date_start_w) & (df_peso['Fecha'].dt.date <= date_end_w)
        df_peso_filt = df_peso.loc[mask_w].copy()
        
        # Formatear fecha para Excel (quitar hora)
        df_peso_filt['Fecha'] = df_peso_filt['Fecha'].dt.date

        # Botón Exportar EXCEL
        with col_f3:
            st.write("📥 **Exportar**")
            if not df_peso_filt.empty:
                excel_data = convert_df_to_excel(df_peso_filt)
                st.download_button(
                    label="Descargar Excel (.xlsx)",
                    data=excel_data,
                    file_name=f'Auditoria_Peso_{date_start_w}_{date_end_w}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                csv_data = convert_df_to_csv(df_peso_filt)
                st.download_button(
                    label="Descargar CSV (;)",
                    data=csv_data,
                    file_name=f'Auditoria_Peso_{date_start_w}_{date_end_w}.csv',
                    mime='text/csv'
                )

        # --- VISUALIZACIÓN ---
        if not df_peso_filt.empty:
            ultimo_peso_periodo = df_peso_filt.iloc[0]['Peso']
            analisis_peso = metrics_engine.analisis_gerencial_salud(ultimo_peso_periodo)
            
            kpi1, kpi2, kpi3 = st.columns(3)
            with kpi1:
                st.metric("Peso (Cierre Periodo)", f"{ultimo_peso_periodo} kg")
            with kpi2:
                st.metric("Límite Rodilla", f"{analisis_peso['Peso_Limite_Rodilla']} kg", 
                         delta=f"{round(ultimo_peso_periodo - analisis_peso['Peso_Limite_Rodilla'], 1)} kg",
                         delta_color="inverse")
            with kpi3:
                st.info(f"Estado en fecha: {analisis_peso['Status']}")

            # Gráfico Filtrado
            fig_peso = px.line(df_peso_filt, x='Fecha', y='Peso', title=f'Tendencia de Peso ({date_start_w} - {date_end_w})', markers=True)
            fig_peso.add_hline(y=analisis_peso['Peso_Limite_Rodilla'], line_dash="dash", line_color="red", annotation_text="Límite Rodilla")
            st.plotly_chart(fig_peso, width="stretch")
            
            with st.expander("Ver Detalle de Pesajes"):
                st.dataframe(df_peso_filt)
        else:
            st.warning("No hay registros de peso en las fechas seleccionadas.")

    # ==============================================================================
    # KPI 2: GESTIÓN DE RIESGO DEPORTIVO (CON EXPORTACIÓN EXCEL)
    # ==============================================================================
    st.markdown("---")
    st.subheader("2. Gestión de Activos (Carga de Entrenamiento)")
    
    # --- ZONA DE FILTROS DEPORTE ---
    if not df_deporte.empty:
        max_date_d = df_deporte['Fecha'].max().date()
        min_date_d = df_deporte['Fecha'].min().date()
        # Por defecto últimos 30 días para deporte
        default_start_d = max_date_d - pd.Timedelta(days=30)
        
        col_d1, col_d2, col_d3 = st.columns([1, 1, 1])
        with col_d1:
            fecha_inicio_d = st.date_input("Desde (Deporte):", value=default_start_d, min_value=min_date_d, max_value=max_date_d)
        with col_d2:
            fecha_fin_d = st.date_input("Hasta (Deporte):", value=max_date_d, min_value=min_date_d, max_value=max_date_d)
            
        mask_d = (df_deporte['Fecha'].dt.date >= fecha_inicio_d) & (df_deporte['Fecha'].dt.date <= fecha_fin_d)
        df_filtered_d = df_deporte.loc[mask_d].copy()
        
        # Formatear fecha para Excel
        df_filtered_d['Fecha'] = df_filtered_d['Fecha'].dt.date
        
        with col_d3:
            st.write("📥 **Exportar**")
            if not df_filtered_d.empty:
                excel_data_d = convert_df_to_excel(df_filtered_d)
                st.download_button(
                    label="Descargar Excel (.xlsx)",
                    data=excel_data_d,
                    file_name=f'Auditoria_Deporte_{fecha_inicio_d}_{fecha_fin_d}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                csv_data_d = convert_df_to_csv(df_filtered_d)
                st.download_button(
                    label="Descargar CSV (;)",
                    data=csv_data_d,
                    file_name=f'Auditoria_Deporte_{fecha_inicio_d}_{fecha_fin_d}.csv',
                    mime='text/csv'
                )

        # --- VISUALIZACIÓN ---
        if not df_filtered_d.empty:
            peso_ref = df_peso.iloc[0]['Peso'] if not df_peso.empty else 80.0
            
            df_filtered_d['Stress_Score'] = df_filtered_d.apply(
                lambda x: metrics_engine.calcular_stress_rodilla(
                    str(x['Tipo']), x['Duracion (min)'], x['Elevacion (m)'], peso_ref
                ), axis=1
            )
            
            col_a, col_b = st.columns([1, 3])
            
            with col_a:
                total_km = df_filtered_d['Distancia (km)'].sum()
                total_carga = df_filtered_d['Stress_Score'].sum()
                sesiones = len(df_filtered_d)
                
                st.metric("Km Totales", f"{round(total_km, 1)} km")
                st.metric("Carga Acumulada", f"{int(total_carga)} pts")
                st.metric("Sesiones", f"{sesiones}")
                
            with col_b:
                fig_bar = px.bar(df_filtered_d, x='Fecha', y='Stress_Score', color='Tipo', 
                                title=f"Impacto en Rodilla ({fecha_inicio_d} - {fecha_fin_d})",
                                text_auto=True)
                st.plotly_chart(fig_bar, width="stretch")
            
            with st.expander("Ver Detalle de Actividades"):
                st.dataframe(df_filtered_d[['Fecha', 'Tipo', 'Distancia (km)', 'Duracion (min)', 'Stress_Score', 'Cadencia_Media']])
                
        else:
            st.info("No hay actividades en el rango seleccionado.")
    else:
        st.info("No hay datos deportivos cargados.")

if __name__ == "__main__":
    main()
