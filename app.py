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
        "unknown_fit_check": "Neumático instalado desconocido",
        "unknown_prog_check": "Neumático programado ECU desconocido",
        "unknown_warning": "⚠️ Al marcar neumáticos como desconocidos, la app evalúa la envolvente completa de opciones dentro del rango homologado ({w_min}/{a_min} R{r_min} — {w_max}/{a_max} R{r_max}). Esto amplía el intervalo de velocidad real y muestra la menor reducción de incertidumbre.",
        "unknown_str": "DESCONOCIDO (Evaluado en rango homologado)",
        "admin_header": "🔐 Administración: Añadir Nuevo Vehículo",
        "admin_pass_label": "🔑 Contraseña de acceso:",
        "admin_unlock_btn": "Desbloquear Panel Admin",
        "admin_form_title": "➕ Registro de Nuevo Vehículo de Ensayo",
        "admin_veh_name": "Marca y Modelo (ej. Tesla Model 3)",
        "admin_veh_year": "Año de Modelo",
        "admin_fitted_tire": "Neumático Montado en Test (ej. 235/45 R18)",
        "admin_prog_tire": "Neumático Programado ECU (ej. 235/45 R18)",
        "admin_save_btn": "💾 Guardar Vehículo en Base de Datos",
        "admin_success_msg": "¡Vehículo '{name}' registrado con éxito!",
        "admin_wrong_pass": "❌ Contraseña incorrecta. Inténtalo de nuevo.",
        "admin_pass_ok": "🔓 Acceso concedido.",
        "admin_custom_badge": " (Personalizado / Custom)",

        "title": "🚗 Calibrador de Velocidad Real EDR",
        "subtitle": "**Herramienta Pericial de Cuantificación de Velocidad Real EDR (Reglamentos UN R160 / UN R39)**\n\n*Basado en la investigación científica de **Mattia Sillo, Matteo Villaraggia y David Camí González** (Congreso Europeo EVU Žilina 2026).*",
        "sidebar_header": "📋 Datos de Entrada EDR y Vehículo",
        "v_edr_label": "Velocidad Indicada EDR Pre-Crash (km/h):",
        "v_edr_help": "Valor de 'Speed, Vehicle Indicated' registrado en el informe EDR (UN R160).",
        "veh_select_label": "Vehículo Ensayado de Referencia:",
        "tire_section": "🛞 Neumáticos del Vehículo del Accidente",
        "customize_tires": "Personalizar neumáticos del vehículo del accidente",
        "w_fit": "Ancho Montado (mm)",
        "a_fit": "Perfil Montado (%)",
        "r_fit": "Llanta Montada (\")",
        "w_prog": "Ancho Programado ECU (mm)",
        "a_prog": "Perfil Programado ECU (%)",
        "r_prog": "Llanta Programada ECU (\")",
        "unk_fit_title": "Neumático Montado",
        "unk_prog_title": "Neumático Programado ECU",
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
        "unknown_fit_check": "Pneumàtic muntat desconegut",
        "unknown_prog_check": "Pneumàtic programat ECU desconegut",
        "unknown_warning": "⚠️ En marcar pneumàtics com a desconeguts, l'app avalua l'envolupant completa d'opcions dins del rang homologat ({w_min}/{a_min} R{r_min} — {w_max}/{a_max} R{r_max}). Això amplia l'interval de velocitat real i mostra la menor reducció d'incertesa.",
        "unknown_str": "DESCONEGUT (Avaluat en rang homologat)",
        "admin_header": "🔐 Administració: Afegir Nou Vehicle",
        "admin_pass_label": "🔑 Contrasenya d'accés:",
        "admin_unlock_btn": "Desbloquejar Panell Admin",
        "admin_form_title": "➕ Registre de Nou Vehicle d'Assaig",
        "admin_veh_name": "Marca i Model (ex. Tesla Model 3)",
        "admin_veh_year": "Any de Model",
        "admin_fitted_tire": "Pneumàtic Muntat en Test (ex. 235/45 R18)",
        "admin_prog_tire": "Pneumàtic Programat ECU (ex. 235/45 R18)",
        "admin_save_btn": "💾 Desar Vehicle a la Base de Dades",
        "admin_success_msg": "Vehicle '{name}' registrat amb èxit!",
        "admin_wrong_pass": "❌ Contrasenya incorrecta. Torna-ho a provar.",
        "admin_pass_ok": "🔓 Accés concedit.",
        "admin_custom_badge": " (Personalitzat)",

        "title": "🚗 Calibrador de Velocitat Real EDR",
        "subtitle": "**Eina Pericial de Quantificació de Velocitat Real EDR (Reglaments UN R160 / UN R39)**\n\n*Basat en la investigació científica de **Mattia Sillo, Matteo Villaraggia i David Camí González** (Congrés Europeu EVU Žilina 2026).*",
        "sidebar_header": "📋 Dades d'Entrada EDR i Vehicle",
        "v_edr_label": "Velocitat Indicada EDR Pre-Crash (km/h):",
        "v_edr_help": "Valor de 'Speed, Vehicle Indicated' registrat a l'informe EDR (UN R160).",
        "veh_select_label": "Vehicle Assajat de Referència:",
        "tire_section": "🛞 Pneumàtics del Vehicle de l'Accident",
        "customize_tires": "Personalitzar pneumàtics del vehicle de l'accident",
        "w_fit": "Amplada Muntat (mm)",
        "a_fit": "Perfil Muntat (%)",
        "r_fit": "Llanda Muntada (\")",
        "w_prog": "Amplada Programada ECU (mm)",
        "a_prog": "Perfil Programat ECU (%)",
        "r_prog": "Llanda Programada ECU (\")",
        "unk_fit_title": "Pneumàtic Muntat",
        "unk_prog_title": "Pneumàtic Programat ECU",
        "test_fitted": "Vehicle Test Muntat:",
        "test_prog": "Vehicle Test ECU Prog:",
        "use_range": "Incloure rang d'incertesa per pneumàtics homologats (Mín/Màx)",
        "range_section": "Rang Homologat Mínim / Màxim:",
        "w_min": "Amplada Mín (mm)",
        "a_min": "Perfil Mín (%)",
        "r_min": "Llanda Mín (\")",
        "w_max": "Amplada Màx (mm)",
        "a_max": "Perfil Màx (%)",
        "r_max": "Llanda Màx (\")",
        "kpi_header": "🎯 Interval Delimitat de Velocitat Real Defensable",
        "kpi1": "Velocitat Real Mínima",
        "kpi2": "Velocitat Real Màxima",
        "kpi3": "Velocitat Nominal Estimada",
        "kpi4": "Reducció de l'Incertesa",
        "vs_edr": "vs EDR",
        "mean_offset": "Desfasament mitjà",
        "range_width": "Amplada del rang",
        "success_msg": "Per a un valor de velocitat indicat en EDR de **{v_edr:.1f} km/h**, la velocitat real de circulació en condicions estables es delimita rigorosament en l'interval **[{v_min:.2f} km/h — {v_max:.2f} km/h]**.",
        "chart_header": "📊 Gràfic Comparatiu: EDR vs Velocitat Real i Límits Normatius",
        "chart_title": "Corba de Calibració - {veh_name}",
        "chart_xaxis": "Velocitat Indicada EDR / Velocímetre (km/h)",
        "chart_yaxis": "Velocitat Real de Circulació VBOX (km/h)",
        "un39_upper": "UN R39 Límit Superior (V_ind = V_real)",
        "un39_lower": "UN R39 Límit Inferior Teòric",
        "vbox_data": "Dades d'Assaig VBOX ({veh_name})",
        "study_case": "Interval Delimitat del Cas d'Estudi",
        "breakdown_header": "🔍 Desglossament dels Factors d'Incertesa",
        "col_factor": "Factor d'Error / Correcció",
        "col_value": "Rang de Mòdul / Valor",
        "col_effect": "Efecte en la Velocitat Real",
        "f1_name": "1. Truncament i Digitalització (UN R160)",
        "f1_eff": "+1.0 km/h d'incertesa en la cota superior",
        "f2_name": "2. Correcció Geomètrica de Pneumàtics Muntats (Ràtio 1)",
        "f2_eff": "{pct:+.2f}% d'ajust dimensional",
        "f3_name": "3. Correcció Geomètrica d'ECU Programada (Ràtio 2)",
        "f3_eff": "{pct:+.2f}% d'ajust de programari",
        "f4_name": "4. Desfasament Empíric del Velocímetre (Proves VBOX)",
        "f4_eff": "Reducció directa de la sobreestimació de fàbrica",
        "f5_name": "5. Desviació Estàndard d'Assaig (2·SD + VBOX Acc)",
        "f5_eff": "Marge estadístic d'estabilitat de l'assaig",
        "f6_name": "RESULTAT DE L'INTERVAL FINAL DELIMITAT",
        "f6_eff": "Interval final delimitat ({width:.2f} km/h)",
        "pdf_header": "📄 Generació d'Informe Pericial en PDF",
        "pdf_button": "📥 Descarregar Informe Pericial (PDF)",
        "expander_title": "📚 Veure la Base de Dades Empírica dels 16 Vehicles Assajats (EVU 2026)",
        "generic_name": "Mitjana Genèrica de la Base de Dades (16 Vehicles)",
        "pdf_title": "INFORME PERICIAL: CALIBRACIO DE VELOCITAT EDR",
        "pdf_sub": "Basat en la metodologia EVU Zilina 2026 (Sillo, Villaraggia & Cami Gonzalez)",
        "pdf_sec1": "1. Dades d'Entrada del Vehicle i de l'EDR",
        "pdf_sec2": "2. Resultat del Càlcul de la Velocitat Real",
        "pdf_sec3": "3. Justificació Tècnica i Normativa",
        "pdf_just": "El càlcul contempla les 4 fonts d'error definides en l'estudi:\n1. Truncament de digitalització de 1 km/h segons la UN R160.\n2. Correcció geomètrica dual de pneumàtics (ràtio de circumferència muntada / programada).\n3. Desfasament empíric mesurat amb VBOX en condicions de circulació estable.\n4. Interval de confiança estadístic del 95% (2xSD + precisió VBOX).\n\nConclusió: La velocitat reportada per l'EDR sobreestima la velocitat real del vehicle en condicions estables, havent-se delimitat el marge real de circulació."
},
    "en": {
        "unknown_fit_check": "Unknown installed tire",
        "unknown_prog_check": "Unknown ECU programmed tire",
        "unknown_warning": "⚠️ When tires are marked as unknown, the app evaluates the complete envelope of options within the approved tire range ({w_min}/{a_min} R{r_min} — {w_max}/{a_max} R{r_max}). This widens the true speed interval and shows lower uncertainty reduction.",
        "unknown_str": "UNKNOWN (Evaluated across approved range)",
        "admin_header": "🔐 Administration: Add New Test Vehicle",
        "admin_pass_label": "🔑 Access Password:",
        "admin_unlock_btn": "Unlock Admin Panel",
        "admin_form_title": "➕ Register New Test Vehicle",
        "admin_veh_name": "Make and Model (e.g. Tesla Model 3)",
        "admin_veh_year": "Model Year",
        "admin_fitted_tire": "Test Fitted Tire (e.g. 235/45 R18)",
        "admin_prog_tire": "Test ECU Programmed Tire (e.g. 235/45 R18)",
        "admin_save_btn": "💾 Save Vehicle to Database",
        "admin_success_msg": "Vehicle '{name}' successfully registered!",
        "admin_wrong_pass": "❌ Incorrect password. Please try again.",
        "admin_pass_ok": "🔓 Access granted.",
        "admin_custom_badge": " (Custom)",

        "title": "🚗 EDR True Speed Calibrator",
        "subtitle": "**Forensic Quantification Tool for EDR True Speed (UN R160 / UN R39 Regulations)**\n\n*Based on scientific research by **Mattia Sillo, Matteo Villaraggia, and David Camí González** (European EVU Congress Žilina 2026).*",
        "sidebar_header": "📋 EDR & Vehicle Input Data",
        "v_edr_label": "EDR Indicated Speed Pre-Crash (km/h):",
        "v_edr_help": "'Speed, Vehicle Indicated' value recorded in the EDR report (UN R160).",
        "veh_select_label": "Reference Test Vehicle:",
        "tire_section": "🛞 Accident Vehicle Tires",
        "customize_tires": "Customize accident vehicle tires",
        "w_fit": "Fitted Width (mm)",
        "a_fit": "Fitted Aspect (%)",
        "r_fit": "Fitted Rim (\")",
        "w_prog": "ECU Programmed Width (mm)",
        "a_prog": "ECU Programmed Aspect (%)",
        "r_prog": "ECU Programmed Rim (\")",
        "unk_fit_title": "Fitted Tire",
        "unk_prog_title": "ECU Programmed Tire",
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
        "unknown_fit_check": "Pneumatico montato sconosciuto",
        "unknown_prog_check": "Pneumatico programmato ECU sconosciuto",
        "unknown_warning": "⚠️ Quando i pneumatici sono sconosciuti, l'app valuta l'inviluppo completo delle opzioni nell'intervallo omologato ({w_min}/{a_min} R{r_min} — {w_max}/{a_max} R{r_max}). Questo amplia l'intervallo di velocità reale.",
        "unknown_str": "SCONOSCIUTO (Valutato nell'intervallo omologato)",
        "admin_header": "🔐 Amministrazione: Aggiungi Nuovo Veicolo",
        "admin_pass_label": "🔑 Password di accesso:",
        "admin_unlock_btn": "Sblocca Pannello Admin",
        "admin_form_title": "➕ Registrazione Nuovo Veicolo Test",
        "admin_veh_name": "Marca e Modello (es. Tesla Model 3)",
        "admin_veh_year": "Anno Modello",
        "admin_fitted_tire": "Pneumatico Montato nel Test (es. 235/45 R18)",
        "admin_prog_tire": "Pneumatico Programmato ECU (es. 235/45 R18)",
        "admin_save_btn": "💾 Salva Veicolo nel Database",
        "admin_success_msg": "Veicolo '{name}' registrato con successo!",
        "admin_wrong_pass": "❌ Password errata. Riprova.",
        "admin_pass_ok": "🔓 Accesso consentito.",
        "admin_custom_badge": " (Personalizzato)",

        "title": "🚗 Calibratore di Velocità Reale EDR",
        "subtitle": "**Strumento Peritale di Quantificazione della Velocità Reale EDR (Regolamenti UN R160 / UN R39)**\n\n*Basato sulla ricerca scientifica di **Mattia Sillo, Matteo Villaraggia e David Camí González** (Congresso Europeo EVU Žilina 2026).*",
        "sidebar_header": "📋 Dati di Input EDR e Veicolo",
        "v_edr_label": "Velocità Indicata EDR Pre-Crash (km/h):",
        "v_edr_help": "Valore di 'Speed, Vehicle Indicated' registrato nel rapporto EDR (UN R160).",
        "veh_select_label": "Veicolo di Riferimento Test:",
        "tire_section": "🛞 Pneumatici del Veicolo Incidentato",
        "customize_tires": "Personalizza pneumatici del veicolo incidentato",
        "w_fit": "Larghezza Montato (mm)",
        "a_fit": "Profilo Montato (%)",
        "r_fit": "Cerchio Montato (\")",
        "w_prog": "Larghezza Programmata ECU (mm)",
        "a_prog": "Profilo Programmato ECU (%)",
        "r_prog": "Cerchio Programmato ECU (\")",
        "unk_fit_title": "Pneumatico Montato",
        "unk_prog_title": "Pneumatico Programmato ECU",
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
    },
    "ro": {
        "unknown_fit_check": "Anvelopă montată necunoscută",
        "unknown_prog_check": "Anvelopă programată ECU necunoscută",
        "unknown_warning": "⚠️ Când anvelopele sunt marcate ca necunoscute, aplicația evaluează anvelopa completă în intervalul omologat ({w_min}/{a_min} R{r_min} — {w_max}/{a_max} R{r_max}). Aceasta extinde intervalul de viteză reală.",
        "unknown_str": "NECUNOSCUT (Evaluat în intervalul omologat)",
        "admin_header": "🔐 Administrare: Adaugă Vehicul Nou",
        "admin_pass_label": "🔑 Parolă de acces:",
        "admin_unlock_btn": "Deblochează Panoul Admin",
        "admin_form_title": "➕ Înregistrare Vehicul Nou de Test",
        "admin_veh_name": "Marcă și Model (ex. Tesla Model 3)",
        "admin_veh_year": "An Model",
        "admin_fitted_tire": "Anvelopă Montată la Test (ex. 235/45 R18)",
        "admin_prog_tire": "Anvelopă Programată ECU (ex. 235/45 R18)",
        "admin_save_btn": "💾 Salvează Vehiculul în Baza de Date",
        "admin_success_msg": "Vehiculul '{name}' a fost înregistrat cu succes!",
        "admin_wrong_pass": "❌ Parolă incorectă. Încearcă din nou.",
        "admin_pass_ok": "🔓 Acces permis.",
        "admin_custom_badge": " (Personalizat)",

        "title": "🚗 Calibrator de Viteză Reală EDR",
        "subtitle": "**Instrument Judiciar de Cuantificare a Vitezei Reale EDR (Reglementările UN R160 / UN R39)**\n\n*Bazat pe cercetarea științifică a autorilor **Mattia Sillo, Matteo Villaraggia și David Camí González** (Congresul European EVU Žilina 2026).*",
        "sidebar_header": "📋 Date de Intrare EDR și Vehicul",
        "v_edr_label": "Viteză Indicată EDR Pre-Crash (km/h):",
        "v_edr_help": "Valoarea 'Speed, Vehicle Indicated' înregistrată în raportul EDR (UN R160).",
        "veh_select_label": "Vehicul de Referință Testat:",
        "tire_section": "🛞 Anvelope Vehicul Accident",
        "customize_tires": "Personalizare anvelope vehicul accident",
        "w_fit": "Lățime Montată (mm)",
        "a_fit": "Talon Montat (%)",
        "r_fit": "Jantă Montată (\")",
        "w_prog": "Lățime Programată ECU (mm)",
        "a_prog": "Talon Programat ECU (%)",
        "r_prog": "Jantă Programată ECU (\")",
        "unk_fit_title": "Anvelopă Montată",
        "unk_prog_title": "Anvelopă Programată ECU",
        "test_fitted": "Vehicul Test Montat:",
        "test_prog": "Vehicul Test ECU Prog:",
        "use_range": "Include intervalul de incertitudine pentru anvelope omologate (Min/Max)",
        "range_section": "Interval Omologat Minim / Maxim:",
        "w_min": "Lățime Min (mm)",
        "a_min": "Talon Min (%)",
        "r_min": "Jantă Min (\")",
        "w_max": "Lățime Max (mm)",
        "a_max": "Talon Max (%)",
        "r_max": "Jantă Max (\")",
        "kpi_header": "🎯 Interval Delimitat de Viteză Reală Apărabil",
        "kpi1": "Viteză Reală Minimă",
        "kpi2": "Viteză Reală Maximă",
        "kpi3": "Viteză Nominală Estimată",
        "kpi4": "Reducerea Incertitudinii",
        "vs_edr": "vs EDR",
        "mean_offset": "Abatere medie",
        "range_width": "Lățime interval",
        "success_msg": "Pentru o viteză indicată EDR de **{v_edr:.1f} km/h**, viteza reală în regim stabil este riguros delimitată în intervalul **[{v_min:.2f} km/h — {v_max:.2f} km/h]**.",
        "chart_header": "📊 Grafic Comparativ: EDR vs Viteză Reală și Limite Normative",
        "chart_title": "Curbă de Calibrare - {veh_name}",
        "chart_xaxis": "Viteză Indicată EDR / Vitezometru (km/h)",
        "chart_yaxis": "Viteză Reală de Rulare VBOX (km/h)",
        "un39_upper": "UN R39 Limită Superioară (V_ind = V_real)",
        "un39_lower": "UN R39 Limită Inferioară Teoretică",
        "vbox_data": "Date Test VBOX ({veh_name})",
        "study_case": "Interval Delimitat Caz de Studiu",
        "breakdown_header": "🔍 Detaliere Factori de Incertitudine",
        "col_factor": "Factor de Eroare / Corecție",
        "col_value": "Magnitudine / Interval Valori",
        "col_effect": "Efect asupra Vitezei Reale",
        "f1_name": "1. Digitalizare și Trunchiere (UN R160)",
        "f1_eff": "+1.0 km/h incertitudine limită superioară",
        "f2_name": "2. Corecție Geometrică Anvelope Montate (Raport 1)",
        "f2_eff": "{pct:+.2f}% ajustare dimensională",
        "f3_name": "3. Corecție Geometrică ECU Programat (Raport 2)",
        "f3_eff": "{pct:+.2f}% ajustare software",
        "f4_name": "4. Abatere Empirică Vitezometru (Teste VBOX)",
        "f4_eff": "Reducere directă a supraestimării din fabrică",
        "f5_name": "5. Abatere Standard Test (2·SD + Precizie VBOX)",
        "f5_eff": "Marjă statistică de stabilitate a testului",
        "f6_name": "REZULTAT INTERVAL FINAL DELIMITAT",
        "f6_eff": "Interval final delimitat ({width:.2f} km/h)",
        "pdf_header": "📄 Generare Raport Expertiză PDF",
        "pdf_button": "📥 Descărcare Raport Expertiză (PDF)",
        "expander_title": "📚 Vizualizare Bază de Date Empirică 16 Vehicule Testate (EVU 2026)",
        "generic_name": "Medie Generică Bază de Date (16 Vehicule)",
        "pdf_title": "RAPORT EXPERTIZA: CALIBRARE VITEZA EDR",
        "pdf_sub": "Bazat pe metodologia EVU Zilina 2026 (Sillo, Villaraggia & Cami Gonzalez)",
        "pdf_sec1": "1. Date Intrare Vehicul si EDR",
        "pdf_sec2": "2. Rezultat Calcul Viteza Reala",
        "pdf_sec3": "3. Justificare Tehnica si Normativa",
        "pdf_just": "Calculul ia in considerare cele 4 surse de eroare definite in studiu:\n1. Trunchiere de digitalizare de 1 km/h conform UN R160.\n2. Corectie geometrica dubla a anvelopelor (raport circumferinta montata / programata).\n3. Abatere empirica masurata cu VBOX in regim stabil de deplasare.\n4. Interval de incredere statistic de 95% (2xSD + precizie VBOX).\n\nConcluzie: Viteza raportata de EDR supraestimeaza viteza reala in regim stabil, oferind un interval aparabil."
},
    "nl": {
        "unknown_fit_check": "Onbekende gemonteerde band",
        "unknown_prog_check": "Onbekende ECU geprogrammeerde band",
        "unknown_warning": "⚠️ Wanneer banden als onbekend zijn gemarkeerd, berekent de app het volledige bereik binnen de goedgekeurde marge ({w_min}/{a_min} R{r_min} — {w_max}/{a_max} R{r_max}), wat het snelheidsinterval vergroot.",
        "unknown_str": "ONBEKEND (Evalueert over goedgekeurd bereik)",
        "admin_header": "🔐 Beheer: Nieuw Testvoertuig Toevoegen",
        "admin_pass_label": "🔑 Toegangswachtwoord:",
        "admin_unlock_btn": "Admin Paneel Ontgrendelen",
        "admin_form_title": "➕ Registreer Nieuw Testvoertuig",
        "admin_veh_name": "Merk en Model (bijv. Tesla Model 3)",
        "admin_veh_year": "Bouwjaar",
        "admin_fitted_tire": "Gemonteerde Band bij Test (bijv. 235/45 R18)",
        "admin_prog_tire": "Geprogrammeerde Band ECU (bijv. 235/45 R18)",
        "admin_save_btn": "💾 Voertuig Opslaan in Database",
        "admin_success_msg": "Voertuig '{name}' succesvol geregistreerd!",
        "admin_wrong_pass": "❌ Onjuist wachtwoord. Probeer het opnieuw.",
        "admin_pass_ok": "🔓 Toegang verleend.",
        "admin_custom_badge": " (Aangepast)",

        "title": "🚗 EDR Werkelijke Snelheid Calibrator",
        "subtitle": "**Forensisch Instrument voor Kwantificering van EDR Werkelijke Snelheid (UN R160 / UN R39 Reglementen)**\n\n*Gebaseerd op wetenschappelijk onderzoek van **Mattia Sillo, Matteo Villaraggia en David Camí González** (Europees EVU Congres Žilina 2026).*",
        "sidebar_header": "📋 EDR & Voertuig Invoergegevens",
        "v_edr_label": "EDR Aangegeven Snelheid Pre-Crash (km/h):",
        "v_edr_help": "'Speed, Vehicle Indicated' waarde geregistreerd in EDR rapport (UN R160).",
        "veh_select_label": "Referentie Testvoertuig:",
        "tire_section": "🛞 Banden Ongevalsvoertuig",
        "customize_tires": "Banden van ongevalsvoertuig aanpassen",
        "w_fit": "Gemonteerde Breedte (mm)",
        "a_fit": "Gemonteerde Wanghoogte (%)",
        "r_fit": "Gemonteerde Velg (\")",
        "w_prog": "ECU Geprogrammeerde Breedte (mm)",
        "a_prog": "ECU Geprogrammeerde Wanghoogte (%)",
        "r_prog": "ECU Geprogrammeerde Velg (\")",
        "unk_fit_title": "Gemonteerde Band",
        "unk_prog_title": "ECU Geprogrammeerde Band",
        "test_fitted": "Testvoertuig Gemonteerd:",
        "test_prog": "Testvoertuig ECU Progr:",
        "use_range": "Onzekerheidsmarge voor goedgekeurde banden opnemen (Min/Max)",
        "range_section": "Minimale / Maximale Goedgekeurde Marge:",
        "w_min": "Min Breedte (mm)",
        "a_min": "Min Wanghoogte (%)",
        "r_min": "Min Velg (\")",
        "w_max": "Max Breedte (mm)",
        "a_max": "Max Wanghoogte (%)",
        "r_max": "Max Velg (\")",
        "kpi_header": "🎯 Verdedigbaar Begrensd Interval Werkelijke Snelheid",
        "kpi1": "Minimale Werkelijke Snelheid",
        "kpi2": "Maximale Werkelijke Snelheid",
        "kpi3": "Geschatte Nominale Snelheid",
        "kpi4": "Onzekerheidsreductie",
        "vs_edr": "vs EDR",
        "mean_offset": "Gemiddelde afwijking",
        "range_width": "Intervalbreedte",
        "success_msg": "Voor een EDR aangegeven snelheid van **{v_edr:.1f} km/h**, is de werkelijke snelheid bij constante rijomstandigheden nauwkeurig begrensd binnen het interval **[{v_min:.2f} km/h — {v_max:.2f} km/h]**.",
        "chart_header": "📊 Vergelijkende Grafiek: EDR vs Werkelijke Snelheid & Wettelijke Limieten",
        "chart_title": "Calibratiecurve - {veh_name}",
        "chart_xaxis": "EDR Aangegeven Snelheid / Snelheidsmeter (km/h)",
        "chart_yaxis": "VBOX Werkelijke Rijsnelheid (km/h)",
        "un39_upper": "UN R39 Bovengrens (V_aang = V_werk)",
        "un39_lower": "UN R39 Theoretische Ondergrens",
        "vbox_data": "VBOX Testgegevens ({veh_name})",
        "study_case": "Casus Begrensd Interval",
        "breakdown_header": "🔍 Specificatie van Onzekerheidsfactoren",
        "col_factor": "Fout- / Correctiefactor",
        "col_value": "Omvang / Waarde-interval",
        "col_effect": "Effect op Werkelijke Snelheid",
        "f1_name": "1. Digitalisering & Afronding (UN R160)",
        "f1_eff": "+1.0 km/h onzekerheid op bovengrens",
        "f2_name": "2. Geometrische Correctie Gemonteerde Banden (Ratio 1)",
        "f2_eff": "{pct:+.2f}% maataanpassing",
        "f3_name": "3. Geometrische Correctie ECU Geprogrammeerd (Ratio 2)",
        "f3_eff": "{pct:+.2f}% software-aanpassing",
        "f4_name": "4. Empirische Snelheidsmeterafwijking (VBOX Tests)",
        "f4_eff": "Directe reductie van fabrieksoverschatting",
        "f5_name": "5. Standaarddeviatie Test (2·SD + VBOX Nauwkeurigheid)",
        "f5_eff": "Statistische marge voor teststabiliteit",
        "f6_name": "EINDRESULTAAT BEGRENSD INTERVAL",
        "f6_eff": "Uiteindelijk begrensd bereik ({width:.2f} km/h)",
        "pdf_header": "📄 Forensisch PDF Rapport Genereren",
        "pdf_button": "📥 Forensisch Rapport Downloaden (PDF)",
        "expander_title": "📚 Empirische Database van 16 Geteste Voertuigen Bekijken (EVU 2026)",
        "generic_name": "Generiek Database Gemiddelde (16 Voertuigen)",
        "pdf_title": "FORENSISCH RAPPORT: EDR SNELHEIDSCALIBRATIE",
        "pdf_sub": "Gebaseerd op EVU Zilina 2026 methodologie (Sillo, Villaraggia & Cami Gonzalez)",
        "pdf_sec1": "1. Invoergegevens Voertuig en EDR",
        "pdf_sec2": "2. Resultaat Berekening Werkelijke Snelheid",
        "pdf_sec3": "3. Technische en Wettelijke Onderbouwing",
        "pdf_just": "De berekening houdt rekening met de 4 foutenbronnen uit de studie:\n1. 1 km/h digitaliseringsafronding volgens UN R160.\n2. Dubbele geometrische bandencorrectie (verhouding gemonteerde / geprogrammeerde omtrek).\n3. Empirische afwijking gemeten met VBOX bij constante rijomstandigheden.\n4. 95% statistisch betrouwbaarheidsinterval (2xSD + VBOX nauwkeurigheid).\n\nConclusie: De gerapporteerde EDR-snelheid overschat de werkelijke snelheid bij constante rit."
},
    "de": {
        "unknown_fit_check": "Unbekannter montierter Reifen",
        "unknown_prog_check": "Unbekannter ECU programmierter Reifen",
        "unknown_warning": "⚠️ Wenn Reifen als unbekannt markiert sind, berechnet die App die vollständige Einhüllende im zugelassenen Bereich ({w_min}/{a_min} R{r_min} — {w_max}/{a_max} R{r_max}), was das Geschwindigkeitsintervall erweitert.",
        "unknown_str": "UNBEKANNT (In zugelassenem Bereich evaluiert)",
        "admin_header": "🔐 Verwaltung: Neues Testfahrzeug Hinzufügen",
        "admin_pass_label": "🔑 Zugangspasswort:",
        "admin_unlock_btn": "Admin Panel Freischalten",
        "admin_form_title": "➕ Neues Testfahrzeug Registrieren",
        "admin_veh_name": "Marke und Modell (z.B. Tesla Model 3)",
        "admin_veh_year": "Modelljahr",
        "admin_fitted_tire": "Montierter Reifen im Test (z.B. 235/45 R18)",
        "admin_prog_tire": "Programmierter Reifen ECU (z.B. 235/45 R18)",
        "admin_save_btn": "💾 Fahrzeug in Datenbank Speichern",
        "admin_success_msg": "Fahrzeug '{name}' erfolgreich registriert!",
        "admin_wrong_pass": "❌ Falsches Passwort. Bitte erneut versuchen.",
        "admin_pass_ok": "🔓 Zugang gewährt.",
        "admin_custom_badge": " (Benutzerdefiniert)",

        "title": "🚗 EDR Realle Geschwindigkeits-Kalibrierer",
        "subtitle": "**Forensisches Werkzeug zur Quantifizierung der realen EDR-Geschwindigkeit (UN R160 / UN R39 Regelungen)**\n\n*Basierend auf der wissenschaftlichen Forschung von **Mattia Sillo, Matteo Villaraggia und David Camí González** (Europäischer EVU-Kongress Žilina 2026).*",
        "sidebar_header": "📋 EDR & Fahrzeug-Eingabedaten",
        "v_edr_label": "EDR Indizierte Geschwindigkeit Pre-Crash (km/h):",
        "v_edr_help": "'Speed, Vehicle Indicated' Wert aus dem EDR-Bericht (UN R160).",
        "veh_select_label": "Referenz-Testfahrzeug:",
        "tire_section": "🛞 Reifen des Unfallfahrzeugs",
        "customize_tires": "Reifen des Unfallfahrzeugs anpassen",
        "w_fit": "Montierte Breite (mm)",
        "a_fit": "Montierte Querschnittshöhe (%)",
        "r_fit": "Montierte Felge (\")",
        "w_prog": "ECU Programmierte Breite (mm)",
        "a_prog": "ECU Programmierte Querschnittshöhe (%)",
        "r_prog": "ECU Programmierte Felge (\")",
        "unk_fit_title": "Montierter Reifen",
        "unk_prog_title": "ECU Programmierter Reifen",
        "test_fitted": "Testfahrzeug Montiert:",
        "test_prog": "Testfahrzeug ECU Prog:",
        "use_range": "Unsicherheitsbereich für zugelassene Reifen einbeziehen (Min/Max)",
        "range_section": "Minimaler / Maximaler Zugelassener Bereich:",
        "w_min": "Min Breite (mm)",
        "a_min": "Min Querschnitt (%)",
        "r_min": "Min Felge (\")",
        "w_max": "Max Breite (mm)",
        "a_max": "Max Querschnitt (%)",
        "r_max": "Max Felge (\")",
        "kpi_header": "🎯 Belastbares Eingegrenztes Intervall der Reallgeschwindigkeit",
        "kpi1": "Minimale Reale Geschwindigkeit",
        "kpi2": "Maximale Reale Geschwindigkeit",
        "kpi3": "Geschätzte Nominalgeschwindigkeit",
        "kpi4": "Unsicherheitsreduktion",
        "vs_edr": "vs EDR",
        "mean_offset": "Mittlerer Abweichungswert",
        "range_width": "Intervallbreite",
        "success_msg": "Für eine indizierte EDR-Geschwindigkeit von **{v_edr:.1f} km/h** wird die reale Geschwindigkeit bei stabiler Fahrt präzise im Intervall **[{v_min:.2f} km/h — {v_max:.2f} km/h]** eingegrenzt.",
        "chart_header": "📊 Vergleichsdiagramm: EDR vs Reale Geschwindigkeit & Normgrenzen",
        "chart_title": "Kalibrierkurve - {veh_name}",
        "chart_xaxis": "EDR Indizierte Geschwindigkeit / Tacho (km/h)",
        "chart_yaxis": "VBOX Reale Fahrgeschwindigkeit (km/h)",
        "un39_upper": "UN R39 Obergrenze (V_ind = V_real)",
        "un39_lower": "UN R39 Theoretische Untergrenze",
        "vbox_data": "VBOX Messdaten ({veh_name})",
        "study_case": "Fallstudie Eingegrenztes Intervall",
        "breakdown_header": "🔍 Aufschlüsselung der Unsicherheitsfaktoren",
        "col_factor": "Fehler- / Korrekturfaktor",
        "col_value": "Größenordnung / Wertebereich",
        "col_effect": "Auswirkung auf reale Geschwindigkeit",
        "f1_name": "1. Digitalisierung & Rundung (UN R160)",
        "f1_eff": "+1.0 km/h Unsicherheit an der Obergrenze",
        "f2_name": "2. Geometrische Korrektur Montierte Reifen (Verhältnis 1)",
        "f2_eff": "{pct:+.2f}% Dimensionale Anpassung",
        "f3_name": "3. Geometrische Korrektur ECU Programmiert (Verhältnis 2)",
        "f3_eff": "{pct:+.2f}% Software-Anpassung",
        "f4_name": "4. Empirische Tachometer-Abweichung (VBOX-Tests)",
        "f4_eff": "Direkte Reduzierung der werkseitigen Übertreibung",
        "f5_name": "5. Test-Standardabweichung (2·SD + VBOX-Genauigkeit)",
        "f5_eff": "Statistischer Marge für Teststabilität",
        "f6_name": "EENDERGEBNIS EINGEGRENZTES INTERVALL",
        "f6_eff": "Finale Intervallbreite ({width:.2f} km/h)",
        "pdf_header": "📄 Erstellung des Forensischen PDF-Gutachtens",
        "pdf_button": "📥 Forensisches Gutachten Herunterladen (PDF)",
        "expander_title": "📚 Empirische Datenbank von 16 Getesteten Fahrzeugen Anzeigen (EVU 2026)",
        "generic_name": "Generischer Datenbank-Mittelwert (16 Fahrzeuge)",
        "pdf_title": "FORENSISCHES GUTACHTEN: EDR GESCHWINDIGKEITSKALIBRIERUNG",
        "pdf_sub": "Basierend auf der EVU Zilina 2026 Methodik (Sillo, Villaraggia & Cami Gonzalez)",
        "pdf_sec1": "1. Fahrzeug- und EDR-Eingabedaten",
        "pdf_sec2": "2. Ergebnis der Realle Geschwindigkeitsberechnung",
        "pdf_sec3": "3. Technische und Rechtliche Begründung",
        "pdf_just": "Die Berechnung berücksichtigt die 4 im Gutachten definierten Fehlerquellen:\n1. 1 km/h Digitalisierungsrundung gemäß UN R160.\n2. Zweifache geometrische Reifenkorrektur (Verhältnis montierter / programmierter Umfang).\n3. Empirische Abweichung gemessen mit VBOX bei stabiler Fahrt.\n4. Statistische 95% Konfidenzintervall (2xSD + VBOX Genauigkeit).\n\nFazit: Die vom EDR berichtete Geschwindigkeit überschätzt die tatsächliche Geschwindigkeit bei stabiler Fahrt."
},
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
        "vbox": [47.922, 67.444, 87.044, 106.502, 125.995],
        "diff": [2.078, 2.556, 2.956, 3.498, 4.005],
        "sd": [0.084, 0.098, 0.136, 0.119, 0.169]
    },
    "2": {
        "name": "BMW X3 xDrive20d (2024)",
        "year": 2024,
        "fitted_test": "245/50 R19",
        "prog_test": "245/50 R19",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.854, 87.803, 87.803, 107.100, 126.354],
        "diff": [2.819, 3.409, 3.409, 4.400, 5.397],
        "sd": [0.795, 0.862, 0.862, 0.750, 0.631]
    },
    "3": {
        "name": "BMW i4 eDrive40 (2024)",
        "year": 2024,
        "fitted_test": "245/40 R19",
        "prog_test": "255/45 R18",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [48.013, 67.284, 87.827, 106.213, 128.054],
        "diff": [1.397, 1.890, 1.112, 2.489, 0.413],
        "sd": [0.379, 0.273, 1.023, 0.370, 1.157]
    },
    "4": {
        "name": "BMW iX1 xDrive30 (2024)",
        "year": 2024,
        "fitted_test": "225/55 R18",
        "prog_test": "225/55 R18",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.827, 68.655, 88.031, 109.873, 127.528],
        "diff": [2.174, 1.345, 1.969, 0.127, 2.472],
        "sd": [0.618, 1.152, 0.413, 1.386, 0.540]
    },
    "5": {
        "name": "BMW 2 Series 220d (2025)",
        "year": 2025,
        "fitted_test": "225/45 R18",
        "prog_test": "225/45 R18",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [48.557, 68.633, 88.468, 108.523, 128.378],
        "diff": [1.443, 1.367, 1.522, 1.477, 1.622],
        "sd": [0.157, 0.149, 0.436, 0.517, 0.469]
    },
    "6": {
        "name": "BMW X1 xDrive18d (2020)",
        "year": 2020,
        "fitted_test": "225/50 R18",
        "prog_test": "225/50 R18",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.509, 66.999, 86.262, 105.672, 125.179],
        "diff": [2.491, 3.001, 3.738, 4.328, 4.821],
        "sd": [0.143, 0.137, 0.126, 0.181, 0.351]
    },
    "7": {
        "name": "Mini Cooper SE (2024)",
        "year": 2024,
        "fitted_test": "215/45 R17",
        "prog_test": "215/45 R17",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [48.442, 68.143, 88.001, 107.803, 127.569],
        "diff": [1.558, 1.857, 1.999, 2.197, 2.431],
        "sd": [0.656, 0.286, 0.103, 0.107, 0.370]
    },
    "8": {
        "name": "Mini Aceman SE (2025)",
        "year": 2025,
        "fitted_test": "225/40 R19",
        "prog_test": "205/50 R18",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [48.276, 67.888, 88.202, 107.803, 127.567],
        "diff": [1.724, 2.112, 1.798, 2.197, 2.433],
        "sd": [0.544, 0.377, 0.331, 0.107, 0.325]
    },
    "9": {
        "name": "Mini Countryman C (2024)",
        "year": 2024,
        "fitted_test": "245/45 R19",
        "prog_test": "225/55 R17",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.902, 68.508, 87.697, 107.464, 128.573],
        "diff": [2.098, 1.492, 2.303, 2.536, 1.427],
        "sd": [0.588, 0.418, 0.593, 0.350, 0.497]
    },
    "10": {
        "name": "Kia Sportage (2025)",
        "year": 2025,
        "fitted_test": "235/50 R19",
        "prog_test": "215/65 R17",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [46.950, 67.445, 87.262, 107.808, 127.737],
        "diff": [3.050, 2.555, 2.738, 2.192, 2.263],
        "sd": [0.355, 0.201, 0.294, 0.152, 0.145]
    },
    "11": {
        "name": "Toyota C-HR (2024)",
        "year": 2024,
        "fitted_test": "225/50 R18",
        "prog_test": "215/60 R17",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.939, 67.501, 87.514, 106.634, 126.047],
        "diff": [2.061, 2.499, 2.486, 3.366, 3.953],
        "sd": [0.116, 0.105, 0.278, 0.183, 0.286]
    },
    "12": {
        "name": "Toyota RAV4 (2023)",
        "year": 2023,
        "fitted_test": "225/60 R18",
        "prog_test": "225/65 R17",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.355, 67.262, 87.109, 107.134, 126.857],
        "diff": [2.645, 2.738, 2.891, 2.866, 3.143],
        "sd": [0.107, 0.099, 0.142, 0.221, 0.230]
    },
    "13": {
        "name": "Lexus RZ 450E (2024)",
        "year": 2024,
        "fitted_test": "235/50 R20",
        "prog_test": "235/60 R18",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [48.036, 68.105, 88.017, 108.318, 128.162],
        "diff": [2.337, 2.417, 2.654, 2.502, 2.807],
        "sd": [0.143, 0.082, 0.118, 0.157, 0.135]
    },
    "14": {
        "name": "Hyundai Tucson IX35 (2025)",
        "year": 2025,
        "fitted_test": "235/50 R19",
        "prog_test": "235/50 R19",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.729, 67.586, 88.500, 107.106, 126.875],
        "diff": [2.271, 2.414, 1.500, 2.894, 3.125],
        "sd": [0.707, 0.704, 1.168, 0.405, 0.859]
    },
    "15": {
        "name": "Suzuki Ignis (2024)",
        "year": 2024,
        "fitted_test": "175/60 R16",
        "prog_test": "175/60 R16",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [46.190, 66.628, 85.927, 106.577, 125.385],
        "diff": [3.810, 3.372, 4.073, 3.423, 4.615],
        "sd": [0.171, 0.150, 0.255, 0.264, 0.152]
    },
    "16": {
        "name": "Fiat 500X (2016)",
        "year": 2016,
        "fitted_test": "215/55 R17",
        "prog_test": "215/60 R16",
        "speeds": [50, 70, 90, 110, 130],
        "vbox": [47.874, 67.235, 87.604, 107.206, 126.919],
        "diff": [2.126, 2.765, 2.396, 2.794, 3.081],
        "sd": [0.143, 0.299, 0.503, 0.414, 0.212]
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
    "Italiano": "it",
    "Română": "ro",
    "Nederlands": "nl",
    "Deutsch": "de"
}

