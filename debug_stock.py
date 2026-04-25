#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug: Imprime valores críticos en cada paso
"""
import sys;
import os;

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)));

from src import (
    ejecutar_simulacion,
    calcular_estados_y_fluxos,
);

def main():
  print("="*70);
  print("  DEBUG - Valores críticos cada 5 pasos");
  print("="*70);
  print();

  resultados = ejecutar_simulacion();
  estados, fluxos = calcular_estados_y_fluxos(resultados);

  print("\n" + "="*70);
  print("DEBUG (muestreo cada 5 puntos)");
  print("="*70);
  print(f"{'Tiempo':<10} {'Cola':<10} {'Stock':<10} {'Reposicion':<10} {'Estado':<15}");
  print("-"*70);

  nombres_estados = ["SERVING", "REPLENISHING", "CERRADO"];

  paso_muestreo = 5;
  for i in range(0, len(resultados["tiempo"]), paso_muestreo):
    t = resultados["tiempo"][i];
    ca = resultados["cola_actual"][i];
    sc = resultados["stock_comida"][i];
    ra = resultados["reposicion_activa"][i];
    estado_idx = estados[i];
    estado_nombre = nombres_estados[estado_idx] if estado_idx < len(nombres_estados) else str(estado_idx);

    print(f"{t:<10.3f} {ca:<10.3f} {sc:<10.3f} {ra:<10.3f} {estado_nombre:<15}");

    if i > 0 and i % 50 == 0:
      print("...");

if __name__ == "__main__":
  main();