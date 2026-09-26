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
# DICCIONARIO DE TRADUCCIONES (i18n)
# ==========================================
TRANSLATIONS = {
    "es": {
        "title": "🚗 Calibrador de Velocidad Real EDR",
        "subtitle": "**Herramienta Pericial de Cuantificación de Velocidad Real EDR (Reglamentos UN R160 / UN R39)**\n\n*Basado en la investigación científica de **Mattia Sillo, Matteo Villaraggia y David Camí González** (Congreso Europeo EVU Žilina 2026).*",
        "sidebar_header": "📋 Datos de Entrada EDR y Vehículo",
        "v_edr_label": "Velocidad Indicada EDR (Pre-Crash km/h):",
        "v_edr_help": "Valor de 'Speed, Vehicle Indicated' registrado en el informe EDR (UN R160).",
        "veh_select_label": "Vehículo Ensayado de Referencia:",
        "tire_section": "🛞 Neumáticos del Vehículo del Accidente",
        "customize_tires": "Personalizar neumáticos del vehículo del accidente",
        "w_fit": "Ancho Montado (mm)",
        "a_fit": "Perfil Montado (%)",
        "r_fit": "Llanta Montada (\")",
        "w_prog": "Ancho Programado ECU",
        "a_prog": "Perfil Programado ECU",
        "r_prog": "Llanta Programada ECU",
        "test_fitted": "Test Vehicle Fitted:",
        "test_prog": "Test Vehicle ECU Prog:",
        "use_range": "Incluir rango de incertidumbre por neumáticos homologados (Min/Max)",
        "range_section": "Rango Homologado Mínimo / Máximo:",
        "w_min": "Ancho Mín (mm)",
        "a_min": "Perfil Mín (%)",
        "r_min": "Llanta Mín (\")",
        "w_max": "Ancho Máx (mm)",
        "a_max": "Perfil Máx (%)",
        "r_max": "Llanta Máx (\")",
        "kpi_header": "🎯 Intervalo Acotado de Velocidad Real Defendible",
        "kpi1": "Velocidad Real Mínima",
        "kpi2": "Velocidad Real Máxima",
        "kpi3": "Velocidad Nominal Estimada",
        "kpi4": "Reducción de Incertidumbre",
        "vs_edr": "vs EDR",
        "mean_offset": "Offset medio",
        "range_width": "Ancho rango",
        "success_msg": "Para un valor de velocidad indicado en EDR de **{v_edr:.1f} km/h**, la velocidad real de circulación en condiciones estables se acota rigurosamente en el intervalo **[{v_min:.2f} km/h — {v_max:.2f} km/h]**.",
        "chart_header": "📊 Gráfico Comparativo: EDR vs Velocidad Real y Límites Normativos",
        "chart_title": "Curva de Calibración - {veh_name}",
        "chart_xaxis": "Velocidad Indicada EDR / Velocímetro (km/h)",
        "chart_yaxis": "Velocidad Real de Circulación VBOX (km/h)",
        "un39_upper": "UN R39 Límite Superior (V_ind = V_real)",
        "un39_lower": "UN R39 Límite Inferior Teórico",
        "vbox_data": "Datos Ensayo VBOX ({veh_name})",
        "study_case": "Intervalo Acotado Caso de Estudio",
        "breakdown_header": "🔍 Desglose de Factores de Incertidumbre",
        "col_factor": "Factor de Error / Corrección",
        "col_value": "Rango de Módulo / Valor",
        "col_effect": "Efecto en la Velocidad Real",
        "f1_name": "1. Truncamiento y Digitalización (UN R160)",
        "f1_eff": "+1.0 km/h de incertidumbre en cota superior",
        "f2_name": "2. Corrección Geométrica Neumáticos Montados (Ratio 1)",
        "f2_eff": "{pct:+.2f}% ajuste dimensional",
        "f3_name": "3. Corrección Geométrica ECU Programada (Ratio 2)",
        "f3_eff": "{pct:+.2f}% ajuste de software",
        "f4_name": "4. Offset Empírico del Velocímetro (Pruebas VBOX)",
        "f4_eff": "Reducción directa de sobreestimación de fábrica",
        "f5_name": "5. Desviación Estándar de Ensayo (2·SD + VBOX Acc)",
        "f5_eff": "Margen estadístico de estabilidad del ensayo",
        "f6_name": "RESULTADO INTERVALO FINAL ACOTADO",
        "f6_eff": "Intervalo final acotado ({width:.2f} km/h)",
        "pdf_header": "📄 Generación de Informe Pericial en PDF",
        "pdf_button": "📥 Descargar Informe Pericial (PDF)",
        "expander_title": "📚 Ver Base de Datos Empírica de los 16 Vehículos Ensayados (EVU 2026)",
        "generic_name": "Promedio Genérico de la Base de Datos (16 Vehículos)",
        "pdf_title": "INFORME PERICIAL: CALIBRACION DE VELOCIDAD EDR",
        "pdf_sub": "Basado en la metodologia EVU Zilina 2026 (Sillo, Villaraggia & Cami Gonzalez)",
        "pdf_sec1": "1. Datos de Entrada del Vehiculo y EDR",
        "pdf_sec2": "2. Resultado del Calculo de Velocidad Real",
        "pdf_sec3": "3. Justificacion Tecnica y Normativa",
        "pdf_just": "El calculo contempla las 4 fuentes de error definidas en el estudio:\n1. Truncamiento de digitalizacion de 1 km/h segun UN R160.\n2. Correccion geometrica dual de neumaticos (ratio de circunferencia montada / programada).\n3. Offset empirico medido con VBOX en condiciones de circulacion estable.\n4. Intervalo de confianza estadistico del 95% (2xSD + precision VBOX).\n\nConclusion: La velocidad reportada por el EDR sobreestima la velocidad real del vehiculo en condiciones estables, habiendose acotado el margen real de circulacion."
    },
    "ca": {
        "title": "🚗 Calibrador de Velocitat Real EDR",
        "subtitle": "**Eina Pericial de Cuantificació de Velocitat Real EDR (Reglaments UN R160 / UN R39)**\n\n*Basat en la investigació científica de **Mattia Sillo, Matteo Villaraggia i David Camí González** (Congrés Europeu EVU Žilina 2026).*",
        "sidebar_header": "📋 Dades d'Entrada EDR i Vehicle",
        "v_edr_label": "Velocitat Indicada EDR (Pre-Crash km/h):",
        "v_edr_help": "Valor de 'Speed, Vehicle Indicated' registrat a l'informe EDR (UN R160).",
        "veh_select_label": "Vehicle Assajat de Referència:",
        "tire_section": "🛞 Neumàtics del Vehicle de l'Accident",
        "customize_tires": "Personalitzar neumàtics del vehicle de l'accident",
        "w_fit": "Ample Muntat (mm)",
        "a_fit": "Perfil Muntat (%)",
        "r_fit": "Llanda Muntada (\")",
        "w_prog": "Ample Programat ECU",
        "a_prog": "Perfil Programat ECU",
        "r_prog": "Llanda Programada ECU",
        "test_fitted": "Vehicle Test Muntat:",
        "test_prog": "Vehicle Test ECU Prog:",
        "use_range": "Incloure rang d'incertesa per neumàtics homologats (Mín/Màx)",
        "range_section": "Rang Homologat Mínim / Màxim:",
        "w_min": "Ample Mín (mm)",
        "a_min": "Perfil Mín (%)",
        "r_min": "Llanda Mín (\")",
        "w_max": "Ample Màx (mm)",
        "a_max": "Perfil Màx (%)",
        "r_max": "Llanda Màx (\")",
        "kpi_header": "🎯 Interval Acotat de Velocitat Real Defensable",
        "kpi1": "Velocitat Real Mínima",
        "kpi2": "Velocitat Real Màxima",
        "kpi3": "Velocitat Nominal Estimada",
        "kpi4": "Reducció d'Incertesa",
        "vs_edr": "vs EDR",
        "mean_offset": "Offset mitjà",
        "range_width": "Ample rang",
        "success_msg": "Per a un valor de velocitat indicat en EDR de **{v_edr:.1f} km/h**, la velocitat real de circulació en condicions estables s'acota rigorosament en l'interval **[{v_min:.2f} km/h — {v_max:.2f} km/h]**.",
        "chart_header": "📊 Gràfic Comparatiu: EDR vs Velocitat Real i Límits Normatius",
        "chart_title": "Corba de Calibració - {veh_name}",
        "chart_xaxis": "Velocitat Indicada EDR / Velocímetre (km/h)",
        "chart_yaxis": "Velocitat Real de Circulació VBOX (km/h)",
        "un39_upper": "UN R39 Límite Superior (V_ind = V_real)",
        "un39_lower": "UN R39 Límite Inferior Teòric",
        "vbox_data": "Dades Assaig VBOX ({veh_name})",
        "study_case": "Interval Acotat Cas d'Estudi",
        "breakdown_header": "🔍 Desglossament de Factors d'Incertesa",
        "col_factor": "Factor d'Error / Correcció",
        "col_value": "Rang de Mòdul / Valor",
        "col_effect": "Efecte en la Velocitat Real",
        "f1_name": "1. Truncament i Digitalització (UN R160)",
        "f1_eff": "+1.0 km/h d'incertesa en cota superior",
        "f2_name": "2. Correcció Geomètrica Neumàtics Muntats (Ratio 1)",
        "f2_eff": "{pct:+.2f}% ajust dimensional",
        "f3_name": "3. Correcció Geomètrica ECU Programada (Ratio 2)",
        "f3_eff": "{pct:+.2f}% ajust de programari",
        "f4_name": "4. Offset Empíric del Velocímetre (Proves VBOX)",
        "f4_eff": "Reducció directa de sobreestimació de fàbrica",
        "f5_name": "5. Desviació Estàndard d'Assaig (2·SD + VBOX Acc)",
        "f5_eff": "Marge estadístic d'estabilitat de l'assaig",
        "f6_name": "RESULTAT INTERVAL FINAL ACOTAT",
        "f6_eff": "Interval final acotat ({width:.2f} km/h)",
        "pdf_header": "📄 Generació d'Informe Pericial en PDF",
        "pdf_button": "📥 Descarregar Informe Pericial (PDF)",
        "expander_title": "📚 Veure Base de Dades Empírica dels 16 Vehicles Assajats (EVU 2026)",
        "generic_name": "Mitjana Genèrica de la Base de Dades (16 Vehicles)",
        "pdf_title": "INFORME PERICIAL: CALIBRACIO DE VELOCITAT EDR",
        "pdf_sub": "Basat en la metodologia EVU Zilina 2026 (Sillo, Villaraggia & Cami Gonzalez)",
        "pdf_sec1": "1. Dades d'Entrada del Vehicle i EDR",
        "pdf_sec2": "2. Resultat del Calcul de Velocitat Real",
        "pdf_sec3": "3. Justificacio Tecnica i Normativa",
        "pdf_just": "El calcul contempla les 4 fonts d'error definides en l'estudi:\n1. Truncament de digitalitzacio de 1 km/h segons UN R160.\n2. Correccio geometrica dual de neumatics (ratio de circumferencia muntada / programada).\n3. Offset empiric mesurat amb VBOX en condicions de circulacio estable.\n4. Interval de confiança estadistic del 95% (2xSD + precisio VBOX).\n\nConclusio: La velocitat reportada per l'EDR sobreestima la velocitat real del vehicle en condicions estables, havent-se acotat el marge real de circulacio."
    },
    "en": {
        "title": "🚗 EDR True Speed Calibrator",
        "subtitle": "**Forensic Quantification Tool for EDR True Speed (UN R160 / UN R39 Regulations)**\n\n*Based on scientific research by **Mattia Sillo, Matteo Villaraggia, and David Camí González** (European EVU Congress Žilina 2026).*",
        "sidebar_header": "📋 EDR & Vehicle Input Data",
        "v_edr_label": "EDR Indicated Speed (Pre-Crash km/h):",
        "v_edr_help": "'Speed, Vehicle Indicated' value recorded in the EDR report (UN R160).",
        "veh_select_label": "Reference Test Vehicle:",
        "tire_section": "🛞 Accident Vehicle Tires",
        "customize_tires": "Customize accident vehicle tires",
        "w_fit": "Fitted Width (mm)",
        "a_fit": "Fitted Aspect (%)",
        "r_fit": "Fitted Rim (\")",
        "w_prog": "ECU Programmed Width",
        "a_prog": "ECU Programmed Aspect",
        "r_prog": "ECU Programmed Rim",
        "test_fitted": "Test Vehicle Fitted:",
        "test_prog": "Test Vehicle ECU Prog:",
        "use_range": "Include uncertainty range for approved tires (Min/Max)",
        "range_section": "Minimum / Maximum Approved Range:",
        "w_min": "Min Width (mm)",
        "a_min": "Min Aspect (%)",
        "r_min": "Min Rim (\")",
        "w_max": "Max Width (mm)",
        "a_max": "Max Aspect (%)",
        "r_max": "Max Rim (\")",
        "kpi_header": "🎯 Defensible True Speed Bounded Interval",
        "kpi1": "Minimum True Speed",
        "kpi2": "Maximum True Speed",
        "kpi3": "Estimated Nominal Speed",
        "kpi4": "Uncertainty Reduction",
        "vs_edr": "vs EDR",
        "mean_offset": "Mean offset",
        "range_width": "Range width",
        "success_msg": "For an EDR indicated speed of **{v_edr:.1f} km/h**, the steady-state true speed is rigorously bounded within the interval **[{v_min:.2f} km/h — {v_max:.2f} km/h]**.",
        "chart_header": "📊 Comparative Chart: EDR vs True Speed & Regulatory Limits",
        "chart_title": "Calibration Curve - {veh_name}",
        "chart_xaxis": "EDR Indicated Speed / Speedometer (km/h)",
        "chart_yaxis": "VBOX True Travel Speed (km/h)",
        "un39_upper": "UN R39 Upper Limit (V_ind = V_true)",
        "un39_lower": "UN R39 Theoretical Lower Limit",
        "vbox_data": "VBOX Test Data ({veh_name})",
        "study_case": "Case Study Bounded Interval",
        "breakdown_header": "🔍 Uncertainty Factors Breakdown",
        "col_factor": "Error / Correction Factor",
        "col_value": "Magnitude / Value Range",
        "col_effect": "Effect on True Speed",
        "f1_name": "1. Digitization & Truncation (UN R160)",
        "f1_eff": "+1.0 km/h upper boundary uncertainty",
        "f2_name": "2. Fitted Tires Geometric Correction (Ratio 1)",
        "f2_eff": "{pct:+.2f}% dimensional adjustment",
        "f3_name": "3. ECU Programmed Geometric Correction (Ratio 2)",
        "f3_eff": "{pct:+.2f}% software adjustment",
        "f4_name": "4. Empirical Speedometer Offset (VBOX Tests)",
        "f4_eff": "Direct reduction of factory overestimation",
        "f5_name": "5. Test Standard Deviation (2·SD + VBOX Acc)",
        "f5_eff": "Statistical margin for test stability",
        "f6_name": "FINAL BOUNDED INTERVAL RESULT",
        "f6_eff": "Final bounded range ({width:.2f} km/h)",
        "pdf_header": "📄 Forensic PDF Report Generation",
        "pdf_button": "📥 Download Forensic Report (PDF)",
        "expander_title": "📚 View Empirical Database of 16 Tested Vehicles (EVU 2026)",
        "generic_name": "Generic Database Average (16 Vehicles)",
        "pdf_title": "FORENSIC REPORT: EDR SPEED CALIBRATION",
        "pdf_sub": "Based on EVU Zilina 2026 methodology (Sillo, Villaraggia & Cami Gonzalez)",
        "pdf_sec1": "1. Vehicle and EDR Input Data",
        "pdf_sec2": "2. True Speed Calculation Result",
        "pdf_sec3": "3. Technical and Regulatory Justification",
        "pdf_just": "The calculation accounts for the 4 error sources defined in the study:\n1. 1 km/h digitization truncation per UN R160.\n2. Dual geometric tire correction (fitted / programmed circumference ratio).\n3. Empirical offset measured with VBOX under steady-state driving conditions.\n4. 95% statistical confidence interval (2xSD + VBOX accuracy).\n\nConclusion: Reported EDR speed overestimates steady-state true speed, yielding a defensible true speed range."
    },
    "it": {
        "title": "🚗 Calibratore di Velocità Reale EDR",
        "subtitle": "**Strumento Peritale di Quantificazione della Velocità Reale EDR (Regolamenti UN R160 / UN R39)**\n\n*Basato sulla ricerca scientifica di **Mattia Sillo, Matteo Villaraggia e David Camí González** (Congresso Europeo EVU Žilina 2026).*",
        "sidebar_header": "📋 Dati di Input EDR e Veicolo",
        "v_edr_label": "Velocità Indicata EDR (Pre-Crash km/h):",
        "v_edr_help": "Valore di 'Speed, Vehicle Indicated' registrato nel rapporto EDR (UN R160).",
        "veh_select_label": "Veicolo di Riferimento Test:",
        "tire_section": "🛞 Pneumatici del Veicolo Incidentato",
        "customize_tires": "Personalizza pneumatici del veicolo incidentato",
        "w_fit": "Larghezza Montato (mm)",
        "a_fit": "Profilo Montato (%)",
        "r_fit": "Cerchio Montato (\")",
        "w_prog": "Larghezza Programmata ECU",
        "a_prog": "Profilo Programmato ECU",
        "r_prog": "Cerchio Programmato ECU",
        "test_fitted": "Veicolo Test Montato:",
        "test_prog": "Veicolo Test ECU Prog:",
        "use_range": "Includere intervallo di incertezza per pneumatici omologati (Min/Max)",
        "range_section": "Intervallo Omologato Minimo / Massimo:",
        "w_min": "Larghezza Min (mm)",
        "a_min": "Profilo Min (%)",
        "r_min": "Cerchio Min (\")",
        "w_max": "Larghezza Max (mm)",
        "a_max": "Profilo Max (%)",
        "r_max": "Cerchio Max (\")",
        "kpi_header": "🎯 Intervallo Delimitato di Velocità Reale Difendibile",
        "kpi1": "Velocità Reale Minima",
        "kpi2": "Velocità Reale Massima",
        "kpi3": "Velocità Nominale Stimata",
        "kpi4": "Riduzione dell'Incertezza",
        "vs_edr": "vs EDR",
        "mean_offset": "Offset medio",
        "range_width": "Larghezza intervallo",
        "success_msg": "Per un valore di velocità indicata in EDR di **{v_edr:.1f} km/h**, la velocità reale di circolazione in condizioni stabili è rigorosamente delimitata nell'intervallo **[{v_min:.2f} km/h — {v_max:.2f} km/h]**.",
        "chart_header": "📊 Grafico Comparativo: EDR vs Velocità Reale e Limiti Normativi",
        "chart_title": "Curva di Calibrazione - {veh_name}",
        "chart_xaxis": "Velocità Indicata EDR / Tachimetro (km/h)",
        "chart_yaxis": "Velocità Reale di Circolazione VBOX (km/h)",
        "un39_upper": "UN R39 Limite Superiore (V_ind = V_real)",
        "un39_lower": "UN R39 Limite Inferiore Teorico",
        "vbox_data": "Dati Test VBOX ({veh_name})",
        "study_case": "Intervallo Delimitato Caso di Studio",
        "breakdown_header": "🔍 Scomposizione dei Fattori di Incertezza",
        "col_factor": "Fattore di Errore / Correzione",
        "col_value": "Intervallo di Modulo / Valore",
        "col_effect": "Effetto sulla Velocità Reale",
        "f1_name": "1. Troncamento e Digitalizzazione (UN R160)",
        "f1_eff": "+1.0 km/h di incertezza sul limite superiore",
        "f2_name": "2. Correzione Geometrica Pneumatici Montati (Rapporto 1)",
        "f2_eff": "{pct:+.2f}% regolazione dimensionale",
        "f3_name": "3. Correzione Geometrica ECU Programmata (Rapporto 2)",
        "f3_eff": "{pct:+.2f}% regolazione software",
        "f4_name": "4. Offset Empirico del Tachimetro (Test VBOX)",
        "f4_eff": "Riduzione diretta della sovrastima di fabbrica",
        "f5_name": "5. Deviazione Standard del Test (2·SD + VBOX Acc)",
        "f5_eff": "Margine statistico di stabilità del test",
        "f6_name": "RISULTATO INTERVALLO FINALE DELIMITATO",
        "f6_eff": "Intervallo finale delimitato ({width:.2f} km/h)",
        "pdf_header": "📄 Generazione del Rapporto Peritale PDF",
        "pdf_button": "📥 Scarica Rapporto Peritale (PDF)",
        "expander_title": "📚 Visualizza Database Empirico dei 16 Veicoli Testati (EVU 2026)",
        "generic_name": "Media Generica del Database (16 Veicoli)",
        "pdf_title": "RAPPORTO PERITALE: CALIBRAZIONE VELOCITA EDR",
        "pdf_sub": "Basato sulla metodologia EVU Zilina 2026 (Sillo, Villaraggia & Cami Gonzalez)",
        "pdf_sec1": "1. Dati di Input Veicolo ed EDR",
        "pdf_sec2": "2. Risultato del Calcolo della Velocita Reale",
        "pdf_sec3": "3. Giustificazione Tecnica e Normativa",
        "pdf_just": "Il calcolo tiene conto delle 4 fonti di errore definite nello studio:\n1. Troncamento di digitalizzazione di 1 km/h secondo UN R160.\n2. Correzione geometrica doppia dei pneumatici (rapporto circonferenza montata / programmata).\n3. Offset empirico misurato con VBOX in condizioni di circolazione stabile.\n4. Intervallo di confidenza statistico del 95% (2xSD + precisione VBOX).\n\nConclusione: La velocita riportata dall'EDR sovrastima la velocita reale in condizioni stabili."
    }
}

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
        "vbox": [47.9, 67.85, 87.8, 107.1, 126.4],
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
        "name_keys": {
            "es": "Promedio Genérico de la Base de Datos (16 Vehículos)",
            "ca": "Mitjana Genèrica de la Base de Dades (16 Vehicles)",
            "en": "Generic Database Average (16 Vehicles)",
            "it": "Media Generica del Database (16 Veicoli)"
        },
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
# SELECTOR DE IDIOMA EN BARRA LATERAL
# ==========================================
lang_options = {
    "English": "en",
    "Español": "es",
    "Català": "ca",
    "Italiano": "it"
}
selected_lang_label = st.sidebar.selectbox("🌐 Idioma / Language / Llengua / Lingua", list(lang_options.keys()), index=0)
lang_code = lang_options[selected_lang_label]
t = TRANSLATIONS[lang_code]

