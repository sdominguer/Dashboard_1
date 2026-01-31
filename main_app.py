import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuración de página y Tema Oscuro Forzado
st.set_page_config(page_title="Agro Dark Pro", layout="wide", page_icon="🌑")

# Inyección de CSS para Fondo Oscuro y Letras Blancas
st.markdown("""
    <style>
    /* Fondo principal y textos */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #FFFFFF !important; }
    
    /* Estilo de las métricas */
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.8rem; }
    [data-testid="stMetricLabel"] { color: #B0B0B0 !important; }
    div[data-testid="metric-container"] {
        background-color: #1E2130;
        border: 1px solid #3E4255;
        padding: 15px;
        border-radius: 10px;
    }
    
    /* Tablas y Dataframes */
    .stDataFrame { background-color: #1E2130; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌑 Agro-Intelligence: Modo Oscuro")

# --- SIDEBAR INTERACTIVO ---
st.sidebar.header("🕹️ Panel de Control")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['Fecha_Ultima_Auditoria'] = pd.to_datetime(df['Fecha_Ultima_Auditoria'])

    # --- NUEVAS COSAS INTERACTIVAS ---
    # 1. Buscador de texto por ID
    search_id = st.sidebar.text_input("🔍 Buscar por ID de Finca", "")

    # 2. Color Picker para la interfaz
    accent_color = st.sidebar.color_picker("Color de acento", "#00D4FF")

    # 3. Slider de Rango de Producción
    prod_min, prod_max = float(df["Produccion_Anual_Ton"].min()), float(df["Produccion_Anual_Ton"].max())
    rango_prod = st.sidebar.slider("Producción (Ton)", prod_min, prod_max, (prod_min, prod_max))

    # 4. Multi-selector de Departamentos
    depts = st.sidebar.multiselect("Departamentos:", options=df["Departamento"].unique(), default=df["Departamento"].unique()[:3])

    # 5. Radio de Nivel Tecnificación
    tec_level = st.sidebar.radio("Filtrar por Tecnificación:", ["Todos", "Bajo", "Medio", "Alto", "Muy Alto"])

    # 6. Date Input
    auditoria_desde = st.sidebar.date_input("Auditorías desde:", df["Fecha_Ultima_Auditoria"].min())

    # --- LÓGICA DE FILTRADO ---
    mask = (df["Produccion_Anual_Ton"].between(*rango_prod)) & \
           (df["Departamento"].isin(depts)) & \
           (df["Fecha_Ultima_Auditoria"].dt.date >= auditoria_desde)
    
    if tec_level != "Todos":
        mask &= (df["Nivel_Tecnificacion"] == tec_level)
    
    if search_id:
        mask &= (df["ID_Finca"].str.contains(search_id, case=False))

    df_f = df[mask]

    # --- PESTAÑAS ---
    tab_cuant, tab_cual, tab_graf = st.tabs(["🔢 CUANTITATIVO", "📄 CUALITATIVO", "📊 GRÁFICO"])

    # BLOQUE 1: CUANTITATIVO
    with tab_cuant:
        st.subheader("Métricas de Rendimiento")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Fincas", len(df_f))
        c2.metric("Área Total", f"{df_f['Area_Hectareas'].sum():,.0f} Ha")
        c3.metric("Producción", f"{df_f['Produccion_Anual_Ton'].sum():,.0f} Ton")
        c4.metric("Precio Prom.", f"${df_f['Precio_Venta_Por_Ton_COP'].mean():,.0f}")
        
        st.markdown("---")
        st.write("### 📈 Análisis de Precios por Suelo")
        # Gráfico rápido de barras interno
        st.bar_chart(df_f.groupby("Tipo_Suelo")["Precio_Venta_Por_Ton_COP"].mean(), color=accent_color)

    # BLOQUE 2: CUALITATIVO
    with tab_cual:
        st.subheader("Detalles Técnicos")
        
        # Botón para descargar
        csv_data = df_f.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte CSV", csv_data, "agro_report.csv", "text/csv")

        st.dataframe(df_f.style.highlight_max(axis=0, color="#2E4A3F"), use_container_width=True)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.write("**Resumen de Tecnificación**")
            st.write(df_f["Nivel_Tecnificacion"].value_counts())
        with col_c2:
            st.write("**Sistema de Riego**")
            st.write(df_f["Sistema_Riego_Tecnificado"].value_counts())

    # BLOQUE 3: GRÁFICO (Cosas bacanas)
    with tab_graf:
        st.subheader("Visualización Avanzada")
        
        # 1. Sunburst Chart: Jerarquía Dept -> Cultivo
        st.write("**Jerarquía: Departamento > Cultivo (Producción)**")
        fig_sun = px.sunburst(
            df_f, path=['Departamento', 'Tipo_Cultivo'], values='Produccion_Anual_Ton',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_dark"
        )
        st.plotly_chart(fig_sun, use_container_width=True)

        g1, g2 = st.columns(2)
        with g1:
            # 2. Box Plot de Precios
            fig_box = px.box(
                df_f, x="Nivel_Tecnificacion", y="Precio_Venta_Por_Ton_COP",
                title="Distribución de Precios por Tecnificación",
                color_discrete_sequence=[accent_color],
                template="plotly_dark"
            )
            st.plotly_chart(fig_box, use_container_width=True)
            
        with g2:
            # 3. Scatter Plot interactivo
            fig_scatter = px.scatter(
                df_f, x="Area_Hectareas", y="Produccion_Anual_Ton",
                size="Precio_Venta_Por_Ton_COP", color="Tipo_Cultivo",
                title="Área vs Producción por Cultivo",
                template="plotly_dark"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

else:
    # Pantalla de bienvenida con la imagen solicitada
    st.info("👋 Sube tu CSV para activar el modo oscuro.")
    st.image(
        "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=1000", 
        caption="Análisis de agro-datos"
    )
    
    # Previsualización de interactividad
    st.write("### Herramientas que se activarán:")
    c1, c2, c3 = st.columns(3)
    c1.write("🎨 **Color Picker** para acentos.")
    c2.write("📅 **Filtro de Calendario**.")
    c3.write("🔍 **Buscador de IDs**.")
