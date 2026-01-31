import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Agro-Interactive Pro", layout="wide", page_icon="🌾")

# --- ESTILO PARA ASEGURAR VISIBILIDAD ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2, h3, p { color: #2c3e50 !important; }
    .stMetric { border: 1px solid #e1e4e8; padding: 10px; border-radius: 10px; background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚜 Dashboard Agro-Interactivo Profesional")

# --- SIDEBAR: CONTROLES BACANOS ---
st.sidebar.header("🛠️ Panel de Control")
uploaded_file = st.sidebar.file_uploader("1. Sube tu base de datos (CSV)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['Fecha_Ultima_Auditoria'] = pd.to_datetime(df['Fecha_Ultima_Auditoria'])

    # 1. Slider para rango de Hectáreas
    min_ha = float(df["Area_Hectareas"].min())
    max_ha = float(df["Area_Hectareas"].max())
    rango_ha = st.sidebar.slider("Filtrar por Tamaño (Ha)", min_ha, max_ha, (min_ha, max_ha))

    # 2. Radio para enfoque de cultivo
    opciones_cultivo = ["Todos"] + list(df["Tipo_Cultivo"].unique())
    enfoque = st.sidebar.radio("Enfoque principal:", opciones_cultivo)

    # 3. Color Picker para personalizar las gráficas
    color_tema = st.sidebar.color_picker("Color de gráficas", "#B5EAD7")

    # 4. Date Input para auditorías
    fecha_min = df["Fecha_Ultima_Auditoria"].min().date()
    fecha_max = df["Fecha_Ultima_Auditoria"].max().date()
    fecha_sel = st.sidebar.date_input("Auditorías desde:", fecha_min)

    # --- LÓGICA DE FILTRADO DINÁMICO ---
    df_f = df[(df["Area_Hectareas"] >= rango_ha[0]) & (df["Area_Hectareas"] <= rango_ha[1])]
    df_f = df_f[df_f["Fecha_Ultima_Auditoria"].dt.date >= fecha_sel]
    
    if enfoque != "Todos":
        df_f = df_f[df_f["Tipo_Cultivo"] == enfoque]

    # --- ESTRUCTURA DE 3 BLOQUES ---
    tab_cuant, tab_cual, tab_graf = st.tabs(["🔢 CUANTITATIVO", "📄 CUALITATIVO", "📊 GRÁFICO"])

    # BLOQUE 1: CUANTITATIVO
    with tab_cuant:
        st.subheader("Indicadores de Rendimiento")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.metric("Total Hectáreas", f"{df_f['Area_Hectareas'].sum():,.1f} ha")
        with c2:
            st.metric("Producción Total", f"{df_f['Produccion_Anual_Ton'].sum():,.1f} Ton")
        with c3:
            st.metric("Precio Promedio", f"${df_f['Precio_Venta_Por_Ton_COP'].mean():,.0f}")

        st.info(f"💡 Estás viendo datos entre {rango_ha[0]} y {rango_ha[1]} Hectáreas.")
        st.write("### Desglose Estadístico")
        st.dataframe(df_f.describe().T, use_container_width=True)

    # BLOQUE 2: CUALITATIVO
    with tab_cual:
        st.subheader("Atributos y Gestión de Datos")
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.write("**Vista Previa de la Data Filtrada**")
            st.dataframe(df_f, use_container_width=True)
            
            # BOTÓN DE DESCARGA
            csv = df_f.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar datos filtrados (CSV)",
                data=csv,
                file_name='agro_data_filtrada.csv',
                mime='text/csv',
            )

        with col_right:
            st.write("**Nivel de Tecnificación**")
            st.bar_chart(df_f["Nivel_Tecnificacion"].value_counts(), color=color_tema)

    # BLOQUE 3: GRÁFICO
    with tab_graf:
        st.subheader("Visualizaciones Dinámicas")
        
        # Gráfico de barras usando el Color Picker
        fig_bar = px.bar(
            df_f.groupby("Departamento")["Produccion_Anual_Ton"].sum().reset_index(),
            x="Departamento", y="Produccion_Anual_Ton",
            title="Producción por Departamento",
            color_discrete_sequence=[color_tema],
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Scatter plot interactivo
        fig_scatter = px.scatter(
            df_f, x="Area_Hectareas", y="Produccion_Anual_Ton",
            color="Tipo_Suelo", size="Precio_Venta_Por_Ton_COP",
            hover_name="ID_Finca",
            title="Relación Área vs Producción (Color por Suelo)",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

else:
    # PANTALLA DE BIENVENIDA
    st.info("👋 ¡Hola! Para empezar, arrastra el archivo CSV al panel de la izquierda.")
    st.image(
        "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=1000", 
        caption="Análisis de agro-datos avanzado"
    )
    
