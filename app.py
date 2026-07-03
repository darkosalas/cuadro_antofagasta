import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# 1. CONFIGURACIÓN E INTERFAZ BASE DEL PANEL
st.set_page_config(
    page_title="Gestión de Residuos - Antofagasta",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS avanzados para replicar un diseño premium de Dashboard (Tarjetas CMI)
st.markdown("""
    <style>
    body {
        background-color: #f4f6f9;
    }
    .kpi-container {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        border-top: 5px solid #1E3A8A;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        text-align: center;
        margin-bottom: 20px;
    }
    .kpi-title {
        font-size: 13px;
        color: #6B7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 32px;
        color: #111827;
        font-weight: 700;
    }
    .kpi-sub {
        font-size: 12px;
        color: #059669;
        font-weight: 500;
        margin-top: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# Menú de Navegación Lateral (Estilo Oscuro Nativo)
st.sidebar.title("🧭 Panel Operativo")
st.sidebar.subheader("Borde Costero Antofagasta")
st.sidebar.write("---")

vista_seleccionada = st.sidebar.radio(
    "Seleccione la pantalla a visualizar:",
    ["1. Vista Estratégica (CMI)", "2. Vista Operativa (Mapa Satelital)", "3. Configuración de Alertas"]
)

# ==============================================================================
# 2. BASE DE DATOS OPTIMIZADA (PUNTOS CRÍTICOS Y SENSORES)
# ==============================================================================
@st.cache_data
def inicializar_datos_borde_costero():
    # Coordenadas y métricas reales simuladas para los puntos críticos de Antofagasta
    return pd.DataFrame({
        'id': [1, 2, 3, 4],
        'sector': ['Caleta Poza del Salitre', 'Borde Costero Terminal', 'Muelle Histórico', 'Sector Playa Las Almejas'],
        'lat': [-23.6412, -23.6428, -23.6457, -23.6692],
        'lon': [-70.4007, -70.3996, -70.3972, -70.4104],
        'llenado_actual': [88, 92, 54, 30], # % medido por sensores ultrasónicos
        'infracciones_2025': [5, 8, 3, 2],
        'infracciones_2026': [2, 4, 3, 1],
        'costo_fijo': [5000, 5000, 5000, 5000],
        'costo_variable': [12000, 14500, 9000, 6200],
        'toneladas': [1.2, 1.5, 0.9, 0.7]
    })

df_datos = inicializar_datos_borde_costero()

# ==============================================================================
# 3. LÓGICA Y RENDERIZADO DE LAS PANTALLAS INTERACTIVAS
# ==============================================================================

# --- PANTALLA 1: CUADRO DE MANDO INTEGRAL (ESTRATEGIA) ---
if vista_seleccionada == "1. Vista Estratégica (CMI)":
    st.title("📊 Cuadro de Mando Integral Público-Ambiental")
    st.caption("Fase 3: Monitoreo automatizado y balanceado de las 4 perspectivas del modelo")
    st.write("---")
    
    # --- CÁLCULO EN TIEMPO REAL CON LAS FÓRMULAS ESTRATÉGICAS ---
    # Perspectiva 1: Sostenibilidad Ambiental (Tasa de Mitigación)
    inf_25 = df_datos['infracciones_2025'].sum()
    inf_26 = df_datos['infracciones_2026'].sum()
    tasa_mitigacion = ((inf_25 - inf_26) / inf_25) * 100
    
    # Perspectiva 2: Procesos Logísticos (% de Contenedores Críticos >= 75%)
    total_contenedores = len(df_datos)
    criticos = len(df_datos[df_datos['llenado_actual'] >= 75])
    pct_criticos = (criticos / total_contenedores) * 100
    
    # Perspectiva 4: Financiera y Eficiencia (Costo Promedio por Tonelada)
    costo_total = df_datos['costo_fijo'].sum() + df_datos['costo_variable'].sum()
    ton_totales = df_datos['toneladas'].sum()
    costo_por_tonelada = costo_total / ton_totales
    
    # --- DESPLIEGUE EN MATRIZ DE LAS 4 TARJETAS DEL CMI ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">🌿 Sostenibilidad Ambiental</div>
                <div class="kpi-value">{tasa_mitigacion:.1f}%</div>
                <div class="kpi-sub">Mitigación de Infracciones</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">🚚 Procesos Logísticos</div>
                <div class="kpi-value">{pct_criticos:.1f}%</div>
                <div class="kpi-sub">Nivel Crítico de Contenedores</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class="kpi-container">
                <div class="kpi-title">👥 Usuarios y Gobernanza</div>
                <div class="kpi-value">86.4%</div>
                <div class="kpi-sub">Índice Satisfacción Vecinal</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">💰 Financiera y Eficiencia</div>
                <div class="kpi-value">${costo_por_tonelada:,.0f}</div>
                <div class="kpi-sub">Costo Medio por Tonelada</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("##")
    
    # --- GRÁFICOS DE ANÁLISIS ESTRATÉGICO ---
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("Análisis de Infracciones Sanitarias (Comparativa Anual)")
        df_inf = pd.DataFrame({
            'Sector': df_datos['sector'],
            'Año Anterior (2025)': df_datos['infracciones_2025'],
            'Año Actual (2026)': df_datos['infracciones_2026']
        }).set_index('Sector')
        st.bar_chart(df_inf)
        
    with col_g2:
        st.subheader("Distribución de Costos Logísticos Operativos ($)")
        df_costos = pd.DataFrame({
            'Sector': df_datos['sector'],
            'Costos Fijos': df_datos['costo_fijo'],
            'Costos Variables': df_datos['costo_variable']
        }).set_index('Sector')
        st.area_chart(df_costos)

# --- PANTALLA 2: MAPA SATELITAL INTERACTIVO (OPERATIVO) ---
elif vista_seleccionada == "2. Vista Operativa (Mapa Satelital)":
    st.title("🗺️ Mapa de Monitoreo Satelital en Tiempo Real")
    st.caption("Localización de puntos críticos costeros protegidos mediante marcas difuminadas (Sin contaminación visual)")
    st.write("---")
    
    # Crear mapa base centrado en el área de estudio del borde costero de Antofagasta
    mapa = folium.Map(location=[-23.644, -70.399], zoom_start=15, tiles="Cartodb Positron")
    
    # Inyectar marcas traslúcidas difuminadas simulando los radios de influencia e IoT
    for _, row in df_datos.iterrows():
        if row['llenado_actual'] >= 75:
            color_difuminado = "#EF4444" # Rojo de Alerta Crítica
            estado_texto = "CRÍTICO (Supera umbral óptimo del 75%)"
            radio_mancha = 50 # Radio extendido para visibilidad de urgencia
        elif row['llenado_actual'] >= 50:
            color_difuminado = "#F59E0B" # Amarillo de Monitoreo Preventivo
            estado_texto = "Atención (Nivel Medio)"
            radio_mancha = 35
        else:
            color_difuminado = "#10B981" # Verde de Estado Normal
            estado_texto = "Normal"
            radio_mancha = 20
            
        # Añadir círculo difuminado al mapa (Efecto traslúcido inteligente)
        folium.Circle(
            location=[row['lat'], row['lon']],
            radius=radio_mancha,
            popup=f"<b>Sector:</b> {row['sector']}<br><b>Llenado:</b> {row['llenado_actual']}%<br><b>Estado:</b> {estado_texto}",
            color=color_difuminado,
            fill=True,
            fill_color=color_difuminado,
            fill_opacity=0.55,
            weight=0 # Oculta la línea externa sólida logrando el look difuminado
        ).add_to(mapa)
    
    # Renderizar el mapa de Folium dentro del ecosistema Streamlit
    st_folium(mapa, width=1100, height=530)
    
    # Tabla de auditoría inferior
    st.write("##")
    st.subheader("📋 Estado Actual de la Infraestructura de Recolección")
    st.dataframe(
        df_datos[['sector', 'llenado_actual']].rename(
            columns={'sector': 'Punto Crítico Costero', 'llenado_actual': 'Volumen Ocupado (%)'}
        ),
        use_container_width=True
    )

# --- PANTALLA 3: CONFIGURACIÓN DE ALERTAS ---
elif vista_seleccionada == "3. Configuración de Alertas":
    st.title("⚙️ Configuración del Motor de Alertas IoT")
    st.caption("Módulo de administración para optimización de parámetros logísticos")
    st.write("---")
    
    st.subheader("Ajuste de Parámetros Matemáticos")
    umbral_ru = st.slider("Definir nivel crítico para activar el algoritmo de rutas óptimas (%):", 60, 100, 75)
    
    st.subheader("Canales Automatizados de Notificación (Webhooks)")
    st.checkbox("Habilitar despacho automático a la API de Telegram para Supervisores en Terreno", value=True)
    st.checkbox("Habilitar envío de informes ejecutivos a la Gobernanza Marítima y Municipalidad", value=False)
    
    st.write("##")
    if st.button("Aplicar Configuración Operativa"):
        st.success(f"Configuración guardada de manera exitosa. El sistema disparará órdenes automáticas al alcanzar el {umbral_ru}% de volumen.")
