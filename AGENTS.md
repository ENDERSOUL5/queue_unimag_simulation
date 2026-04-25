# AGENTS.md - Simulación Comedor Unimagdalena

## Proyecto
Modelado de dinámica de sistemas para el comedor de la Universidad del Magdalena usando **Python puro** con integración Euler.

## Fuente Autoritativa
- `contexto.md` — Documento maestro con todas las ecuaciones, parámetros y lógica del modelo.

## Comandos de Simulación
```bash
cd /home/endersoul/sim_unimag
source venv/bin/activate
python main.py              # Ejecuta simulación y genera gráficas
```

## Estructura del Modelo (contexto.md)
- **Stock principal**: `Cola_actual` (beneficiarios esperando ahora)
- **Flujos**: Entrada (Tasa_Llegada + Tasa_Colados), Salida (Tasa_Atencion)
- **4 Estados FSM**: SERVING → DEPLETED → REPLENISHING → CERRADO
- **Bucles**: Caos (refuerzo), Suministro (balance), Fallo biométrico (refuerzo)
- **TIME_STEP**: 0.125 min para precisión en bloqueos de 5-15 min
- **Horizonte**: 240 minutos (4 horas, de 11am a 3pm)

## Distribución de Llegadas
La tasa de llegada varía según la hora del día (t = minutos desde apertura = 11am):
- t < 30 min: 20% de Tasa_Llegada_base (llegada lenta)
- 30 <= t < 60 min: 70% (pre-pico)
- 60 <= t < 90 min: 100% (pico a las 12pm)
- t >= 90 min: 50% (va bajando)

## Parámetros Clave
| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| Beneficiarios | 150 | Total de estudiantes con derecho a almuerzo |
| Tasa_Llegada_base | 15 est/min | Tasa base para distribución horaria |
| Tasa_asistencia | 0.8 | Porcentaje de beneficiarios que asiste (variable) |
| Capacidad_Biometrica | 6 est/min | Outflow |
| Tiempo_reposicion | 10 min | Latencia interrupción |
| Stock_inicial | 50 platos | |
| Cola_inicial | 0 | Beneficiarios en cola al abrir |
| Tiempo_cierre | 240 min | Fin del servicio |

## Consistencia Física
```
Tasa_Atencion = MIN(Capacidad_Biometrica * Personal, Cola_actual / TIME_STEP)
```
Evita negativos: no se atiende más de lo que hay en la cola.

## Límite de Cola
```
Cola_actual <= Beneficiarios (150)
```
La cola nunca puede superar el total de beneficiarios.

## Políticas Disponibles
1. **Logística**: `Tiempo_reposicion = 2` (stock seguridad)
2. **Tecnológica**: `Capacidad_Biometrica = 12` (doble biométrico)
3. **Social**: `Costo_etico = 0.9` (campañas ciudadanas)

## Lenguaje
- Código y comentarios en **español**
- Indentación: **2 espacios**
- Semicolons al final de statements