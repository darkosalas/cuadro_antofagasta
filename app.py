import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import time

# 1. CONFIGURACIÓN DEL ENTORNO
st.set_page_config(page_title="CMI Público-Ambiental", layout="wide", initial_sidebar_state="expanded")

# CSS ESTILOS
st.markdown("""
    <style>
    .alerta-operativo { background-color: #fef2f2; border-left: 5px solid #991b1b; color: #7f1d1d; padding: 15px; border-radius: 4px; }
    .despacho-exito { background-color: #f0fdf4; border-left: 5px solid #16a34a; color: #14532d; padding: 15px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# 2. CONTROLADORES
st.sidebar.markdown("### 📋 PANEL OPERATIVO")
simulacion_activa = st.sidebar.toggle("Ejecutar Simulación IoT", value=True)
velocidad_sim = st.sidebar.slider("Barrido de tiempo (segundos):", 2, 10, 4)

if 'ciclo_actual' not in st.session_state: st.session_state.ciclo_actual = 0
if 'ruta_despachada' not in st.session_state: st.session_state.ruta_despachada = False
if 'ultimo_atendido' not in st.session_state: st.session_state.ultimo_atendido = ""

if st.sidebar.button("🔄 Reiniciar Parámetros Base"):
    for key in ['ciclo_actual', 'ruta_despachada', 'ultimo_atendido', 'datos_simulados']:
        if key in st.session_state: del st.session_state[key]
    st.rerun()

# 3. SET DE DATOS CON PROTECCIÓN ANTI-ERROR
if 'datos_simulados' not in st.session_state:
    st.session_state.datos_simulados = pd.DataFrame({
        'id': range(1, 10),
        'sector': ['Terminal Pesquero Antofagasta', 'Muelle Histórico Melbourn Clark', 'Balneario Municipal', 'Playa Trocadero', 'Playa Paraíso', 'Playa Brava', 'Playa Las Almejas', 'Playa El Huáscar', 'Caleta Poza del Salitre'],
        'lat': [-23.6428, -23.6457, -23.6675, -23.6015, -23.6362, -23.6558, -23.6692, -23.7250, -23.6412],
        'lon': [-70.3996, -70.3972, -70.4095, -70.3878, -70.3955, -70.4042, -70.4104, -70.4312, -70.4007],
        'llenado_actual': [65.0, 32.0, 50.0, 41.0, 25.0, 58.0, 18.0, 12.0, 30.0],
        'toneladas_max': [2.5, 1.2, 2.0, 1.8, 1.5, 2.2, 1.2, 1.0, 1.6],
        'factor_generacion': [1.6, 0.8, 1.4, 1.1, 0.9, 1.3, 0.7, 0.4, 1.0]
    })
    # Asegurar columnas calculadas iniciales
    df = st.session_state.datos_simulados
    df['toneladas'] = np.round((df['llenado_actual'] / 100.0) * df['toneladas_max'], 2)
    df['eta_min'] = ((100.0 - df['llenado_actual']) * 6).astype(int)

df_datos = st.session_state.datos_simulados

# PARCHE DE SEGURIDAD PARA EL ERROR DE "image_de5d64.png"
if 'factor_generacion' not in df_datos.columns:
    df_datos['factor_generacion'] = [1.6, 0.8, 1.4, 1.1, 0.9, 1.3, 0.7, 0.4, 1.0]
    st.session_state.datos_simulados = df_datos

# 4. LÓGICA DE SIMULACIÓN SECUENCIAL
saturados = df_datos[df_datos['llenado_actual'] >= 100.0]
hay_alarma_activa = not saturados.empty

if simulacion_activa and not hay_alarma_activa:
    st.session_state.ciclo_actual += 1
    st.session_state.ruta_despachada = False
    
    incremento = np.random.uniform(3.0, 7.0, size=len(df_datos)) * df_datos['factor_generacion']
    df_datos['llenado_actual'] = (df_datos['llenado_actual'] + incremento).clip(upper=100.0)
    df_datos['toneladas'] = np.round((df_datos['llenado_actual'] / 100.0) * df_datos['toneladas_max'], 2)
    df_datos['eta_min'] = ((100.0 - df_datos['llenado_actual']) * 6).astype(int)
    st.session_state.datos_simulados = df_datos
    saturados = df_datos[df_datos['llenado_actual'] >= 100.0]
    hay_alarma_activa = not saturados.empty

# 5. INTERFAZ
st.title("📊 CMI Público-Ambiental")

if st.session_state.ruta_despachada:
    st.markdown(f'<div class="despacho-exito">✅ Mitigación ejecutada en: {st.session_state.ultimo_atendido}.</div>', unsafe_allow_html=True)
elif hay_alarma_activa:
    st.markdown(f'<div class="alerta-operativo">🚨 Alerta Crítica: {saturados.iloc[0]["sector"]}. Simulación pausada.</div>', unsafe_allow_html=True)
    if st.button("⚡ Despachar Ruta VRP"):
        st.session_state.ultimo_atendido = saturados.iloc[0]['sector']
        df_datos.loc[df_datos['sector'] == st.session_state.ultimo_atendido, 'llenado_actual'] = 15.0
        df_datos['toneladas'] = np.round((df_datos['llenado_actual'] / 100.0) * df_datos['toneladas_max'], 2)
        st.session_state.ruta_despachada = True
        st.rerun()

st.dataframe(df_datos[['sector', 'llenado_actual', 'toneladas']], use_container_width=True)

if simulacion_activa and not hay_alarma_activa:
    time.sleep(velocidad_sim)
    st.rerun()
