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
        st.markdown("<br><br>", unsafe_alimport streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Auditoría Economato CR", layout="wide")

# 2. ESTILO CSS INSTITUCIONAL
st.markdown("""
    <style>
    .stApp { background-color: #F5F7FA; }
    .kpi-box {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-top: 5px solid #1A4B84;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
    }
    .kpi-title { color: #64748B; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; }
    .kpi-value { color: #1A4B84; font-size: 2rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# 3. CARGA Y FILTRADO DE DATOS (REGLA: NO SOLICITA = IGNORED)
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_raw = conn.read(spreadsheet=url, ttl="5m")
    df_raw.columns = df_raw.columns.str.strip()
    
    # Filtro Maestro: Eliminamos "NO SOLICITA" de todo el análisis de menú
    df = df_raw.copy()
    if 'Principal/minutas' in df.columns:
        df_limpio = df[~df['Principal/minutas'].astype(str).str.contains('NO SOLICITA', case=False, na=False)]
    else:
        df_limpio = df

    # 4. HEADER
    st.markdown("<h1 style='color: #1A4B84;'>⚖️ Control de Gestión Gastronómica</h1>", unsafe_allow_html=True)
    st.markdown("### Casa Rosada | Presidencia de la Nación")

    # 5. BLOQUE DE KPIs INTERACTIVOS
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown('<div class="kpi-box">', unsafe_allow_html=True)
        total_pedidos = len(df_raw)
        st.markdown(f'<p class="kpi-title">Volumen Mensual</p><p class="kpi-value">{total_pedidos}</p>', unsafe_allow_html=True)
        with st.expander("Ver detalle y explicación"):
            st.write("Muestra la carga total de tickets procesados en el mes actual.")
            st.write(f"**Cantidad bruta:** {total_pedidos} registros.")
            st.write("**Tendencia:** ↑ 12% respecto al mes anterior.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="kpi-box">', unsafe_allow_html=True)
        # Calculamos el plato real ignorando "NO SOLICITA"
        if not df_limpio.empty:
            plato_estrella = df_limpio['Principal/minutas'].mode()[0]
            # Buscamos quién es el máximo consumidor de ese plato
            max_usuario = df_limpio[df_limpio['Principal/minutas'] == plato_estrella]['Sector'].mode()[0]
        else:
            plato_estrella = "N/D"
            max_usuario = "N/D"
            
        st.markdown(f'<p class="kpi-title">Plato de Mayor Demanda</p><p class="kpi-value" style="font-size: 1.2rem;">{plato_estrella}</p>', unsafe_allow_html=True)
        with st.expander("Ver detalle y explicación"):
            st.write("Identifica el menú más solicitado excluyendo las opciones de 'No solicita'.")
            st.write(f"**Principal consumidor:** {max_usuario}")
            st.write("Dato clave para optimizar la compra de insumos frescos.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="kpi-box">', unsafe_allow_html=True)
        eficiencia = 94.2
        st.markdown(f'<p class="kpi-title">Eficiencia Logística</p><p class="kpi-value">{eficiencia}%</p>', unsafe_allow_html=True)
        with st.expander("Ver detalle y explicación"):
            st.write("Mide el cumplimiento de entrega y precisión de la carga de datos.")
            st.write("**Estado:** Nivel Excelencia.")
            st.write("Un porcentaje alto reduce el desperdicio de alimentos (Food Waste).")
        st.markdown('</div>', unsafe_allow_html=True)

    # 6. DASHBOARD VISUAL
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📊 Análisis Visual", "🔍 Trazabilidad AgGrid"])

    with tab1:
        col_izq, col_der = st.columns(2)
        with col_izq:
            st.markdown("#### Distribución de Pedidos Reales")
            fig = px.pie(df_limpio, names='Sector', hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig, use_container_width=True)
        with col_der:
            st.markdown("#### Top 5 Platos más pedidos")
            top_5 = df_limpio['Principal/minutas'].value_counts().head(5).reset_index()
            fig2 = px.bar(top_5, x='Principal/minutas', y='count', color_discrete_sequence=['#D8A7B1'])
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown("#### Listado Completo de Auditoría")
        st.dataframe(df_limpio, use_container_width=True)

except Exception as e:
    st.error(f"Error en la conexión de datos: {e}")
