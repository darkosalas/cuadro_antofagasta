import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import time
import random

# 1. CONFIGURACIÓN E INTERFAZ BASE DEL PANEL
st.set_page_config(
    page_title="Gestión de Residuos - Antofagasta",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS avanzados para las Tarjetas CMI
st.markdown("""
    <style>
    body { background-color: #f4f6f9; }
    .kpi-container {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        border-top: 5px solid #1E3A8A;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 20px;
    }
    .kpi-title { font-size: 13px; color: #6B7280; font-weight: 600; text-transform: uppercase; margin-bottom: 10px; }
    .kpi-value { font-size: 32px; color: #111827; font-weight: 700; }
    .kpi-sub { font-size: 12px; color: #059669; font-weight: 500; margin-top: 6px; }
    </style>
""", unsafe_allow_html=True)

# Menú de Navegación Lateral
st.sidebar.title("🧭 Panel Operativo")
st.sidebar.subheader("Borde Costero Antofagasta")
st.sidebar.write("---")

# Controles de la Simulación en la Barra Lateral
st.sidebar.markdown("### ⚙️ Control de Simulación")
simulacion_activa = st.sidebar.toggle("Activar Simulación en Tiempo Real", value=True)
velocidad_sim = st.sidebar.slider("Velocidad de actualización (segundos):", 2, 10, 4)

st.sidebar.write("---")
vista_seleccionada = st.sidebar.radio(
    "Seleccione la pantalla a visualizar:",
    ["1. Vista Estratégica (CMI)", "2. Vista Operativa (Mapa Satelital)", "3. Configuración de Alertas"]
)

# ==============================================================================
# 2. SISTEMA DE DATOS Y SIMULACIÓN INTERACTIVA
# ==============================================================================
# Inicializamos las variables en el estado de la sesión si no existen
if 'datos_simulados' not in st.session_state:
    st.session_state.datos_simulados = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'sector': ['Caleta Poza del Salitre', 'Borde Costero Terminal', 'Muelle Histórico', 'Sector Playa Las Almejas'],
        'lat': [-23.6412, -23.6428, -23.6457, -23.6692],
        'lon': [-70.4007, -70.3996, -70.3972, -70.4104],
        'llenado_actual': [72.0, 85.0, 40.0, 25.0], 
        'infracciones_2025': [5, 8, 3, 2],
        'infracciones_2026': [2, 4, 3, 1],
        'costo_fijo': [5000, 5000, 5000, 5000],
        'costo_variable': [12000, 14500, 9000, 6200],
        'toneladas': [1.2, 1.5, 0.9, 0.7]
    })

# Modificar valores aleatoriamente si la simulación está encendida
if simulacion_activa:
    nuevos_niveles = []
    nuevas_toneladas = []
    for _, fila in st.session_state.datos_simulados.iterrows():
        # Generar una fluctuación de llenado entre -8% y +12% para simular acumulación
        cambio = random.uniform(-8.0, 12.0)
        nuevo_llenado = max(0.0, min(100.0, fila['llenado_actual'] + cambio))
        nuevos_niveles.append(nuevo_llenado)
        # Escalar las toneladas de manera proporcional al nivel de llenado
        nuevas_toneladas.append(round((nuevo_llenado / 100.0) * 1.6, 2))
        
    st.session_state.datos_simulados['llenado_actual'] = nuevos_niveles
    st.session_state.datos_simulados['toneladas'] = nuevas_toneladas

df_datos = st.session_state.datos_simulados

# ==============================================================================
# 3. LÓGICA DE LAS PANTALLAS
# ==============================================================================

