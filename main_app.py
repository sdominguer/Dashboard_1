import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Analizador de Datos Agrícolas", layout="wide", page_icon="🌱")

st.title("🚜 Dashboard Agrícola Personalizable")
st.markdown("Sube tu archivo CSV con los datos de las fincas para comenzar el análisis.")

# --- CARGA DE ARCHIVO ---
uploaded_file = st.sidebar.file_uploader("Carga tu archivo CSV aquí", type=["csv"])

if uploaded_file is not None:
    try:
        # Leer el archivo cargado
        df = pd.read_csv(uploaded_file)
        
        # Convertir fecha si existe la columna
        if 'Fecha_Ultima_Auditoria' in df.columns:
            df['Fecha_Ultima_Auditoria'] = pd.to_datetime(df['Fecha_Ultima_Auditoria'])

        # --- BARRA LATERAL (FILTROS) ---
        st.sidebar.header("Filtros de Datos")
        
        # Filtro de Departamento
        depts = df["Departamento"].unique()
        sel_depts = st.sidebar.multiselect("Departamentos:", options=depts, default=depts)

        # Filtro de Cultivo
        cultivos = df["Tipo_Cultivo"].unique()
        sel_cultivos = st.sidebar.multiselect("Tipo de Cultivo:", options=cultivos, default=cultivos)

        # Aplicar filtros
        df_selection = df.query("Departamento == @sel_depts & Tipo_Cultivo == @sel_cultivos")

        if df_selection.empty:
            st.warning("No hay datos que coincidan con los filtros seleccionados.")
        else:
            # --- MÉTRICAS (KPIs) ---
            m1, m2, m3 = st.columns(3)
            m1.metric("Hectáreas Totales", f"{df_selection['Area_Hectareas'].sum():,.1f} ha")
            m2.metric("Producción Total", f"{df_selection['Produccion_Anual_Ton'].sum():,.1f} Ton")
            m3.metric("Precio Promedio Ton", f"${df_selection['Precio_Venta_Por_Ton_COP'].mean():,.0f}")

            st.divider()

            # --- VISUALIZACIONES ---
            col_left, col_right = st.columns(2)

            with col_left:
                # Top Departamentos por Producción
                fig_bar = px.bar(
                    df_selection.groupby("Departamento")["Produccion_Anual_Ton"].sum().nlargest(10).reset_index(),
                    x="Produccion_Anual_Ton",
                    y="Departamento",
                    orientation="h",
                    title="Top 10 Departamentos (Producción)",
                    color_discrete_sequence=["#4CAF50"]
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_right:
                # Distribución de Suelos
                fig_pie = px.pie(
                    df_selection, 
                    names="Tipo_Suelo", 
                    title="Distribución por Tipo de Suelo",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            # Gráfico de Dispersión: Área vs Producción
            fig_scatter = px.scatter(
                df_selection,
                x="Area_Hectareas",
                y="Produccion_Anual_Ton",
                size="Precio_Venta_Por_Ton_COP",
                color="Nivel_Tecnificacion",
                hover_name="ID_Finca",
                title="Relación Tamaño vs. Productividad",
                labels={"Area_Hectareas": "Área (Ha)", "Produccion_Anual_Ton": "Producción (Ton)"},
                template="plotly_dark"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

            # Tabla de datos crudos
            with st.expander("🔍 Explorar tabla de datos completa"):
                st.dataframe(df_selection, use_container_width=True)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        st.info("Asegúrate de que el CSV tenga las columnas: Departamento, Tipo_Cultivo, Area_Hectareas, Produccion_Anual_Ton, etc.")

else:
    # Estado inicial cuando no hay archivo
    st.info("👆 Por favor, sube un archivo CSV desde la barra lateral para generar el dashboard.")
    
    # Imagen de referencia o placeholder
    st.image("https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=1000", caption="Análisis de agro-datos")
