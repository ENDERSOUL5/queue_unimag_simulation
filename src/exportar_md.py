# -*- coding: utf-8 -*-
"""
Exportador de resultados de simulacion a Markdown
Genera resultados_simulacion.md con formato de tabla para analisis
"""
import os;
import numpy as np;
from .parametros import PARAMETROS, ESTADOS;

# Mapeo inverso de estados para obtener nombres
NOMBRES_ESTADOS = {v: k for k, v in ESTADOS.items()};


def exportar_resultados_md(resultados, estados, fluxos,
                            ruta="/home/endersoul/sim_unimag/resultados_simulacion.md",
                            intervalo_muestreo=2.0):
  """
  Exporta los resultados de la simulacion a un archivo Markdown.
  """
  p = PARAMETROS;
  t = resultados["tiempo"];
  ca = resultados["cola_actual"];
  sc = resultados["stock_comida"];
  fr = resultados["frustracion"];
  ta = resultados["total_atendidos"];

  # Parametros para el encabezado
  dt = p["TIME_STEP"];
  t_final = p["Tiempo_cierre"];
  beneficiarios = p["Beneficiarios"];
  tasa_base = p["Tasa_Llegada_base"];
  cap_bio = p["Capacidad_Biometrica"];
  t_repo = p["Tiempo_reposicion"];
  stock_ini = p["Stock_inicial"];
  factor_red = p["Factor_reduccion_frustracion"];
  factor_escala = p.get("Factor_escala_frustracion", 10.0);

  # Indices para muestreo cada intervalo minutos
  paso_muestra = max(1, int(intervalo_muestreo / dt));
  indices = list(range(0, len(t), paso_muestra));
  if indices[-1] != len(t) - 1:
    indices.append(len(t) - 1);

  lineas = [];
  lineas.append("# Resultados de Simulacion - Comedor Unimagdalena\n");
  lineas.append("## Parametros de la Simulacion\n");
  lineas.append(f"- TIME_STEP: {dt} min\n");
  lineas.append(f"- Horizonte: {t_final} min (11am - 3pm)\n");
  lineas.append(f"- Beneficiarios: {beneficiarios}\n");
  lineas.append(f"- Tasa_Llegada_base: {tasa_base} est/min\n");
  lineas.append(f"- Capacidad_Biometrica: {cap_bio} est/min\n");
  lineas.append(f"- Tiempo_reposicion: {t_repo} min\n");
  lineas.append(f"- Stock_inicial: {stock_ini}\n");
  lineas.append(f"- Factor_reduccion_frustracion: {factor_red}\n");
  lineas.append(f"- Factor_escala_frustracion: {factor_escala}\n");
  lineas.append("\n---\n");

  lineas.append("\n## Tabla: Evolucion del Sistema (cada 2 minutos)\n");
  lineas.append("| t | Cola | Stock | Frustr | Atend | Estado | Llegada | Colados | Atencion |\n");
  lineas.append("|---|---|---|---|---|---|---|---|---|\n");

  for i in indices:
    estado_nombre = NOMBRES_ESTADOS.get(estados[i], str(estados[i]));
    llegada = fluxos["tasa_llegada"][i];
    colados = fluxos["tasa_colados"][i];
    atencion = fluxos["tasa_atencion"][i];
    lineas.append(
      f"| {t[i]:>5.0f} | {ca[i]:>7.2f} | {sc[i]:>7.2f} | {fr[i]:>8.2f} | "
      f"{ta[i]:>7.1f} | {estado_nombre:>12} | {llegada:>7.2f} | {colados:>7.2f} | {atencion:>8.2f} |\n"
    );

  lineas.append("\n---\n");

  # Resumen estadistico
  idx_max_cola = int(np.argmax(ca));
  idx_min_stock = int(np.argmin(sc));
  idx_max_frustr = int(np.argmax(fr));

  lineas.append("\n## Resumen Estadistico\n");
  lineas.append("| Metrica | Valor | Tiempo |\n");
  lineas.append("|---------|-------|--------|\n");
  lineas.append(f"| Cola maxima | {ca.max():.2f} | {t[idx_max_cola]:.1f} |\n");
  lineas.append(f"| Cola promedio | {ca.mean():.2f} | - |\n");
  lineas.append(f"| Cola final | {ca[-1]:.2f} | {t[-1]:.0f} |\n");
  lineas.append(f"| Stock minimo | {sc.min():.2f} | {t[idx_min_stock]:.1f} |\n");
  lineas.append(f"| Stock promedio | {sc.mean():.2f} | - |\n");
  lineas.append(f"| Stock final | {sc[-1]:.2f} | {t[-1]:.0f} |\n");
  lineas.append(f"| Total atendidos | {ta[-1]:.1f} | - |\n");
  lineas.append(f"| Frustracion maxima | {fr.max():.2f} | {t[idx_max_frustr]:.1f} |\n");
  lineas.append(f"| Frustracion final | {fr[-1]:.2f} | - |\n");

  lineas.append("\n---\n");

  # Cambios de estado
  lineas.append("\n## Cambios de Estado\n");
  lineas.append("| Tiempo | De | A |\n");
  lineas.append("|--------|----|----|\n");

  estado_anterior = -1;
  for i in range(len(estados)):
    if estados[i] != estado_anterior:
      nombre_anterior = NOMBRES_ESTADOS.get(estado_anterior, "-") if estado_anterior != -1 else "INICIO";
      nombre_actual = NOMBRES_ESTADOS.get(estados[i], str(estados[i]));
      lineas.append(f"| {t[i]:.1f} | {nombre_anterior} | {nombre_actual} |\n");
      estado_anterior = estados[i];

  with open(ruta, "w", encoding="utf-8") as f:
    f.writelines(lineas);

  print(f"\nResultados exportados a: {ruta}");
