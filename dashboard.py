# dashboard.py - Bio-Engine Gonzalo (Versión Optimizada Final)
import streamlit as st
import pandas as pd
import config
import os
import altair as alt
import datetime
import cloud_sync
import super_merger
import json
import io
import dashboard_components
import visualizations
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


# ============================================
# AUTHENTICATION LAYER
# ============================================
# Load credentials from Streamlit secrets or local file
try:
    # Try Streamlit Cloud secrets first
    # Secrets come as a nested dict, we need to extract properly
    credentials_dict = {
        "usernames": dict(st.secrets["credentials"]["usernames"])
    }
except:
    # Fallback to local file for development
    try:
        with open('.streamlit/credentials.yaml') as file:
            config_data = yaml.load(file, Loader=SafeLoader)
            credentials_dict = config_data
    except:
        # Create default if not exists
        credentials_dict = {
            "usernames": {
                "gonzalo": {
                    "name": "Gonzalo Obispo",
                    "password": "$2b$12$PLACEHOLDER"  # This will be replaced
                }
            }
        }

authenticator = stauth.Authenticate(
    credentials_dict,
    'bioengine_cookie',
    'bioengine_signature_key',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login(fields={'Form name': 'Acceso BioEngine'})

if authentication_status == False:
    st.error('Usuario/Contraseña incorrectos')
    st.stop()
elif authentication_status == None:
    st.warning('Por favor ingresa tu usuario y contraseña')
    st.stop()

# If authenticated, show logout button in sidebar
authenticator.logout('Cerrar Sesión', 'sidebar')
st.sidebar.write(f'Bienvenido *{name}*')

# ============================================
# MAIN DASHBOARD (Only shown if authenticated)
# ============================================

# Parse mixed date formats (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
def _parse_fecha_mixta(series):
    series = series.astype(str).str.strip()
    parsed = pd.to_datetime(series, format='%Y-%m-%d %H:%M:%S', errors='coerce')
    return parsed.fillna(pd.to_datetime(series, format='%Y-%m-%d', errors='coerce'))

def _parse_num_es(series):
    s = series.astype(str).str.strip()
    s = s.replace('', pd.NA)
    has_comma = s.str.contains(',', na=False)
    s = s.where(~has_comma, s.str.replace('.', '', regex=False).str.replace(',', '.', regex=False))
    return pd.to_numeric(s, errors='coerce')

def _format_num_es(value, decimals=2):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"
    try:
        num = float(value)
    except Exception:
        return str(value)
    if decimals == 0:
        s = f"{int(round(num)):,}"
    else:
        s = f"{num:,.{decimals}f}"
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')

def _format_df_numbers_es(df, columns, decimals=2):
    if df.empty:
        return df
    df_out = df.copy()
    for col in columns:
        if col in df_out.columns:
            df_out[col] = df_out[col].map(lambda v: _format_num_es(v, decimals=decimals))
    return df_out

def _format_df_numbers_es_map(df, column_decimals):
    if df.empty:
        return df
    df_out = df.copy()
    for col, decimals in column_decimals.items():
        if col in df_out.columns:
            df_out[col] = df_out[col].map(lambda v: _format_num_es(v, decimals=decimals))
    return df_out

def _normalize_fuente_label(value):
    v = str(value).strip()
    if v in ('Pesobook (Histórico)', 'PesoBook (Histórico)'):
        return 'Pesobook'
    if v.startswith('Apple CDA') or v.startswith('Apple Health'):
        return 'Apple'
    return v

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Bio-Engine Gonzalo", layout="wide", page_icon="🧬")

# Compactar sidebar y botones
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] { width: 240px !important; }
    section[data-testid="stSidebar"] .stButton>button {
        padding: 0.2rem 0.6rem;
        font-size: 0.85rem;
        min-height: 1.6rem;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stText,
    section[data-testid="stSidebar"] label {
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sincronización automática al abrir (solo datos de APIs)
# @st.cache_data(ttl=300)  # Deshabilitado para testing
def sync_and_load_data():
    with st.spinner("Sincronizando datos frescos de APIs..."):
        result = cloud_sync.sincronizar_todo()
        if "Sin datos nuevos" in result:
            st.session_state["api_sync_notice"] = ("info", "No hay datos nuevos en las APIs.")
        else:
            st.session_state["api_sync_notice"] = ("success", f"Sincronizaci¢n completada: {result}")
        # Fusionar datos después de sincronización
        super_merger.actualizacion_rapida()
    
    # Cargar datos frescos (APIs + maestro completo)
    try:
        df_p_apis = pd.read_csv(config.CSV_PESO_MAESTRO_APIS, sep=';') if os.path.exists(config.CSV_PESO_MAESTRO_APIS) else pd.DataFrame()
        df_p_full = pd.read_csv(config.CSV_PESO_MAESTRO, sep=';') if os.path.exists(config.CSV_PESO_MAESTRO) else pd.DataFrame()
        df_s = pd.read_csv(config.CSV_DEPORTE_MAESTRO, sep=';') if os.path.exists(config.CSV_DEPORTE_MAESTRO) else pd.DataFrame()
        if not df_p_apis.empty:
            df_p_apis['Fecha'] = _parse_fecha_mixta(df_p_apis['Fecha'])
            if 'Peso' in df_p_apis.columns:
                df_p_apis['Peso'] = _parse_num_es(df_p_apis['Peso'])
        if not df_p_full.empty:
            df_p_full['Fecha'] = _parse_fecha_mixta(df_p_full['Fecha'])
            if 'Peso' in df_p_full.columns:
                df_p_full['Peso'] = _parse_num_es(df_p_full['Peso'])
            for col in ['Grasa_Pct', 'Masa_Muscular_Kg']:
                if col in df_p_full.columns:
                    df_p_full[col] = _parse_num_es(df_p_full[col])
        if not df_s.empty:
            df_s['Fecha'] = _parse_fecha_mixta(df_s['Fecha'])
            for col in ['Distancia (km)', 'Duracion (min)', 'Calorias']:
                if col in df_s.columns:
                    df_s[col] = _parse_num_es(df_s[col])
        print(f"Debug: Peso APIs tiene {len(df_p_apis)} registros, fecha máxima: {df_p_apis['Fecha'].max() if not df_p_apis.empty else 'N/A'}")
        print(f"Debug: Peso maestro tiene {len(df_p_full)} registros, fecha máxima: {df_p_full['Fecha'].max() if not df_p_full.empty else 'N/A'}")
        return df_p_apis, df_p_full, df_s
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

st.title("🧬 Bio-Engine: Inteligencia Biomecánica")

# Ejecutar sincronización automática
df_peso_apis, df_peso_full, df_sport = sync_and_load_data()

# --- 2. BARRA LATERAL ---
st.sidebar.header("🔄 Sincronización")
if st.sidebar.button("🔄 Sincronizar"):
    with st.spinner("Forzando actualización completa..."):
        result = cloud_sync.sincronizar_todo()
        super_merger.actualizacion_rapida()
        st.sidebar.success(f"Actualización forzada: {result}")
    st.rerun()

if st.sidebar.button("🗑️ Resetear"):
    with st.spinner("Reseteando datos..."):
        import os
        # Borrar solo archivos de APIs (mantener historicos)
        files_to_delete = [
            config.CSV_PESO_MAESTRO_APIS,
            os.path.join(config.DATA_PROCESSED, 'historial_withings_raw.csv'),
            os.path.join(config.DATA_PROCESSED, 'historial_garmin_raw.csv'),
            os.path.join(config.DATA_PROCESSED, 'historial_deportivo_total_full.csv')
        ]
        for file in files_to_delete:
            if os.path.exists(file):
                os.remove(file)
        st.sidebar.success("Datos reseteados. Sincroniza para recargar.")
    st.rerun()

st.sidebar.divider()
st.sidebar.header("🎛️ Filtros de Auditoría")
min_candidates = []
max_candidates = []
if not df_sport.empty and 'Fecha' in df_sport.columns:
    min_candidates.append(df_sport['Fecha'].min())
    max_candidates.append(df_sport['Fecha'].max())
if not df_peso_apis.empty and 'Fecha' in df_peso_apis.columns:
    min_candidates.append(df_peso_apis['Fecha'].min())
    max_candidates.append(df_peso_apis['Fecha'].max())
if not df_peso_full.empty and 'Fecha' in df_peso_full.columns:
    min_candidates.append(df_peso_full['Fecha'].min())
    max_candidates.append(df_peso_full['Fecha'].max())
min_date = min(min_candidates).date() if min_candidates else datetime.date(2024, 1, 1)
max_date = max(max_candidates).date() if max_candidates else datetime.date.today()
if max_date < datetime.date.today():
    max_date = datetime.date.today()

prefs_path = os.path.join(config.BASE_DIR, 'user_prefs.json')
prefs = {}
if os.path.exists(prefs_path):
    try:
        with open(prefs_path, 'r', encoding='utf-8') as f:
            prefs = json.load(f)
    except Exception:
        prefs = {}

default_start = min_date
default_end = datetime.date.today()
saved_start = prefs.get('start_date')
saved_end = prefs.get('end_date')
if saved_start:
    try:
        default_start = datetime.date.fromisoformat(saved_start)
    except ValueError:
        default_start = min_date
if saved_end:
    try:
        default_end = datetime.date.fromisoformat(saved_end)
    except ValueError:
        default_end = max_date

start_date = st.sidebar.date_input(
    "Analizar desde",
    value=default_start,
    min_value=min_date,
    max_value=max_date,
    key="start_date",
    format="DD/MM/YYYY",
)
end_date = st.sidebar.date_input(
    "Hasta",
    value=default_end,
    min_value=min_date,
    max_value=max_date,
    key="end_date",
    format="DD/MM/YYYY",
)

if st.session_state.get("start_date"):
    prefs['start_date'] = st.session_state["start_date"].isoformat()
if st.session_state.get("end_date"):
    prefs['end_date'] = st.session_state["end_date"].isoformat()
try:
    with open(prefs_path, 'w', encoding='utf-8') as f:
        json.dump(prefs, f)
except Exception:
    pass

# Aplicar filtros (proteger cuando no hay columna Fecha)
if not df_sport.empty and 'Fecha' in df_sport.columns:
    df_s_f = df_sport[(df_sport['Fecha'].dt.date >= start_date) & (df_sport['Fecha'].dt.date <= end_date)].sort_values('Fecha', ascending=False)
else:
    df_s_f = pd.DataFrame()

if not df_peso_apis.empty and 'Fecha' in df_peso_apis.columns:
    df_p_f_apis = df_peso_apis[(df_peso_apis['Fecha'].dt.date >= start_date) & (df_peso_apis['Fecha'].dt.date <= end_date)].sort_values('Fecha')
else:
    df_p_f_apis = pd.DataFrame()

if not df_peso_full.empty and 'Fecha' in df_peso_full.columns:
    df_p_f_full = df_peso_full[(df_peso_full['Fecha'].dt.date >= start_date) & (df_peso_full['Fecha'].dt.date <= end_date)].sort_values('Fecha')
else:
    df_p_f_full = pd.DataFrame()

# --- 3. RENDERIZADO DE SECCIONES DINÁMICAS ---
if not df_s_f.empty and (not df_p_f_apis.empty or not df_p_f_full.empty):
    # Obtener último peso para el header
    df_p_sorted = df_p_f_full.dropna(subset=['Fecha']).sort_values('Fecha')
    last_p = df_p_sorted.iloc[-1]['Peso'] if not df_p_sorted.empty else 76.0
    last_p_date = df_p_sorted.iloc[-1]['Fecha'].strftime('%d/%m/%y') if not df_p_sorted.empty else 'N/A'

    # 1. Header de KPIs
    dashboard_components.render_kpi_header(df_s_f, df_p_f_full, last_p, last_p_date)

    # 2. Coach Personal (Asistente de Recuperación Proactivo)
    from trainer_assistant import TrainerAssistant
    assistant = TrainerAssistant()
    
    # a) Pestañas del Asistente
    tab_coach, tab_plan, tab_timeline, tab_chat = st.tabs(["💡 Estado y Consejos", "📅 Plan Semanal", "⏳ Bio-Timeline", "💬 Chat Coach"])
    
    with tab_coach:
        dashboard_components.render_trainer_assistant(assistant, df_s_f, df_p_f_full)
        with st.expander("Ver Perfil Clínico e Historial Médico"):
            dashboard_components.render_medical_profile()
            
    with tab_plan:
        dashboard_components.render_weekly_plan(assistant)

    with tab_timeline:
        dashboard_components.render_bio_timeline_section(df_sport, assistant)
        
    with tab_chat:
        dashboard_components.render_coach_chat(assistant)

    # 3. Salud de Rodilla (Plotly interactivo)
    # Mostramos la evolución completa para contexto, o filtrada según prefiera el usuario
    dashboard_components.render_knee_health_section(df_s_f, df_p_f_full)

    # 4. Gestión de Calzado (Barras de progreso)
    # Usamos df_sport completo (sin filtrar por fecha) para ver el desgaste histórico acumulado
    dashboard_components.render_shoe_management(df_sport)

    # 5. ROI y Eficiencia
    dashboard_components.render_roi_section(df_s_f)

    # 6. Datos Crudos y Exportación (Sección compacta)
    st.divider()
    st.header("🏃 Auditoría de Datos y Calendario")
    with st.expander("Ver Historial de Pesos y Sesiones"):
        t1, t2 = st.tabs(["Historial de Peso", "Sesiones Deportivas"])
        with t1:
            st.dataframe(df_p_f_full.sort_values('Fecha', ascending=False), hide_index=True)
        with t2:
            st.dataframe(df_s_f.sort_values('Fecha', ascending=False), hide_index=True)
            
else:
    st.warning("⚠️ No hay datos suficientes para el rango seleccionado. Por favor, amplía el filtro en la barra lateral o sincroniza la nube.")




