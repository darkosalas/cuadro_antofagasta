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



# REPLICACIÓN DE LA PALETA ESTÉTICA DE LA IMAGEN (CSS) + ESTILOS NUEVOS

st.markdown("""

    <style>

    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

    body { background-color: #ffffff; }

    

    /* Barra Lateral Dark Navy */

    [data-testid="stSidebar"] { background-color: #0e1e38 !important; }

    [data-testid="stSidebar"] * { color: #ffffff !important; }

    

    /* Contenedor Base de Tarjetas KPI */

    .card-kpi {

        padding: 15px 20px;

        border-radius: 6px;

        box-shadow: 0 1px 3px rgba(0,0,0,0.1);

        margin-bottom: 15px;

        min-height: 125px;

    }

    .card-title { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #475569; margin-bottom: 4px; }

    .card-value { font-size: 28px; font-weight: 800; color: #1e293b; display: flex; align-items: center; gap: 5px; }

    .card-sub { font-size: 11px; color: #64748b; margin-top: 4px; font-weight: 500; }

    

    /* Colores Pastel de Tarjetas */

    .kpi-ambiental { background-color: #e6f4ea; border-top: 4px solid #137333; }

    .kpi-ambiental .card-title { color: #137333; }

    .kpi-ambiental .delta { color: #137333; font-size: 18px; }

    

    .kpi-logistica { background-color: #feeee3; border-top: 4px solid #e67e22; }

    .kpi-logistica .card-title { color: #b06000; }

    .kpi-logistica .delta { color: #137333; font-size: 18px; }

    

    .kpi-comunidad { background-color: #f3e8fd; border-top: 4px solid #8430ce; }

    .kpi-comunidad .card-title { color: #681da8; }

    .kpi-comunidad .delta { color: #137333; font-size: 18px; }

    

    .kpi-financiera { background-color: #fef7e0; border-top: 4px solid #f2a104; }

    .kpi-financiera .card-title { color: #b06000; }

    .kpi-financiera .delta { color: #c5221f; font-size: 18px; }



    /* Alerta de Contingencia */

    .alerta-operativo {

        background-color: #fef2f2;

        border-left: 5px solid #991b1b;

        color: #7f1d1d;

        padding: 15px;

        border-radius: 4px;

        font-weight: 500;

        margin-bottom: 15px;

        font-size: 13.5px;

    }

    

    /* Caja de Éxito de Despacho */

    .despacho-exito {

        background-color: #f0fdf4;

        border-left: 5px solid #16a34a;

        color: #14532d;

        padding: 15px;

        border-radius: 4px;

        font-weight: 500;

        margin-bottom: 15px;

        font-size: 13.5px;

    }

    </style>

""", unsafe_allow_html=True)



# 2. CONTROLADORES EN MENÚ LATERAL

st.sidebar.markdown("### 📋 PANEL OPERATIVO")

st.sidebar.write("---")



simulacion_activa = st.sidebar.toggle("Ejecutar Simulación IoT", value=True)

velocidad_sim = st.sidebar.slider("Barrido de tiempo (segundos):", 2, 10, 4)



# Inicialización de Estados Globales de la Simulación

if 'ciclo_actual' not in st.session_state:

    st.session_state.ciclo_actual = 0

if 'ruta_despachada' not in st.session_state:

    st.session_state.ruta_despachada = False



if st.sidebar.button("🔄 Reiniciar Parámetros Base"):

    st.session_state.ciclo_actual = 0

    st.session_state.ruta_despachada = False

    if 'datos_simulados' in st.session_state:

        del st.session_state['datos_simulados']

    st.rerun()



st.sidebar.write("---")

vista_seleccionada = st.sidebar.radio(

    "Navegación del Sistema:",

    ["1. Vista Estratégica (CMI)", "2. Vista Operativa (Mapa Satelital)", "3. Configuración de Alertas"]

)



# ==============================================================================

# 3. SET DE DATOS DINÁMICOS CON TODAS LAS UBICACIONES DE ANTOFAGASTA

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

        'toneladas_max': [2.5, 1.2, 2.0, 1.8, 1.5, 2.2, 1.2, 1.0, 1.6],

        'toneladas': [1.12, 0.48, 1.2, 0.63, 0.75, 1.21, 0.3, 0.15, 0.48],

        'eta_min': [120, 340, 180, 410, 220, 190, 500, 800, 290]

    })



# EVOLUCIÓN CRONOLÓGICA CON FILTRO DE ACCIÓN EN VIVO

if simulacion_activa and not st.session_state.ruta_despachada:

    st.session_state.ciclo_actual += 1

    df = st.session_state.datos_simulados

    

    if st.session_state.ciclo_actual <= 3:

        df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 45.0 + (st.session_state.ciclo_actual * 10)

        df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'eta_min'] = 90 - (st.session_state.ciclo_actual * 20)

    elif 4 <= st.session_state.ciclo_actual <= 5:

        df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 78.0 if st.session_state.ciclo_actual == 4 else 94.0

        df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'eta_min'] = 25 if st.session_state.ciclo_actual == 4 else 8

    else:

        df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 100.0

        df.loc[df['sector'] == 'Terminal Pesquero Antofagasta', 'eta_min'] = 0



    df['toneladas'] = np.round((df['llenado_actual'] / 100.0) * df['toneladas_max'], 2)

    st.session_state.datos_simulados = df



