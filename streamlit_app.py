import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Auditoría Economato CR", layout="wide")

# 2. ESTILO: AZUL, BLANCO Y LETRAS NEGRAS (Sin fallos)
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    
    /* Forzar negro en todos los textos */
    html, body, [class*="st-"], p, h1, h2, h3, span, label { 
        color: #000000 !important; 
    }
    
    /* Tarjetas Blancas Estilo Ejecutivo */
    .card { 
        background: white; 
        padding: 20px; 
        border-radius: 12px; 
        border-top: 5px solid #1A4B84; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
        margin-bottom: 20px;
    }

    /* Estilo de las métricas */
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. ACCESO (SIDEBAR)
with st.sidebar:
    st.image("https://uplimport streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# =========================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Auditoría Economato - Casa Rosada",
    page_icon="⚖️",
    layout="wide"
)

# =========================================================
# 2. DISEÑO CSS (Azul, Blanco y Letras Negras)
# =========================================================
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; }
    
    /* Forzar color negro en todos los textos y etiquetas */
    html, body, [class*="st-"], p, h1, h2, h3, span, label { 
        color: #000000 !important; 
    }
    
    /* Tarjetas blancas con borde superior azul institucional */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-top: 6px solid #1A4B84;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }

    /* Ajuste de métricas */
    [data-testid="stMetricValue"] { font-weight: 800; font-size: 32px; }
    
    /* Estilo de las pestañas */
    .stTabs [data-baseweb="tab"] { color: #1A4B84; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. ACCESO / LOGIN (SIDEBAR)
# =========================================================
# =========================================================
# 3. ACCESO / LOGIN (SIDEBAR)
# =========================================================
with st.sidebar:
    # Asegúrate de que la URL esté completa y cerrada con comillas
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Coat_of_arms_of_Argentina.svg", width=100)
    
    st.markdown("## Acceso Institucional")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if usuario != "admin" or password != "1234":
        st.warning("Por favor, ingrese credenciales válidas.")
        st.stop()
    
    st.success("Conexión segura establecida")

# =========================================================
# 4. TÍTULO Y CARGA DE DATOS
# =========================================================
st.title("⚖️ Sistema de Auditoría Gastronómica")
st.markdown("### Casa Rosada · Presidencia de la Nación")

# URL de tu Google Sheets
url = "https://docs.google.com/spreadsheets/d/1lqX4uss9CdW-QUqPlaBnvWoMePzuaBQ-89cfu7cDi3A/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="5m")
    
    # Limpieza de datos (respetando los nombres de tus columnas)
    df.columns = df.columns.str.strip()
    df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], errors='coerce')
    df = df.dropna(subset=['Marca temporal'])
    
    # Filtro automático de pedidos vacíos
    if 'Principal/minutas' in df.columns:
        df = df[~df['Principal/minutas'].astype(str).str.contains('NO SOLICITA', case=False, na=False)]

    # =========================================================
    # 5. INTERFAZ DE PESTAÑAS (TABS)
    # =========================================================
    tab1, tab2 = st.tabs(["📊 Dashboard de Control", "🔍 Trazabilidad de Pedidos"])

    with tab1:
        # Fila de métricas clave
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total de Pedidos", f"{len(df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            top_plato = df['Principal/minutas'].mode()[0] if not df.empty else "N/A"
            st.metric("Plato más solicitado", top_plato)
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            sectores = df['Sector'].nunique() if 'Sector' in df.columns else 0
            st.metric("Sectores Atendidos", sectores)
            st.markdown('</div>', unsafe_allow_html=True)

        # Gráficos
        col_a, col_b = st.columns(2)
        with col_a:
            if 'Sector' in df.columns:
                fig_pie = px.pie(df, names='Sector', title="Distribución por Sector", hole=0.4,
                                 color_discrete_sequence=px.colors.sequential.Blues_r)
                st.plotly_chart(fig_pie, use_container_width=True)
        with col_b:
            serie = df.groupby(df['Marca temporal'].dt.date).size().reset_index(name='Cant')
            fig_line = px.line(serie, x='Marca temporal', y='Cant', title="Evolución de Consumo",
                               markers=True, line_shape="spline")
            st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        st.markdown("### Buscador de Registros")
        busqueda = st.text_input("Ingrese funcionario, mozo o sector para auditar:")
        
        if busqueda:
            mask = df.astype(str).apply(lambda row: row.str.contains(busqueda, case=False, na=False).any(), axis=1)
            df_final = df[mask]
        else:
            df_final = df

        st.dataframe(df_final, use_container_width=True, height=500)

except Exception as e:
    st.error(f"Error técnico al conectar con la base de datos: {e}")

# Pie de página
st.markdown("---")
st.caption("Sistema de Auditoría Gastronómica · Economato Casa Rosada")
