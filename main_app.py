import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página (Fondo blanco por defecto)
st.set_page_config(page_title="Agro Premium Dashboard", layout="wide", page_icon="🌱")

# --- PALETA TIERRA SELECCIONADA ---
EARTH_COLORS = ["#4F6F52", "#739072", "#86A789", "#D2B48C", "#A98467", "#606C38"]

# --- ESTILO LIMPIO Y PROFESIONAL ---
st.markdown("""
    <style>
    /* Forzar fondo blanco y letras oscuras */
    .stApp { background-color: #FFFFFF; color: #2D2D2D; }
    
    /* Estilo para las métricas (Tarjetas) */
    div[data-testid="metric-container"] {
        background-color: #F8F9F3;
        border: 1px solid #E6E6E1;
        border-left: 5px solid #4F6F52; /* Borde verde tierra */
        padding: 20px;
        border-radius: 10px;
    }
    
    /* Ajuste de Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #F8F9F3;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px;
        color: #4F6F52;
    }
    </style>
    """, unsafe_allow_html=True)

# Título con estilo
st.title("🍃 Sistema de Inteligencia Agrícola")
st.markdown("---")

# --- SIDEBAR (PANEL DE CONTROL) ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=1000")
    st.header("⚙️ Configuración")
    uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])
    
    if uploaded_file:
        st.success("Archivo cargado")
        # Slider de simulador (0-1000)
        eficiencia = st.slider("Simulador de Eficiencia (%)", 0, 1000, 100)
        # Filtro de Departamento
        df_temp = pd.read_csv(uploaded_file)
        depts = st.multiselect("Filtrar Departamentos", df_temp["Departamento"].unique())

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['Fecha_Ultima_Auditoria'] = pd.to_datetime(df['Fecha_Ultima_Auditoria'])
    
    # Aplicar filtros si existen
    if depts:
        df = df[df["Departamento"].isin(depts)]

    # --- PESTAÑAS PRINCIPALES ---
    tab1, tab2, tab3 = st.tabs(["📊 VISTA GENERAL", "🧐 DETALLE CUALITATIVO", "🎨 ANÁLISIS VISUAL"])

    # --- TAB 1: CUANTITATIVO ---
    with tab1:
        st.subheader("Indicadores de Producción")
        c1, c2, c3, c4 = st.columns(4)
        
        prod_total = df["Produccion_Anual_Ton"].sum()
        # Aplicamos el simulador del slider
        prod_simulada = prod_total * (eficiencia / 100)

        c1.metric("Producción Total", f"{prod_total:,.0f} T")
        c2.metric("Proyección (Slider)", f"{prod_simulada:,.0f} T", delta=f"{eficiencia}%")
        c3.metric("Área Cultivada", f"{df['Area_Hectareas'].sum():,.0f} Ha")
        c4.metric("Precio Promedio", f"${df['Precio_Venta_Por_Ton_COP'].mean():,.0f}")

        st.markdown("### Rendimiento por Tipo de Suelo")
        resumen_suelo = df.groupby("Tipo_Suelo").agg({"Produccion_Anual_Ton": "sum", "Area_Hectareas": "mean"})
        st.dataframe(resumen_suelo.style.background_gradient(cmap='YlGn'), use_container_width=True)

    # --- TAB 2: CUALITATIVO ---
    with tab2:
        st.subheader("Análisis de Calidad y Gestión")
        
        col_a, col_b = st.columns([1, 2])
        
        with col_a:
            st.write("**Nivel de Tecnificación**")
            # Un gráfico de barras horizontal pequeño y limpio
            tec_count = df["Nivel_Tecnificacion"].value_counts()
            st.bar_chart(tec_count, color="#A98467")
            
            st.write("**Sistemas de Riego**")
            st.info(f"Fincas con Riego: {len(df[df['Sistema_Riego_Tecnificado']==True])}")

        with col_b:
            st.write("**Buscador Global de Fincas**")
            st.dataframe(df[["ID_Finca", "Departamento", "Tipo_Cultivo", "Tipo_Suelo"]], height=400)

    # --- TAB 3: GRÁFICO (MOOD TIERRA) ---
    with tab3:
        st.subheader("Visualización del Campo")
        
        # 1. Gráfico de Áreas (Sunburst)
        fig_sun = px.sunburst(
            df, path=['Departamento', 'Tipo_Cultivo'], values='Produccion_Anual_Ton',
            color_discrete_sequence=EARTH_COLORS,
            template="plotly_white"
        )
        st.plotly_chart(fig_sun, use_container_width=True)

        st.markdown("---")
        
        # 2. Relación de Precios y Área
        fig_scatter = px.scatter(
            df, x="Area_Hectareas", y="Produccion_Anual_Ton",
            size="Precio_Venta_Por_Ton_COP", color="Tipo_Cultivo",
            color_discrete_sequence=EARTH_COLORS,
            title="Eficiencia por Cultivo (Tamaño = Precio)",
            template="plotly_white"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Botón para descargar lo que filtró
        st.download_button("📥 Descargar Reporte Final", df.to_csv(), "reporte_agro.csv")

else:
    st.info("👋 Por favor, sube el archivo 'agro_colombia.csv' en la barra lateral para generar la magia.")
    st.image("https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&q=80&w=1000", caption="El futuro del campo colombiano")
