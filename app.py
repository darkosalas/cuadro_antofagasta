import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import time

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
    
    .alerta-operativo {
        background-color: #FEE2E2;
        border-left: 6px solid #DC2626;
        color: #991B1B;
        padding: 15px;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 15px;
        font-size: 15px;
        animation: pulse 2s infinite;
    }
    </style>
""", unsafe_allow_html=True)

# Menú de Navegación Lateral
st.sidebar.title("🧭 Panel Operativo")
st.sidebar.subheader("Borde Costero Antofagasta")
st.sidebar.write("---")

# CONTROLADOR DE TIEMPO / PASOS DE LA DEFENSA
st.sidebar.markdown("### ⏱️ Cronograma de la Simulación")
simulacion_activa = st.sidebar.toggle("Iniciar Flujo de Simulación", value=True)
velocidad_sim = st.sidebar.slider("Paso del tiempo (segundos):", 2, 10, 4)

# Inicializar el contador de ciclos/tiempo para controlar la trama
if 'ciclo_actual' not in st.session_state:
    st.session_state.ciclo_actual = 0

# Botón para resetear la simulación en vivo frente a los profesores
if st.sidebar.button("🔄 Reiniciar Simulación al Estado Inicial"):
    st.session_state.ciclo_actual = 0
    if 'datos_simulados' in st.session_state:
        del st.session_state['datos_simulados']
    st.rerun()

st.sidebar.write("---")
vista_seleccionada = st.sidebar.radio(
    "Seleccione la pantalla a visualizar:",
    ["1. Vista Estratégica (CMI)", "2. Vista Operativa (Mapa Satelital)", "3. Configuración de Alertas"]
)

# Muestra en qué punto de la línea de tiempo va el sistema
st.sidebar.info(f"Ciclo temporal activo: Paso {st.session_state.ciclo_actual}")

# ==============================================================================
# 2. BASE DE DATOS Y LÓGICA DE EVENTO CONTROLADO
# ==============================================================================
if 'datos_simulados' not in st.session_state:
    st.session_state.datos_simulados = pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'sector': [
            'Terminal Pesquero Antofagasta', 'Muelle Histórico Melbourn Clark', 
            'Balneario Municipal', 'Playa Trocadero', 'Playa Paraíso', 
            'Playa Brava', 'Playa Las Almejas', 'Playa El Huáscar', 'Caleta Poza del Salitre'
        ],
        'lat': [-23.6428, -23.6457, -23.6675, -23.6015, -23.6362, -23.6558, -23.6692, -23.7250, -23.6412],
        'lon': [-70.3996, -70.3972, -70.4095, -70.3878, -70.3955, -70.4042, -70.4104, -70.4312, -70.4007],
        'llenado_actual': [45.0, 40.0, 60.0, 35.0, 50.0, 55.0, 25.0, 15.0, 30.0], 
        'infracciones_2025': [8, 3, 5, 4, 4, 6, 2, 1, 5],
        'infracciones_2026': [4, 2, 2, 1, 2, 3, 1, 0, 2],
        'costo_fijo': [5000] * 9,
        'costo_variable': [14500, 9000, 11000, 8500, 9500, 13000, 6200, 5000, 12000],
        'toneladas_max': [2.5, 1.2, 2.0, 1.8, 1.5, 2.2, 1.2, 1.0, 1.6],
        'toneladas': [1.12, 0.48, 1.2, 0.63, 0.75, 1.21, 0.3, 0.15, 0.48]
    })

# EVOLUCIÓN PROGRAMADA DE LOS HECHOS
if simulacion_activa:
    st.session_state.ciclo_actual += 1
    df = st.session_state.datos_simulados
    
    # PASO 1 al 3: Estado Estable. Pequeñas variaciones normales.
    if st.session_state.ciclo_actual <= 3:
        df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 45.0 + (st.session_state.ciclo_actual * 5)
        df.loc[df['sector'] == 'Playa Brava', 'llenado_actual'] = 55.0 + (st.session_state.ciclo_actual * 2)
        
    # PASO 4 al 6: Pico de descarga. El Terminal Pesquero colapsa drásticamente.
    elif 4 <= st.session_state.ciclo_actual <= 6:
        if st.session_state.ciclo_actual == 4:
            df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 76.0
        elif st.session_state.ciclo_actual == 5:
            df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 92.0
        else:
            # ¡Llegamos al colapso programado!
            df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 100.0
            
    # Mantener el 100% de ahí en adelante hasta que se decida reiniciar
    elif st.session_state.ciclo_actual > 6:
        df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 100.0

    # Recalcular toneladas matemáticamente según el estado de la línea de tiempo
    df['toneladas'] = np.round((df['llenado_actual'] / 100.0) * df['toneladas_max'], 2)
    st.session_state.datos_simulados = df

df_datos = st.session_state.datos_simulados

# ==============================================================================
# 3. INTERFACES DE USUARIO
# ==============================================================================

# --- PANTALLA 1: CUADRO DE MANDO INTEGRAL (ESTRATEGIA) ---
if vista_seleccionada == "1. Vista Estratégica (CMI)":
    st.title("📊 Cuadro de Mando Integral Público-Ambiental")
    st.caption("Fase 3: Monitoreo en tiempo real del borde costero")
    st.write("---")
    
    # GATILLO DE ALERTA AL 100%
    sectores_saturados = df_datos[df_datos['llenado_actual'] == 100.0]
    if not sectores_saturados.empty:
        for _, sat in sectores_saturados.iterrows():
            st.markdown(f"""
            <div class="alerta-operativo">
                🚨 DETECTADA LOGÍSTICA CRÍTICA: El contenedor en <b>{sat['sector']}</b> ha llegado a su capacidad límite ({sat['toneladas']:.2f} Ton). 
                El sistema exige activar el Algoritmo de Optimización VRP para un Operativo de Reducción Inmediata.
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✔️ Todos los nodos logísticos de Antofagasta se encuentran bajo los límites críticos de recolección.")

    # Tarjetas e Indicadores
    inf_25 = df_datos['infracciones_2025'].sum()
    inf_26 = df_datos['infracciones_2026'].sum()
    tasa_mitigacion = ((inf_25 - inf_26) / inf_25) * 100
    criticos = len(df_datos[df_datos['llenado_actual'] >= 75])
    ton_totales = df_datos['toneladas'].sum()
    costo_por_tonelada = (df_datos['costo_fijo'].sum() + df_datos['costo_variable'].sum()) / max(0.1, ton_totales)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">🌿 Sostenibilidad Ambiental</div><div class="kpi-value">{tasa_mitigacion:.1f}%</div><div class="kpi-sub">Mitigación Infracciones</div></div>', unsafe_allow_html=True)
    with col2:
        sub_txt = "Flota en Espera" if criticos == 0 else f"{criticos} Puntos Críticos"
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">🚚 Procesos Logísticos</div><div class="kpi-value">{df_datos["llenado_actual"].mean():.1f}%</div><div class="kpi-sub" style="color: {"#DC2626" if criticos > 0 else "#059669"}">{sub_txt}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="kpi-container"><div class="kpi-title">👥 Usuarios y Gobernanza</div><div class="kpi-value">86.4%</div><div class="kpi-sub">Satisfacción Vecinal</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">💰 Financiera y Eficiencia</div><div class="kpi-value">${costo_por_tonelada:,.0f}</div><div class="kpi-sub">Costo por Tonelada</div></div>', unsafe_allow_html=True)

    st.write("##")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Estado de Saturación por Contenedor (%)")
        st.bar_chart(pd.DataFrame({'Sector': df_datos['sector'], 'Ocupación (%)': df_datos['llenado_actual']}).set_index('Sector'), color="#1E3A8A")
    with col_g2:
        st.subheader("Carga Neta en Tolvas Extensas (Ton)")
        st.area_chart(pd.DataFrame({'Sector': df_datos['sector'], 'Toneladas Métricas': df_datos['toneladas']}).set_index('Sector'), color="#DC2626")

