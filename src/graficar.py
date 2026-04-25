# -*- coding: utf-8 -*-
"""
Funciones de graficación con matplotlib
"""
import matplotlib.pyplot as plt;
import numpy as np;
import os;
from .parametros import PARAMETROS;

DIR_SALIDA = "/home/endersoul/sim_unimag/output";

def asegurar_directorio():
  if not os.path.exists(DIR_SALIDA):
    os.makedirs(DIR_SALIDA);

def graficar_cola_actual(resultados, estados):
  """
  Gráfica de cola actual de beneficiarios esperando
  """
  fig, ax = plt.subplots(figsize=(12, 6));

  t = resultados["tiempo"];
  ca = resultados["cola_actual"];

  ax.plot(t, ca, color="#2E86AB", linewidth=2, label="Cola actual");
  ax.fill_between(t, 0, ca, alpha=0.3, color="#2E86AB");

  ax.axhline(y=PARAMETROS["Beneficiarios"], color="red", linestyle="--", linewidth=1.5,
              label=f'Beneficiarios ({PARAMETROS["Beneficiarios"]})');
  ax.axhline(y=0, color="gray", linestyle="-", linewidth=0.5);

  replenishing_mask = estados == 1;
  if np.any(replenishing_mask):
    ax.fill_between(t, 0, ca, where=replenishing_mask,
                     alpha=0.5, color="orange", label="REPLENISHING");

  cerrado_mask = estados == 2;
  if np.any(cerrado_mask):
    ax.fill_between(t, 0, ca, where=cerrado_mask,
                     alpha=0.5, color="green", label="CERRADO");

  ax.set_xlabel("Tiempo (minutos)", fontsize=12);
  ax.set_ylabel("Beneficiarios en cola", fontsize=12);
  ax.set_title("Cola Actual vs Tiempo", fontsize=14, fontweight="bold");
  ax.legend(loc="upper left");
  ax.grid(True, alpha=0.3);
  ax.set_xlim(0, t[-1]);
  ax.set_ylim(0, None);

  plt.tight_layout();
  path = os.path.join(DIR_SALIDA, "cola_actual.png");
  plt.savefig(path, dpi=150);
  print(f"Guardado: {path}");
  plt.close();

def graficar_stock_comida(resultados):
  """
  Gráfica de stock de comida
  """
  fig, ax = plt.subplots(figsize=(12, 6));

  t = resultados["tiempo"];
  sc = resultados["stock_comida"];

  ax.plot(t, sc, color="#28A745", linewidth=2, label="Stock comida");
  ax.fill_between(t, 0, sc, alpha=0.3, color="#28A745");

  ax.axhline(y=0, color="red", linestyle="--", linewidth=1.5,
             label="Agotamiento (0)");
  ax.axhline(y=50, color="blue", linestyle=":", linewidth=1,
             label="Stock inicial (50)");

  ax.set_xlabel("Tiempo (minutos)", fontsize=12);
  ax.set_ylabel("Platos", fontsize=12);
  ax.set_title("Stock de Comida vs Tiempo", fontsize=14, fontweight="bold");
  ax.legend(loc="upper right");
  ax.grid(True, alpha=0.3);
  ax.set_xlim(0, t[-1]);
  ax.set_ylim(0, None);

  plt.tight_layout();
  path = os.path.join(DIR_SALIDA, "stock_comida.png");
  plt.savefig(path, dpi=150);
  print(f"Guardado: {path}");
  plt.close();