# ==========================================
# FUNCIONES MATEMÁTICAS Y GEOMÉTRICAS
# ==========================================
def parse_tire_str(tire_str):
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
    rim_mm = rim * 25.4
    sidewall_mm = width * (aspect / 100.0)
    diameter_mm = rim_mm + (2.0 * sidewall_mm)
    circumference_mm = math.pi * diameter_mm
    return diameter_mm, circumference_mm

def interpolate_test_data(vehicle_key, v_edr):
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

def get_vehicle_name(key, lang):
    v = VEHICLES_DB[key]
    if key == "GENERIC":
        return v["name_keys"].get(lang, v["name_keys"]["es"])
    return v["name"]

# ==========================================
# HEADER Y METADATOS EN PANTALLA
# ==========================================
st.title(t["title"])
st.markdown(t["subtitle"])
st.divider()

# ==========================================
# BARRA LATERAL (INPUTS DEL RECONSTRUCTOR)
# ==========================================
st.sidebar.header(t["sidebar_header"])

v_edr_input = st.sidebar.number_input(
    t["v_edr_label"],
    min_value=10.0,
    max_value=250.0,
    value=50.0,
    step=1.0,
    help=t["v_edr_help"]
)

veh_keys = list(VEHICLES_DB.keys())
veh_names = [get_vehicle_name(k, lang_code) for k in veh_keys]

