import math
import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="EDR Speed Calibrator - EVU 2026",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# BASE DE DATOS EMPÍRICA (EVU 2026 - 16 VEHÍCULOS)
# Fuentes: Sillo, Villaraggia & Camí (EVU Žilina 2026)
# ==========================================
VEHICLES_DB = {
    "1": {
        "name": "BMW 3 Series 320d xDrive (2018)",
        "year": 2018,
        "fitted_test": "225/50 R17",
        "prog_test": "205/60 R16",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.9, 67.4, 87.0, 106.5, 126.0],
        "diff": [2.1, 2.6, 3.0, 3.5, 4.0],
        "sd": [0.1, 0.1, 0.1, 0.1, 0.2]
    },
    "2": {
        "name": "BMW X3 xDrive20d (2024)",
        "year": 2024,
        "fitted_test": "245/50 R19",
        "prog_test": "245/50 R19",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.9, 67.85, 87.8, 107.1, 126.4],  # 70 y 110 interpolados por falta de señal GPS en ensayo
        "diff": [2.8, 3.1, 3.4, 4.4, 5.4],
        "sd": [0.8, 0.85, 0.9, 0.75, 0.6]
    },
    "3": {
        "name": "BMW i4 eDrive40 (2024)",
        "year": 2024,
        "fitted_test": "225/55 R17",
        "prog_test": "225/50 R18",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [48.0, 67.3, 87.8, 106.2, 128.1],
        "diff": [1.4, 1.9, 1.1, 2.5, 0.4],
        "sd": [0.4, 0.3, 1.0, 0.4, 1.2]
    },
    "4": {
        "name": "BMW iX1 xDrive30 (2024)",
        "year": 2024,
        "fitted_test": "225/55 R18",
        "prog_test": "225/55 R18",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.8, 68.7, 88.0, 109.9, 127.5],
        "diff": [2.2, 1.3, 2.0, 0.1, 2.5],
        "sd": [0.6, 1.2, 0.4, 1.4, 0.5]
    },
    "5": {
        "name": "BMW 2 Series 220d (2025)",
        "year": 2025,
        "fitted_test": "225/45 R18",
        "prog_test": "225/45 R18",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [48.6, 68.6, 88.5, 108.5, 128.4],
        "diff": [1.4, 1.4, 1.5, 1.5, 1.6],
        "sd": [0.2, 0.1, 0.4, 0.5, 0.5]
    },
    "6": {
        "name": "BMW X1 xDrive18d (2020)",
        "year": 2020,
        "fitted_test": "225/50 R18",
        "prog_test": "225/50 R18",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.5, 67.0, 86.3, 105.7, 125.2],
        "diff": [2.5, 3.0, 3.7, 4.3, 4.8],
        "sd": [0.1, 0.1, 0.1, 0.2, 0.4]
    },
    "7": {
        "name": "Mini Cooper SE (2024)",
        "year": 2024,
        "fitted_test": "215/45 R17",
        "prog_test": "215/45 R17",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [48.4, 68.1, 88.0, 107.8, 127.6],
        "diff": [1.6, 1.9, 2.0, 2.2, 2.4],
        "sd": [0.7, 0.3, 0.1, 0.1, 0.4]
    },
    "8": {
        "name": "Mini Aceman SE (2025)",
        "year": 2025,
        "fitted_test": "225/40 R19",
        "prog_test": "205/50 R18",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [48.3, 67.9, 88.2, 107.8, 127.6],
        "diff": [1.7, 2.1, 1.8, 2.2, 2.4],
        "sd": [0.5, 0.4, 0.3, 0.1, 0.3]
    },
    "9": {
        "name": "Mini Countryman C (2024)",
        "year": 2024,
        "fitted_test": "245/45 R19",
        "prog_test": "225/55 R17",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.9, 68.5, 87.7, 107.5, 128.6],
        "diff": [2.1, 1.5, 2.3, 2.5, 1.4],
        "sd": [0.6, 0.4, 0.6, 0.4, 0.5]
    },
    "10": {
        "name": "Kia Sportage (2025)",
        "year": 2025,
        "fitted_test": "235/50 R19",
        "prog_test": "215/65 R17",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.0, 67.4, 87.3, 107.8, 127.7],
        "diff": [3.1, 2.6, 2.7, 2.2, 2.3],
        "sd": [0.4, 0.2, 0.3, 0.2, 0.1]
    },
    "11": {
        "name": "Toyota C-HR (2024)",
        "year": 2024,
        "fitted_test": "225/50 R18",
        "prog_test": "215/60 R17",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.9, 67.5, 87.5, 106.6, 126.0],
        "diff": [2.1, 2.5, 2.5, 3.4, 4.0],
        "sd": [0.1, 0.1, 0.3, 0.2, 0.3]
    },
    "12": {
        "name": "Toyota RAV4 (2023)",
        "year": 2023,
        "fitted_test": "225/60 R18",
        "prog_test": "225/65 R17",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.4, 67.3, 87.1, 107.1, 126.9],
        "diff": [2.6, 2.7, 2.9, 2.9, 3.1],
        "sd": [0.1, 0.1, 0.1, 0.2, 0.2]
    },
    "13": {
        "name": "Lexus RZ 450E (2024)",
        "year": 2024,
        "fitted_test": "235/50 R20",
        "prog_test": "235/60 R18",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [48.0, 68.1, 88.0, 108.3, 128.2],
        "diff": [2.3, 2.4, 2.7, 2.5, 2.8],
        "sd": [0.1, 0.1, 0.1, 0.2, 0.1]
    },
    "14": {
        "name": "Hyundai Tucson IX35 (2025)",
        "year": 2025,
        "fitted_test": "235/50 R19",
        "prog_test": "235/50 R19",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.7, 67.6, 88.5, 107.1, 126.9],
        "diff": [2.3, 2.4, 1.5, 2.9, 3.1],
        "sd": [0.7, 0.7, 1.2, 0.4, 0.9]
    },
    "15": {
        "name": "Suzuki Ignis (2024)",
        "year": 2024,
        "fitted_test": "175/60 R16",
        "prog_test": "175/60 R16",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [46.2, 66.6, 85.9, 106.6, 125.4],
        "diff": [3.8, 3.4, 4.1, 3.4, 4.6],
        "sd": [0.2, 0.2, 0.3, 0.3, 0.2]
    },
    "16": {
        "name": "Fiat 500X (2016)",
        "year": 2016,
        "fitted_test": "215/55 R17",
        "prog_test": "215/60 R16",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.9, 67.2, 87.6, 107.2, 126.9],
        "diff": [2.1, 2.8, 2.4, 2.8, 3.1],
        "sd": [0.1, 0.3, 0.5, 0.4, 0.2]
    },
    "GENERIC": {
        "name": "Promedio Genérico de la Base de Datos (16 Vehículos)",
        "year": 2024,
        "fitted_test": "225/50 R17",
        "prog_test": "225/50 R17",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.6, 67.5, 87.5, 107.1, 126.9],
        "diff": [2.4, 2.5, 2.5, 2.9, 3.1],
        "sd": [0.4, 0.4, 0.4, 0.4, 0.4]
    }
}

