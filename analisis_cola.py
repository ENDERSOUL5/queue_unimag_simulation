# -*- coding: utf-8 -*-
"""
Análisis de Cola del Comedor Unimagdalena
Permite comparar escenarios y analizar bloqueos
"""
import numpy as np;
import pandas as pd;
import matplotlib.pyplot as plt;
import os;

DIR_SALIDA = "/home/endersoul/sim_unimag/output";

def asegurar_directorio():
  if not os.path.exists(DIR_SALIDA):
    os.makedirs(DIR_SALIDA);

PARAMETROS_BASE = {
    "Beneficiarios": 150,
    "Tasa_Llegada_base": 15.0,
    "Tasa_asistencia": 0.8,
    "Capacidad_Biometrica": 6.0,
    "Capacidad_Manual": 2.0,
    "Tiempo_reposicion": 10.0,
    "Stock_inicial": 50.0,
    "Stock_Seguridad": 10.0,
    "Personal_presente": 1.0,
    "Costo_etico": 0.5,
    "Tasa_falla_biometrica": 0.1,
    "Tiempo_cierre": 240.0,
    "TIME_STEP": 0.125,
    "Factor_colado": 0.5,
    "Tasa_redaccion_frustracion": 0.1,
    "Cola_inicial": 0.0,
};

ESCENARIOS = {
    "Base": dict(PARAMETROS_BASE),
    "Politica_Logistica": {**PARAMETROS_BASE, "Tiempo_reposicion": 2.0},
    "Politica_Tecnologica": {**PARAMETROS_BASE, "Capacidad_Biometrica": 12.0},
    "Politica_Social": {**PARAMETROS_BASE, "Costo_etico": 0.9},
};

ESTADOS_MAP = {
    0: "SERVING",
    1: "REPLENISHING",
    2: "CERRADO",
};

def distribucion_llegadas(t, tasa_base):
  if t < 30:
    factor = 0.2;
  elif t < 60:
    factor = 0.7;
  elif t < 90:
    factor = 1.0;
  else:
    factor = 0.5;
  return tasa_base * factor;

def obtener_estado(cola_actual, stock_comida, reposicion_activa, tiempo, params):
  if tiempo >= params["Tiempo_cierre"]:
    return 2;
  if reposicion_activa > 0:
    return 1;
  if stock_comida <= 0:
    return 1;
  return 0;

def calcular_flux(cola_actual, stock_comida, frustracion, tiempo, estado, params):
  if estado == 2:
    tasa_llegada = 0.0;
    tasa_colados = 0.0;
    capacidad_atencion = min(params["Capacidad_Biometrica"] * params["Personal_presente"],
                              cola_actual / params["TIME_STEP"]);
    llegada_comida = 0.0;
  elif estado == 1:
    tasa_llegada = 0.0;
    tasa_colados = 0.0;
    capacidad_atencion = 0.0;
    llegada_comida = params["Stock_inicial"] / params["Tiempo_reposicion"];
  else:
    tasa_base = distribucion_llegadas(tiempo, params["Tasa_Llegada_base"]);
    tasa_llegada = tasa_base * params["Tasa_asistencia"];
    if cola_actual >= params["Beneficiarios"]:
      tasa_llegada = 0.0;
    demora = max(0.0, cola_actual - params["Capacidad_Biometrica"] * params["Personal_presente"]);
    tasa_colados = params["Costo_etico"] * (frustracion / 10.0) * params["Factor_colado"];
    capacidad_atencion = min(params["Capacidad_Biometrica"] * params["Personal_presente"],
                              cola_actual / params["TIME_STEP"]);
    llegada_comida = 0.0;

  tasa_atencion = max(0.0, capacidad_atencion);
  return {
      "tasa_llegada": tasa_llegada,
      "tasa_colados": tasa_colados,
      "tasa_atencion": tasa_atencion,
      "llegada_comida": llegada_comida,
  };