# --- PANTALLA 2: MAPA SATELITAL INTERACTIVO (OPERATIVO) ---
elif vista_seleccionada == "2. Vista Operativa (Mapa Satelital)":
    st.title("🗺️ Sistema de Telemetría y Alertas del Borde Costero")
    st.caption("Simulación en vivo orientada a eventos críticos.")
    st.write("---")
    
    mapa = folium.Map(location=[-23.655, -70.405], zoom_start=12, tiles="Cartodb Positron")
    
    for _, row in df_datos.iterrows():
        if row['llenado_actual'] == 100.0:
            color_difuminado = "#7F1D1D"
            estado_texto = "🚨 ALERTA: OPERATIVO DE REDUCCIÓN REQUERIDO (100% LLENO)"
            radio_mancha = 130
            peso_borde = 4
        elif row['llenado_actual'] >= 75:
            color_difuminado = "#EF4444"
            estado_texto = "Crítico (Por sobre el umbral)"
            radio_mancha = 65
            peso_borde = 0
        elif row['llenado_actual'] >= 50:
            color_difuminado = "#F59E0B"
            estado_texto = "Atención Intermedia"
            radio_mancha = 40
            peso_borde = 0
        else:
            color_difuminado = "#10B981"
            estado_texto = "Normal"
            radio_mancha = 25
            peso_borde = 0
            
        folium.Circle(
            location=[row['lat'], row['lon']],
            radius=radio_mancha,
            popup=f"<b>{row['sector']}</b><br>Llenado: {row['llenado_actual']:.1f}%<br>Carga: {row['toneladas']:.2f} Ton<br>Estado: {estado_texto}",
            color="#DC2626" if row['llenado_actual'] == 100.0 else color_difuminado,
            fill=True,
            fill_color=color_difuminado,
            fill_opacity=0.75 if row['llenado_actual'] == 100.0 else 0.45,
            weight=peso_borde
        ).add_to(mapa)
    
    st_folium(mapa, width=1100, height=520)
    
    st.write("##")
    st.subheader("📋 Consola de Monitoreo")
    st.dataframe(
        df_datos[['sector', 'llenado_actual', 'toneladas']].rename(
            columns={'sector': 'Punto Costero', 'llenado_actual': 'Nivel de Llenado (%)', 'toneladas': 'Masa'}
        ).style.format({'Nivel de Llenado (%)': '{:.1f}%', 'Masa': '{:.2f} Ton'}),
        use_container_width=True
    )

# --- PANTALLA 3: CONFIGURACIÓN DE ALERTAS ---
else:
    st.title("⚙️ Módulo de Administración Logística")
    st.write("---")
    st.success("Línea de tiempo del motor analítico vinculada con éxito.")

# Re-ejecución automática basada en el temporizador
if simulacion_activa and st.session_state.ciclo_actual < 8:
    time.sleep(velocidad_sim)
    st.rerun()
