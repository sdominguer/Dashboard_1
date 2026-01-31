import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de página
st.set_page_config(page_title="Agro Earth Mood", layout="wide", page_icon="🌿")

# --- PALETA TIERRA (EARTH TONES) ---
# Cafés, ocres, verdes bosque y arcilla
EARTH_PALETTE = ["#8B4513", "#A0522D", "#556B2F", "#D2B48C", "#BC8F8F", "#CD853F"]

# --- ESTILO DARK CON LETRA BLANCA ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown { color: #FFFFFF !important; }
    [data-testid="stMetricValue"] { color: #D2B48C !important; } /* Color Tan para números */
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    div[data-testid="metric-container"] {
        background-color: #1E2130;
        border: 1px solid #556B2F;
        border-radius: 15px;
    }
    .stSlider > div > div > div > div { color: #CD853F; } /* Slider color tierra */
    </style>
    """, unsafe_allow_html=True)

st.title("🍂 Agro-Intelligence: Mood Tierra")

# --- SIDEBAR INTERACTIVO ---
st.sidebar.header("🪵 Herramientas de Campo")
uploaded_file = st.sidebar.file_uploader("Sube tu cosecha de datos (CSV)", type=["csv"])

if uploaded_file is not None:
    st.sidebar.success("¡Datos cargados con éxito!")
    df = pd.read_csv(uploaded_file)
    df['Fecha_Ultima_Auditoria'] = pd.to_datetime(df['Fecha_Ultima_Auditoria'])

    # --- NUEVAS COSAS INTERACTIVAS ---
    
    # 1. El slider de 0 a 1000 que pediste (Simulador de productividad)
    st.sidebar.subheader("📈 Simulador")
    meta_produccion = st.sidebar.slider("Ajustar Meta de Rendimiento (0-1000)", 0, 1000, 500)
    
    # 2. Búsqueda por palabra clave en el tipo de suelo
    suelo_busqueda = st.sidebar.selectbox("Filtrar por tipo de suelo:", ["Todos"] + list(df["Tipo_Suelo"].unique()))

    # 3. Color Picker para el acento de los bordes
    color_finca = st.sidebar.color_picker("Color de marcador", "#556B2F")

    # --- LÓGICA DE FILTRADO ---
    df_f = df.copy()
    if suelo_busqueda != "Todos":
        df_f = df_f[df_f["Tipo_Suelo"] == suelo_busqueda]

    # --- PESTAÑAS ---
    tab_cuant, tab_cual, tab_graf = st.tabs(["🔢 CUANTITATIVO", "📄 CUALITATIVO", "📊 GRÁFICO"])

    # BLOQUE 1: CUANTITATIVO
    with tab_cuant:
        st.subheader("Análisis de Cosecha")
        c1, c2, c3 = st.columns(3)
        
        produccion_real = df_f['Produccion_Anual_Ton'].sum()
        # Usamos el slider para un cálculo dinámico "bacano"
        rendimiento_simulado = (produccion_real * meta_produccion) / 500

        c1.metric("Producción Real", f"{produccion_real:,.0f} Ton")
        c2.metric("Simulación Meta", f"{rendimiento_simulado:,.0f} Ton", delta=f"{meta_produccion - 500} pts")
        c3.metric("Fincas Analizadas", len(df_f))

        st.write("### 🪵 Estadísticas de Suelos")
        st.dataframe(df_f.groupby("Tipo_Suelo").agg({
            "Area_Hectareas": "sum",
            "Precio_Venta_Por_Ton_COP": "mean"
        }).style.background_gradient(cmap='YlOrBr'))

    # BLOQUE 2: CUALITATIVO
    with tab_cual:
        st.subheader("Gestión y Auditoría")
        
        with st.expander("🛠️ Opciones Avanzadas de Visualización"):
            st.write("Aquí puedes ver el detalle de tecnificación por cada finca.")
            mostrar_todo = st.checkbox("Mostrar toda la tabla")
        
        if mostrar_todo:
            st.dataframe(df_f, use_container_width=True)
        else:
            st.dataframe(df_f.head(10), use_container_width=True)

        st.write("**Resumen de Riego:**")
        st.progress(len(df_f[df_f['Sistema_Riego_Tecnificado'] == True]) / len(df_f))
        st.caption("Porcentaje de fincas con riego tecnificado")

    # BLOQUE 3: GRÁFICO (Mood Tierra)
    with tab_graf:
        st.subheader("Visualización en Tonos Tierra")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Treemap: Estructura de cultivos
            fig_tree = px.treemap(
                df_f, path=['Departamento', 'Tipo_Cultivo'], values='Produccion_Anual_Ton',
                title="Jerarquía de Producción",
                color_discrete_sequence=EARTH_PALETTE,
                template="plotly_dark"
            )
            st.plotly_chart(fig_tree, use_container_width=True)

        with col2:
            # Boxplot con colores tierra
            fig_box = px.box(
                df_f, x="Tipo_Cultivo", y="Precio_Venta_Por_Ton_COP",
                title="Variación de Precios",
                color_discrete_sequence=[EARTH_PALETTE[1]],
                template="plotly_dark"
            )
            st.plotly_chart(fig_box, use_container_width=True)

        # Gráfico de burbujas personalizado
        fig_bubble = px.scatter(
            df_f, x="Area_Hectareas", y="Produccion_Anual_Ton",
            size="Precio_Venta_Por_Ton_COP", color="Tipo_Suelo",
            hover_name="ID_Finca",
            title="Relación Área vs Producción (Burbujas por Suelo)",
            color_discrete_sequence=EARTH_PALETTE,
            template="plotly_dark"
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

else:
    # BIENVENIDA
    st.info("🚜 ¡Listo para la cosecha! Sube tu CSV para empezar.")
    st.image(
        "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=1000", 
        caption="Mood Agro - Análisis de Datos"
    )
    
    if st.button("Lanzar Globos de Bienvenida"):
        st.balloons()