# ==========================================
# FUNCIONES MATEMÁTICAS Y GEOMÉTRICAS
# ==========================================
def parse_tire_str(tire_str):
    """
    Parsea cadenas como '225/50 R17' a (ancho, perfil, llanta).
    """
    try:
        clean = tire_str.strip().upper().replace("R", "").replace(" ", "")
        parts = clean.split("/")
        width = float(parts[0])
        subparts = parts[1].split("-") if "-" in parts[1] else [parts[1]]
        aspect = float(subparts[0])
        rim = float(subparts[1]) if len(subparts) > 1 else float(parts[1][len(str(int(aspect))):])
        return width, aspect, rim
    except Exception:
        return 225.0, 50.0, 17.0

def calc_tire_geometry(width, aspect, rim):
    """
    Calcula diámetro total (mm) y circunferencia (mm) de un neumático.
    D = (Rim * 25.4) + 2 * (Width * Aspect / 100)
    C = pi * D
    """
    rim_mm = rim * 25.4
    sidewall_mm = width * (aspect / 100.0)
    diameter_mm = rim_mm + (2.0 * sidewall_mm)
    circumference_mm = math.pi * diameter_mm
    return diameter_mm, circumference_mm

def interpolate_test_data(vehicle_key, v_edr):
    """
    Interpola linealmente la diferencia empírica (Diff) y desviación estándar (SD)
    para la velocidad EDR ingresada entre los puntos 50, 70, 90, 110, 130 km/h.
    """
    v_data = VEHICLES_DB[vehicle_key]
    speeds = np.array(v_data["speeds"])
    diffs = np.array(v_data["diff"])
    sds = np.array(v_data["sd"])

    if v_edr <= speeds[0]:
        diff_interp = float(diffs[0])
        sd_interp = float(sds[0])
    elif v_edr >= speeds[-1]:
        diff_interp = float(diffs[-1])
        sd_interp = float(sds[-1])
    else:
        diff_interp = float(np.interp(v_edr, speeds, diffs))
        sd_interp = float(np.interp(v_edr, speeds, sds))

    return diff_interp, sd_interp