# ==========================================
# INICIALIZACIÓN DE ESTADO DE SESIÓN (SESSION STATE)
# ==========================================
if "custom_vehicles" not in st.session_state:
    st.session_state.custom_vehicles = {}

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

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
    ALL_VEHICLES_DB = {**VEHICLES_DB, **st.session_state.custom_vehicles}
    v_data = ALL_VEHICLES_DB[vehicle_key]
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

    # Mantener precisión técnica de al menos 4 decimales para los cálculos intermedios
    return round(diff_interp, 4), round(sd_interp, 4)

def get_vehicle_name(key, lang):
    ALL_VEHICLES_DB = {**VEHICLES_DB, **st.session_state.custom_vehicles}
    v = ALL_VEHICLES_DB[key]
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

ALL_VEHICLES_DB = {**VEHICLES_DB, **st.session_state.custom_vehicles}
veh_keys = list(ALL_VEHICLES_DB.keys())
veh_names = [get_vehicle_name(k, lang_code) for k in veh_keys]

selected_veh_idx = st.sidebar.selectbox(
    t["veh_select_label"],
    options=range(len(veh_names)),
    format_func=lambda i: veh_names[i],
    index=2
)
selected_key = veh_keys[selected_veh_idx]
veh_info = ALL_VEHICLES_DB[selected_key]
selected_veh_name = get_vehicle_name(selected_key, lang_code)

