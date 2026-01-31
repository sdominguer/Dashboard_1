import streamlit as st
import pandas as pd
import plotly.express as px
import os
# Importamos la librería de Groq (asegúrate de instalarla)
try:
    from groq import Groq
except ImportError:
    st.error("⚠️ Falta la librería 'groq'. Por favor agrégala a requirements.txt")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="AgroAnalytics Pro + AI",
    layout="wide",
    page_icon="🌾",
    initial_sidebar_state="expanded"
)

# --- PALETA TIERRA ---
EARTH_PALETTE = ["#556B2F", "#8B4513", "#CD853F", "#DAA520", "#BC8F8F", "#2E8B57"]

# --- CSS LIMPIO ---
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stApp { background-color: #FFFFFF; color: #1E1E1E; }
    div[data-testid="metric-container"] {
        background-color: #F9FBF9;
        border: 1px solid #E0E4D9;
        border-top: 4px solid #556B2F;
        padding: 15px;
        border-radius: 8px;
    }
    /* Estilo para el chat */
    .stChatMessage { background-color: #F1F3F0; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIÓN DE CARGA ---
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    if 'Fecha_Ultima_Auditoria' in df.columns:
        df['Fecha_Ultima_Auditoria'] = pd.to_datetime(df['Fecha_Ultima_Auditoria'])
    return df

# --- FUNCIÓN GENERADOR DE CONTEXTO PARA LA IA ---
def get_dataframe_context(df):
    """Crea un resumen textual de los datos para que la IA los entienda."""
    desc = df.describe().to_string()
    cols = ", ".join(df.columns)
    sample = df.head(3).to_string()
    total_rows = len(df)
    
    context = f"""
    Eres un experto analista agrónomo. Tienes acceso a un dataset con {total_rows} registros.
    Columnas disponibles: {cols}.
    
    Estadísticas descriptivas (promedios, máx, min):
    {desc}
    
    Muestra de las primeras filas:
    {sample}
    
    Tu objetivo es encontrar patrones, anomalías o sugerir mejoras basadas en estos datos.
    Responde siempre en español, de forma profesional y ejecutiva.
    """
    return context

# --- SIDEBAR ---
with st.sidebar:
    st.title("🚜 Panel de Control")
    uploaded_file = st.file_uploader("📂 Cargar Datos (CSV)", type=["csv"])
    
    st.divider()

    # --- SECCIÓN API KEY ---
    st.subheader("🤖 Configuración IA")
    groq_api_key = st.text_input("Groq API Key", type="password", help="Obtén tu key gratis en console.groq.com")
    
    st.divider()

    if uploaded_file:
        df_raw = load_data(uploaded_file)
        
        with st.expander("📍 Filtros de Ubicación", expanded=True):
            all_depts = sorted(df_raw["Departamento"].unique())
            sel_depts = st.multiselect("Departamentos", all_depts, default=all_depts[:2])
            
        with st.expander("🌿 Filtros de Cultivo"):
            all_crops = sorted(df_raw["Tipo_Cultivo"].unique())
            sel_crops = st.multiselect("Cultivos", all_crops, default=all_crops)
            
        eficiencia = st.slider("Simular incremento (%)", 0, 200, 100)

# --- LÓGICA PRINCIPAL ---
if uploaded_file and sel_depts and sel_crops:
    # Aplicar filtros
    df = df_raw[
        (df_raw["Departamento"].isin(sel_depts)) & 
        (df_raw["Tipo_Cultivo"].isin(sel_crops))
    ].copy()

    st.title("🌾 Inteligencia de Negocios Agrícola")
    st.markdown("---")

    # --- KPIS ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    prod_total = df["Produccion_Anual_Ton"].sum()
    with kpi1:
        with st.container(border=True):
            st.metric("Total Producción", f"{prod_total:,.0f} Ton")
    with kpi2:
        with st.container(border=True):
            st.metric("Área Cultivada", f"{df['Area_Hectareas'].sum():,.0f} Ha")
    with kpi3:
        with st.container(border=True):
            st.metric("Precio Promedio", f"${df['Precio_Venta_Por_Ton_COP'].mean():,.0f}")
    with kpi4:
        with st.container(border=True):
            st.metric("Fincas Filtradas", f"{len(df)}")

    st.markdown("###") 

    # --- TABS CON IA INCLUIDA ---
    tab_panorama, tab_detalles, tab_scatter, tab_ai = st.tabs([
        "📊 Panorama General", 
        "🔬 Detalles Técnicos", 
        "📍 Relación Variables",
        "🤖 IA Agrónoma"
    ])

    # ... (TAB 1, 2 y 3 se mantienen igual para ahorrar espacio visual en el código, 
    # pero aquí está la TAB 4 NUEVA) ...
    
    with tab_panorama:
        # Gráficos básicos para contexto
        col_g1, col_g2 = st.columns([2, 1], gap="large")
        with col_g1:
            fig_bar = px.bar(
                df.groupby("Departamento")["Produccion_Anual_Ton"].sum().reset_index(),
                x="Produccion_Anual_Ton", y="Departamento", orientation='h',
                color_discrete_sequence=[EARTH_PALETTE[0]], template="plotly_white",
                title="<b>Producción por Departamento</b>"
            )
            fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_g2:
            fig_pie = px.pie(
                df, names="Tipo_Cultivo", values="Area_Hectareas",
                color_discrete_sequence=EARTH_PALETTE, hole=0.5, template="plotly_white",
                title="<b>Uso del Suelo</b>"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with tab_detalles:
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            fig_sun = px.sunburst(
                df, path=['Nivel_Tecnificacion', 'Sistema_Riego_Tecnificado'], 
                values='Produccion_Anual_Ton', color_discrete_sequence=EARTH_PALETTE
            )
            st.plotly_chart(fig_sun, use_container_width=True)
        with col_d2:
             # Tabla de precios
             st.dataframe(df.groupby("Tipo_Suelo")["Precio_Venta_Por_Ton_COP"].mean().reset_index(), use_container_width=True)

    with tab_scatter:
        fig_scatter = px.scatter(
            df, x="Area_Hectareas", y="Produccion_Anual_Ton",
            color="Departamento", size="Precio_Venta_Por_Ton_COP",
            color_discrete_sequence=EARTH_PALETTE, template="plotly_white",
            title="<b>Análisis de Eficiencia</b>"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- AQUÍ ESTÁ LA NUEVA PESTAÑA DE IA ---
    with tab_ai:
        st.subheader("🧠 Asistente de Análisis Inteligente (Llama 3.3)")
        
        if not groq_api_key:
            st.warning("⚠️ Por favor ingresa tu **Groq API Key** en la barra lateral izquierda para activar el cerebro de la IA.")
            st.info("💡 Puedes obtener una gratis en [console.groq.com](https://console.groq.com).")
        else:
            # Inicializar cliente
            client = Groq(api_key=groq_api_key)
            
            # Historial de chat en session_state
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Mostrar mensajes previos
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Input del usuario
            if prompt := st.chat_input("Ej: ¿Qué departamento tiene el mejor rendimiento por hectárea?"):
                # Mostrar mensaje del usuario
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Generar respuesta
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    try:
                        # Crear contexto de datos actualizado
                        data_context = get_dataframe_context(df)
                        
                        # Llamada a Groq
                        completion = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {"role": "system", "content": data_context},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.5,
                            max_tokens=1024,
                            stream=True
                        )
                        
                        # Stream de respuesta
                        for chunk in completion:
                            if chunk.choices[0].delta.content:
                                full_response += chunk.choices[0].delta.content
                                message_placeholder.markdown(full_response + "▌")
                        
                        message_placeholder.markdown(full_response)
                        
                        # Guardar en historial
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        
                    except Exception as e:
                        st.error(f"Error al conectar con Groq: {e}")

elif not uploaded_file:
    st.info("Carga el archivo CSV para comenzar.")