# ==========================================
# HEADER Y METADATOS EN PANTALLA
# ==========================================
st.title("🚗 EDR True Speed Calibrator")
st.markdown("""
**Herramienta Pericial de Cuantificación de Velocidad Real EDR (Reglamentos UN R160 / UN R39)**  
*Basado en la investigación científica de **Mattia Sillo, Matteo Villaraggia y David Camí González** (Congreso Europeo EVU Žilina 2026).*
""")
st.divider()

# ==========================================
# BARRA LATERAL (INPUTS DEL RECONSTRUCTOR)
# ==========================================
st.sidebar.header("📋 Datos de Entrada EDR y Vehículo")

# 1. Velocidad EDR
v_edr_input = st.sidebar.number_input(
    "Velocidad Indicada EDR (Pre-Crash km/h):",
    min_value=10.0,
    max_value=250.0,
    value=50.0,
    step=1.0,
    help="Valor de 'Speed, Vehicle Indicated' registrado en el informe EDR (UN R160)."
)

# 2. Selección de Vehículo Base de Datos
veh_keys = list(VEHICLES_DB.keys())
veh_names = [VEHICLES_DB[k]["name"] for k in veh_keys]

selected_veh_idx = st.sidebar.selectbox(
    "Vehículo Ensayado de Referencia:",
    options=range(len(veh_names)),
    format_func=lambda i: veh_names[i],
    index=2  # Por defecto BMW i4
)
selected_key = veh_keys[selected_veh_idx]
veh_info = VEHICLES_DB[selected_key]

st.sidebar.subheader("🛞 Neumáticos del Vehículo del Accidente")

# Checkbox modo avanzado neumáticos
use_custom_tires = st.sidebar.checkbox("Personalizar neumáticos del vehículo del accidente", value=True)

if use_custom_tires:
    col_t1, col_t2 = st.sidebar.columns(2)
    with col_t1:
        w_fit = st.number_input("Ancho Montado (mm)", 135, 335, 225, 5)
        a_fit = st.number_input("Perfil Montado (%)", 25, 80, 50, 5)
        r_fit = st.number_input("Llanta Montada (\")", 13, 23, 17, 1)
    with col_t2:
        w_prog = st.number_input("Ancho Programado ECU", 135, 335, 205, 5)
        a_prog = st.number_input("Perfil Programado ECU", 25, 80, 60, 5)
        r_prog = st.number_input("Llanta Programada ECU", 13, 23, 16, 1)
    
    crash_fitted_str = f"{w_fit}/{a_prog} R{r_fit}"
    crash_prog_str = f"{w_prog}/{a_prog} R{r_prog}"
else:
    crash_fitted_str = veh_info["fitted_test"]
    crash_prog_str = veh_info["prog_test"]
    w_fit, a_fit, r_fit = parse_tire_str(crash_fitted_str)
    w_prog, a_prog, r_prog = parse_tire_str(crash_prog_str)

st.sidebar.caption(f"**Test Vehicle Fitted:** {veh_info['fitted_test']}")
st.sidebar.caption(f"**Test Vehicle ECU Prog:** {veh_info['prog_test']}")

# Residual Uncertainty (Rango Min/Max Homologado)
use_range = st.sidebar.checkbox("Incluir rango de incertidumbre por neumáticos homologados (Min/Max)", value=False)