st.sidebar.subheader(t["tire_section"])

col_unk1, col_unk2 = st.sidebar.columns(2)
with col_unk1:
    unk_fitted = st.checkbox(t["unknown_fit_check"], value=False, key=f"unk_fit_{selected_key}")
with col_unk2:
    unk_prog = st.checkbox(t["unknown_prog_check"], value=False, key=f"unk_prog_{selected_key}")

use_custom_tires = st.sidebar.checkbox(t["customize_tires"], value=True)

def_w_f, def_a_f, def_r_f = parse_tire_str(veh_info["fitted_test"])
def_w_p, def_a_p, def_r_p = parse_tire_str(veh_info["prog_test"])

if use_custom_tires:
    col_t1, col_t2 = st.sidebar.columns(2)
    with col_t1:
        if not unk_fitted:
            w_fit = st.number_input(t["w_fit"], 135, 335, int(def_w_f), 5, key=f"wf_{selected_key}")
            a_fit = st.number_input(t["a_fit"], 25, 80, int(def_a_f), 5, key=f"af_{selected_key}")
            r_fit = st.number_input(t["r_fit"], 13, 23, int(def_r_f), 1, key=f"rf_{selected_key}")
        else:
            st.info(f"**{t['unk_fit_title']}**:\n{t['unknown_str']}")
            w_fit, a_fit, r_fit = def_w_f, def_a_f, def_r_f
    with col_t2:
        if not unk_prog:
            w_prog = st.number_input(t["w_prog"], 135, 335, int(def_w_p), 5, key=f"wp_{selected_key}")
            a_prog = st.number_input(t["a_prog"], 25, 80, int(def_a_p), 5, key=f"ap_{selected_key}")
            r_prog = st.number_input(t["r_prog"], 13, 23, int(def_r_p), 1, key=f"rp_{selected_key}")
        else:
            st.info(f"**{t['unk_prog_title']}**:\n{t['unknown_str']}")
            w_prog, a_prog, r_prog = def_w_p, def_a_p, def_r_p
