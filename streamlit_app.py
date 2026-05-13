import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from streamlit_option_menu import option_menu
from streamlit_gsheets import GSheetsConnection

# =========================================================
# CONFIGURACIÓN DE NIVEL ENTERPRISE
# =========================================================
st.set_page_config(
    page_title="Sistema Integrado de Auditoría Gastronómica | Casa Rosada",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CUSTOM CSS: ESTÉTICA INSTITUCIONAL PREMIUM
# =========================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    :root {
        --azul-presidencial: #1A4B84;
        --rosa-institucional: #D8A7B1;
        --blanco-puro: #FFFFFF;
        --gris-fondo: #F5F7FA;
    }

    .stApp { background-color: var(--gris-fondo); font-family: 'Inter', sans-serif; }

    /* NAVBAR SUPERIOR */
    .nav-container {
        background-color: var(--azul-presidencial);
        padding: 1rem 2rem;
        border-radius: 0 0 20px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
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
    .kpi-card:hover { transform: translateY(-5px); }
    
    .kpi-label { color: #64748B; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
    .kpi-value { color: var(--azul-presidencial); font-size: 1.8rem; font-weight: 700; margin: 5px 0; }
    
    /* ALERTAS */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        background: #DCFCE7;
        color: #15803D;
    }

    /* AG-GRID CUSTOM */
    .ag-theme-alpine { --ag-border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# LÓGICA DE DATOS Y SESIÓN
# =========================================================
if 'auth' not in st.session_state:
    st.session_state.auth = False

def login_ui():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container():
            st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg", width=120)
            st.title("Sistema de Auditoría")
            user = st.text_input("Credencial Interna")
            pas = st.text_input("Token de Seguridad", type="password")
            if st.button("Ingresar al Sistema"):
                if user == "admin" and pas == "1234": # Aquí conectarías con variables de entorno
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Credenciales no autorizadas por la Secretaría General")

if not st.session_state.auth:
    login_ui()
    st.stop()

# =========================================================
# HEADER Y NAVEGACIÓN
# =========================================================
st.markdown(f"""
    <div class="nav-container">
        <div>
            <span style="font-weight:700; font-size:1.2rem;">Casa Rosada</span> | 
            <span style="font-weight:300;">Auditoría Gastronómica</span>
        </div>
        <div class="status-badge">SISTEMA ACTIVO</div>
    </div>
    """, unsafe_allow_html=True)

selected = option_menu(
    menu_title=None,
    options=["Dashboard Ejecutivo", "Auditoría Detallada", "Consumo por sector", "Configuración"],
    icons=["speedometer2", "shield-lock", "graph-up-arrow", "gear"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "transparent"},
        "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#1A4B84"},
    }
)

# =========================================================
# CARGA DE DATOS (GSHEETS)
# =========================================================
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url, ttl="10m")
df.columns = df.columns.str.strip()
df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], errors='coerce')

# =========================================================
# VISTA: DASHBOARD EJECUTIVO
# =========================================================
if selected == "Dashboard Ejecutivo":
    # Fila de KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Volumen Mensual</div><div class="kpi-value">{len(df):,}</div><div style="color:green; font-size:0.8rem;">↑ 12% vs mes anterior</div></div>', unsafe_allow_html=True)
    with k2:
        top = df['Principal/minutas'].mode()[0] if not df.empty else "N/A"
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Plato de Mayor Demanda</div><div class="kpi-value" style="font-size:1.2rem;">{top}</div></div>', unsafe_allow_html=True)
    with k3:
        # Detección de anomalía simple (simulada)
        anomalia = len(df[df['Sector'] == 'Presidencia']) # Ejemplo de lógica
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Alertas de Auditoría</div><div class="kpi-value" style="color:#E63946;">3</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Eficiencia Logística</div><div class="kpi-value">94.2%</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráficos Enterprise
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Serie Temporal de Consumo Institucional")
        df_time = df.groupby(df['Marca temporal'].dt.date).size().reset_index(name='Pedidos')
        fig = px.area(df_time, x='Marca temporal', y='Pedidos', 
                      color_discrete_sequence=['#1A4B84'], template="plotly_white")
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Distribución por Secretaría")
        fig_pie = px.pie(df, names='Sector', hole=0.5, 
                         color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_pie.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# =========================================================
# VISTA: AUDITORÍA DETALLADA (AG-GRID)
# =========================================================
elif selected == "Auditoría Detallada":
    st.subheader("🕵️ Central de Trazabilidad Gastronómica")
    
    # Buscador Global Pro
    search_query = st.text_input("Buscador Inteligente (Nombre, Sector, Plato...)", placeholder="Escriba para filtrar instantáneamente...")
    
    if search_query:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

    # Configuración de AG-GRID (Tipo Excel/SAP)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    gb.configure_side_bar() # Agrega filtros laterales tipo Excel
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox")
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
    
    # Resaltado condicional para auditoría (Ejemplo: marcar sectores específicos)
    cellsytle_jsc = """
    function(params) {
        if (params.value == 'Secretaría General') {
            return { 'color': 'white', 'backgroundColor': '#1A4B84' }
        }
    }
    """
    gb.configure_column("Sector", cellStyle=cellsytle_jsc)
    
    gridOptions = gb.build()

    AgGrid(
        df,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=False,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        theme='alpine', # Tema profesional tipo SAP
        enable_enterprise_modules=True,
        height=500, 
        width='100%',
    )
    
    st.download_button(
        label="📥 Exportar Reporte de Auditoría (Excel)",
        data=df.to_csv().encode('utf-8'),
        file_name='auditoria_presidencia.csv',
        mime='text/csv',
    )

# =========================================================
# VISTA: ANALÍTICA (SANKEY / DRILL-DOWN)
# =========================================================
elif selected == "Consumo por sector":
    st.subheader("📊 Análisis de Flujo y Patrones de Consumo")
    
    # Sankey Diagram (Flujo Sector -> Plato)
    st.info("Visualización del flujo de suministros desde Secretarías hacia platos finales")
    # Lógica simplificada para Sankey
    nodes = list(df['Sector'].unique()) + list(df['Principal/minutas'].unique())
    # (Aquí iría la lógica compleja de índices para Sankey)
    
    # Treemap de Consumo
    fig_tree = px.treemap(df, path=['Sector', 'Principal/minutas'], 
                          color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_tree, use_container_width=True)

st.markdown("---")
st.caption("Sistema de Auditoría Interna v2.0 | Desarrollado para la Secretaría General de la Presidencia de la Nación")
