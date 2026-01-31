import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración básica
st.set_page_config(page_title="Agro Dashboard Colombia", layout="wide")

# Título principal
st.title("🚜 Dashboard de Análisis Agropecuario")

# --- CARGA DE DATOS ---
st.sidebar.header("1. Configuración de Datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo agro_colombia.csv", type=["csv"])

if uploaded_file is not None:
    # Cargar DF
    df = pd.read_csv(uploaded_file)
    
    # Pre-procesamiento de fechas
    if 'Fecha_Ultima_Auditoria' in df.columns:
        df['Fecha_Ultima_Auditoria'] = pd.to_datetime(df['Fecha_Ultima_Auditoria'])

    # --- FILTROS DINÁMICOS EN SIDEBAR ---
    st.sidebar.header("2. Filtros Dinámicos")
    
    # Filtro Departamento
    dept_list = sorted(df["Departamento"].unique())
    selected_depts = st.sidebar.multiselect("Selecciona Departamentos:", dept_list, default=dept_list)

    # Filtro Cultivo
    crop_list = sorted(df["Tipo_Cultivo"].unique())
    selected_crops = st.sidebar.multiselect("Selecciona Cultivos:", crop_list, default=crop_list)

    # Aplicar Filtros
    df_selection = df[df["Departamento"].isin(selected_depts) & df["Tipo_Cultivo"].isin(selected_crops)]

    # --- ESTRUCTURA DE 3 BLOQUES ---
    tab_cuant, tab_cual, tab_graf = st.tabs(["🔢 CUANTITATIVO", "📄 CUALITATIVO", "📊 GRÁFICO"])

    # --- BLOQUE 1: CUANTITATIVO ---
    with tab_cuant:
        st.header("Indicadores Numéricos Clave")
        
        # Usamos columnas estándar para asegurar visibilidad
        col1, col2, col3 = st.columns(3)
        
        area_total = df_selection['Area_Hectareas'].sum()
        prod_total = df_selection['Produccion_Anual_Ton'].sum()
        precio_prom = df_selection['Precio_Venta_Por_Ton_COP'].mean()

        col1.metric("Área Total (Ha)", f"{area_total:,.1f}")
        col2.metric("Producción Total (Ton)", f"{prod_total:,.1f}")
        col3.metric("Precio Promedio (COP)", f"${precio_prom:,.0f}")

        st.markdown("---")
        st.subheader("Resumen Estadístico")
        st.dataframe(df_selection.describe(), use_container_width=True)

    # --- BLOQUE 2: CUALITATIVO ---
    with tab_cual:
        st.header("Análisis de Categorías")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Nivel de Tecnificación")
            # Conteo simple para ver la calidad del agro
            tec_df = df_selection["Nivel_Tecnificacion"].value_counts().reset_index()
            tec_df.columns = ["Nivel", "Cantidad de Fincas"]
            st.table(tec_df)

        with c2:
            st.subheader("Tipos de Suelo")
            suelo_df = df_selection["Tipo_Suelo"].value_counts().reset_index()
            suelo_df.columns = ["Suelo", "Cantidad"]
            st.table(suelo_df)

        st.subheader("Explorador de Datos Crudos")
        st.dataframe(df_selection, use_container_width=True)

    # --- BLOQUE 3: GRÁFICO ---
    with tab_graf:
        st.header("Visualización de Tendencias")
        
        # Gráfico de Barras - Producción por Departamento (Colores originales de Plotly)
        fig_bar = px.bar(
            df_selection.groupby("Departamento")["Produccion_Anual_Ton"].sum().reset_index(),
            x="Departamento", 
            y="Produccion_Anual_Ton",
            title="Producción Total por Departamento",
            color="Departamento",
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            # Gráfico de Torta - Cultivos
            fig_pie = px.pie(
                df_selection, 
                names="Tipo_Cultivo", 
                values="Produccion_Anual_Ton",
                title="Participación por Cultivo",
                hole=0.3
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_g2:
            # Scatter Plot - Área vs Producción
            fig_scatter = px.scatter(
                df_selection,
                x="Area_Hectareas",
                y="Produccion_Anual_Ton",
                color="Nivel_Tecnificacion",
                size="Precio_Venta_Por_Ton_COP",
                title="Área vs Producción (Tamaño por Precio)",
                template="ggplot2" # Un estilo clásico y legible
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

else:
    # Pantalla de bienvenida si no hay archivo
    st.warning("⚠️ Esperando archivo CSV...")
    st.info("Por favor, sube el archivo 'agro_colombia.csv' desde la barra lateral izquierda.")
    st.image("https://www.agrifuturo.com/wp-content/uploads/2021/05/agronomo-scaled.jpg", caption="Dashboard Agro Industrial")
