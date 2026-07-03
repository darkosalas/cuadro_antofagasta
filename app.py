import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import time

# 1. CONFIGURACIÓN DEL ENTORNO INSTITUCIONAL
st.set_page_config(page_title="CMI Público-Ambiental", layout="wide", initial_sidebar_state="expanded")

# CSS ESTILOS (MANTENIDOS DE TU CÓDIGO ORIGINAL)
st.markdown("""
    <style>
    .card-kpi { padding: 15px 20px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 15px; min-height: 125px; }
    .card-title { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #475569; margin-bottom: 4px; }
    .card-value { font-size: 28px; font-weight: 800; color: #1e293b; display: flex; align-items: center; gap: 5px; }
    .card-sub { font-size: 11px; color: #64748b; margin-top: 4px; font-weight: 500; }
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

if st.sidebar.button("🔄 Reiniciar Parámetros"):
    st.session_state.ciclo_actual = 0
    st.session_state.ruta_despachada = False
    if 'datos_simulados' in st.session_state: del st.session_state['datos_simulados']
    st.rerun()

vista_seleccionada = st.sidebar.radio("Navegación del Sistema:", ["1. Vista Estratégica (CMI)", "2. Vista Operativa (Mapa Satelital)"])

# 3. SET DE DATOS
if 'datos_simulados' not in st.session_state:
    st.session_state.datos_simulados = pd.DataFrame({
        'sector': ['Terminal Pesquero Antofagasta', 'Muelle Histórico Melbourn Clark', 'Balneario Municipal', 'Playa Trocadero', 'Playa Paraíso', 'Playa Brava', 'Playa Las Almejas', 'Playa El Huáscar', 'Caleta Poza del Salitre'],
        'lat': [-23.6428, -23.6457, -23.6675, -23.6015, -23.6362, -23.6558, -23.6692, -23.7250, -23.6412],
        'lon': [-70.3996, -70.3972, -70.4095, -70.3878, -70.3955, -70.4042, -70.4104, -70.4312, -70.4007],
        'llenado_actual': [45.0, 40.0, 60.0, 35.0, 50.0, 55.0, 25.0, 15.0, 30.0],
        'toneladas_max': [2.5, 1.2, 2.0, 1.8, 1.5, 2.2, 1.2, 1.0, 1.6],
        'toneladas': [1.12, 0.48, 1.2, 0.63, 0.75, 1.21, 0.3, 0.15, 0.48],
        'eta_min': [120, 340, 180, 410, 220, 190, 500, 800, 290]
    })

# EVOLUCIÓN CRONOLÓGICA
if simulacion_activa and not st.session_state.ruta_despachada:
    st.session_state.ciclo_actual += 1
    df = st.session_state.datos_simulados
    df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = min(df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] + 10, 100.0)
    df['toneladas'] = np.round((df['llenado_actual'] / 100.0) * df['toneladas_max'], 2)
    st.session_state.datos_simulados = df

df_datos = st.session_state.datos_simulados

# 4. RENDERIZADO DE VISTAS
if vista_seleccionada == "1. Vista Estratégica (CMI)":
    st.markdown("<h2>📊 Cuadro de Mando Integral Público-Ambiental</h2>", unsafe_allow_html=True)
    
    # Lógica de Alertas
    saturados = df_datos[df_datos['llenado_actual'] >= 100.0]
    if st.session_state.ruta_despachada:
        st.markdown('<div class="despacho-exito">✅ Sistema en mitigación: Unidad recolectora en ruta.</div>', unsafe_allow_html=True)
    elif not saturados.empty:
        st.markdown('<div class="alerta-operativo">🚨 ALERTA CRÍTICA: Capacidad límite alcanzada.</div>', unsafe_allow_html=True)
        if st.button("⚡ DESPACHAR RUTA VRP"):
            df_datos.loc[df_datos['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 15.0
            st.session_state.ruta_despachada = True
            st.rerun()

    # Tarjetas KPI (Tu diseño original)
    cols = st.columns(4)
    cols[0].markdown('<div class="card-kpi kpi-ambiental"><div class="card-title">1. Ambiental</div><div class="card-value">42.5%</div></div>', unsafe_allow_html=True)
    cols[1].markdown(f'<div class="card-kpi kpi-logistica"><div class="card-title">2. Logística</div><div class="card-value">{df_datos["llenado_actual"].mean():.1f}%</div></div>', unsafe_allow_html=True)
    # ... (Puedes completar las otras 2 tarjetas igual)

elif vista_seleccionada == "2. Vista Operativa (Mapa Satelital)":
    st.title("📍 Vista Operativa: Monitoreo Satelital")
    # Mapa con tiles de satélite (Esri World Imagery)
    mapa = folium.Map(location=[-23.648, -70.400], zoom_start=13, tiles="Esri.WorldImagery")
    
    for _, row in df_datos.iterrows():
        color = "red" if row['llenado_actual'] >= 90 else "orange" if row['llenado_actual'] >= 60 else "green"
        folium.Circle(location=[row['lat'], row['lon']], radius=100, color=color, fill=True, 
                      popup=f"{row['sector']}: {row['llenado_actual']}%").add_to(mapa)
    
    st_folium(mapa, width=1200, height=600)

if simulacion_activa:
    time.sleep(velocidad_sim)
    st.rerun()