# --- PANTALLA 1: CUADRO DE MANDO INTEGRAL (ESTRATEGIA) ---
if vista_seleccionada == "1. Vista Estratégica (CMI)":
    st.title("📊 Cuadro de Mando Integral Público-Ambiental")
    st.caption("Fase 3: Monitoreo balanceado con actualización automatizada mediante sensores IoT")
    st.write("---")
    
    # Cálculos dinámicos basados en la simulación actual
    inf_25 = df_datos['infracciones_2025'].sum()
    inf_26 = df_datos['infracciones_2026'].sum()
    tasa_mitigacion = ((inf_25 - inf_26) / inf_25) * 100
    
    total_contenedores = len(df_datos)
    criticos = len(df_datos[df_datos['llenado_actual'] >= 75])
    pct_criticos = (criticos / total_contenedores) * 100
    
    costo_total = df_datos['costo_fijo'].sum() + df_datos['costo_variable'].sum()
    ton_totales = df_datos['toneladas'].sum()
    costo_por_tonelada = costo_total / max(0.1, ton_totales) # Evitar división por cero
    
    # Renderizado de Tarjetas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">🌿 Sostenibilidad Ambiental</div><div class="kpi-value">{tasa_mitigacion:.1f}%</div><div class="kpi-sub">Mitigación Infracciones</div></div>', unsafe_allow_html=True)
    with col2:
        # Cambia dinámicamente el mensaje inferior según el estado crítico general
        sub_logistica = "Estado Óptimo" if pct_criticos == 0 else f"{pct_criticos:.0f}% en Nivel Crítico"
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">🚚 Procesos Logísticos</div><div class="kpi-value">{df_datos["llenado_actual"].mean():.1f}%</div><div class="kpi-sub">{sub_logistica}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="kpi-container"><div class="kpi-title">👥 Usuarios y Gobernanza</div><div class="kpi-value">86.4%</div><div class="kpi-sub">Satisfacción Vecinal</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">💰 Financiera y Eficiencia</div><div class="kpi-value">${costo_por_tonelada:,.0f}</div><div class="kpi-sub">Costo por Tonelada</div></div>', unsafe_allow_html=True)

    st.write("##")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Nivel de Volumen Actual por Contenedor (%)")
        df_volumen = pd.DataFrame({'Sector': df_datos['sector'], 'Ocupación (%)': df_datos['llenado_actual']}).set_index('Sector')
        st.bar_chart(df_volumen, color="#1E3A8A")
    with col_g2:
        st.subheader("Distribución Proporcional de Carga Simétrica (Toneladas)")
        df_ton = pd.DataFrame({'Sector': df_datos['sector'], 'Toneladas Métricas': df_datos['toneladas']}).set_index('Sector')
        st.area_chart(df_ton, color="#10B981")

# --- PANTALLA 2: MAPA SATELITAL INTERACTIVO (OPERATIVO) ---
elif vista_seleccionada == "2. Vista Operativa (Mapa Satelital)":
    st.title("🗺️ Mapa de Monitoreo Satelital en Tiempo Real")
    st.caption("Los círculos cambian dinámicamente de tamaño y color según el volumen medido por los sensores")
    st.write("---")
    
    mapa = folium.Map(location=[-23.644, -70.399], zoom_start=15, tiles="Cartodb Positron")
    
    for _, row in df_datos.iterrows():
        if row['llenado_actual'] >= 75:
            color_difuminado = "#EF4444"  # Alerta Roja
            estado_texto = "CRÍTICO"
            radio_mancha = 55
        elif row['llenado_actual'] >= 50:
            color_difuminado = "#F59E0B"  # Alerta Amarilla
            estado_texto = "PREVENTIVO"
            radio_mancha = 40
        else:
            color_difuminado = "#10B981"  # Estado Verde
            estado_texto = "NORMAL"
            radio_mancha = 25
            
        folium.Circle(
            location=[row['lat'], row['lon']],
            radius=radio_mancha,
            popup=f"<b>{row['sector']}</b><br>Llenado: {row['llenado_actual']:.1f}%<br>Estado: {estado_texto}",
            color=color_difuminado,
            fill=True,
            fill_color=color_difuminado,
            fill_opacity=0.6,
            weight=0
        ).add_to(mapa)
    
    st_folium(mapa, width=1100, height=500)
    
    st.write("##")
    st.subheader("📋 Datos Captados por Telemetría de Sensores")
    st.dataframe(df_datos[['sector', 'llenado_actual', 'toneladas']].style.format({'llenado_actual': '{:.1f}%', 'toneladas': '{:.2f} Ton'}), use_container_width=True)

# --- PANTALLA 3: CONFIGURACIÓN DE ALERTAS ---
else:
    st.title("⚙️ Configuración del Motor de Alertas IoT")
    st.write("---")
    st.info("El sistema está corriendo en modo simulación automática. Puedes desactivarlo en el interruptor de la barra lateral.")

# Mecanismo de autorefresco cíclico para gatillar la animación constante
if simulacion_activa:
    time.sleep(velocidad_sim)
    st.rerun()
