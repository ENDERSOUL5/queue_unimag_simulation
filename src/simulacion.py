# -*- coding: utf-8 -*-
"""
Ejecutor de simulación
Usa integración Euler para resolver el sistema de ecuaciones diferenciales
Más simple y rápido para modelos con discontinuidades (FSM)
"""
import numpy as np;
from .parametros import PARAMETROS;
from .modelos import derivatives, get_initial_conditions, obtener_estado, calcular_flux, ESTADOS;

def ejecutar_simulacion():
  """
  Ejecuta la simulación completa y retorna DataFrame con resultados
  """
  p = PARAMETROS;
  t_inicial = 0.0;
  t_final = p["Tiempo_cierre"];
  dt = p["TIME_STEP"];

  n_pasos = int((t_final - t_inicial) / dt);
  tiempos = np.linspace(t_inicial, t_final, n_pasos + 1);

  print(f"Ejecutando simulación: {n_pasos} pasos de tiempo");
  print(f"  Horizonte: {t_inicial} a {t_final} minutos");
  print(f"  TIME_STEP: {dt} minutos");

  n_vars = 5;
  resultados = np.zeros((n_pasos + 1, n_vars));

  y = get_initial_conditions();
  resultados[0] = y;

  for i in range(n_pasos):
    t = tiempos[i];
    dydt = derivatives(t, y);
    y = y + np.array(dydt) * dt;

    beneficiarios_disponibles = p["Beneficiarios"] - y[4];
    y[0] = max(0.0, y[0]);
    y[0] = min(y[0], float(beneficiarios_disponibles));
    y[1] = max(0.0, y[1]);
    y[2] = max(0.0, y[2]);
    y[3] = max(0.0, y[3]);
    y[4] = max(0.0, y[4]);

    prev_reposicion = float(resultados[i][2]);
    if prev_reposicion > 0 and y[2] <= 0:
      y[1] = p["Stock_inicial"];

    if y[4] >= p["Beneficiarios"]:
      y[0] = 0.0;

    resultados[i + 1] = y;

    if i % 400 == 0:
      print(f"  Progreso: {i}/{n_pasos} pasos ({(i/n_pasos*100):.1f}%)");

  print(f"  Progreso: {n_pasos}/{n_pasos} pasos (100.0%)");

  return {
      "tiempo": tiempos,
      "cola_actual": resultados[:, 0],
      "stock_comida": resultados[:, 1],
      "reposicion_activa": resultados[:, 2],
      "frustracion": resultados[:, 3],
      "total_atendidos": resultados[:, 4],
  };

def calcular_estados_y_fluxos(resultados):
  """
  Calcula estados y flujos para cada punto de tiempo
  """
  n = len(resultados["tiempo"]);
  estados = np.zeros(n, dtype=int);
  fluxos = {
      "tasa_llegada": np.zeros(n),
      "tasa_colados": np.zeros(n),
      "tasa_atencion": np.zeros(n),
      "llegada_comida": np.zeros(n),
  };

  stocks = np.zeros(5);
  for i in range(n):
    stocks[0] = resultados["cola_actual"][i];
    stocks[1] = resultados["stock_comida"][i];
    stocks[2] = resultados["reposicion_activa"][i];
    stocks[3] = resultados["frustracion"][i];
    stocks[4] = resultados["total_atendidos"][i];

    t = resultados["tiempo"][i];
    estado = obtener_estado(stocks[0], stocks[1], stocks[2], t);
    estados[i] = estado;

    flux = calcular_flux(stocks[0], stocks[1], stocks[3], stocks[4], t, estado);
    fluxos["tasa_llegada"][i] = flux["tasa_llegada"];
    fluxos["tasa_colados"][i] = flux["tasa_colados"];
    fluxos["tasa_atencion"][i] = flux["tasa_atencion"];
    fluxos["llegada_comida"][i] = flux["llegada_comida"];

  return estados, fluxos;

def imprimir_resumen(resultados, estados):
  """
  Imprime resumen de resultados de la simulación
  """
  ca = resultados["cola_actual"];
  sc = resultados["stock_comida"];
  ta = resultados["total_atendidos"];

  print("\n" + "="*50);
  print("RESUMEN DE SIMULACIÓN");
  print("="*50);
  print(f"Tiempo final:           {resultados['tiempo'][-1]:.2f} min");
  print(f"Cola máxima:            {ca.max():.1f}");
  print(f"Cola final:             {ca[-1]:.1f}");
  print(f"Stock comida mínimo:    {sc.min():.1f}");
  print(f"Stock comida final:     {sc[-1]:.1f}");
  print(f"Total atendidos:        {ta[-1]:.1f}");
  print(f"Beneficiarios restantes:{resultados['cola_actual'][-1] + ta[-1]:.1f}");

  n_replenishing = np.sum(estados == ESTADOS["REPLENISHING"]);
  n_cerrado = np.sum(estados == ESTADOS["CERRADO"]);
  print(f"Pasos en REPLENISHING:  {n_replenishing}");
  print(f"Pasos en CERRADO:       {n_cerrado}");
  print("="*50);