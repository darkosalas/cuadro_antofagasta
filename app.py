import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import time

# 1. CONFIGURACIÓN DEL ENTORNO INSTITUCIONAL
st.set_page_config(
    page_title="Cuadro de Mando Integral Público-Ambiental",
    layout="wide",
    initial_sidebar_state="expanded"
)

# REPLICACIÓN DE LA PALETA ESTÉTICA
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    [data-testid="stSidebar"] { background-color: #0e1e38 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .card-kpi { padding: 15px 20px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 15px; min-height: 125px; }
    .card-title { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #475569; margin-bottom: 4px; }
    .card-value { font-size: 28px; font-weight: 800; color: #1e293b; display: flex; align-items: center; gap: 5px; }
    .kpi-ambiental { background-color: #e6f4ea; border-top: 4px solid #137333; }
    .kpi-logistica { background-color: #feeee3; border-top: 4px solid #e67e22; }
    .kpi-comunidad { background-color: #f3e8fd; border-top: 4px solid #8430ce; }
    .kpi-financiera { background-color: #fef7e0; border-top: 4px solid #f2a104; }
    .alerta-operativo { background-color: #fef2f2; border-left: 5px solid #991b1b; color: #7f1d1d; padding: 15px; border-radius: 4px; font-weight: 500; margin-bottom: 15px; font-size: 13.5px; }
    .despacho-exito { background-color: #f0fdf4; border-left: 5px solid #16a34a; color: #14532d; padding: 15px; border-radius: 4px; font-weight: 500; margin-bottom: 15px; font-size: 13.5px; }
    </style>
""", unsafe_allow_html=True)

# 2. CONTROLADORES
st.sidebar.markdown("### 📋 PANEL OPERATIVO")
simulacion_activa = st.sidebar.toggle("Ejecutar Simulación IoT", value=True)
velocidad_sim = st.sidebar.slider("Barrido de tiempo (segundos):", 2, 10, 4)

if 'ciclo_actual' not in st.session_state: st.session_state.ciclo_actual = 0
if 'ruta_despachada' not in st.session_state: st.session_state.ruta_despachada = False

if st.sidebar.button("🔄 Reiniciar Parámetros Base"):
    st.session_state.ciclo_actual = 0
    st.session_state.ruta_despachada = False
    if 'datos_simulados' in st.session_state: del st.session_state['datos_simulados']
    st.rerun()

vista_seleccionada = st.sidebar.radio("Navegación del Sistema:", ["1. Vista Estratégica (CMI)", "2. Configuración de Alertas"])

# 3. SET DE DATOS
if 'datos_simulados' not in st.session_state:
    st.session_state.datos_simulados = pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'sector': ['Terminal Pesquero Antofagasta', 'Muelle Histórico Melbourn Clark', 'Balneario Municipal', 'Playa Trocadero', 'Playa Paraíso', 'Playa Brava', 'Playa Las Almejas', 'Playa El Huáscar', 'Caleta Poza del Salitre'],
        'lat': [-23.6428, -23.6457, -23.6675, -23.6015, -23.6362, -23.6558, -23.6692, -23.7250, -23.6412],
        'lon': [-70.3996, -70.3972, -70.4095, -70.3878, -70.3955, -70.4042, -70.4104, -70.4312, -70.4007],
        'llenado_actual': [45.0, 40.0, 60.0, 35.0, 50.0, 55.0, 25.0, 15.0, 30.0],
        'toneladas_max': [2.5, 1.2, 2.0, 1.8, 1.5, 2.2, 1.2, 1.0, 1.6],
        'toneladas': [1.12, 0.48, 1.2, 0.63, 0.75, 1.21, 0.3, 0.15, 0.48],
        'eta_min': [120, 340, 180, 410, 220, 190, 500, 800, 290]
    })

# Lógica de actualización (mantenida)
if simulacion_activa and not st.session_state.ruta_despachada:
    st.session_state.ciclo_actual += 1
    df = st.session_state.datos_simulados
    if st.session_state.ciclo_actual <= 3:
        df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] += 10
    elif st.session_state.ciclo_actual > 5:
        df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 100.0
    df['toneladas'] = np.round((df['llenado_actual'] / 100.0) * df['toneladas_max'], 2)
    st.session_state.datos_simulados = df

df_datos = st.session_state.datos_simulados

# 4. RENDERIZADO
if vista_seleccionada == "1. Vista Estratégica (CMI)":
    st.markdown("<h2>📊 Cuadro de Mando Integral Público-Ambiental</h2>", unsafe_allow_html=True)
    
    # Lógica de Alertas y Despacho
    saturados = df_datos[df_datos['llenado_actual'] == 100.0]
    if st.session_state.ruta_despachada:
        st.markdown('<div class="despacho-exito">✅ <strong>SISTEMA EN ETAPA DE MITIGACIÓN:</strong> Unidad en ruta.</div>', unsafe_allow_html=True)
    elif not saturados.empty:
        if st.button("⚡ CALCULAR Y DESPACHAR RUTA OPTIMIZADA (MODELO VRP)"):
            df_datos.loc[df_datos['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 15.0
            st.session_state.ruta_despachada = True
            st.rerun()

    # --- MAPA SATELITAL (Cambio aplicado aquí) ---
    st.markdown("##### Monitoreo de Saturación Georreferenciada en Tiempo Real")
    # Se utiliza tiles="Esri.WorldImagery" para la vista satelital
    mapa = folium.Map(location=[-23.648, -70.400], zoom_start=13, tiles="Esri.WorldImagery")
    
    for _, row in df_datos.iterrows():
        color = "red" if row['llenado_actual'] >= 90 else "orange" if row['llenado_actual'] >= 60 else "green"
        folium.Circle(location=[row['lat'], row['lon']], radius=100, color=color, fill=True).add_to(mapa)
    
    st_folium(mapa, width=1300, height=380)

if simulacion_activa:
    time.sleep(velocidad_sim)
    st.rerun()
