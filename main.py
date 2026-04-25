#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Punto de entrada principal - Simulación Comedor Unimagdalena
Ejecuta el modelo de dinámica de sistemas usando Python puro con scipy
"""
import sys;
import os;

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)));

from src import (
    ejecutar_simulacion,
    calcular_estados_y_fluxos,
    imprimir_resumen,
    graficar_resumen_completo,
);

def main():
  print("="*60);
  print("  SIMULACIÓN COMEDOR UNIMAGDALENA");
  print("  Modelo de Dinámica de Sistemas - Python Puro");
  print("="*60);
  print();

  resultados = ejecutar_simulacion();

  estados, fluxos = calcular_estados_y_fluxos(resultados);

  imprimir_resumen(resultados, estados);

  graficar_resumen_completo(resultados, estados, fluxos);

  print("\nSimulación completada exitosamente!");

if __name__ == "__main__":
  main();
