import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página (Fondo blanco y layout ancho)
st.set_page_config(page_title="Agro Intelligence Colombia", layout="wide", page_icon="🚜")

# --- ESTILO CSS PARA MÁXIMA CLARIDAD ---
st.markdown("""
    <style>
    /* Fondo general blanco */
    .stApp { background-color: #FFFFFF; color: #1E1E1E; }
    
    /* Títulos y subtítulos */
    h1, h2, h3 { color: #3E4A34 !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Tarjetas de Métricas */
    div[data-testid="metric-container"] {
        background-color: #F9FBF9;
        border: 1px solid #E0E4D9;
        border-top: 4px solid #5D4037; /* Acento color café */
        padding: 15px;
        border-radius: 8px;
    }
    
    /* Tabs con diseño limpio */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #F1F3F0; padding: 5px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #5D4037; padding: 8px 20px; font-weight: 500; }
    .stTabs [aria-selected="true"] { background-color: #FFFFFF; border-radius: 8px; box-shadow: 0px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- PALETA TIERRA PROFESIONAL ---
EARTH_TONES = ["#4F6F52", "#86A789", "#D2B48C", "#A98467", "#739072", "#5D4037"]

st.title("🚜 Inteligencia de Datos Agrícolas")
st.markdown("Analice el rendimiento, la tecnificación y los suelos de sus fincas de manera intuitiva.")

# --- CARGA Y PROCESAMIENTO ---
with st.sidebar:
    st.header("📂 Gestión de Datos")
    uploaded_file = st.file_uploader("Subir archivo agro_colombia.csv", type=["csv"])
    st.markdown("---")
    
    if uploaded_file:
        # Carga inteligente para evitar errores de puntero
        @st.cache_data
        def load_data(file):
            data = pd.read_csv(file)
            data['Fecha_Ultima_Auditoria'] = pd.to_datetime(data['Fecha_Ultima_Auditoria'])
            return data
        
        df_base = load_data(uploaded_file)
        
        # Filtros Organizados
        st.subheader("🔍 Filtros de Búsqueda")
        dept_sel = st.multiselect("Departamentos:", options=sorted(df_base["Departamento"].unique()), default=sorted(df_base["Departamento"].unique())[:3])
        cultivo_sel = st.selectbox("Tipo de Cultivo:", ["Todos"] + sorted(list(df_base["Tipo_Cultivo"].unique())))
        
        st.subheader("⚙️ Simulación")
        eficiencia = st.slider("Simular incremento de producción (%)", 0, 200, 100)

if uploaded_file:
    # Aplicar filtros
    df_f = df_base[df_base["Departamento"].isin(dept_sel)]
    if cultivo_sel != "Todos":
        df_f = df_f[df_f["Tipo_Cultivo"] == cultivo_sel]

    # --- CUERPO PRINCIPAL (MÉTRICAS CLAVE) ---
    col1, col2, col3, col4 = st.columns(4)
    
    prod_total = df_f["Produccion_Anual_Ton"].sum()
    prod_simulada = prod_total * (eficiencia / 100)
    
    with col1:
        st.metric("Producción Real", f"{prod_total:,.1f} Ton")
    with col2:
        st.metric("Proyección Eficiencia", f"{prod_simulada:,.1f} Ton", delta=f"{eficiencia-100}%")
    with col3:
        st.metric("Área Cultivada", f"{df_f['Area_Hectareas'].sum():,.1f} Ha")
    with col4:
        st.metric("Precio Promedio Ton", f"${df_f['Precio_Venta_Por_Ton_COP'].mean():,.0f}")

    st.markdown("---")

    # --- PESTAÑAS ORGANIZADAS ---
    tab_resumen, tab_analisis, tab_datos = st.tabs(["📊 Resumen de Rendimiento", "🧪 Calidad y Suelos", "📋 Lista de Fincas"])

    # --- TAB 1: RESUMEN GRÁFICO ---
    with tab_resumen:
        st.subheader("Análisis de Producción por Zona")
        
        col_g1, col_g2 = st.columns([2, 1])
        
        with col_g1:
            # Gráfico de barras limpio sin fondo oscuro
            fig_bar = px.bar(
                df_f.groupby("Departamento")["Produccion_Anual_Ton"].sum().reset_index(),
                x="Departamento", y="Produccion_Anual_Ton",
                color_discrete_sequence=[EARTH_TONES[0]],
                template="plotly_white",
                title="Producción Total por Departamento Seleccionado"
            )
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_g2:
            # Distribución de Cultivos
            fig_pie = px.pie(
                df_f, names="Tipo_Cultivo", values="Produccion_Anual_Ton",
                color_discrete_sequence=EARTH_TONES,
                template="plotly_white",
                hole=0.4,
                title="% Producción por Cultivo"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- TAB 2: CALIDAD Y SUELOS ---
    with tab_analisis:
        st.subheader("Factores Técnicos del Suelo")
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.write("**Eficiencia de Producción por Tipo de Suelo**")
            # Gráfico de puntos para ver rentabilidad
            fig_scatter = px.scatter(
                df_f, x="Area_Hectareas", y="Produccion_Anual_Ton",
                color="Tipo_Suelo", size="Precio_Venta_Por_Ton_COP",
                color_discrete_sequence=EARTH_TONES,
                template="plotly_white",
                title="Relación Área vs Producción (Tamaño=Precio)"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with col_t2:
            st.write("**Promedio de Precios por Tecnificación**")
            # Tabla de resumen con degradado verde (requiere matplotlib)
            resumen_tec = df_f.groupby("Nivel_Tecnificacion")["Precio_Venta_Por_Ton_COP"].mean().sort_values(ascending=False).reset_index()
            st.dataframe(resumen_tec.style.background_gradient(cmap='YlGn'), use_container_width=True)

    # --- TAB 3: LISTA DE DATOS ---
    with tab_datos:
        st.subheader("Explorador Detallado")
        
        # Filtro de texto interno
        search = st.text_input("Filtrar por ID de Finca o palabra clave:")
        if search:
            df_final = df_f[df_f.stack().str.contains(search, case=False).groupby(level=0).any()]
        else:
            df_final = df_f

        st.dataframe(df_final, use_container_width=True)
        
        # Botón de exportación
        csv_file = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte en Excel/CSV", csv_file, "reporte_agro_premium.csv", "text/csv")

else:
    # Estado inicial cuando no hay archivo
    st.info("👆 Por favor, cargue su archivo CSV en el panel de la izquierda para comenzar el análisis.")
    st.image("https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=1000", caption="Gestión Inteligente del Agro Colombiano")
