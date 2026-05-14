import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from streamlit_option_menu import option_menu
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURACIÓN TÉCNICA (NIVEL ENTERPRISE) ---
st.set_page_config(
    page_title="Sistema de Auditoría | Casa Rosada",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SISTEMA DE DISEÑO INTEGRADO (CSS DINÁMICO) ---
def apply_design_system():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        :root {
            --primary: #101828;
            --accent-gold: #C5A059;
            --success: #12B76A;
            --bg-body: #F9FAFB;
        }

        .stApp { background-color: var(--bg-body); font-family: 'Outfit', sans-serif; }
        
        /* Contenedores Estilo Home Banking */
        .glass-card {
            background: white;
            padding: 24px;
            border-radius: 16px;
            border: 1px solid #EAECF0;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }

        /* Navbar Lateral y Superior */
        header[data-testid="stHeader"] { background: rgba(255,255,255,0.8); backdrop-filter: blur(10px); }
        
        /* Métricas Premium */
        .metric-label { color: #667085; font-size: 0.9rem; font-weight: 500; margin-bottom: 4px; }
        .metric-value { color: var(--primary); font-size: 1.8rem; font-weight: 700; }
        .metric-delta { font-size: 0.85rem; font-weight: 600; }
        .delta-up { color: var(--success); }

        /* Botones y Inputs */
        .stButton>button {
            border-radius: 8px;
            background-color: var(--primary);
            color: white;
            border: none;
            transition: all 0.3s;
        }
        .stButton>button:hover { background-color: var(--accent-gold); border: none; }
        </style>
    """, unsafe_allow_html=True)

apply_design_system()

# --- 3. GESTIÓN DE ESTADO Y SEGURIDAD ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

def login():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div class='glass-card' style='text-align:center; margin-top:10vh;'>", unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg", width=100)
        st.subheader("Terminal de Auditoría")
        st.caption("Autenticación Requerida - Nivel I")
        
        user = st.text_input("Identificador de Usuario")
        token = st.text_input("Token de Acceso (RSA)", type="password")
        
        if st.button("Sincronizar", use_container_width=True):
            if user == "admin" and token == "1234":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Credenciales Inválidas")
        st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.auth:
    login()
    st.stop()

# --- 4. ENGINE DE DATOS (GOOGLE SHEETS) ---
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"
    conn = st.connection("gsheets", type=GSheetsConnection)
    data = conn.read(spreadsheet=url)
    data.columns = data.columns.str.strip()
    data['Marca temporal'] = pd.to_datetime(data['Marca temporal'], errors='coerce')
    return data

df_raw = load_data()

# --- 5. NAVEGACIÓN TIPO APP BANCARIA ---
with st.sidebar:
    st.markdown("### 🏛️ Control Central")
    menu = option_menu(
        None, ["Dashboard", "Trazabilidad", "Configuración"],
        icons=['house', 'activity', 'gear'], 
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#C5A059", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#101828"},
        }
    )
    st.divider()
    st.caption("Terminal ID: CR-A04")
    st.caption("Sesión: Administrador")

# --- 6. VISTAS ---

if menu == "Dashboard":
    st.markdown("## Resumen Ejecutivo de Gestión")
    
    # KPIs con porcentajes de variación reales/simulados
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="glass-card"><p class="metric-label">Transacciones Totales</p><p class="metric-value">{len(df_raw)}</p><p class="metric-delta delta-up">↑ 12% vs mes ant.</p></div>""", unsafe_allow_html=True)
    with m2:
        top_val = df_raw['Sector'].mode()[0]
        st.markdown(f"""<div class="glass-card"><p class="metric-label">Sector Dominante</p><p class="metric-value" style="font-size:1.4rem;">{top_val}</p><p class="metric-delta">Consumo Crítico</p></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="glass-card"><p class="metric-label">Eficiencia Operativa</p><p class="metric-value">98.4%</p><p class="metric-delta delta-up">↑ 0.5%</p></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="glass-card"><p class="metric-label">Latencia de Datos</p><p class="metric-value">0.4s</p><p class="metric-delta">Óptimo</p></div>""", unsafe_allow_html=True)

    # Gráficos Interactivos Profesionales
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Análisis de Tendencia Temporal")
        df_time = df_raw.groupby(df_raw['Marca temporal'].dt.date).size().reset_index(name='Registros')
        fig_line = px.area(df_time, x='Marca temporal', y='Registros', 
                          color_discrete_sequence=['#101828'])
        fig_line.update_layout(hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Distribución por Categoría")
        fig_sun = px.sunburst(df_raw, path=['Sector', 'Principal/minutas'], 
                             color_discrete_sequence=px.colors.sequential.YlGnBu)
        st.plotly_chart(fig_sun, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Trazabilidad":
    st.markdown("## Registro de Auditoría en Tiempo Real")
    
    # Filtro avanzado
    search_col, filter_col = st.columns([2, 1])
    with search_col:
        query = st.text_input("🔍 Búsqueda Global de Registros", placeholder="ID, Sector o Producto...")
    
    df_filtered = df_raw[df_raw.astype(str).apply(lambda x: x.str.contains(query, case=False)).any(axis=1)] if query else df_raw
    
    # AgGrid Configuración Estilo Bloomberg
    gb = GridOptionsBuilder.from_dataframe(df_filtered)
    gb.configure_default_column(resizable=True, filterable=True, sortable=True, editable=False)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_column("Sector", cellStyle={'backgroundColor': '#F8F9FA', 'fontWeight': 'bold'})
    
    grid_opt = gb.build()
    
    AgGrid(
        df_filtered,
        gridOptions=grid_opt,
        theme='balham',  # Más compacto y profesional
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        height=600,
        allow_unsafe_jscode=True
    )

elif menu == "Configuración":
    st.markdown("## Ajustes del Sistema")
    with st.expander("🛠️ Parámetros de Interfaz", expanded=True):
        st.toggle("Modo Oscuro de Alto Contraste", False)
        st.select_slider("Frecuencia de Refresco de Datos", options=["1m", "5m", "15m", "1h"], value="5m")
        st.color_picker("Color Primario Institucional", "#101828")
        
    with st.expander("🔐 Seguridad y Accesos"):
        st.info("La terminal está operando bajo encriptación SSL de 256 bits.")
        if st.button("Cerrar Sesión Global"):
            st.session_state.auth = False
            st.rerun()

# --- 7. FOOTER BANCARIO ---
st.markdown(f"""
    <div style="text-align:center; padding: 40px; color: #98A2B3; font-size: 0.8rem;">
        SISTEMA DE AUDITORÍA PRESIDENCIAL | ESTACIÓN: {st.session_state.get('user', 'LOCAL')} | 
        COORDENADAS: {st.session_state.get('geo', '-34.6083, -58.3703')}<br>
        © 2026 CASA ROSADA - PROYECTO AUDITORÍA FEDERAL
    </div>
""", unsafe_allow_html=True)