if use_range:
    st.sidebar.markdown("**Rango Homologado Mínimo / Máximo:**")
    col_r1, col_r2 = st.sidebar.columns(2)
    with col_r1:
        w_min = st.number_input("Ancho Mín (mm)", 135, 335, 225, 5)
        a_min = st.number_input("Perfil Mín (%)", 25, 80, 40, 5)
        r_min = st.number_input("Llanta Mín (\")", 13, 23, 18, 1)
    with col_r2:
        w_max = st.number_input("Ancho Máx (mm)", 135, 335, 225, 5)
        a_max = st.number_input("Perfil Máx (%)", 25, 80, 55, 5)
        r_max = st.number_input("Llanta Máx (\")", 13, 23, 16, 1)

# ==========================================
# CÁLCULOS PRINCIPALES
# ==========================================
# 1. Truncamiento EDR (UN R160)
v_edr_min = v_edr_input
v_edr_max = v_edr_input + 1.0  # Truncamiento de 1 km/h

# 2. Geometría de Neumáticos
# Vehículo de Accidente
_, c_crash_fitted = calc_tire_geometry(w_fit, a_fit, r_fit)
_, c_crash_prog = calc_tire_geometry(w_prog, a_prog, r_prog)

# Vehículo de Ensayo
w_tf, a_tf, r_tf = parse_tire_str(veh_info["fitted_test"])
w_tp, a_tp, r_tp = parse_tire_str(veh_info["prog_test"])
_, c_test_fitted = calc_tire_geometry(w_tf, a_tf, r_tf)
_, c_test_prog = calc_tire_geometry(w_tp, a_tp, r_tp)

# Ratio Dual (Pestaña i4 Final & Sección III.3 Paper)
ratio1 = c_crash_fitted / c_test_fitted
ratio2 = c_crash_prog / c_test_prog

if use_range:
    _, c_min = calc_tire_geometry(w_min, a_min, r_min)
    _, c_max = calc_tire_geometry(w_max, a_max, r_max)
    ratio1_min = min(c_crash_fitted, c_min) / c_test_fitted
    ratio1_max = max(c_crash_fitted, c_max) / c_test_fitted
    ratio2_min = min(c_crash_prog, c_min) / c_test_prog
    ratio2_max = max(c_crash_prog, c_max) / c_test_prog
else:
    ratio1_min = ratio1_max = ratio1
    ratio2_min = ratio2_max = ratio2

# 3. Offset Empírico Interpolado
diff_exp, sd_exp = interpolate_test_data(selected_key, v_edr_input)

# Error algebraico experimental (95% confianza con 2*SD + Precisión VBOX 0.1)
vbox_acc = 0.1
delta_v_test_max_neg = -(diff_exp + (2.0 * sd_exp) + vbox_acc)  # cota inferior de velocidad real
delta_v_test_min_neg = -(max(0.0, diff_exp - (2.0 * sd_exp) - vbox_acc))  # cota superior de velocidad real

# 4. Velocidad Real Acotada (Bounded Interval)
# Fórmulas Sección III.3:
# V_min = (V_edr_min * (Ratio1_min / Ratio2_max)) + delta_v_test_max_neg
# V_max = (V_edr_max * (Ratio1_max / Ratio2_min)) + delta_v_test_min_neg
v_real_min = (v_edr_min * (ratio1_min / ratio2_max)) + delta_v_test_max_neg
v_real_max = (v_edr_max * (ratio1_max / ratio2_min)) + delta_v_test_min_neg
v_nominal = (v_real_min + v_real_max) / 2.0

# 5. Comparativa UN R39 Teórico
v_un39_max = v_edr_input
v_un39_min = (v_edr_input - 6.0) / 1.1

width_un39 = v_un39_max - v_un39_min
width_real = v_real_max - v_real_min
reduction_pct = ((width_un39 - width_real) / width_un39) * 100.0

# ==========================================
# DESPLIEGUE DE RESULTADOS EN MAIN
# ==========================================
st.subheader("🎯 Intervalo Acotado de Velocidad Real Defendible")

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.metric(
        label="Velocidad Real Mínima",
        value=f"{v_real_min:.2f} km/h",
        delta=f"{(v_real_min - v_edr_input):.2f} km/h vs EDR"
    )