else:
    w_fit, a_fit, r_fit = parse_tire_str(veh_info["fitted_test"])
    w_prog, a_prog, r_prog = parse_tire_str(veh_info["prog_test"])

crash_fitted_str = t["unknown_str"] if unk_fitted else f"{w_fit}/{a_fit} R{r_fit}"
crash_prog_str = t["unknown_str"] if unk_prog else f"{w_prog}/{a_prog} R{r_prog}"

st.sidebar.caption(f"**{t['test_fitted']}** {veh_info['fitted_test']}")
st.sidebar.caption(f"**{t['test_prog']}** {veh_info['prog_test']}")

use_range_user = st.sidebar.checkbox(t["use_range"], value=False)
use_range = use_range_user or unk_fitted or unk_prog

# Default range bounds
if use_range or unk_fitted or unk_prog:
    st.sidebar.markdown(f"**{t['range_section']}**")
    col_r1, col_r2 = st.sidebar.columns(2)
    with col_r1:
        w_min = st.number_input(t["w_min"], 135, 335, 225, 5, key=f"wmin_{selected_key}")
        a_min = st.number_input(t["a_min"], 25, 80, 40, 5, key=f"amin_{selected_key}")
        r_min = st.number_input(t["r_min"], 13, 23, 18, 1, key=f"rmin_{selected_key}")
    with col_r2:
        w_max = st.number_input(t["w_max"], 135, 335, 255, 5, key=f"wmax_{selected_key}")
        a_max = st.number_input(t["a_max"], 25, 80, 55, 5, key=f"amax_{selected_key}")
        r_max = st.number_input(t["r_max"], 13, 23, 18, 1, key=f"rmax_{selected_key}")
    
    if unk_fitted or unk_prog:
        st.sidebar.warning(t["unknown_warning"].format(
            w_min=w_min, a_min=a_min, r_min=r_min,
            w_max=w_max, a_max=a_max, r_max=r_max
        ))

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

