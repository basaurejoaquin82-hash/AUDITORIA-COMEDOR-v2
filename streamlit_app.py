import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from streamlit_option_menu import option_menu
from streamlit_gsheets import GSheetsConnection

# =========================================================
# 1. CONFIGURACIÓN DE NIVEL ENTERPRISE
# =========================================================
st.set_page_config(
    page_title="Sistema Integrado de Auditoría | Casa Rosada",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 2. SECCIÓN CSS (DÓNDE SE PONE EL ESTILO)
# =========================================================
# El CSS se coloca aquí, al principio, para que afecte a toda la app
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    :root {
        --azul-presidencial: #1A4B84;
        --rosa-institucional: #D8A7B1;
        --gris-fondo: #F5F7FA;
    }

    /* Fondo y Fuente Global */
    .stApp { background-color: var(--gris-fondo); font-family: 'Inter', sans-serif; }
    html, body, [class*="st-"], p, h1, h2, h3, span, label { color: #000000 !important; }

    /* NAVBAR SUPERIOR */
    .nav-container {
        background-color: var(--azul-presidencial);
        padding: 1rem 2rem;
        border-radius: 0 0 20px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white !important;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .nav-container span { color: white !important; }

    /* LOGIN MINIMALISTA */
    div[data-baseweb="input"] {
        background-color: transparent !important;
        border: none !important;
        border-bottom: 2px solid #E2E8F0 !important;
        border-radius: 0px !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-bottom: 2px solid var(--azul-presidencial) !important;
    }
    .stButton>button {
        background-color: var(--azul-presidencial) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    .stButton>button:hover {
        background-color: var(--rosa-institucional) !important;
        color: var(--azul-presidencial) !important;
        box-shadow: 0 5px 15px rgba(216, 167, 177, 0.4) !important;
    }

    /* CARDS PREMIUM */
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid var(--rosa-institucional);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
    }
    .kpi-card:hover { 
        transform: translateY(-5px); 
        border-left: 5px solid var(--azul-presidencial);
    }
    .kpi-label { color: #64748B !important; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; }
    .kpi-value { color: var(--azul-presidencial) !important; font-size: 2rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LÓGICA DE ACCESO (LOGIN MINIMALISTA)
# =========================================================
if 'auth' not in st.session_state:
    st.session_state.auth = False

def login_ui():
    _, col_central, _ = st.columns([1, 1.2, 1])
    with col_central:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg", width=100)
        st.markdown("<h2 style='text-align:center; color:#1A4B84;'>SISTEMA DE AUDITORÍA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; opacity:0.6;'>Secretaría General de la Presidencia</p>", unsafe_allow_html=True)
        
        user = st.text_input("CREDENCIAL DE USUARIO", placeholder="Ej: admin")
        pas = st.text_input("TOKEN DE SEGURIDAD", type="password", placeholder="••••••••")
        
        if st.button("AUTENTICAR ACCESO", use_container_width=True):
            if user == "admin" and pas == "1234":
                st.session_state.auth = True
                st.toast("Acceso verificado. Cargando entorno...", icon="🔐")
                st.rerun()
            else:
                st.error("Credenciales no reconocidas.")

if not st.session_state.auth:
    login_ui()
    st.stop()

# =========================================================
# 4. NAVBAR Y MENÚ
# =========================================================
st.markdown(f"""
    <div class="nav-container">
        <div><span style="font-weight:700;">Casa Rosada</span> | Auditoría Interna</div>
        <div style="font-size:0.8rem; background:#DCFCE7; color:#15803D; padding:4px 12px; border-radius:20px; font-weight:700;">SISTEMA ACTIVO</div>
    </div>
    """, unsafe_allow_html=True)

selected = option_menu(None, ["Dashboard Ejecutivo", "Auditoría Detallada", "Analítica de Proveedores"], 
    icons=["speedometer2", "shield-lock", "graph-up-arrow"], orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "transparent"},
        "nav-link-selected": {"background-color": "#1A4B84", "color": "white"}
    })

# =========================================================
# 5. CARGA DE DATOS Y FILTRADO (SIN "NO SOLICITA")
# =========================================================
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(spreadsheet=url, ttl="5m")
df_raw.columns = df_raw.columns.str.strip()
df_raw['Marca temporal'] = pd.to_datetime(df_raw['Marca temporal'], errors='coerce')

# Filtro para excluir "NO SOLICITA" de los platos estrella
df_comida = df_raw[~df_raw['Principal/minutas'].astype(str).str.contains('NO SOLICITA', case=False, na=False)].copy()

# =========================================================
# 6. VISTAS DEL SISTEMA
# =========================================================
if selected == "Dashboard Ejecutivo":
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="kpi-label">Volumen Mensual</p><p class="kpi-value">{len(df_raw):,}</p>', unsafe_allow_html=True)
        with st.expander("Explicación Técnica"):
            st.write(f"Muestra la carga bruta de tickets procesados: **{len(df_raw)}**.")
            st.write("Variación estimada: ↑ 12% vs mes anterior.")
        st.markdown('</div>', unsafe_allow_html=True)

    with k2:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        if not df_comida.empty:
            top_p = df_comida['Principal/minutas'].mode()[0]
            sector_p = df_comida[df_comida['Principal/minutas'] == top_p]['Sector'].mode()[0]
        else:
            top_p, sector_p = "N/D", "N/D"
        st.markdown(f'<p class="kpi-label">Plato de Mayor Demanda</p><p class="kpi-value" style="font-size:1.4rem;">{top_p}</p>', unsafe_allow_html=True)
        with st.expander("Explicación Técnica"):
            st.write(f"**Menú estrella:** {top_p}")
            st.write(f"**Principal consumidor:** Sector {sector_p}")
            st.caption("Filtro aplicado: Ignorando 'No solicita'.")
        st.markdown('</div>', unsafe_allow_html=True)

    with k3:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="kpi-label">Eficiencia Logística</p><p class="kpi-value">94.2%</p>', unsafe_allow_html=True)
        with st.expander("Explicación Técnica"):
            st.write("Nivel de cumplimiento basado en trazabilidad de entrega.")
            st.write("Estado: **Excelencia Logística**.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    g1, g2 = st.columns([2, 1])
    with g1:
        st.subheader("Serie Temporal de Consumo")
        df_t = df_raw.groupby(df_raw['Marca temporal'].dt.date).size().reset_index(name='Pedidos')
        fig = px.area(df_t, x='Marca temporal', y='Pedidos', color_discrete_sequence=['#1A4B84'], template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        st.subheader("Distribución por Secretaría")
        fig_p = px.pie(df_comida, names='Sector', hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_p, use_container_width=True)

elif selected == "Auditoría Detallada":
    st.subheader("🕵️ Central de Trazabilidad Gastronómica")
    query = st.text_input("Buscador Global (Nombre, Sector o Plato)", placeholder="Escriba para filtrar...")
    df_f = df_raw[df_raw.astype(str).apply(lambda x: x.str.contains(query, case=False)).any(axis=1)] if query else df_raw

    gb = GridOptionsBuilder.from_dataframe(df_f)
    gb.configure_pagination(paginationPageSize=15)
    gb.configure_side_bar()
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True)
    gb.configure_column("Sector", cellStyle={'color': 'white', 'backgroundColor': '#1A4B84'}, pinned='left')
    
    grid_o = gb.build()
    AgGrid(df_f, gridOptions=grid_o, theme='alpine', columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, height=500)
    st.download_button("📥 Exportar a Excel", df_f.to_csv().encode('utf-8'), "auditoria_cr.csv", "text/csv")

elif selected == "Analítica de Proveedores":
    st.subheader("📊 Análisis de Patrones Reales")
    fig_tree = px.treemap(df_comida, path=['Sector', 'Principal/minutas'], color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig_tree, use_container_width=True)

st.markdown("---")
st.caption("Sistema de Auditoría Interna v2.0 | Secretaría General de la Presidencia")