with col_kpi2:
    st.metric(
        label="Velocidad Real Máxima",
        value=f"{v_real_max:.2f} km/h",
        delta=f"{(v_real_max - v_edr_input):.2f} km/h vs EDR"
    )

with col_kpi3:
    st.metric(
        label="Velocidad Nominal Estimada",
        value=f"{v_nominal:.2f} km/h",
        delta=f"Offset medio: -{diff_exp:.2f} km/h"
    )

with col_kpi4:
    st.metric(
        label="Reducción de Incertidumbre",
        value=f"{reduction_pct:.1f}%",
        delta=f"Ancho rango: {width_real:.2f} km/h vs {width_un39:.2f} UN R39",
        delta_color="normal"
    )

st.success(f"**Resultado para Informe Pericial:** Para un valor de velocidad indicado en EDR de **{v_edr_input:.1f} km/h**, la velocidad real de circulación en condiciones estables se acota rigurosamente en el intervalo **[{v_real_min:.2f} km/h — {v_real_max:.2f} km/h]**.")

# ==========================================
# GRÁFICO INTERACTIVO (PLOTLY)
# ==========================================
st.subheader("📊 Gráfico Comparativo: EDR vs Velocidad Real y Límites Normativos")

speed_range = np.linspace(30, 150, 100)
un39_upper = speed_range
un39_lower = (speed_range - 6.0) / 1.1

fig = go.Figure()

# Rango UN R39
fig.add_trace(go.Scatter(
    x=speed_range, y=un39_upper,
    mode='lines', name='UN R39 Límite Superior (V_ind = V_real)',
    line=dict(color='gray', dash='dash')
))
fig.add_trace(go.Scatter(
    x=speed_range, y=un39_lower,
    mode='lines', name='UN R39 Límite Inferior Teórico',
    line=dict(color='lightgray', dash='dash'),
    fill='tonexty', fillcolor='rgba(200, 200, 200, 0.2)'
))

# Curva del vehículo seleccionado
v_test_speeds = np.array(veh_info["speeds"])
v_test_vbox = np.array(veh_info["vbox"])

fig.add_trace(go.Scatter(
    x=v_test_speeds, y=v_test_vbox,
    mode='markers+lines', name=f'Datos Ensayo VBOX ({veh_info["name"]})',
    marker=dict(size=8, color='blue')
))

# Punto de Estudio Accidente
fig.add_trace(go.Scatter(
    x=[v_edr_input, v_edr_input],
    y=[v_real_min, v_real_max],
    mode='lines+markers',
    name='Intervalo Acotado Caso de Estudio',
    line=dict(color='red', width=4),
    marker=dict(size=10, symbol='square', color='red')
))