df_datos = st.session_state.datos_simulados



# ==============================================================================

# 4. DISPOSITIVOS DE INTERFAZ DE USUARIO (DASHBOARD COMPLETO)

# ==============================================================================

if vista_seleccionada == "1. Vista Estratégica (CMI)":

    

    st.markdown("<h2>📊 Cuadro de Mando Integral Público-Ambiental</h2>", unsafe_allow_html=True)

    st.markdown("<p style='color:#475569; margin-top:-10px; font-size:14px;'>Monitoreo automatizado de las 4 perspectivas estratégicas del proyecto</p>", unsafe_allow_html=True)

    

    saturados = df_datos[df_datos['llenado_actual'] == 100.0]

    

    if st.session_state.ruta_despachada:

        st.markdown("""

        <div class="despacho-exito">

            ✅ <strong>SISTEMA EN ETAPA DE MITIGACIÓN:</strong> Se ha ejecutado el algoritmo matemático de ruteo vehicular VRP. La unidad recolectora municipal ha salido desde la <strong>Ilustre Municipalidad de Antofagasta</strong> y se encuentra en ruta. Los niveles del nodo crítico se han restablecido a parámetros seguros (15% de capacidad remanente).

        </div>

        """, unsafe_allow_html=True)

    elif not saturados.empty:

        for _, sat in saturados.iterrows():

            st.markdown(f"""

            <div class="alerta-operativo">

                🚨 <strong>ALERTA LOGÍSTICA CRÍTICA DETECTADA:</strong> El contenedor de <strong>{sat['sector']}</strong> ha alcanzado su capacidad límite estructural ({sat['toneladas']:.2f} Ton). Tiempo de Resiliencia: 0 min.

            </div>

            """, unsafe_allow_html=True)

        

        if st.button("⚡ CALCULAR Y DESPACHAR RUTA OPTIMIZADA (MODELO VRP)"):

            df_datos.loc[df_datos['sector'] == 'Terminal Pesquero Antofagasta', 'llenado_actual'] = 15.0

            df_datos.loc[df_datos['sector'] == 'Terminal Pesquero Antofagasta', 'toneladas'] = 0.35

            df_datos.loc[df_datos['sector'] == 'Terminal Pesquero Antofagasta', 'eta_min'] = 240

            st.session_state.datos_simulados = df_datos

            st.session_state.ruta_despachada = True

            st.rerun()



    # RENDERIZADO DE LAS 4 TARJETAS ESTILO PASTEL

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown('<div class="card-kpi kpi-ambiental"><div class="card-title">1. (Ambiental)<br><b>🌿 SOSTENIBILIDAD AMBIENTAL</b></div><div class="card-value">42.5% <span class="delta">▲</span></div><div class="card-sub">Mitigación de Infracciones (vs. 2025)</div></div>', unsafe_allow_html=True)

    with col2:

        media_llenado = df_datos['llenado_actual'].mean()

        st.markdown(f'<div class="card-kpi kpi-logistica"><div class="card-title">2. (Logística)<br><b>🚚 PROCESOS LOGÍSTICOS</b></div><div class="card-value">{media_llenado:.1f}% <span class="delta">▲</span></div><div class="card-sub">Capacidad Promedio General del Borde Costero</div></div>', unsafe_allow_html=True)

    with col3:

        st.markdown('<div class="card-kpi kpi-comunidad"><div class="card-title">3. (Comunidad)<br><b>👥 USUARIOS Y GOBERNANZA</b></div><div class="card-value">86.4% <span class="delta">▲</span></div><div class="card-sub">Índice Satisfacción Vecinal (Encuestas)</div></div>', unsafe_allow_html=True)

    with col4:

        ton_totales = df_datos['toneladas'].sum()

        costo_por_tonelada = (14500 / max(1.0, ton_totales)) * 3.5

        st.markdown(f'<div class="card-kpi kpi-financiera"><div class="card-title">4. (Financiera)<br><b>💰 FINANCIERA Y EFICIENCIA</b></div><div class="card-value">${costo_por_tonelada:,.0f} <span class="delta" style="color:#c5221f;">▼</span></div><div class="card-sub">Costo Promedio por Tonelada Recolectada</div></div>', unsafe_allow_html=True)



    st.write("---")



    # SECCIÓN DE GRÁFICOS PARALELOS (Corregido de image_ddec43.png usando stack=True)

    col_g1, col_g2 = st.columns(2)

    with col_g1:

        st.markdown("##### Análisis Comparativo de Infracciones Sanitarias (Anual)")

        meses_chart = ['Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct']

        df_infracciones = pd.DataFrame({

            'Año Anterior (2025)': [11, 9.5, 8.2, 7.5, 5.8, 4.2, 3.1, 1.8],

            'Año Actual (2026)': [10.2, 7.0, 6.3, 5.2, 3.8, 2.5, 1.2, 0.7]

        }, index=meses_chart)

        st.bar_chart(df_infracciones, color=["#3182bd", "#31a354"])

        

    with col_g2:

        st.markdown("##### 🌱 Destinación de Residuos a Economía Circular (Toneladas)")

        categorias_sustentables = pd.DataFrame({

            'Composting Orgánico': [df_datos.loc[0, 'toneladas'] * 0.65, 0.4, 0.8, 0.1],

            'Reciclaje Industrial': [0.2, 0.1, 0.3, 0.5],

            'Vertedero Tradicional': [df_datos.loc[0, 'toneladas'] * 0.35, 0.2, 0.4, 0.3]

        }, index=['Terminal Pesquero', 'Balneario Municipal', 'Playa Brava', 'Playa Trocadero'])

        st.bar_chart(categorias_sustentables, stack=True, color=["#31a354", "#3182bd", "#e67e22"])



    st.write("---")



    # INTEGRACIÓN DEL MAPA CON TRAZADO DE RUTA DESDE LA MUNICIPALIDAD

    st.markdown("##### Monitoreo de Saturación Georreferenciada en Tiempo Real")

    mapa = folium.Map(location=[-23.648, -70.400], zoom_start=13, tiles="Cartodb Positron")

    

    # Marcador fijo de la Municipalidad de Antofagasta

    folium.Marker(

        location=[-23.6450, -70.3950],

        popup="<b>Municipalidad de Antofagasta</b><br>Base Central de Despacho Logístico",

        icon=folium.Icon(color='blue', icon='building', prefix='fa')

    ).add_to(mapa)



    # Si se activa la mitigación, traza el camino optimizado desde la municipalidad

    if st.session_state.ruta_despachada:

        coordenadas_ruta = [

            [-23.6450, -70.3950], # ORIGEN: Municipalidad de Antofagasta

            [-23.6457, -70.3972], # Enlace vial (Muelle Histórico)

            [-23.6428, -70.3996]  # DESTINO: Terminal Pesquero

        ]

        folium.PolyLine(

            locations=coordenadas_ruta,

            color="#16a34a",

            weight=5,

            opacity=0.85,

            tooltip="Ruta de Mitigación Despachada desde la Municipalidad"

        ).add_to(mapa)

        

        folium.Marker(

            location=[-23.6454, -70.3965],

            popup="Unidad Recolectora Municipal en Ruta",

            icon=folium.Icon(color='green', icon='truck', prefix='fa')

        ).add_to(mapa)



    for _, row in df_datos.iterrows():

        if row['llenado_actual'] == 100.0:

            color_nodo = "#ff0000"

            radio = 140

            opacidad = 0.7

            txt_eta = "COLAPSO CRÍTICO ACTIVO"

        elif row['llenado_actual'] >= 75:

            color_nodo = "#e67e22"

            radio = 80

            opacidad = 0.5

            txt_eta = f"Inminente ({row['eta_min']} min)"

        else:

            color_nodo = "#2ecc71"

            radio = 40

            opacidad = 0.4

            txt_eta = f"Estable (> {row['eta_min']} min)"

            

        folium.Circle(

            location=[row['lat'], row['lon']],

            radius=radio,

            popup=f"<b>Sector:</b> {row['sector']}<br><b>Llenado:</b> {row['llenado_actual']:.1f}%<br><b>Masa:</b> {row['toneladas']} Ton<br><b>Predicción de Colapso:</b> {txt_eta}",

            color=color_nodo,

            fill=True,

            fill_color=color_nodo,

            fill_opacity=opacidad,

            weight=1 if row['llenado_actual'] == 100.0 else 0

        ).add_to(mapa)

        

    st_folium(mapa, width=1300, height=380)



    # NUEVO DISPOSITIVO: TABLA CON EL DESGLOSE DE CAPACIDADES DE TODOS LOS SECTORES Y PLAYAS

    st.write("---")

    st.markdown("##### 🏖️ Monitoreo de Capacidad por Nodo Regional (Playas y Sectores)")

    

    # Formatear el DataFrame para la lectura del usuario académico/comisión

    df_tabla = df_datos[['sector', 'llenado_actual', 'toneladas', 'toneladas_max', 'eta_min']].copy()

    df_tabla.columns = ['Sector / Playa', '% de Llenado Actual', 'Masa Almacenada (Ton)', 'Capacidad Máxima (Ton)', 'Tiempo de Resiliencia (Min)']

    

    # Renderizado en una tabla nativa estilizada y ordenada por nivel de saturación

    st.dataframe(

        df_tabla.sort_values(by='% de Llenado Actual', ascending=False),

        use_container_width=True,

        hide_index=True

    )



else:

    st.title("⚙️ Configuración del Sistema")

    st.info("Utilice el menú lateral para regresar al Cuadro de Mando Integral principal.")



if simulacion_activa and st.session_state.ciclo_actual < 8 and not st.session_state.ruta_despachada:

    time.sleep(velocidad_sim)

    st.rerun() en el apartado de 2. vista operativa(mapa satelital)