selected_veh_idx = st.sidebar.selectbox(
    t["veh_select_label"],
    options=range(len(veh_names)),
    format_func=lambda i: veh_names[i],
    index=2
)
selected_key = veh_keys[selected_veh_idx]
veh_info = VEHICLES_DB[selected_key]
selected_veh_name = get_vehicle_name(selected_key, lang_code)

st.sidebar.subheader(t["tire_section"])

use_custom_tires = st.sidebar.checkbox(t["customize_tires"], value=True)

if use_custom_tires:
    col_t1, col_t2 = st.sidebar.columns(2)
    with col_t1:
        w_fit = st.number_input(t["w_fit"], 135, 335, 225, 5)
        a_fit = st.number_input(t["a_fit"], 25, 80, 50, 5)
        r_fit = st.number_input(t["r_fit"], 13, 23, 17, 1)
    with col_t2:
        w_prog = st.number_input(t["w_prog"], 135, 335, 205, 5)
        a_prog = st.number_input(t["a_prog"], 25, 80, 60, 5)
        r_prog = st.number_input(t["r_prog"], 13, 23, 16, 1)
    
    crash_fitted_str = f"{w_fit}/{a_fit} R{r_fit}"
    crash_prog_str = f"{w_prog}/{a_prog} R{r_prog}"
