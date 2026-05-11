# Simulación Comedor Unimagdalena

Modelo de dinámica de sistemas para el comedor de la Universidad del Magdalena usando **Python puro** con integración Euler.

## Requisitos

- Python 3.8+
- numpy
- matplotlib

## Instalación

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# source venv/Scripts/activate  # Windows
pip install numpy matplotlib
```

## Uso

```bash
python main.py
```

La simulación ejecuta 1920 pasos de tiempo (TIME_STEP = 0.125 min) en un horizonte de 240 minutos (11am - 3pm).

## Parámetros

Todos los parámetros están en `src/parametros.py`:

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| Beneficiarios | 800 | Total de estudiantes con derecho a almuerzo |
| Tasa_Llegada_base | 9 est/min | Tasa base para distribución horaria |
| Capacidad_Biometrica | 5 est/min | Outflow máximo |
| Stock_inicial | 100 platos | |
| Tiempo_reposicion | 5 min | Latencia de reposición |
| TIME_STEP | 0.125 min | Intervalo de simulación |
| Tiempo_cierre | 240 min | Horario de cierre (3pm) |

## Distribución de Llegadas

La tasa de llegada varía según la hora del día:

| Minutes | Factor |
|---------|--------|
| 0-30 | 20% |
| 30-60 | 70% |
| 60-90 | 100% |
| 90+ | 50% |

## Estados FSM

El modelo tiene 3 estados:
- **SERVING**: Operación normal
- **REPLENISHING**: Stock agotado, reposición activa
- **CERRADO**: Fin del servicio (t >= 240 min)

## Políticas Disponibles

Para modificar los parámetros, edita `src/parametros.py`:

**Política 1 - Logística** (reposición rápida):
```python
"Tiempo_reposicion": 2.0
```

**Política 2 - Tecnológica** (doble biométrico):
```python
"Capacidad_Biometrica": 10.0
```

**Política 3 - Social** (campañas ciudadanas):
```python
"Costo_etico": 0.9
```

## Salida

La simulación genera:
- Resumen en consola
- Gráficas en `output/`:
  - `cola_actual.png`
  - `stock_comida.png`
  - `estados_reposicion.png`
  - `frustracion.png`
  - `flujos.png`
- `resultados_simulacion.md` con tabla de evolución

## Estructura del Proyecto

```
├── main.py              # Punto de entrada
├── contexto.md           # Documento maestro del modelo
├── src/
│   ├── parametros.py    # Parámetros del modelo
│   ├── modelos.py       # Ecuaciones diferenciales y FSM
│   ├── simulacion.py     # Ejecutor Euler
│   ├── graficar.py      # Visualización
│   └── exportar_md.py   # Exportación a markdown
├── output/              # Gráficas generadas
└── venv/                # Entorno virtual
```