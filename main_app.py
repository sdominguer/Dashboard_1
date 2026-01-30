import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Agropecuario Colombia", layout="wide")

# Carga de datos
@st.cache_data
def load_data():
    df = pd.read_csv("agro_colombia.csv")
    df['Fecha_Ultima_Auditoria'] = pd.to_datetime(df['Fecha_Ultima_Auditoria'])
    return df

try:
    df = load_data()

    # --- TÍTULO Y SIDEBAR ---
    st.title("🚜 Análisis de Producción Agrícola - Colombia")
    st.sidebar.header("Filtros de Búsqueda")

    # Filtros dinámicos
    departamentos = st.sidebar.multiselect(
        "Selecciona Departamento(s):",
        options=df["Departamento"].unique(),
        default=df["Departamento"].unique()
    )

    cultivos = st.sidebar.multiselect(
        "Selecciona Tipo de Cultivo:",
        options=df["Tipo_Cultivo"].unique(),
        default=df["Tipo_Cultivo"].unique()
    )

    # Filtrado del dataframe
    df_selection = df.query(
        "Departamento == @departamentos & Tipo_Cultivo == @cultivos"
    )

    # --- KPI'S PRINCIPALES ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Hectáreas", f"{df_selection['Area_Hectareas'].sum():,.1f} ha")
    with col2:
        st.metric("Producción Total", f"{df_selection['Produccion_Anual_Ton'].sum():,.1f} Ton")
    with col3:
        st.metric("Precio Promedio/Ton", f"${df_selection['Precio_Venta_Por_Ton_COP'].mean():,.0f} COP")
    with col4:
        st.metric("N° de Fincas", len(df_selection))

    st.markdown("---")

    # --- GRÁFICOS ---
    left_column, right_column = st.columns(2)

    # Gráfico 1: Producción por Departamento
    fig_prod_dept = px.bar(
        df_selection.groupby("Departamento")["Produccion_Anual_Ton"].sum().reset_index(),
        x="Produccion_Anual_Ton",
        y="Departamento",
        orientation="h",
        title="<b>Producción Total por Departamento</b>",
        color_discrete_sequence=["#2E7D32"] * len(df_selection),
        template="plotly_white",
    )
    left_column.plotly_chart(fig_prod_dept, use_container_width=True)

    # Gráfico 2: Distribución de Cultivos (Donut Chart)
    fig_cultivo = px.pie(
        df_selection, 
        names="Tipo_Cultivo", 
        values="Produccion_Anual_Ton",
        title="<b>Distribución por Tipo de Cultivo</b>",
        hole=0.4
    )
    right_column.plotly_chart(fig_cultivo, use_container_width=True)

    st.markdown("---")

    # --- RELACIÓN ÁREA VS PRODUCCIÓN ---
    fig_scatter = px.scatter(
        df_selection,
        x="Area_Hectareas",
        y="Produccion_Anual_Ton",
        color="Nivel_Tecnificacion",
        size="Precio_Venta_Por_Ton_COP",
        hover_name="ID_Finca",
        title="<b>Relación Área vs. Producción (Color por Tecnificación)</b>",
        labels={"Area_Hectareas": "Área (Ha)", "Produccion_Anual_Ton": "Producción (Ton)"}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Vista de Datos
    with st.expander("Ver base de datos filtrada"):
        st.dataframe(df_selection)

except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.info("Asegúrate de que el archivo 'agro_colombia.csv' esté en la misma carpeta que este script.")