else:
    crash_fitted_str = veh_info["fitted_test"]
    crash_prog_str = veh_info["prog_test"]
    w_fit, a_fit, r_fit = parse_tire_str(crash_fitted_str)
    w_prog, a_prog, r_prog = parse_tire_str(crash_prog_str)

st.sidebar.caption(f"**{t['test_fitted']}** {veh_info['fitted_test']}")
st.sidebar.caption(f"**{t['test_prog']}** {veh_info['prog_test']}")

use_range = st.sidebar.checkbox(t["use_range"], value=False)

if use_range:
    st.sidebar.markdown(f"**{t['range_section']}**")
    col_r1, col_r2 = st.sidebar.columns(2)
    with col_r1:
        w_min = st.number_input(t["w_min"], 135, 335, 225, 5)
        a_min = st.number_input(t["a_min"], 25, 80, 40, 5)
        r_min = st.number_input(t["r_min"], 13, 23, 18, 1)
    with col_r2:
        w_max = st.number_input(t["w_max"], 135, 335, 225, 5)
        a_max = st.number_input(t["a_max"], 25, 80, 55, 5)
        r_max = st.number_input(t["r_max"], 13, 23, 16, 1)

# ==========================================
# CÁLCULOS PRINCIPALES
# ==========================================
v_edr_min = v_edr_input
v_edr_max = v_edr_input + 1.0

