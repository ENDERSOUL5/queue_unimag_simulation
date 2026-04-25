# -*- coding: utf-8 -*-
"""
Definiciones del modelo de dinámica de sistemas
Contiene las ecuaciones diferenciales y lógica FSM
"""
import numpy as np;
from .parametros import PARAMETROS, INDICES_STOCKS, ESTADOS;

def distribucion_llegadas(t):
  """
  Distribución horaria de llegadas de beneficiarios.
  t = tiempo en minutos desde la apertura (0 = 11am)

  Distribución por tramos:
  - t < 30 min:   20% de tasa base (llegada lenta)
  - 30 <= t < 60: 70% de tasa base (pre-pico)
  - 60 <= t < 90: 100% de tasa base (pico máximo a las 12pm)
  - t >= 90:      50% de tasa base (va bajando)
  """
  p = PARAMETROS;

  if t < 30:
    factor = 0.2;
  elif t < 60:
    factor = 0.7;
  elif t < 90:
    factor = 1.0;
  else:
    factor = 0.5;

  return p["Tasa_Llegada_base"] * factor;

def obtener_estado(cola_actual, stock_comida, reposicion_activa, tiempo):
  """
  Determina el estado actual del sistema (FSM)
  """
  if tiempo >= PARAMETROS["Tiempo_cierre"]:
    return ESTADOS["CERRADO"];

  if reposicion_activa > 0:
    return ESTADOS["REPLENISHING"];

  if stock_comida <= 0:
    return ESTADOS["REPLENISHING"];

  return ESTADOS["SERVING"];

def calcular_flux(cola_actual, stock_comida, frustracion, total_atendidos, tiempo, estado):
  """
  Calcula todos los flujos del sistema según el estado actual
  """
  p = PARAMETROS;
  beneficiarios_disponibles = p["Beneficiarios"] - total_atendidos;

  if beneficiarios_disponibles <= 0:
    return {
        "tasa_llegada": 0.0,
        "tasa_colados": 0.0,
        "tasa_atencion": 0.0,
        "llegada_comida": 0.0,
    };

  if estado == ESTADOS["CERRADO"]:
    tasa_llegada = 0.0;
    tasa_colados = 0.0;
    capacidad_atencion = min(p["Capacidad_Biometrica"] * p["Personal_presente"],
                              min(cola_actual, beneficiarios_disponibles) / p["TIME_STEP"]);
    llegada_comida = 0.0;

  elif estado == ESTADOS["REPLENISHING"]:
    tasa_base = distribucion_llegadas(tiempo);
    tasa_llegada = tasa_base * p["Tasa_asistencia"];
    if cola_actual >= beneficiarios_disponibles:
      tasa_llegada = 0.0;
    if cola_actual >= beneficiarios_disponibles:
      tasa_colados = 0.0;
    else:
      tasa_colados = p["Costo_etico"] * (frustracion / 10.0) * p["Factor_colado"];
    capacidad_atencion = 0.0;
    llegada_comida = 0.0;

  else:
    tasa_base = distribucion_llegadas(tiempo);
    tasa_llegada = tasa_base * p["Tasa_asistencia"];

    if cola_actual >= beneficiarios_disponibles:
      tasa_llegada = 0.0;

    demora = max(0.0, cola_actual - p["Capacidad_Biometrica"] * p["Personal_presente"]);
    tasa_colados = p["Costo_etico"] * (frustracion / 10.0) * p["Factor_colado"];

    capacidad_atencion = min(p["Capacidad_Biometrica"] * p["Personal_presente"],
                              min(cola_actual, beneficiarios_disponibles) / p["TIME_STEP"]);
    llegada_comida = 0.0;

  tasa_atencion = max(0.0, capacidad_atencion);

  return {
      "tasa_llegada": tasa_llegada,
      "tasa_colados": tasa_colados,
      "tasa_atencion": tasa_atencion,
      "llegada_comida": llegada_comida,
  };

def derivatives(t, y):
  """
  Calcula las derivadas para odeint
  y = [Cola_actual, Stock_comida, Reposicion_activa, Frustracion, Total_atendidos]
  """
  y = np.atleast_1d(np.asarray(y));
  cola_actual = float(y[0]);
  stock_comida = float(y[1]);
  reposicion_activa = float(y[2]);
  frustracion = float(y[3]);
  total_atendidos = float(y[4]);

  estado = obtener_estado(cola_actual, stock_comida, reposicion_activa, t);
  flux = calcular_flux(cola_actual, stock_comida, frustracion, total_atendidos, t, estado);

  p = PARAMETROS;
  beneficiarios_disponibles = p["Beneficiarios"] - total_atendidos;

  dCola = flux["tasa_llegada"] + flux["tasa_colados"] - flux["tasa_atencion"];
  if cola_actual <= 0:
    dCola = max(0.0, dCola);
  if cola_actual >= beneficiarios_disponibles:
    dCola = min(0.0, dCola);

  dComida = flux["llegada_comida"] - flux["tasa_atencion"];

  if stock_comida <= 0 and reposicion_activa <= 0:
    dReposicion = 1.0 / p["TIME_STEP"];
  elif reposicion_activa > 0:
    dReposicion = -1.0 / p["Tiempo_reposicion"];
  else:
    dReposicion = 0.0;

  demora = max(0.0, cola_actual - p["Capacidad_Biometrica"] * p["Personal_presente"]);
  dFrustracion = demora - (flux["tasa_atencion"] * p["Factor_reduccion_frustracion"]);

  dAtendidos = flux["tasa_atencion"];

  return [dCola, dComida, dReposicion, dFrustracion, dAtendidos];

def get_initial_conditions():
  """
  Condiciones iniciales de los stocks
  """
  return np.array([
      PARAMETROS["Cola_inicial"],
      PARAMETROS["Stock_inicial"],
      0.0,
      0.0,
      0.0,
  ]);