def graficar_estado_reposicion(resultados, estados):
  """
  Gráfica de reposición activa y estados
  """
  fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True);

  t = resultados["tiempo"];
  ra = resultados["reposicion_activa"];

  ax1.plot(t, ra, color="#FF6B35", linewidth=2, label="Reposición activa");
  ax1.set_ylabel("Reposición activa (dmnl)", fontsize=12);
  ax1.set_title("Estado de Reposición", fontsize=14, fontweight="bold");
  ax1.legend(loc="upper right");
  ax1.grid(True, alpha=0.3);
  ax1.set_ylim(0, None);

  nombres_estados = ["SERVING", "REPLENISHING", "CERRADO"];
  colores = ["green", "orange", "gray"];

  for i, (nombre, color) in enumerate(zip(nombres_estados, colores)):
    mask = estados == i;
    if np.any(mask):
      ax2.fill_between(t, 0, 1, where=mask, alpha=0.7, color=color, label=nombre);

  ax2.set_ylabel("Estado", fontsize=12);
  ax2.set_xlabel("Tiempo (minutos)", fontsize=12);
  ax2.set_title("Máquina de Estados Finitos (FSM)", fontsize=14, fontweight="bold");
  ax2.legend(loc="upper right");
  ax2.grid(True, alpha=0.3);
  ax2.set_xlim(0, t[-1]);
  ax2.set_yticks([]);

  plt.tight_layout();
  path = os.path.join(DIR_SALIDA, "estados_reposicion.png");
  plt.savefig(path, dpi=150);
  print(f"Guardado: {path}");
  plt.close();

def graficar_frustracion(resultados):
  """
  Gráfica de frustración acumulada
  """
  fig, ax = plt.subplots(figsize=(12, 6));

  t = resultados["tiempo"];
  fr = resultados["frustracion"];

  ax.plot(t, fr, color="#9B59B6", linewidth=2, label="Frustración");
  ax.fill_between(t, 0, fr, alpha=0.3, color="#9B59B6");

  ax.set_xlabel("Tiempo (minutos)", fontsize=12);
  ax.set_ylabel("Frustración (acumulada)", fontsize=12);
  ax.set_title("Nivel de Frustración vs Tiempo", fontsize=14, fontweight="bold");
  ax.legend(loc="upper left");
  ax.grid(True, alpha=0.3);
  ax.set_xlim(0, t[-1]);
  ax.set_ylim(0, None);

  plt.tight_layout();
  path = os.path.join(DIR_SALIDA, "frustracion.png");
  plt.savefig(path, dpi=150);
  print(f"Guardado: {path}");
  plt.close();

def graficar_fluxos(resultados, fluxos):
  """
  Gráfica de flujos de entrada y salida
  """
  fig, ax = plt.subplots(figsize=(12, 6));

  t = resultados["tiempo"];

  ax.plot(t, fluxos["tasa_llegada"], color="#3498DB", linewidth=1.5,
          label="Llegadas", linestyle="-");
  ax.plot(t, fluxos["tasa_colados"], color="#E74C3C", linewidth=1.5,
          label="Colados", linestyle="-");
  ax.plot(t, fluxos["tasa_atencion"], color="#2ECC71", linewidth=2,
          label="Atención (salida)", linestyle="-");

  ax.set_xlabel("Tiempo (minutos)", fontsize=12);
  ax.set_ylabel("Tasa (estudiantes/min)", fontsize=12);
  ax.set_title("Flujos de Entrada y Salida", fontsize=14, fontweight="bold");
  ax.legend(loc="upper right");
  ax.grid(True, alpha=0.3);
  ax.set_xlim(0, t[-1]);
  ax.set_ylim(0, None);

  plt.tight_layout();
  path = os.path.join(DIR_SALIDA, "flujos.png");
  plt.savefig(path, dpi=150);
  print(f"Guardado: {path}");
  plt.close();

def graficar_resumen_completo(resultados, estados, fluxos):
  """
  Genera todas las gráficas
  """
  asegurar_directorio();

  print("\nGenerando gráficas...");
  graficar_cola_actual(resultados, estados);
  graficar_stock_comida(resultados);
  graficar_estado_reposicion(resultados, estados);
  graficar_frustracion(resultados);
  graficar_fluxos(resultados, fluxos);
  print("Todas las gráficas generadas.\n");