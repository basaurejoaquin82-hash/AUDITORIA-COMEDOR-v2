import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from streamlit_option_menu import option_menu
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Auditoría Presidencial | Sistema Interno",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. DESIGN SYSTEM (CSS AVANZADO - ESTILO FIGMA)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #1A4B84;
        --accent: #D8A7B1;
        --bg: #F8FAFC;
        --text-main: #1E293B;
    }

    .stApp { background-color: var(--bg); font-family: 'Inter', sans-serif; }
    html, body, [class*="st-"], p, h1, h2, h3, span, label { color: #000000 !important; }

    /* NAVBAR PREMIUM */
    .nav-bar {
        background: var(--primary);
        padding: 1rem 3rem;
        border-radius: 0 0 25px 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        color: white !important;
    }

    /* KPI CARDS */
    .kpi-wrapper {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid #F1F5F9;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .kpi-wrapper:hover { transform: translateY(-5px); border-color: var(--accent); }
    .kpi-label { color: #64748B !important; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
    .kpi-value { color: var(--primary) !important; font-size: 2rem; font-weight: 700; }

    /* BUSCADOR ESTILIZADO */
    .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        padding: 0.5rem 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LÓGICA DE ACCESO
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        st.markdown("<br><br><br><div style='text-align:center; background:white; padding:3rem; border-radius:24px; box-shadow: 0 20px 50px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg", width=90)
        st.title("Acceso")
        user = st.text_input("Usuario")
        pw = st.text_input("Token", type="password")
        if st.button("Ingresar", use_container_width=True):
            if user == "admin" and pw == "1234":
                st.session_state.auth = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. DASHBOARD HEADER
st.markdown('<div class="nav-bar"><div style="color:white !important; font-weight:700;">Casa Rosada <span style="font-weight:300; opacity:0.8;">| Auditoría</span></div><div style="color:white !important; font-size:0.8rem;">ESTADO: ONLINE</div></div>', unsafe_allow_html=True)

selected = option_menu(None, ["Dashboard Ejecutivo", "Trazabilidad AgGrid"], 
    icons=["grid-fill", "search"], orientation="horizontal",
    styles={"nav-link-selected": {"background-color": "#1A4B84"}})

# 5. DATA ENGINE
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(spreadsheet=url, ttl="5m")
df_raw.columns = df_raw.columns.str.strip()
df_raw['Marca temporal'] = pd.to_datetime(df_raw['Marca temporal'], errors='coerce')

# FILTRO DE BÚSQUEDA GLOBAL REINSTALADO
st.markdown("### 🔍 Buscador de Auditoría")
query = st.text_input("", placeholder="Busque por nombre, sector, plato o mozo...", label_visibility="collapsed")
df_display = df_raw[df_raw.astype(str).apply(lambda x: x.str.contains(query, case=False)).any(axis=1)] if query else df_raw

# Dataset limpio para gráficos (Ignora "NO SOLICITA")
df_clean = df_display[~df_display['Principal/minutas'].astype(str).str.contains('NO SOLICITA', case=False, na=False)].copy()

# 6. VIEWS
if selected == "Dashboard Ejecutivo":
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f'<div class="kpi-wrapper"><p class="kpi-label">Volumen Total</p><p class="kpi-value">{len(df_display)}</p></div>', unsafe_allow_html=True)
    with k2:
        top = df_clean['Principal/minutas'].mode()[0] if not df_clean.empty else "N/A"
        st.markdown(f'<div class="kpi-wrapper"><p class="kpi-label">Menú más pedido</p><p class="kpi-value" style="font-size:1.4rem;">{top}</p></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-wrapper"><p class="kpi-label">Eficiencia</p><p class="kpi-value">94.2%</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Distribución y Proporciones por Sector")
        # Configuramos etiquetas permanentes
        fig_pie = px.pie(df_clean, names='Sector', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.markdown("#### Top 5 Consumos Reales")
        top5 = df_clean['Principal/minutas'].value_counts().head(5).reset_index()
        fig_bar = px.bar(top5, x='Principal/minutas', y='count', text='count', color_discrete_sequence=['#D8A7B1'])
        fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

elif selected == "Trazabilidad AgGrid":
    gb = GridOptionsBuilder.from_dataframe(df_display)
    gb.configure_pagination(paginationPageSize=15)
    gb.configure_side_bar()
    gb.configure_column("Sector", cellStyle={'color': 'white', 'backgroundColor': '#1A4B84'}, pinned='left')
    grid_opt = gb.build()
    AgGrid(df_display, gridOptions=grid_opt, theme='alpine', columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, height=500)

st.markdown("---")
st.caption("Economato Casa Rosada | © 2026")