fig.update_layout(
    title=f"Curva de Calibración - {veh_info['name']}",
    xaxis_title="Velocidad Indicada EDR / Velocímetro (km/h)",
    yaxis_title="Velocidad Real de Circulación VBOX (km/h)",
    hovermode="x unified",
    height=450,
    margin=dict(l=40, r=40, t=40, b=40)
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TABLA DE DESGLOSE DE COMPONENTES DE ERROR
# ==========================================
st.subheader("🔍 Desglose de Factores de Incertidumbre")

breakdown_data = {
    "Factor de Error / Corrección": [
        "1. Truncamiento y Digitalización (UN R160)",
        "2. Corrección Geométrica Neumáticos Montados (Ratio 1)",
        "3. Corrección Geométrica ECU Programada (Ratio 2)",
        "4. Offset Empírico del Velocímetro (Pruebas VBOX)",
        "5. Desviación Estándar de Ensayo (2·SD + VBOX Acc)",
        "RESULTADO INTERVALO FINAL ACOTADO"
    ],
    "Rango de Módulo / Valor": [
        f"[{v_edr_min:.1f} — {v_edr_max:.1f}] km/h",
        f"Ratio 1 = {ratio1:.4f} (Circ: {c_crash_fitted:.1f} vs {c_test_fitted:.1f} mm)",
        f"Ratio 2 = {ratio2:.4f} (Circ: {c_crash_prog:.1f} vs {c_test_prog:.1f} mm)",
        f"-{diff_exp:.2f} km/h (a {v_edr_input:.0f} km/h)",
        f"±{(2.0*sd_exp + vbox_acc):.2f} km/h (95% CI)",
        f"[{v_real_min:.2f} — {v_real_max:.2f}] km/h"
    ],
    "Efecto en la Velocidad Real": [
        "+1.0 km/h de incertidumbre en cota superior",
        f"{((ratio1-1.0)*100):+.2f}% ajuste dimensional",
        f"{((1.0/ratio2-1.0)*100):+.2f}% ajuste de software",
        "Reducción directa de sobreestimación de fábrica",
        "Margen estadístico de estabilidad del ensayo",
        f"Intervalo final acotado ({width_real:.2f} km/h)"
    ]
}

st.table(pd.DataFrame(breakdown_data))

# ==========================================
# GENERADOR DE INFORME PERICIAL PDF
# ==========================================
st.divider()
st.subheader("📄 Generación de Informe Pericial en PDF")

def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Título
    pdf.cell(0, 10, "INFORME PERICIAL: CALIBRACION DE VELOCIDAD EDR", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "Basado en la metodologia EVU Zilina 2026 (Sillo, Villaraggia & Cami Gonzalez)", ln=True, align="C")
    pdf.ln(10)
    
    # Datos de entrada
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "1. Datos de Entrada del Vehiculo y EDR", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"- Velocidad Indicada EDR Pre-Crash: {v_edr_input:.1f} km/h", ln=True)
    pdf.cell(0, 6, f"- Vehiculo de Referencia Ensayo: {veh_info['name']}", ln=True)
    pdf.cell(0, 6, f"- Neumatico Montado Vehiculo Accidente: {crash_fitted_str}", ln=True)
    pdf.cell(0, 6, f"- Neumatico Programado ECU Accidente: {crash_prog_str}", ln=True)
    pdf.ln(5)
    
    # Resultados
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "2. Resultado del Calculo de Velocidad Real", ln=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, f"Intervalo Acotado de Velocidad Real: [{v_real_min:.2f} km/h - {v_real_max:.2f} km/h]", ln=True)
    pdf.cell(0, 6, f"Velocidad Nominal Estimada: {v_nominal:.2f} km/h", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Ancho del Rango Acotado: {width_real:.2f} km/h (vs {width_un39:.2f} km/h teorico UN R39)", ln=True)
    pdf.cell(0, 6, f"Reduccion de Incertidumbre: {reduction_pct:.1f}% respecto a UN R39", ln=True)
    pdf.ln(5)
    
    # Justificación
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "3. Justificacion Tecnica y Normativa", ln=True)
    pdf.set_font("Arial", "", 9)
    justification = (
        "El calculo contempla las 4 fuentes de error definidas en el estudio:\n"
        "1. Truncamiento de digitalizacion de 1 km/h segun UN R160.\n"
        "2. Correccion geometrica dual de neumaticos (ratio de circunferencia montada / programada).\n"
        "3. Offset empirico medido con VBOX en condiciones de circulacion estable.\n"
        "4. Intervalo de confianza estadistico del 95% (2xSD + precision VBOX).\n\n"
        "Conclusion: La velocidad reportada por el EDR sobreestima la velocidad real del vehiculo "
        "en condiciones estables, habiendose acotado el margen real de circulacion."
    )
    pdf.multi_cell(0, 5, justification)
    
    return pdf.output(dest='S').encode('latin1')

pdf_bytes = generate_pdf()

st.download_button(
    label="📥 Descargar Informe Pericial (PDF)",
    data=pdf_bytes,
    file_name=f"Informe_EDR_Velocidad_{v_edr_input:.0f}kmh.pdf",
    mime="application/pdf"
)

# ==========================================
# EXPLORADOR DE LA BASE DE DATOS EMPÍRICA
# ==========================================
with st.expander("📚 Ver Base de Datos Empírica de los 16 Vehículos Ensayados (EVU 2026)"):
    table_rows = []
    for k, v in VEHICLES_DB.items():
        if k == "GENERIC":
            continue
        for i, spd in enumerate(v["speeds"]):
            table_rows.append({
                "Nº": k,
                "Vehículo": v["name"],
                "Año": v["year"],
                "V_EDR (km/h)": spd,
                "V_Real VBOX (km/h)": v["vbox"][i],
                "Diferencia (km/h)": v["diff"][i],
                "SD (km/h)": v["sd"][i]
            })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True)
