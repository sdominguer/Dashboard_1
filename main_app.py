import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Agro Intelligence Pro", layout="wide", page_icon="🌱")

# --- ESTILO CSS PERSONALIZADO (Limpio y Tierra) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #2D2D2D; }
    [data-testid="stMetricValue"] { color: #5D4037 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #795548 !important; }
    div[data-testid="metric-container"] {
        background-color: #FDFBF7;
        border: 1px solid #D7CCC8;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] { background-color: #F1F8E9; border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: #33691E; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- PALETA DE COLORES TIERRA ---
EARTH_COLORS = ["#5D4037", "#8D6E63", "#388E3C", "#689F38", "#AFB42B", "#FBC02D"]

st.title("🌱 Sistema de Inteligencia Agrícola Premium")
st.markdown("---")

# --- CARGA DE DATOS (FIX DE ERROR) ---
st.sidebar.image("https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=1000")
st.sidebar.header("🕹️ Centro de Control")
uploaded_file = st.sidebar.file_uploader("Carga tu cosecha (CSV)", type=["csv"])

if uploaded_file is not None:
    # LEEMOS UNA SOLA VEZ para evitar el EmptyDataError
    @st.cache_data
    def load_data(file):
        data = pd.read_csv(file)
        if 'Fecha_Ultima_Auditoria' in data.columns:
            data['Fecha_Ultima_Auditoria'] = pd.to_datetime(data['Fecha_Ultima_Auditoria'])
        return data

    df_base = load_data(uploaded_file)

    # --- ELEMENTOS INTERACTIVOS BACANOS ---
    with st.sidebar:
        st.markdown("### 🛠️ Ajustes")
        # El slider de 0 a 1000 que querías
        multiplicador = st.slider("📈 Simulador de Rendimiento (Unidades)", 0, 1000, 100)
        
        # Filtros dinámicos
        search_term = st.text_input("🔍 Buscar Cultivo (ej: Café)", "")
        
        depts = st.multiselect("📍 Filtrar Departamentos", 
                               options=sorted(df_base["Departamento"].unique()),
                               default=sorted(df_base["Departamento"].unique())[:2])

    # --- LÓGICA DE FILTRADO ---
    df_f = df_base[df_base["Departamento"].isin(depts)]
    if search_term:
        df_f = df_f[df_f["Tipo_Cultivo"].str.contains(search_term, case=False)]

    # --- TABS "MÁS CHIMBAS" ---
    tab_cuant, tab_cual, tab_graf = st.tabs(["💰 INDICADORES", "🔬 DETALLE TÉCNICO", "🖼️ VISUALIZACIÓN"])

    # 🔢 TAB 1: CUANTITATIVO
    with tab_cuant:
        st.subheader("Análisis de Rentabilidad y Volumen")
        
        # Cálculo de métricas
        prod_total = df_f["Produccion_Anual_Ton"].sum()
        valor_estimado = (prod_total * multiplicador) # Usamos el slider para algo loco
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Producción Total", f"{prod_total:,.1f} Ton")
        m2.metric("Valor Simulado", f"${valor_estimado:,.0f}", delta=f"x{multiplicador}")
        m3.metric("Área Promedio", f"{df_f['Area_Hectareas'].mean():,.1f} Ha")
        m4.metric("N° de Fincas", len(df_f))

        st.markdown("---")
        st.write("#### 📊 Resumen Estadístico por Departamento")
        stats = df_f.groupby("Departamento").agg({
            "Produccion_Anual_Ton": "sum",
            "Area_Hectareas": "mean",
            "Precio_Venta_Por_Ton_COP": "mean"
        })
        st.dataframe(stats.style.background_gradient(cmap='YlOrBr'), use_container_width=True)

    # 📄 TAB 2: CUALITATIVO
    with tab_cual:
        st.subheader("Calidad y Tecnificación del Suelo")
        
        c_a, c_b = st.columns([1, 1])
        with c_a:
            st.write("**Distribución por Tipo de Suelo**")
            suelo_chart = df_f["Tipo_Suelo"].value_counts()
            st.bar_chart(suelo_chart, color="#8D6E63") # Color tierra
            
        with c_b:
            st.write("**Nivel de Tecnificación**")
            st.info(f"El nivel más común es: **{df_f['Nivel_Tecnificacion'].mode()[0]}**")
            st.table(df_f["Nivel_Tecnificacion"].value_counts())

        with st.expander("🔍 Explorar Data Cruda"):
            st.dataframe(df_f, use_container_width=True)

    # 📊 TAB 3: GRÁFICO (Mood Tierra Total)
    with tab_graf:
        st.subheader("Galería de Visualización")
        
        # Gráfico 1: Sunburst (Jerarquía)
        fig_sun = px.sunburst(
            df_f, path=['Departamento', 'Tipo_Cultivo'], values='Produccion_Anual_Ton',
            title="Distribución de Producción (Dept > Cultivo)",
            color_discrete_sequence=EARTH_COLORS,
            template="plotly_white"
        )
        st.plotly_chart(fig_sun, use_container_width=True)

        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            # Gráfico de áreas
            fig_area = px.area(
                df_f.sort_values("Fecha_Ultima_Auditoria"), 
                x="Fecha_Ultima_Auditoria", y="Produccion_Anual_Ton",
                color="Departamento",
                title="Evolución de Auditorías vs Producción",
                color_discrete_sequence=EARTH_COLORS,
                template="plotly_white"
            )
            st.plotly_chart(fig_area, use_container_width=True)
            
        with col_g2:
            # Scatter de eficiencia
            fig_scat = px.scatter(
                df_f, x="Area_Hectareas", y="Produccion_Anual_Ton",
                size="Precio_Venta_Por_Ton_COP", color="Tipo_Suelo",
                title="Eficiencia por Suelo (Tamaño=Precio)",
                color_discrete_sequence=EARTH_COLORS,
                template="plotly_white"
            )
            st.plotly_chart(fig_scat, use_container_width=True)

        # Botón de descarga bacano
        csv = df_f.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte de Cosecha",
            data=csv,
            file_name='reporte_agro_chimba.csv',
            mime='text/csv',
        )

else:
    # Pantalla de bienvenida
    st.info("👋 ¡Todo listo! Sube el CSV en el panel de la izquierda para desplegar el dashboard.")
    st.image("https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&q=80&w=1000")
    if st.button("✨ ¡Sorpresa!"):
        st.balloons()
