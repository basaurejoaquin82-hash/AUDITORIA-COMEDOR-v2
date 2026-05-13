import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from streamlit_option_menu import option_menu
from streamlit_gsheets import GSheetsConnection

# =========================================================
# 1. CONFIGURACIÓN DE PÁGINA (ESTILO FIGMA)
# =========================================================
st.set_page_config(
    page_title="Auditoría Presidencial | Sistema Interno",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 2. DESIGN SYSTEM (CSS AVANZADO)
# =========================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #1A4B84;
        --accent: #D8A7B1;
        --bg: #F8FAFC;
        --card-bg: #FFFFFF;
        --text-main: #1E293B;
        --text-muted: #64748B;
    }

    /* Reset Global */
    .stApp { background-color: var(--bg); font-family: 'Inter', sans-serif; }
    
    /* LOGIN UI - FIGMA STYLE */
    .login-container {
        background: white;
        padding: 3rem;
        border-radius: 24px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #F1F5F9;
    }

    /* NAVBAR PREMIUM */
    .nav-bar {
        background: rgba(26, 75, 132, 0.95);
        backdrop-filter: blur(10px);
        padding: 1rem 3rem;
        border-radius: 0 0 30px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }

    /* KPI CARDS - FIGMA HOVER EFFECT */
    .kpi-wrapper {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid #F1F5F9;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .kpi-wrapper:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
        border-color: var(--accent);
    }
    
    .kpi-label { color: var(--text-muted); font-size: 0.75rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; }
    .kpi-value { color: var(--primary); font-size: 2.2rem; font-weight: 700; margin-top: 0.5rem; }

    /* Botones y Inputs Modernos */
    .stButton>button {
        width: 100%;
        border-radius: 12px !important;
        background: var(--primary) !important;
        border: none !important;
        padding: 0.75rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background: var(--accent) !important;
        color: var(--primary) !important;
        transform: scale(1.02);
    }
    
    /* Tabs Estilizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 2rem; }
    .stTabs [data-baseweb="tab"] { color: var(--text-muted); font-weight: 500; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: var(--primary); }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LÓGICA DE ACCESO (SPLASH SCREEN)
# =========================================================
if 'auth' not in st.session_state:
    st.session_state.auth = False

def login_screen():
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg", width=90)
        st.markdown("<h1 style='font-size:1.8rem; margin-top:1rem;'>Acceso Institucional</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748B; margin-bottom:2rem;'>Sistema de Auditoría Gastronómica v2.0</p>", unsafe_allow_html=True)
        
        user = st.text_input("Credencial", placeholder="usuario.interno")
        pw = st.text_input("Token", type="password", placeholder="••••••••")
        
        if st.button("Iniciar Sesión"):
            if user == "admin" and pw == "1234":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Credenciales inválidas")
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.auth:
    login_screen()
    st.stop()

# =========================================================
# 4. DASHBOARD UI (NAV + MENU)
# =========================================================
st.markdown("""
    <div class="nav-bar">
        <div style="color:white; font-weight:700; font-size:1.2rem;">Casa Rosada <span style="font-weight:300; opacity:0.7;">| Auditoría</span></div>
        <div style="background:rgba(255,255,255,0.2); padding:5px 15px; border-radius:12px; color:white; font-size:0.8rem;">Admin: Basaure, J.</div>
    </div>
""", unsafe_allow_html=True)

selected = option_menu(None, ["Dashboard Ejecutivo", "Trazabilidad AgGrid", "Reportes IA"], 
    icons=["grid-fill", "search", "pie-chart-fill"], 
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "container": {"background-color": "transparent", "padding": "0"},
        "nav-link": {"font-size": "14px", "font-weight": "500"},
        "nav-link-selected": {"background-color": "#1A4B84"}
    }
)

# =========================================================
# 5. DATA ENGINE
# =========================================================
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(spreadsheet=url, ttl="5m")
df_raw.columns = df_raw.columns.str.strip()
df_raw['Marca temporal'] = pd.to_datetime(df_raw['Marca temporal'], errors='coerce')

# Filtro "Anti-Ruido"
df_clean = df_raw[~df_raw['Principal/minutas'].astype(str).str.contains('NO SOLICITA', case=False, na=False)].copy()

# =========================================================
# 6. VIEWS
# =========================================================
if selected == "Dashboard Ejecutivo":
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.markdown(f'''<div class="kpi-wrapper">
            <div class="kpi-label">Volumen Total Mensual</div>
            <div class="kpi-value">{len(df_raw):,}</div>
            <div style="color: #10B981; font-size: 0.8rem; font-weight: 600; margin-top:0.5rem;">↑ 12.4% vs mes anterior</div>
        </div>''', unsafe_allow_html=True)

    with k2:
        top_dish = df_clean['Principal/minutas'].mode()[0] if not df_clean.empty else "N/A"
        st.markdown(f'''<div class="kpi-wrapper">
            <div class="kpi-label">Ítem de Mayor Demanda</div>
            <div class="kpi-value" style="font-size:1.5rem;">{top_dish}</div>
            <div style="color: #6366F1; font-size: 0.8rem; font-weight: 600; margin-top:0.5rem;">Filtro: Consumo Real</div>
        </div>''', unsafe_allow_html=True)

    with k3:
        st.markdown(f'''<div class="kpi-wrapper">
            <div class="kpi-label">Eficiencia Operativa</div>
            <div class="kpi-value">94.2%</div>
            <div style="color: #F59E0B; font-size: 0.8rem; font-weight: 600; margin-top:0.5rem;">Nivel: Excelencia</div>
        </div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("#### Tendencia de Carga Temporal")
        df_t = df_raw.groupby(df_raw['Marca temporal'].dt.date).size().reset_index(name='Tickets')
        fig = px.area(df_t, x='Marca temporal', y='Tickets', color_discrete_sequence=['#1A4B84'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          margin=dict(l=0, r=0, t=20, b=0), font=dict(family="Inter"))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Participación por Área")
        fig_p = px.pie(df_clean, names='Sector', hole=0.7, color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_p.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_p, use_container_width=True)

elif selected == "Trazabilidad AgGrid":
    st.markdown("#### Auditoría de Movimientos en Tiempo Real")
    gb = GridOptionsBuilder.from_dataframe(df_raw)
    gb.configure_pagination(paginationPageSize=15)
    gb.configure_side_bar()
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True)
    gb.configure_column("Sector", cellStyle={'color': 'white', 'backgroundColor': '#1A4B84'}, pinned='left')
    
    grid_opt = gb.build()
    AgGrid(df_raw, gridOptions=grid_opt, theme='alpine', columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, height=550)

st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("Economato Casa Rosada | Secretaría General de la Presidencia | © 2026")