def ejecutar_simulacion(params):
  t_inicial = 0.0;
  t_final = params["Tiempo_cierre"];
  dt = params["TIME_STEP"];
  n_pasos = int((t_final - t_inicial) / dt);
  tiempos = np.linspace(t_inicial, t_final, n_pasos + 1);

  resultados = np.zeros((n_pasos + 1, 4));

  cola_actual = params["Cola_inicial"];
  stock_comida = params["Stock_inicial"];
  reposicion_activa = 0.0;
  frustracion = 0.0;

  resultados[0] = [cola_actual, stock_comida, reposicion_activa, frustracion];

  for i in range(n_pasos):
    t = tiempos[i];
    estado = obtener_estado(cola_actual, stock_comida, reposicion_activa, t, params);
    flux = calcular_flux(cola_actual, stock_comida, frustracion, t, estado, params);

    dCola = flux["tasa_llegada"] + flux["tasa_colados"] - flux["tasa_atencion"];
    if cola_actual <= 0:
      dCola = max(0.0, dCola);

    dComida = flux["llegada_comida"] - flux["tasa_atencion"];
    if stock_comida <= 0:
      dComida = max(0.0, dComida);

    if estado == 1:
      if stock_comida <= 0 and reposicion_activa <= 0:
        dReposicion = 1.0;
      else:
        dReposicion = -1.0 / params["Tiempo_reposicion"];
    else:
      dReposicion = -1.0 / params["TIME_STEP"] if reposicion_activa > 0 else 0.0;

    demora = max(0.0, cola_actual - params["Capacidad_Biometrica"] * params["Personal_presente"]);
    dFrustracion = demora - params["Tasa_redaccion_frustracion"];

    cola_actual = max(0.0, min(cola_actual + dCola * dt, float(params["Beneficiarios"])));
    stock_comida = max(0.0, stock_comida + dComida * dt);
    reposicion_activa = max(0.0, reposicion_activa + dReposicion * dt);
    frustracion = max(0.0, frustracion + dFrustracion * dt);

    resultados[i + 1] = [cola_actual, stock_comida, reposicion_activa, frustracion];

  return {
      "tiempo": tiempos,
      "cola_actual": resultados[:, 0],
      "stock_comida": resultados[:, 1],
      "reposicion_activa": resultados[:, 2],
      "frustracion": resultados[:, 3],
  };

def calcular_estados(resultados, params):
  n = len(resultados["tiempo"]);
  estados = np.zeros(n, dtype=int);
  for i in range(n):
    stocks = [
        resultados["cola_actual"][i],
        resultados["stock_comida"][i],
        resultados["reposicion_activa"][i],
    ];
    t = resultados["tiempo"][i];
    estados[i] = obtener_estado(stocks[0], stocks[1], stocks[2], t, params);
  return estados;

def crear_dataframe_minutado(resultados, estados):
  df = pd.DataFrame({
      "tiempo": resultados["tiempo"],
      "cola": resultados["cola_actual"],
      "stock": resultados["stock_comida"],
      "reposicion": resultados["reposicion_activa"],
      "estado_cod": estados,
  });
  df["estado"] = df["estado_cod"].map(ESTADOS_MAP);
  df_minuto = df.groupby(df["tiempo"].astype(int), as_index=False).last();
  return df_minuto;

def identificar_bloqueos(estados, tiempos):
  bloqueos = [];
  en_bloqueo = False;
  inicio = 0;
  cola_max = 0;

  for i in range(len(estados)):
    if estados[i] == 1:
      if not en_bloqueo:
        en_bloqueo = True;
        inicio = tiempos[i];
        cola_max = 0;
    else:
      if en_bloqueo:
        duracion = tiempos[i - 1] - inicio if i > 0 else 0;
        bloqueos.append({
            "inicio": inicio,
            "fin": tiempos[i - 1] if i > 0 else tiempos[-1],
            "duracion": duracion,
            "cola_maxima": cola_max,
        });
        en_bloqueo = False;
    if estados[i] == 1:
      cola_max = max(cola_max, 0);

  if en_bloqueo:
    bloqueos.append({
        "inicio": inicio,
        "fin": tiempos[-1],
        "duracion": tiempos[-1] - inicio,
        "cola_maxima": cola_max,
    });

  return bloqueos;

def analizar_escenario(nombre, params):
  resultados = ejecutar_simulacion(params);
  estados = calcular_estados(resultados, params);
  df_minuto = crear_dataframe_minutado(resultados, estados);
  bloqueos = identificar_bloqueos(estados, resultados["tiempo"]);

  cola_max = resultados["cola_actual"].max();
  tiempo_replenishing = np.sum(estados == 1);

  return {
      "nombre": nombre,
      "resultados": resultados,
      "estados": estados,
      "df_minuto": df_minuto,
      "bloqueos": bloqueos,
      "cola_maxima": cola_max,
      "tiempo_replenishing": tiempo_replenishing,
  };

def imprimir_resumen_bloqueos(nombre, analisis):
  print(f"\n{'='*50}");
  print(f"ESCENARIO: {nombre}");
  print(f"{'='*50}");
  print(f"Cola máxima: {analisis['cola_maxima']:.1f}");
  print(f"Tiempo en REPLENISHING: {analisis['tiempo_replenishing']:.0f} pasos");

  if analisis["bloqueos"]:
    print(f"\nBloqueos detectados: {len(analisis['bloqueos'])}");
    for i, b in enumerate(analisis["bloqueos"]):
      print(f"  Bloqueo {i+1}: t={b['inicio']:.1f}-{b['fin']:.1f} min, "
            f"duración={b['duracion']:.1f} min");
  else:
    print("\nSin bloqueos detectados");

