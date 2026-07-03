import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import time

# 1. CONFIGURACIÓN E INTERFAZ INSTITUCIONAL
st.set_page_config(
    page_title="Sistema de Telemetría Gubernamental - SMA Antofagasta",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS de Alta Densidad Informativa (Estilo Dashboard de Control Central)
st.markdown("""
    <style>
    body { background-color: #f8fafc; }
    .kpi-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border-top: 4px solid #0f172a; /* Azul Prusia Institucional */
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
        text-align: left;
        margin-bottom: 15px;
    }
    .kpi-title { font-size: 11px; color: #475569; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
    .kpi-value { font-size: 28px; color: #1e293b; font-weight: 800; letter-spacing: -0.5px; }
    .kpi-sub { font-size: 12px; color: #0f766e; font-weight: 600; margin-top: 4px; }
    
    /* Protocolo de Emergencia VRP */
    .alerta-operativo {
        background-color: #fef2f2;
        border-left: 5px solid #991b1b;
        color: #7f1d1d;
        padding: 16px;
        border-radius: 6px;
        font-weight: 500;
        margin-bottom: 20px;
        font-size: 14px;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

# Menú de Navegación Lateral - Control de Comandos
st.sidebar.title("🏛️ Dirección de Operaciones")
st.sidebar.subheader("Sistema de Monitoreo Costero Integrado")
st.sidebar.write("---")

st.sidebar.markdown("### ⚙️ Telemetría y Línea de Tiempo")
simulacion_activa = st.sidebar.toggle("Ejecutar Flujo de Datos en Tiempo Real", value=True)
velocidad_sim = st.sidebar.slider("Intervalo de barrido (segundos):", 2, 10, 4)

if 'ciclo_actual' not in st.session_state:
    st.session_state.ciclo_actual = 0

if st.sidebar.button("🔄 Restablecer Parámetros Base"):
    st.session_state.ciclo_actual = 0
    if 'datos_simulados' in st.session_state:
        del st.session_state['datos_simulados']
    st.rerun()

st.sidebar.write("---")
vista_seleccionada = st.sidebar.radio(
    "Módulos de Supervisión:",
    ["1. Cuadro de Mando Estratégica (CMI)", "2. Despacho Operativo (Cartografía Satelital)", "3. Matrices de Configuración"]
)

st.sidebar.write("---")
st.sidebar.caption("🔒 Acceso Restringido - Autoridades Gubernamentales de la Región de Antofagasta.")

# ==============================================================================
# 2. MARCO DE DATOS FLUIDO (CRONOGRAMA DE AUDITORÍA)
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

if simulacion_activa:
    st.session_state.ciclo_actual += 1
    df = st.session_state.datos_simulados
    
    # Secuencia analítica controlada
    if st.session_state.ciclo_actual <= 3:
        df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 45.0 + (st.session_state.ciclo_actual * 5)
        df.loc[df['sector'] == 'Playa Brava', 'llenado_actual'] = 55.0 + (st.session_state.ciclo_actual * 2)
    elif 4 <= st.session_state.ciclo_actual <= 6:
        if st.session_state.ciclo_actual == 4:
            df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 76.0
        elif st.session_state.ciclo_actual == 5:
            df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 92.0
        else:
            df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 100.0
    elif st.session_state.ciclo_actual > 6:
        df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 100.0

    df['toneladas'] = np.round((df['llenado_actual'] / 100.0) * df['toneladas_max'], 2)
    st.session_state.datos_simulados = df

df_datos = st.session_state.datos_simulados

# ==============================================================================
# 3. COMPONENTES VISUALES EJECUTIVOS
# ==============================================================================

# --- PANTALLA 1: CUADRO DE MANDO INTEGRAL (CMI ESTRATÉGICO) ---
if vista_seleccionada == "1. Cuadro de Mando Estratégica (CMI)":
    st.title("📈 Cuadro de Mando Integral: Gestión Público-Ambiental")
    st.caption("Indicadores macro del borde costero e impacto logístico institucional.")
    st.write("---")
    
    # INTERRUPCIÓN DE PROTOCOLO FORMAL AL 100%
    sectores_saturados = df_datos[df_datos['llenado_actual'] == 100.0]
    if not sectores_saturados.empty:
        for _, sat in sectores_saturados.iterrows():
            st.markdown(f"""
            <div class="alerta-operativo">
                <strong>⚠️ PROTOCOLO DE CONTINGENCIA ACTIVO:</strong> El nodo crítico <strong>{sat['sector']}</strong> 
                registra una saturación del 100% con un volumen de masa de <strong>{sat['toneladas']:.2f} Ton</strong>. 
                El sistema ha despachado la orden de mitigación inmediata mediante el modelo de ruteo vehicular optimizado (VRP) automatizado.
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Estado del Sistema: Todos los activos logísticos operan bajo los umbrales de tolerancia establecidos.")

    # KPIs de Dirección General
    inf_25 = df_datos['infracciones_2025'].sum()
    inf_26 = df_datos['infracciones_2026'].sum()
    tasa_mitigacion = ((inf_25 - inf_26) / inf_25) * 100
    criticos = len(df_datos[df_datos['llenado_actual'] >= 75])
    ton_totales = df_datos['toneladas'].sum()
    costo_por_tonelada = (df_datos['costo_fijo'].sum() + df_datos['costo_variable'].sum()) / max(0.1, ton_totales)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">🌿 Persp. Sustentabilidad</div><div class="kpi-value">{tasa_mitigacion:.1f}%</div><div class="kpi-sub">Reducción de Infracciones</div></div>', unsafe_allow_html=True)
    with col2:
        sub_color = "#991b1b" if criticos > 0 else "#0f766e"
        sub_txt = "Flota en Equilibrio" if criticos == 0 else f"{criticos} Activos Comprometidos"
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">🚚 Persp. Procesos Internos</div><div class="kpi-value">{df_datos["llenado_actual"].mean():.1f}%</div><div class="kpi-sub" style="color: {sub_color}">{sub_txt}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="kpi-container"><div class="kpi-title">👥 Persp. Ciudadana y Gobernanza</div><div class="kpi-value">86.4%</div><div class="kpi-sub">Índice de Aceptación Social</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">💰 Persp. Eficiencia Financiera</div><div class="kpi-value">${costo_por_tonelada:,.0f}</div><div class="kpi-sub">Costo de Operación / Ton</div></div>', unsafe_allow_html=True)

    st.write("##")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Índice de Capacidad Absorbida por Activo (%)")
        st.bar_chart(pd.DataFrame({'Nodo Costero': df_datos['sector'], 'Capacidad Utilizada (%)': df_datos['llenado_actual']}).set_index('Nodo Costero'), color="#334155")
    with col_g2:
        st.subheader("Masa Acumulada Registrada por Estación Telemetrada (Ton)")
        st.area_chart(pd.DataFrame({'Nodo Costero': df_datos['sector'], 'Masa Absoluta (Masa/Ton)': df_datos['toneladas']}).set_index('Nodo Costero'), color="#475569")

# --- PANTALLA 2: CARTOGRAFÍA OPERATIVA ---
elif vista_seleccionada == "2. Despacho Operativo (Cartografía Satelital)":
    st.title("🗺️ Matriz Georreferenciada de Telemetría IoT")
    st.caption("Visualización espacial de estaciones costeras reguladas bajo los estándares de la Gobernanza Ambiental.")
    st.write("---")
    
    mapa = folium.Map(location=[-23.655, -70.405], zoom_start=12, tiles="Cartodb Positron")
    
    for _, row in df_datos.iterrows():
        if row['llenado_actual'] == 100.0:
            color_difuminado = "#450a0a"  # Rojo Corporativo Oscuro de Emergencia
            estado_texto = "Saturación Crítica: Requiere Despacho Vehicular Inmediato (VRP)"
            radio_mancha = 140
            peso_borde = 3
        elif row['llenado_actual'] >= 75:
            color_difuminado = "#b91c1c"  # Umbral Crítico Técnico
            estado_texto = "Umbral de Alerta Temprana Superado"
            radio_mancha = 65
            peso_borde = 0
        elif row['llenado_actual'] >= 50:
            color_difuminado = "#d97706"  # Transición
            estado_texto = "Capacidad Intermedia Estable"
            radio_mancha = 40
            peso_borde = 0
        else:
            color_difuminado = "#0f766e"  # Estado Óptimo Operacional
            estado_texto = "Rendimiento Operacional Nominal"
            radio_mancha = 25
            peso_borde = 0
            
        folium.Circle(
            location=[row['lat'], row['lon']],
            radius=radio_mancha,
            popup=f"<b>Estación:</b> {row['sector']}<br><b>Capacidad:</b> {row['llenado_actual']:.1f}%<br><b>Carga Neta:</b> {row['toneladas']:.2f} Ton<br><b>Estatus:</b> {estado_texto}",
            color="#7f1d1d" if row['llenado_actual'] == 100.0 else color_difuminado,
            fill=True,
            fill_color=color_difuminado,
            fill_opacity=0.75 if row['llenado_actual'] == 100.0 else 0.40,
            weight=peso_borde
        ).add_to(mapa)
    
    st_folium(mapa, width=1100, height=520)
    
    st.write("##")
    st.subheader("📋 Consola Analítica de Activos Fiscalizados")
    st.dataframe(
        df_datos[['sector', 'llenado_actual', 'toneladas']].rename(
            columns={'sector': 'Punto de Control', 'llenado_actual': 'Uso de Capacidad (%)', 'toneladas': 'Masa Retenida (Ton)'}
        ).style.format({'Uso de Capacidad (%)': '{:.1f}%', 'Masa Retenida (Ton)': '{:.2f} Ton'}),
        use_container_width=True
    )

# --- PANTALLA 3: CONFIGURACIÓN MÁSTER ---
else:
    st.title("⚙️ Configuración y Consola del Administrador")
    st.write("---")
    st.success("Variables del modelo matemático alineadas con los marcos regulatorios regionales.")

# Control de flujo de barrido técnico
if simulacion_activa and st.session_state.ciclo_actual < 8:
    time.sleep(velocidad_sim)
    st.rerun()