_, c_crash_fitted = calc_tire_geometry(w_fit, a_fit, r_fit)
_, c_crash_prog = calc_tire_geometry(w_prog, a_prog, r_prog)

w_tf, a_tf, r_tf = parse_tire_str(veh_info["fitted_test"])
w_tp, a_tp, r_tp = parse_tire_str(veh_info["prog_test"])
_, c_test_fitted = calc_tire_geometry(w_tf, a_tf, r_tf)
_, c_test_prog = calc_tire_geometry(w_tp, a_tp, r_tp)

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

diff_exp, sd_exp = interpolate_test_data(selected_key, v_edr_input)

vbox_acc = 0.1
delta_v_test_max_neg = -(diff_exp + (2.0 * sd_exp) + vbox_acc)
delta_v_test_min_neg = -(max(0.0, diff_exp - (2.0 * sd_exp) - vbox_acc))

v_real_min = (v_edr_min * (ratio1_min / ratio2_max)) + delta_v_test_max_neg
v_real_max = (v_edr_max * (ratio1_max / ratio2_min)) + delta_v_test_min_neg
v_nominal = (v_real_min + v_real_max) / 2.0

v_un39_max = v_edr_input
v_un39_min = (v_edr_input - 6.0) / 1.1

width_un39 = v_un39_max - v_un39_min
width_real = v_real_max - v_real_min
reduction_pct = ((width_un39 - width_real) / width_un39) * 100.0

