import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Auditoría Economato CR", layout="wide")

# 2. ESTILO CSS
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    html, body, [class*="st-"], p, h1, h2, h3, span, label { color: #000000 !important; }
    .card { background: white; padding: 20px; border-radius: 12px; border-top: 5px solid #1A4B84; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. ACCESO (SIDEBAR) - AQUÍ ESTABA EL ERROR
with st.sidebar:
    # Esta es la línea 37 que se había roto:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg", width=100)
    
    st.markdown("## Acceso Institucional")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if usuario != "admin" or password != "1234":
        st.warning("Ingrese credenciales.")
        st.stop()
    st.success("Conexión establecida")

# 4. CARGA DE DATOS Y DASHBOARD
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="5m")
    
    st.title("⚖️ Sistema de Auditoría Gastronómica")
    st.markdown("### Casa Rosada · Presidencia de la Nación")

    tab1, tab2 = st.tabs(["📊 Dashboard", "🔍 Trazabilidad"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="card"><h4>Total Pedidos</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        with c2:
            if 'Sector' in df.columns:
                fig = px.pie(df, names='Sector', title="Pedidos por Sector")
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")
