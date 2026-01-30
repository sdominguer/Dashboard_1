import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración estética de la página
st.set_page_config(page_title="Agro Dashboard Pastel", layout="wide")

# Colores Pastel Personalizados
PASTEL_COLORS = ["#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", "#F3B0C3"]

# Estilo CSS para mejorar la apariencia (opcional)
st.markdown("""
    <style>
    .stMetric { background-color: #f9f9f9; padding: 15px; border-radius: 10px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌱 Dashboard de Análisis Agropecuario")

# --- BLOQUE DE CARGA DE DATOS ---
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Limpieza básica
    if 'Fecha_Ultima_Auditoria' in df.columns:
        df['Fecha_Ultima_Auditoria'] = pd.to_datetime(df['Fecha_Ultima_Auditoria'])

    # --- FILTROS DINÁMICOS (Modifican todos los bloques) ---
    st.sidebar.header("Configuración Dinámica")
    
    dept_list = df["Departamento"].unique().tolist()
    selected_depts = st.sidebar.multiselect("Filtrar por Departamento", dept_list, default=dept_list[:3])

    crop_list = df["Tipo_Cultivo"].unique().tolist()
    selected_crops = st.sidebar.multiselect("Filtrar por Cultivo", crop_list, default=crop_list)

    # DataFrame Filtrado
    df_filtered = df[df["Departamento"].isin(selected_depts) & df["Tipo_Cultivo"].isin(selected_crops)]

    # --- ESTRUCTURA DE 3 BLOQUES ---
    tab_cuant, tab_cual, tab_graf = st.tabs(["🔢 Cuantitativo", "📄 Cualitativo", "📊 Gráfico"])

    # --- BLOQUE 1: CUANTITATIVO ---
    with tab_cuant:
        st.subheader("Indicadores Numéricos Clave")
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.metric("Total Área (Ha)", f"{df_filtered['Area_Hectareas'].sum():,.0f}")
        with c2:
            st.metric("Producción (Ton)", f"{df_filtered['Produccion_Anual_Ton'].sum():,.0f}")
        with c3:
            st.metric("Precio Promedio", f"${df_filtered['Precio_Venta_Por_Ton_COP'].mean():,.0f}")
        with c4:
            st.metric("Rendimiento Prom.", f"{(df_filtered['Produccion_Anual_Ton']/df_filtered['Area_Hectareas']).mean():,.2f} T/Ha")
        
        st.write("### Resumen Estadístico")
        st.dataframe(df_filtered.describe().T.style.background_gradient(cmap='Pastel1'))

    # --- BLOQUE 2: CUALITATIVO ---
    with tab_cual:
        st.subheader("Análisis de Categorías y Detalles")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Distribución por Nivel de Tecnificación**")
            tec_counts = df_filtered["Nivel_Tecnificacion"].value_counts().reset_index()
            st.table(tec_counts)
        
        with col_b:
            st.write("**Tipos de Suelo Predominantes**")
            suelo_counts = df_filtered["Tipo_Suelo"].value_counts().reset_index()
            st.table(suelo_counts)

        st.write("### Datos Detallados (Filtrados)")
        st.dataframe(df_filtered)

    # --- BLOQUE 3: GRÁFICO ---
    with tab_graf:
        st.subheader("Visualización de Tendencias")
        
        g1, g2 = st.columns(2)

        with g1:
            # Gráfico de barras pastel
            fig_bar = px.bar(
                df_filtered.groupby("Tipo_Cultivo")["Produccion_Anual_Ton"].sum().reset_index(),
                x="Tipo_Cultivo", y="Produccion_Anual_Ton",
                title="Producción por Cultivo",
                color_discrete_sequence=[PASTEL_COLORS[0]]
            )
            fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True)

        with g2:
            # Gráfico de Torta pastel
            fig_pie = px.pie(
                df_filtered, names="Tipo_Suelo", 
                title="Distribución de Suelos",
                color_discrete_sequence=PASTEL_COLORS
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Gráfico de Dispersión
        fig_scatter = px.scatter(
            df_filtered, x="Area_Hectareas", y="Produccion_Anual_Ton",
            color="Nivel_Tecnificacion",
            size="Precio_Venta_Por_Ton_COP",
            title="Relación Área vs Producción (Tamaño por Precio)",
            color_discrete_sequence=PASTEL_COLORS,
            template="plotly_white"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

else:
    st.info("👋 ¡Bienvenido! Por favor carga un archivo CSV en la barra lateral para generar el reporte.")
    # Imagen placeholder con tonos suaves
    st.image("https://images.unsplash.com/photo-1495107336281-19d4f7a7d0bf?auto=format&fit=crop&q=80&w=1000", caption="Análisis de datos agrícolas")