# ==========================================
# DESPLIEGUE DE RESULTADOS EN MAIN
# ==========================================
st.subheader(t["kpi_header"])

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.metric(
        label=t["kpi1"],
        value=f"{v_real_min:.2f} km/h",
        delta=f"{(v_real_min - v_edr_input):.2f} km/h {t['vs_edr']}"
    )

with col_kpi2:
    st.metric(
        label=t["kpi2"],
        value=f"{v_real_max:.2f} km/h",
        delta=f"{(v_real_max - v_edr_input):.2f} km/h {t['vs_edr']}"
    )

with col_kpi3:
    st.metric(
        label=t["kpi3"],
        value=f"{v_nominal:.2f} km/h",
        delta=f"{t['mean_offset']}: -{diff_exp:.2f} km/h"
    )

with col_kpi4:
    st.metric(
        label=t["kpi4"],
        value=f"{reduction_pct:.1f}%",
        delta=f"{t['range_width']}: {width_real:.2f} km/h vs {width_un39:.2f} UN R39",
        delta_color="normal"
    )

st.success(t["success_msg"].format(v_edr=v_edr_input, v_min=v_real_min, v_max=v_real_max))

# ==========================================
# GRÁFICO INTERACTIVO (PLOTLY)
# ==========================================
st.subheader(t["chart_header"])

