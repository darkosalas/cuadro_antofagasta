import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import time

# 1. CONFIGURACIÓN DEL ENTORNO
st.set_page_config(page_title="CMI Público-Ambiental", layout="wide", initial_sidebar_state="expanded")

# CSS (Mantenido)
st.markdown("""
    <style>
    .card-kpi { padding: 15px 20px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 15px; min-height: 125px; }
    .card-title { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #475569; margin-bottom: 4px; }
    .card-value { font-size: 28px; font-weight: 800; color: #1e293b; display: flex; align-items: center; gap: 5px; }
    .kpi-ambiental { background-color: #e6f4ea; border-top: 4px solid #137333; }
    .kpi-logistica { background-color: #feeee3; border-top: 4px solid #e67e22; }
    .kpi-comunidad { background-color: #f3e8fd; border-top: 4px solid #8430ce; }
    .kpi-financiera { background-color: #fef7e0; border-top: 4px solid #f2a104; }
    .alerta-operativo { background-color: #fef2f2; border-left: 5px solid #991b1b; color: #7f1d1d; padding: 15px; border-radius: 4px; font-weight: 500; margin-bottom: 15px; }
    .despacho-exito { background-color: #f0fdf4; border-left: 5px solid #16a34a; color: #14532d; padding: 15px; border-radius: 4px; font-weight: 500; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# 2. CONTROLADORES
st.sidebar.markdown("### 📋 PANEL OPERATIVO")
simulacion_activa = st.sidebar.toggle("Ejecutar Simulación IoT", value=True)
velocidad_sim = st.sidebar.slider("Barrido de tiempo (seg):", 2, 10, 4)

if 'ciclo_actual' not in st.session_state: st.session_state.ciclo_actual = 0
if 'ruta_despachada' not in st.session_state: st.session_state.ruta_despachada = False
if 'datos_simulados' not in st.session_state:
    st.session_state.datos_simulados = pd.DataFrame({
        'sector': ['Terminal Pesquero Antofagasta', 'Muelle Histórico', 'Balneario Municipal', 'Playa Trocadero'],
        'lat': [-23.6428, -23.6457, -23.6675, -23.6015],
        'lon': [-70.3996, -70.3972, -70.4095, -70.3878],
        'llenado_actual': [45.0, 40.0, 60.0, 35.0],
        'toneladas': [1.1, 0.5, 1.2, 0.6]
    })

vista_seleccionada = st.sidebar.radio("Navegación:", ["1. Vista Estratégica (CMI)", "2. Vista Operativa (Mapa Satelital)"])

# 3. LÓGICA DE SIMULACIÓN
if simulacion_activa and not st.session_state.ruta_despachada:
    st.session_state.ciclo_actual += 1
    df = st.session_state.datos_simulados
    df.loc[0, 'llenado_actual'] = min(df.loc[0, 'llenado_actual'] + 15, 100.0)
    st.session_state.datos_simulados = df

df_datos = st.session_state.datos_simulados

# 4. VISTAS
if vista_seleccionada == "1. Vista Estratégica (CMI)":
    st.title("📊 Cuadro de Mando Integral")
    # Tarjetas sin mapa
    cols = st.columns(4)
    cols[0].markdown('<div class="card-kpi kpi-ambiental"><div class="card-title">Ambiental</div><div class="card-value">42.5%</div></div>', unsafe_allow_html=True)
    cols[1].markdown(f'<div class="card-kpi kpi-logistica"><div class="card-title">Logística</div><div class="card-value">{df_datos["llenado_actual"].mean():.1f}%</div></div>', unsafe_allow_html=True)
    # ... (Resto de tarjetas)
    st.bar_chart(df_datos.set_index('sector')['llenado_actual'])

elif vista_seleccionada == "2. Vista Operativa (Mapa Satelital)":
    st.title("📍 Vista Operativa: Monitoreo Satelital")
    
    # Lógica de despacho en Vista 2
    if st.session_state.ruta_despachada:
        st.markdown('<div class="despacho-exito">✅ Ruta VRP despachada correctamente.</div>', unsafe_allow_html=True)
    elif df_datos['llenado_actual'].max() >= 100:
        if st.button("⚡ CALCULAR Y DESPACHAR RUTA VRP"):
            df_datos.loc[0, 'llenado_actual'] = 15.0
            st.session_state.ruta_despachada = True
            st.rerun()
    
    # Mapa Satelital
    mapa = folium.Map(location=[-23.648, -70.400], zoom_start=14, tiles="Esri.WorldImagery")
    for _, row in df_datos.iterrows():
        folium.CircleMarker([row['lat'], row['lon']], radius=10, color="red" if row['llenado_actual']>=90 else "green").add_to(mapa)
    st_folium(mapa, width=1200, height=500)

if simulacion_activa:
    time.sleep(velocidad_sim)
    st.rerun()
