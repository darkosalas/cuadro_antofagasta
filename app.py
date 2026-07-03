import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import time
import random

# 1. CONFIGURACIÓN E INTERFAZ BASE DEL PANEL
st.set_page_config(
    page_title="Gestión de Residuos Costeros - Antofagasta",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS avanzados para las Tarjetas CMI y Alertas Críticas
st.markdown("""
    <style>
    body { background-color: #f4f6f9; }
    .kpi-container {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 12px;
        border-top: 5px solid #1E3A8A;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 15px;
    }
    .kpi-title { font-size: 13px; color: #6B7280; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }
    .kpi-value { font-size: 30px; color: #111827; font-weight: 700; }
    .kpi-sub { font-size: 12px; color: #059669; font-weight: 500; margin-top: 4px; }
    
    /* Estilo especial para el Banner de Alerta Crítica 100% */
    .alerta-operativo {
        background-color: #FEE2E2;
        border-left: 6px solid #DC2626;
        color: #991B1B;
        padding: 15px;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 15px;
        font-size: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Menú de Navegación Lateral
st.sidebar.title("🧭 Panel Operativo")
st.sidebar.subheader("Borde Costero Antofagasta")
st.sidebar.write("---")

# Controles de la Simulación en la Barra Lateral
st.sidebar.markdown("### ⚙️ Control de Simulación IoT")
simulacion_activa = st.sidebar.toggle("Activar Simulación en Tiempo Real", value=True)
velocidad_sim = st.sidebar.slider("Frecuencia de actualización (segundos):", 2, 10, 4)

st.sidebar.write("---")
vista_seleccionada = st.sidebar.radio(
    "Seleccione la pantalla a visualizar:",
    ["1. Vista Estratégica (CMI)", "2. Vista Operativa (Mapa Satelital)", "3. Configuración de Alertas"]
)

# ==============================================================================
# 2. BASE DE DATOS AMPLIADA: PLAYAS Y TERMINAL PESQUERO DE ANTOFAGASTA
# ==============================================================================
if 'datos_simulados' not in st.session_state:
    st.session_state.datos_simulados = pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'sector': [
            'Terminal Pesquero Antofagasta', 
            'Muelle Histórico Melbourn Clark', 
            'Balneario Municipal', 
            'Playa Trocadero', 
            'Playa Paraíso', 
            'Playa Brava', 
            'Playa Las Almejas',
            'Playa El Huáscar',
            'Caleta Poza del Salitre'
        ],
        'lat': [-23.6428, -23.6457, -23.6675, -23.6015, -23.6362, -23.6558, -23.6692, -23.7250, -23.6412],
        'lon': [-70.3996, -70.3972, -70.4095, -70.3878, -70.3955, -70.4042, -70.4104, -70.4312, -70.4007],
        'llenado_actual': [95.0, 40.0, 60.0, 35.0, 50.0, 78.0, 25.0, 15.0, 88.0], 
        'infracciones_2025': [8, 3, 5, 4, 4, 6, 2, 1, 5],
        'infracciones_2026': [4, 2, 2, 1, 2, 3, 1, 0, 2],
        'costo_fijo': [5000] * 9,
        'costo_variable': [14500, 9000, 11000, 8500, 9500, 13000, 6200, 5000, 12000],
        'toneladas_max': [2.5, 1.2, 2.0, 1.8, 1.5, 2.2, 1.2, 1.0, 1.6], # Capacidad máxima del contenedor por sector
        'toneladas': [2.3, 0.48, 1.2, 0.63, 0.75, 1.71, 0.3, 0.15, 1.4]
    })

# Algoritmo de Fluctuación Dinámica (Acumulación y descompresión de basura)
if simulacion_activa:
    nuevos_niveles = []
    nuevas_toneladas = []
    for _, fila in st.session_state.datos_simulados.iterrows():
        # Generar una tasa alta de acumulación para propiciar que lleguen al 100%
        cambio = random.uniform(-10.0, 16.0)
        nuevo_llenado = max(0.0, min(100.0, fila['llenado_actual'] + cambio))
        nuevos_niveles.append(nuevo_llenado)
        # Las toneladas se calculan multiplicando el % de llenado actual por su capacidad máxima
        nuevas_toneladas.append(round((nuevo_llenado / 100.0) * fila['toneladas_max'], 2))
        
    st.session_state.datos_simulados['llenado_actual'] = nuevos_niveles
    st.session_state.datos_simulados['toneladas'] = nuevas_toneladas

df_datos = st.session_state.datos_simulados

# ==============================================================================
# 3. LÓGICA Y RENDIMIENTO DE INTERFACES
# ==============================================================================

# --- PANTALLA 1: CUADRO DE MANDO INTEGRAL (ESTRATEGIA) ---
if vista_seleccionada == "1. Vista Estratégica (CMI)":
    st.title("📊 Cuadro de Mando Integral Público-Ambiental")
    st.caption("Fase 3: Indicadores clave de rendimiento para la red costera extendida de Antofagasta")
    st.write("---")
    
    # Comprobación de alertas urgentes al 100% para la cabecera
    sectores_saturados = df_datos[df_datos['llenado_actual'] == 100.0]
    if not sectores_saturados.empty:
        for _, sat in sectores_saturados.iterrows():
            st.markdown(f"""
            <div class="alerta-operativo">
                🚨 ALERTA LOGÍSTICA CRÍTICA: El contenedor de <b>{sat['sector']}</b> ha alcanzado el 100% de su capacidad ({sat['toneladas']:.2f} Ton). 
                Se requiere despachar un OPERATIVO DE REDUCCIÓN INMEDIATA.
            </div>
            """, unsafe_allow_html=True)

    # Cálculos estratégicos en tiempo real
    inf_25 = df_datos['infracciones_2025'].sum()
    inf_26 = df_datos['infracciones_2026'].sum()
    tasa_mitigacion = ((inf_25 - inf_26) / inf_25) * 100
    
    total_contenedores = len(df_datos)
    criticos = len(df_datos[df_datos['llenado_actual'] >= 75])
    pct_criticos = (criticos / total_contenedores) * 100
    
    costo_total = df_datos['costo_fijo'].sum() + df_datos['costo_variable'].sum()
    ton_totales = df_datos['toneladas'].sum()
    costo_por_tonelada = costo_total / max(0.1, ton_totales)
    
    # Despliegue de Tarjetas CMI
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">🌿 Sostenibilidad Ambiental</div><div class="kpi-value">{tasa_mitigacion:.1f}%</div><div class="kpi-sub">Mitigación Infracciones</div></div>', unsafe_allow_html=True)
    with col2:
        sub_logistica = "Flota Estable" if criticos == 0 else f"{criticos} Puntos Críticos"
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">🚚 Procesos Logísticos</div><div class="kpi-value">{df_datos["llenado_actual"].mean():.1f}%</div><div class="kpi-sub">{sub_logistica}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="kpi-container"><div class="kpi-title">👥 Usuarios y Gobernanza</div><div class="kpi-value">86.4%</div><div class="kpi-sub">Satisfacción Vecinal</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">💰 Financiera y Eficiencia</div><div class="kpi-value">${costo_por_tonelada:,.0f}</div><div class="kpi-sub">Costo por Tonelada</div></div>', unsafe_allow_html=True)

    st.write("##")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Estado de Saturación por Punto Marítimo (%)")
        df_volumen = pd.DataFrame({'Sector': df_datos['sector'], 'Ocupación (%)': df_datos['llenado_actual']}).set_index('Sector')
        st.bar_chart(df_volumen, color="#1E3A8A")
    with col_g2:
        st.subheader("Masa Total Acumulada por Zona (Toneladas)")
        df_ton = pd.DataFrame({'Sector': df_datos['sector'], 'Toneladas Métricas': df_datos['toneladas']}).set_index('Sector')
        st.area_chart(df_ton, color="#DC2626")

# --- PANTALLA 2: MAPA SATELITAL INTERACTIVO (OPERATIVO) ---
elif vista_seleccionada == "2. Vista Operativa (Mapa Satelital)":
    st.title("🗺️ Sistema de Telemetría y Alertas del Borde Costero")
    st.caption("Los contenedores al 100% activan automáticamente el protocolo de Operativo Logístico de Emergencia.")
    st.write("---")
    
    # Centramos el mapa para que abarque desde Playa Trocadero (Norte) hasta Playa El Huáscar (Sur)
    mapa = folium.Map(location=[-23.655, -70.405], zoom_start=12, tiles="Cartodb Positron")
    
    # Inyección de capas geográficas con la nueva lógica al 100%
    for _, row in df_datos.iterrows():
        if row['llenado_actual'] == 100.0:
            color_difuminado = "#7F1D1D"  # Rojo Oscuro / Sangre de Máxima Alerta
            estado_texto = "🚨 REQUERIDO: OPERATIVO DE REDUCCIÓN INMEDIATA (100% SATURADO)"
            radio_mancha = 120            # Radio gigante para llamar la atención del despachador
            peso_borde = 3
        elif row['llenado_actual'] >= 75:
            color_difuminado = "#EF4444"  # Rojo Estándar (Crítico)
            estado_texto = "Crítico (Llenado Alto)"
            radio_mancha = 60
            peso_borde = 0
        elif row['llenado_actual'] >= 50:
            color_difuminado = "#F59E0B"  # Amarillo (Preventivo)
            estado_texto = "Atención Intermedia"
            radio_mancha = 40
            peso_borde = 0
        else:
            color_difuminado = "#10B981"  # Verde (Normal)
            estado_texto = "Normal / Despejado"
            radio_mancha = 25
            peso_borde = 0
            
        # Añadir la mancha traslúcida al mapa
        folium.Circle(
            location=[row['lat'], row['lon']],
            radius=radio_mancha,
            popup=f"<b>{row['sector']}</b><br><b>Llenado:</b> {row['llenado_actual']:.1f}%<br><b>Carga:</b> {row['toneladas']:.2f} Ton<br><b>Estado:</b> {estado_texto}",
            color="#DC2626" if row['llenado_actual'] == 100.0 else color_difuminado,
            fill=True,
            fill_color=color_difuminado,
            fill_opacity=0.70 if row['llenado_actual'] == 100.0 else 0.50,
            weight=peso_borde
        ).add_to(mapa)
    
    st_folium(mapa, width=1100, height=520)
    
    # Sección inferior de control de operaciones
    st.write("##")
    st.subheader("📋 Consola de Monitoreo en Tiempo Real")
    
    # Filtrar los que necesitan operativo urgente para mostrarlos destacados en una tabla
    urgentes = df_datos[df_datos['llenado_actual'] == 100.0]
    if not urgentes.empty:
        st.error(f"⚠️ ATENCIÓN: Hay {len(urgentes)} puntos costeros requiriendo despacho de camiones de manera inmediata.")
        
    st.dataframe(
        df_datos[['sector', 'llenado_actual', 'toneladas']].rename(
            columns={'sector': 'Punto Costero / Playa', 'llenado_actual': 'Nivel de Llenado (%)', 'toneladas': 'Masa Almacenada'}
        ).style.format({'Nivel de Llenado (%)': '{:.1f}%', 'Masa Almacenada': '{:.2f} Ton'}),
        use_container_width=True
    )

# --- PANTALLA 3: CONFIGURACIÓN DE ALERTAS ---
else:
    st.title("⚙️ Módulo de Administración Logística")
    st.write("---")
    st.success("El motor matemático de optimización se encuentra activo vinculando las coordenadas del Terminal Pesquero y las 6 playas.")

# Bucle de recarga automática
if simulacion_activa:
    time.sleep(velocidad_sim)
    st.rerun()