speed_range = np.linspace(30, 150, 100)
un39_upper = speed_range
un39_lower = (speed_range - 6.0) / 1.1

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=speed_range, y=un39_upper,
    mode='lines', name=t["un39_upper"],
    line=dict(color='gray', dash='dash')
))
fig.add_trace(go.Scatter(
    x=speed_range, y=un39_lower,
    mode='lines', name=t["un39_lower"],
    line=dict(color='lightgray', dash='dash'),
    fill='tonexty', fillcolor='rgba(200, 200, 200, 0.2)'
))

v_test_speeds = np.array(veh_info["speeds"])
v_test_vbox = np.array(veh_info["vbox"])

fig.add_trace(go.Scatter(
    x=v_test_speeds, y=v_test_vbox,
    mode='markers+lines', name=t["vbox_data"].format(veh_name=selected_veh_name),
    marker=dict(size=8, color='blue')
))

fig.add_trace(go.Scatter(
    x=[v_edr_input, v_edr_input],
    y=[v_real_min, v_real_max],
    mode='lines+markers',
    name=t["study_case"],
    line=dict(color='red', width=4),
    marker=dict(size=10, symbol='square', color='red')
))

fig.update_layout(
    title=t["chart_title"].format(veh_name=selected_veh_name),
    xaxis_title=t["chart_xaxis"],
    yaxis_title=t["chart_yaxis"],
    hovermode="x unified",
    height=450,
    margin=dict(l=40, r=40, t=40, b=40)
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TABLA DE DESGLOSE DE COMPONENTES DE ERROR
# ==========================================
st.subheader(t["breakdown_header"])

breakdown_data = {
    t["col_factor"]: [
        t["f1_name"],
        t["f2_name"],
        t["f3_name"],
        t["f4_name"],
        t["f5_name"],
        t["f6_name"]
    ],
    t["col_value"]: [
        f"[{v_edr_min:.1f} — {v_edr_max:.1f}] km/h",
        f"Ratio 1 = {ratio1:.4f} (Circ: {c_crash_fitted:.1f} vs {c_test_fitted:.1f} mm)",
        f"Ratio 2 = {ratio2:.4f} (Circ: {c_crash_prog:.1f} vs {c_test_prog:.1f} mm)",
        f"-{diff_exp:.2f} km/h (a {v_edr_input:.0f} km/h)",
        f"±{(2.0*sd_exp + vbox_acc):.2f} km/h (95% CI)",
        f"[{v_real_min:.2f} — {v_real_max:.2f}] km/h"
    ],
    t["col_effect"]: [
        t["f1_eff"],
        t["f2_eff"].format(pct=(ratio1-1.0)*100),
        t["f3_eff"].format(pct=(1.0/ratio2-1.0)*100),
        t["f4_eff"],
        t["f5_eff"],
        t["f6_eff"].format(width=width_real)
    ]
}

st.table(pd.DataFrame(breakdown_data))

# ==========================================
# GENERADOR DE INFORME PERICIAL PDF
# ==========================================
st.divider()
st.subheader(t["pdf_header"])

def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    pdf.cell(0, 10, t["pdf_title"], ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, t["pdf_sub"], ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, t["pdf_sec1"], ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"- EDR Indicated Speed: {v_edr_input:.1f} km/h", ln=True)
    pdf.cell(0, 6, f"- Reference Vehicle: {selected_veh_name}", ln=True)
    pdf.cell(0, 6, f"- Accident Vehicle Fitted Tire: {crash_fitted_str}", ln=True)
    pdf.cell(0, 6, f"- Accident Vehicle ECU Prog Tire: {crash_prog_str}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, t["pdf_sec2"], ln=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, f"True Speed Bounded Interval: [{v_real_min:.2f} km/h - {v_real_max:.2f} km/h]", ln=True)
    pdf.cell(0, 6, f"Estimated Nominal Speed: {v_nominal:.2f} km/h", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Range Width: {width_real:.2f} km/h (vs {width_un39:.2f} km/h UN R39 theoretical)", ln=True)
    pdf.cell(0, 6, f"Uncertainty Reduction: {reduction_pct:.1f}% vs UN R39", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, t["pdf_sec3"], ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, t["pdf_just"])
    
    return pdf.output(dest='S').encode('latin1')

pdf_bytes = generate_pdf()

st.download_button(
    label=t["pdf_button"],
    data=pdf_bytes,
    file_name=f"EDR_Speed_Report_{v_edr_input:.0f}kmh.pdf",
    mime="application/pdf"
)

# ==========================================
# EXPLORADOR DE LA BASE DE DATOS EMPÍRICA
# ==========================================
with st.expander(t["expander_title"]):
    table_rows = []
    for k, v in VEHICLES_DB.items():
        if k == "GENERIC":
            continue
        v_name = get_vehicle_name(k, lang_code)
        for i, spd in enumerate(v["speeds"]):
            table_rows.append({
                "Nº": k,
                "Vehicle": v_name,
                "Year": v["year"],
                "V_EDR (km/h)": spd,
                "V_Real VBOX (km/h)": v["vbox"][i],
                "Diff (km/h)": v["diff"][i],
                "SD (km/h)": v["sd"][i]
            })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True)
