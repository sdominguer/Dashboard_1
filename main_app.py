import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="AgroAnalytics Pro",
    layout="wide",
    page_icon="🌾",
    initial_sidebar_state="expanded"
)

# --- PALETA TIERRA (Contrastada para ambos modos) ---
# Usamos tonos que se ven bien sobre blanco Y sobre negro
EARTH_PALETTE = ["#556B2F", "#8B4513", "#CD853F", "#DAA520", "#BC8F8F", "#2E8B57"]

# --- CSS MÍNIMO (SOLO PARA ESPACIADO, NO COLORES) ---
st.markdown("""
    <style>
    /* Aumentar el espacio superior para que no se vea pegado */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Ocultar el menú de hamburguesa default para limpieza */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- FUNCIÓN DE CARGA ---
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    if 'Fecha_Ultima_Auditoria' in df.columns:
        df['Fecha_Ultima_Auditoria'] = pd.to_datetime(df['Fecha_Ultima_Auditoria'])
    return df

# --- SIDEBAR: LIMPIO Y ORGANIZADO ---
with st.sidebar:
    st.title("🚜 Panel de Control")
    st.markdown("Configura los parámetros de tu análisis.")
    
    uploaded_file = st.file_uploader("📂 Cargar Datos (CSV)", type=["csv"])
    
    st.divider() # Línea separadora elegante

    if uploaded_file:
        df_raw = load_data(uploaded_file)
        
        # Filtros colapsables para ahorrar espacio
        with st.expander("📍 Filtros de Ubicación", expanded=True):
            all_depts = sorted(df_raw["Departamento"].unique())
            sel_depts = st.multiselect("Departamentos", all_depts, default=all_depts[:2])
            
        with st.expander("🌿 Filtros de Cultivo"):
            all_crops = sorted(df_raw["Tipo_Cultivo"].unique())
            sel_crops = st.multiselect("Cultivos", all_crops, default=all_crops)
            
        with st.expander("⚙️ Simulador de Precio"):
            # Slider interactivo que afecta proyecciones
            price_factor = st.slider("Ajuste de Precio de Mercado (%)", 80, 120, 100, help="Simula una caída o subida de precios en el mercado.")

# --- LÓGICA PRINCIPAL ---
if uploaded_file and sel_depts and sel_crops:
    # Aplicar filtros
    df = df_raw[
        (df_raw["Departamento"].isin(sel_depts)) & 
        (df_raw["Tipo_Cultivo"].isin(sel_crops))
    ].copy()

    # TÍTULO PRINCIPAL
    st.title("🌾 Inteligencia de Negocios Agrícola")
    st.markdown(f"Mostrando datos para **{len(sel_depts)} departamentos** y **{len(sel_crops)} tipos de cultivo**.")
    st.markdown("---")

    # --- SECCIÓN 1: KPIS (TARJETAS LIMPIAS) ---
    # Usamos st.container(border=True) para que se vean organizados
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    # Cálculos
    total_prod = df["Produccion_Anual_Ton"].sum()
    total_area = df["Area_Hectareas"].sum()
    avg_price = df["Precio_Venta_Por_Ton_COP"].mean()
    # Precio simulado basado en el slider
    simulated_income = (total_prod * avg_price) * (price_factor / 100)

    with kpi1:
        with st.container(border=True):
            st.metric("Total Producción", f"{total_prod:,.0f} Ton", delta="vs año anterior (est.)")
    
    with kpi2:
        with st.container(border=True):
            st.metric("Área Cultivada", f"{total_area:,.0f} Ha")
            
    with kpi3:
        with st.container(border=True):
            st.metric("Ingresos Proyectados", f"${simulated_income:,.0f}", delta=f"{price_factor-100}% ajuste precio")

    with kpi4:
        with st.container(border=True):
            st.metric("Fincas Activas", f"{len(df)}")

    st.markdown("###") # Espacio en blanco

    # --- SECCIÓN 2: GRÁFICOS INTERACTIVOS (TABS) ---
    tab_panorama, tab_detalles, tab_scatter = st.tabs(["📊 Panorama General", "🔬 Detalles Técnicos", "📍 Relación Variables"])

    # TAB 1: VISIÓN GENERAL
    with tab_panorama:
        st.subheader("Distribución de la Producción")
        
        col_graf1, col_graf2 = st.columns([2, 1], gap="large") # gap="large" da el espacio que pediste
        
        with col_graf1:
            # Gráfico de Barras Limpio
            fig_bar = px.bar(
                df.groupby("Departamento")["Produccion_Anual_Ton"].sum().reset_index().sort_values("Produccion_Anual_Ton", ascending=True),
                x="Produccion_Anual_Ton", y="Departamento",
                orientation='h',
                title="<b>Producción por Departamento</b>",
                color_discrete_sequence=[EARTH_PALETTE[0]],
                template="plotly_white"
            )
            # Quitamos bordes y fondos extraños
            fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Toneladas", yaxis_title="")
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_graf2:
            # Donut Chart
            fig_pie = px.pie(
                df, names="Tipo_Cultivo", values="Area_Hectareas",
                title="<b>Uso del Suelo (Ha)</b>",
                color_discrete_sequence=EARTH_PALETTE,
                hole=0.5,
                template="plotly_white"
            )
            fig_pie.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig_pie, use_container_width=True)

    # TAB 2: DETALLES TÉCNICOS
    with tab_detalles:
        st.subheader("Análisis de Calidad")
        
        col_d1, col_d2 = st.columns(2, gap="medium")
        
        with col_d1:
            with st.container(border=True):
                st.markdown("**🌱 Tecnificación vs Riego**")
                # Sunburst para ver jerarquía
                fig_sun = px.sunburst(
                    df, path=['Nivel_Tecnificacion', 'Sistema_Riego_Tecnificado'], 
                    values='Produccion_Anual_Ton',
                    color_discrete_sequence=EARTH_PALETTE,
                    template="plotly_white"
                )
                st.plotly_chart(fig_sun, use_container_width=True)
                
        with col_d2:
            with st.container(border=True):
                st.markdown("**🍂 Precios por Tipo de Suelo**")
                # Box Plot limpio
                fig_box = px.box(
                    df, x="Tipo_Suelo", y="Precio_Venta_Por_Ton_COP",
                    color="Tipo_Suelo",
                    color_discrete_sequence=EARTH_PALETTE,
                    template="plotly_white"
                )
                fig_box.update_layout(showlegend=False)
                st.plotly_chart(fig_box, use_container_width=True)

    # TAB 3: SCATTER (INTERACTIVO)
    with tab_scatter:
        st.subheader("Análisis de Eficiencia")
        st.caption("Usa el zoom en el gráfico para explorar fincas específicas.")
        
        # Scatter Plot Grande
        fig_scatter = px.scatter(
            df, 
            x="Area_Hectareas", 
            y="Produccion_Anual_Ton",
            color="Departamento",
            size="Precio_Venta_Por_Ton_COP",
            hover_name="ID_Finca",
            hover_data=["Tipo_Cultivo", "Nivel_Tecnificacion"],
            color_discrete_sequence=EARTH_PALETTE,
            template="plotly_white",
            title="<b>Relación Área vs. Producción</b> (El tamaño de la burbuja es el precio)"
        )
        fig_scatter.update_layout(height=500, plot_bgcolor="rgba(0,0,0,0)")
        fig_scatter.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#EEE')
        fig_scatter.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#EEE')
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- DATA TABLE AL FINAL ---
    with st.expander("📋 Ver Datos Detallados (Tabla)", expanded=False):
        st.dataframe(
            df.style.background_gradient(cmap="YlOrBr", subset=["Produccion_Anual_Ton", "Precio_Venta_Por_Ton_COP"]),
            use_container_width=True
        )
        
        # Botón de descarga
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV Filtrado",
            data=csv,
            file_name="reporte_agro_clean.csv",
            mime="text/csv"
        )

elif not uploaded_file:
    # PANTALLA DE INICIO LIMPIA
    st.container()
    col_center, _ = st.columns([1, 0.1])
    with col_center:
        st.info("👋 **Bienvenido.** Por favor cargue su archivo `agro_colombia.csv` en el menú lateral.")
        # Imagen de alta calidad
        st.image("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1000&auto=format&fit=crop", caption="Agro Data Analytics", use_column_width=True)
