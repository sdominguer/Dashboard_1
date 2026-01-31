import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página limpia
st.set_page_config(page_title="Agro Dashboard", layout="wide")

# Paleta Pastel para los Gráficos
PASTEL_PALETTE = ["#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", "#F3B0C3"]

st.title("🚜 Dashboard de Análisis Agropecuario")

# --- CARGA DE DATOS ---
st.sidebar.header("Configuración")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    # Carga de datos
    df = pd.read_csv(uploaded_file)
    
    # Filtros Dinámicos
    st.sidebar.subheader("Filtros")
    dept_list = sorted(df["Departamento"].unique())
    selected_depts = st.sidebar.multiselect("Departamentos:", dept_list, default=dept_list)

    crop_list = sorted(df["Tipo_Cultivo"].unique())
    selected_crops = st.sidebar.multiselect("Tipos de Cultivo:", crop_list, default=crop_list)

    # DataFrame Filtrado
    df_filtered = df[df["Departamento"].isin(selected_depts) & df["Tipo_Cultivo"].isin(selected_crops)]

    # --- ESTRUCTURA DE 3 BLOQUES (TABS) ---
    tab_cuant, tab_cual, tab_graf = st.tabs(["🔢 CUANTITATIVO", "📄 CUALITATIVO", "📊 GRÁFICO"])

    # BLOQUE 1: CUANTITATIVO (Métricas y números)
    with tab_cuant:
        st.subheader("Indicadores Numéricos Clave")
        
        # Usamos columnas nativas de Streamlit para asegurar legibilidad
        m1, m2, m3 = st.columns(3)
        m1.metric("Área Total (Ha)", f"{df_filtered['Area_Hectareas'].sum():,.1f}")
        m2.metric("Producción Total (Ton)", f"{df_filtered['Produccion_Anual_Ton'].sum():,.1f}")
        m3.metric("Precio Promedio Ton", f"${df_filtered['Precio_Venta_Por_Ton_COP'].mean():,.0f}")

        st.markdown("---")
        st.write("**Resumen Estadístico del Terreno:**")
        # Estilo de tabla legible
        st.dataframe(df_filtered.describe(), use_container_width=True)

    # BLOQUE 2: CUALITATIVO (Categorías y tablas)
    with tab_cual:
        st.subheader("Análisis de Atributos")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Distribución por Suelo**")
            st.table(df_filtered["Tipo_Suelo"].value_counts())
            
        with c2:
            st.write("**Nivel de Tecnificación**")
            st.table(df_filtered["Nivel_Tecnificacion"].value_counts())

        st.subheader("Explorador de Datos Seleccionados")
        st.dataframe(df_filtered, use_container_width=True)

    # BLOQUE 3: GRÁFICO (Visualizaciones con tonos pastel)
    with tab_graf:
        st.subheader("Visualización Dinámica")
        
        # Gráfico 1: Producción por Cultivo
        fig_bar = px.bar(
            df_filtered.groupby("Tipo_Cultivo")["Produccion_Anual_Ton"].sum().reset_index(),
            x="Tipo_Cultivo", 
            y="Produccion_Anual_Ton",
            color="Tipo_Cultivo",
            title="Producción por Cultivo",
            color_discrete_sequence=PASTEL_PALETTE,
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Gráfico 2: Relación Área vs Producción
        fig_scatter = px.scatter(
            df_filtered,
            x="Area_Hectareas",
            y="Produccion_Anual_Ton",
            color="Nivel_Tecnificacion",
            size="Precio_Venta_Por_Ton_COP",
            title="Relación Área vs Producción (Color por Tecnificación)",
            color_discrete_sequence=PASTEL_PALETTE,
            template="plotly_white"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

else:
    # Estado inicial: Imagen y aviso
    st.info("👋 Por favor, sube un archivo CSV en el panel izquierdo para comenzar.")
    st.image(
        "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=1000", 
        caption="Análisis de agro-datos"
    )
