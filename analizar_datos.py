#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analizador de datos de simulación - Muestra valores X,Y
"""
import sys;
import os;

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)));

from src import (
    ejecutar_simulacion,
    calcular_estados_y_fluxos,
    PARAMETROS,
);

def main():
  print("="*70);
  print("  ANÁLISIS DE COLA ACTUAL - VALORES X,Y");
  print("="*70);
  print();

  resultados = ejecutar_simulacion();
  estados, fluxos = calcular_estados_y_fluxos(resultados);

  print("\n" + "="*70);
  print("COLA ACTUAL (muestreo cada 20 puntos para legibilidad)");
  print("="*70);
  print(f"{'Tiempo(min)':<12} {'Cola':<10} {'Stock':<10} {'Atendidos':<10} {'Estado':<15}");
  print("-"*70);

  nombres_estados = ["SERVING", "REPLENISHING", "CERRADO"];

  paso_muestreo = 20;
  for i in range(0, len(resultados["tiempo"]), paso_muestreo):
    t = resultados["tiempo"][i];
    ca = resultados["cola_actual"][i];
    sc = resultados["stock_comida"][i];
    ta = resultados["total_atendidos"][i];
    estado_idx = estados[i];
    estado_nombre = nombres_estados[estado_idx] if estado_idx < len(nombres_estados) else str(estado_idx);

    print(f"{t:<12.3f} {ca:<10.3f} {sc:<10.3f} {ta:<10.3f} {estado_nombre:<15}");

  print();
  print("="*70);
  print("PUNTOS DE INTERÉS");
  print("="*70);

  cola = resultados["cola_actual"];
  stock = resultados["stock_comida"];
  tiempo = resultados["tiempo"];
  ta = resultados["total_atendidos"];

  idx_max_cola = cola.argmax();

  print(f"Cola máxima:        {cola.max():.2f} en t={tiempo[idx_max_cola]:.2f} min");
  print(f"Stock mínimo:      {stock.min():.2f}");
  print(f"Total atendidos:   {ta[-1]:.2f}");
  print(f"Atendidos restantes: {PARAMETROS['Beneficiarios'] - ta[-1]:.2f}");

  print();
  print("="*70);
  print("TRANSICIONES DE ESTADO (cuando cambia el estado)");
  print("="*70);
  print(f"{'Tiempo(min)':<12} {'Estado':<15} {'Cola':<10} {'Stock':<10} {'Atendidos':<10}");
  print("-"*70);

  estado_anterior = -1;
  for i in range(len(estados)):
    if estados[i] != estado_anterior:
      t = resultados["tiempo"][i];
      ca = resultados["cola_actual"][i];
      sc = resultados["stock_comida"][i];
      ta = resultados["total_atendidos"][i];
      estado_nombre = nombres_estados[estados[i]];
      print(f"{t:<12.3f} {estado_nombre:<15} {ca:<10.3f} {sc:<10.3f} {ta:<10.3f}");
      estado_anterior = estados[i];

  print();
  print("="*70);
  print("FLUJOS EN PICO DE COLA");
  print("="*70);
  print(f"{'Tiempo(min)':<12} {'Llegada':<10} {'Colados':<10} {'Atención':<10}");
  print("-"*70);

  idx_pico = cola.argmax();
  for i in range(max(0, idx_pico - 40), min(len(cola), idx_pico + 41), 5):
    t = resultados["tiempo"][i];
    ll = fluxos["tasa_llegada"][i];
    co = fluxos["tasa_colados"][i];
    at = fluxos["tasa_atencion"][i];
    print(f"{t:<12.3f} {ll:<10.3f} {co:<10.3f} {at:<10.3f}");

if __name__ == "__main__":
  main();