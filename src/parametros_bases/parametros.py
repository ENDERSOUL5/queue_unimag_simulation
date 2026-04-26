# -*- coding: utf-8 -*-
"""
Parámetros del modelo del Comedor Unimagdalena
"""

PARAMETROS = {
    "Beneficiarios": 800,
    "Tasa_Llegada_base": 9.0,
    "Tasa_asistencia": 0.8,
    "Capacidad_Biometrica": 5.0,
    "Capacidad_Manual": 2.0,
    "Tiempo_reposicion": 5.0,
    "Stock_inicial": 100.0,
    "Stock_Seguridad": 10.0,
    "Personal_presente": 1.0,
    "Costo_etico": 0.5,
    "Tasa_falla_biometrica": 0.1,
    "Tiempo_cierre": 240.0,
    "TIME_STEP": 0.125,
    "Factor_colado": 0.5,
    "Tasa_redaccion_frustracion": 0.1,
    "Factor_reduccion_frustracion": 10.0,
    "Factor_escala_frustracion": 10.0,
    "Tasa_decaimiento_frustracion": 0.1,
    "Cola_inicial": 0.0,
};

ESTADOS = {
    "SERVING": 0,
    "REPLENISHING": 1,
    "CERRADO": 2,
};

INDICES_STOCKS = {
    "Cola_actual": 0,
    "Stock_comida": 1,
    "Reposicion_activa": 2,
    "Frustracion": 3,
    "Total_atendidos": 4,
};