if use_range or unk_fitted or unk_prog:
    _, c_min_calc = calc_tire_geometry(w_min, a_min, r_min)
    _, c_max_calc = calc_tire_geometry(w_max, a_max, r_max)
    c_min = min(c_min_calc, c_max_calc)
    c_max = max(c_min_calc, c_max_calc)

    if unk_fitted:
        ratio1_min = c_min / c_test_fitted
        ratio1_max = c_max / c_test_fitted
        ratio1 = (c_min + c_max) / 2.0 / c_test_fitted
    elif use_range_user:
        ratio1_min = min(c_crash_fitted, c_min) / c_test_fitted
        ratio1_max = max(c_crash_fitted, c_max) / c_test_fitted
        ratio1 = c_crash_fitted / c_test_fitted
    else:
        ratio1 = c_crash_fitted / c_test_fitted
        ratio1_min = ratio1_max = ratio1

    if unk_prog:
        ratio2_min = c_min / c_test_prog
        ratio2_max = c_max / c_test_prog
        ratio2 = (c_min + c_max) / 2.0 / c_test_prog
    elif use_range_user:
        ratio2_min = min(c_crash_prog, c_min) / c_test_prog
        ratio2_max = max(c_crash_prog, c_max) / c_test_prog
        ratio2 = c_crash_prog / c_test_prog
    else:
        ratio2 = c_crash_prog / c_test_prog
        ratio2_min = ratio2_max = ratio2