def graficar_comparativa(resultados_dict, labels=None):
  if labels is None:
    labels = list(resultados_dict.keys());

  fig, axes = plt.subplots(2, 2, figsize=(14, 10));

  colores = ["#2E86AB", "#E74C3C", "#2ECC71", "#9B59B6"];
  estilos = ["-", "--", "-.", ":"];

  axes[0, 0].set_title("Cola Actual vs Tiempo", fontweight="bold");
  axes[0, 1].set_title("Stock Comida vs Tiempo", fontweight="bold");
  axes[1, 0].set_title("Estado del Sistema (FSM)", fontweight="bold");
  axes[1, 1].set_title("Comparación de Colas Máximas", fontweight="bold");

  for i, (nombre, analisis) in enumerate(resultados_dict.items()):
    resultados = analisis["resultados"];
    estados = analisis["estados"];
    color = colores[i % len(colores)];
    estilo = estilos[i % len(estilos)];

    t = resultados["tiempo"];
    axes[0, 0].plot(t, resultados["cola_actual"], color=color,
                    linestyle=estilo, linewidth=2, label=nombre);
    axes[0, 1].plot(t, resultados["stock_comida"], color=color,
                    linestyle=estilo, linewidth=2, label=nombre);

    estados_binarios = (estados == 1).astype(float);
    axes[1, 0].plot(t, estados_binarios, color=color,
                    linestyle=estilo, linewidth=2, label=nombre,
                    alpha=0.7);

  axes[0, 0].axhline(y=150, color="red", linestyle="--", linewidth=1.5,
                    label="Aforo máximo");
  axes[0, 0].set_xlabel("Tiempo (min)");
  axes[0, 0].set_ylabel("Beneficiarios");
  axes[0, 0].legend(loc="upper left");
  axes[0, 0].grid(True, alpha=0.3);

  axes[0, 1].axhline(y=0, color="red", linestyle="--", linewidth=1.5);
  axes[0, 1].set_xlabel("Tiempo (min)");
  axes[0, 1].set_ylabel("Platos");
  axes[0, 1].legend(loc="upper right");
  axes[0, 1].grid(True, alpha=0.3);

  axes[1, 0].set_xlabel("Tiempo (min)");
  axes[1, 0].set_ylabel("REPLENISHING (1=Sí)");
  axes[1, 0].set_yticks([0, 1]);
  axes[1, 0].set_yticklabels(["NO", "SÍ"]);
  axes[1, 0].legend(loc="upper right");
  axes[1, 0].grid(True, alpha=0.3);

  nombres = [a["nombre"] for a in resultados_dict.values()];
  colas_max = [a["cola_maxima"] for a in resultados_dict.values()];
  bars = axes[1, 1].bar(nombres, colas_max, color=colores[:len(nombres)]);
  axes[1, 1].axhline(y=150, color="red", linestyle="--", linewidth=1.5,
                    label="Aforo máximo");
  axes[1, 1].set_ylabel("Cola máxima");
  axes[1, 1].legend();
  axes[1, 1].grid(True, alpha=0.3, axis="y");

  for bar, cola in zip(bars, colas_max):
    axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f"{cola:.0f}", ha="center", va="bottom", fontweight="bold");

  plt.tight_layout();
  path = os.path.join(DIR_SALIDA, "comparativa_escenarios.png");
  plt.savefig(path, dpi=150);
  print(f"Guardado: {path}");
  plt.close();

def main():
  asegurar_directorio();
  print("="*60);
  print("ANÁLISIS DE COLA - COMEDOR UNIMAGDALENA");
  print("="*60);

  resultados_dict = {};
  for nombre, params in ESCENARIOS.items():
    analisis = analizar_escenario(nombre, params);
    resultados_dict[nombre] = analisis;
    imprimir_resumen_bloqueos(nombre, analisis);

  print(f"\n{'='*60}");
  print("COMPARACIÓN DE ESCENARIOS");
  print(f"{'='*60}");
  print(f"{'Escenario':<25} {'Cola Max':<12} {'Tiempo Rep':<12}");
  print("-"*50);
  for nombre, analisis in resultados_dict.items():
    print(f"{nombre:<25} {analisis['cola_maxima']:<12.1f} "
          f"{analisis['tiempo_replenishing']:<12.0f}");

  graficar_comparativa(resultados_dict);

  print(f"\nGráficas guardadas en: {DIR_SALIDA}");
  print("\nAnálisis completado!");

if __name__ == "__main__":
  main();