else:
    ratio1 = c_crash_fitted / c_test_fitted
    ratio2 = c_crash_prog / c_test_prog
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
        f"Ratio 1 = [{ratio1_min:.4f} — {ratio1_max:.4f}] ({t['unknown_str']})" if unk_fitted else f"Ratio 1 = {ratio1:.4f} (Circ: {c_crash_fitted:.1f} vs {c_test_fitted:.1f} mm)",
        f"Ratio 2 = [{ratio2_min:.4f} — {ratio2_max:.4f}] ({t['unknown_str']})" if unk_prog else f"Ratio 2 = {ratio2:.4f} (Circ: {c_crash_prog:.1f} vs {c_test_prog:.1f} mm)",
        f"-{diff_exp:.4f} km/h (a {v_edr_input:.1f} km/h)",
        f"±{(2.0*sd_exp + vbox_acc):.4f} km/h (SD = {sd_exp:.4f}, 95% CI)",
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
    
    return bytes(pdf.output())

pdf_bytes = generate_pdf()

st.download_button(
    label=t["pdf_button"],
    data=pdf_bytes,
    file_name=f"EDR_Speed_Report_{v_edr_input:.0f}kmh.pdf",
    mime="application/pdf"
)


# ==========================================
# SECCIÓN PROTEGIDA DE ADMINISTRACIÓN (Zilina_2026)
# ==========================================
st.sidebar.divider()
with st.sidebar.expander(t["admin_header"]):
    if not st.session_state.admin_authenticated:
        admin_pass = st.text_input(t["admin_pass_label"], type="password", key="admin_password_input")
        if st.button(t["admin_unlock_btn"], key="btn_unlock_admin"):
            if admin_pass == "Zilina_2026":
                st.session_state.admin_authenticated = True
                st.success(t["admin_pass_ok"])
                st.rerun()
            else:
                st.error(t["admin_wrong_pass"])
    else:
        st.markdown(f"### {t['admin_form_title']}")
        new_name = st.text_input(t["admin_veh_name"], value="", key="admin_name")
        new_year = st.number_input(t["admin_veh_year"], min_value=2000, max_value=2030, value=2026, step=1, key="admin_year")
        new_fitted = st.text_input(t["admin_fitted_tire"], value="225/50 R17", key="admin_fitted")
        new_prog = st.text_input(t["admin_prog_tire"], value="225/50 R17", key="admin_prog")
        
        st.markdown("**Velocidades y Resultados VBOX / Speed Benchmark Data:**")
        speeds_list = [50, 70, 90, 110, 130]
        diffs_input = []
        sds_input = []
        vbox_input = []
        
        for sp in speeds_list:
            c1, c2 = st.columns(2)
            with c1:
                df_val = st.number_input(f"Diff @ {sp} km/h", min_value=0.0, max_value=20.0, value=2.0, step=0.1, key=f"diff_{sp}")
                diffs_input.append(df_val)
                vbox_input.append(round(sp - df_val, 2))
            with c2:
                sd_val = st.number_input(f"SD @ {sp} km/h", min_value=0.0, max_value=10.0, value=0.4, step=0.05, key=f"sd_{sp}")
                sds_input.append(sd_val)
                
        if st.button(t["admin_save_btn"], key="btn_save_custom_vehicle"):
            if new_name.strip():
                new_key = f"custom_{len(st.session_state.custom_vehicles) + 1}"
                st.session_state.custom_vehicles[new_key] = {
                    "name": f"{new_name.strip()} ({new_year}){t['admin_custom_badge']}",
                    "year": int(new_year),
                    "fitted_test": new_fitted.strip(),
                    "prog_test": new_prog.strip(),
                    "speeds": speeds_list,
                    "vbox": vbox_input,
                    "diff": diffs_input,
                    "sd": sds_input
                }
                st.success(t["admin_success_msg"].format(name=new_name))
                st.rerun()
            else:
                st.warning("Por favor introduce el nombre del vehículo / Please enter vehicle name")


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
