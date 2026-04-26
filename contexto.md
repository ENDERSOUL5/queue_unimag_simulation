# Caso de Estudio: Dinámica de Sistemas - Comedor Unimagdalena
**Estado del Documento:** Borrador Técnico V4.0 (Actualizado)
**Dominio:** Ingeniería de Sistemas / Dinámica de Sistemas
**Autor:** Senior System Architect (AI Assistant)

---

## 1. Descripción de la Problemática

El sistema de filas del comedor de la **Universidad del Magdalena** presenta un comportamiento oscilatorio amortiguado por límites físicos. La problemática reside en la interrupción del flujo de salida por el agotamiento del stock de platos, generando un **bloqueo de estado** en la entrada cuando se alcanza el número máximo de beneficiarios.

Además, el bloqueo recurrente genera una degradación del contrato social: erosión del costo ético (el usuario percibe que la norma de hacer fila no es útil) e inhibición del castigo social (la comunidad deja de reprochar al que se cuela). Este arquetipo "Soluciones contraproducentes" cierra un bucle de refuerzo donde la conducta disruptiva (colarse) emerge como respuesta adaptativa al fallo técnico del sistema.

### Parámetros Críticos (Inputs)
- **Beneficiarios:** 800 Estudiantes (Total con derecho a almuerzo).
- **Tasa_Llegada_base:** 9 est/min (Tasa base para distribución horaria).
- **Tasa_asistencia:** 0.8 (80% de beneficiarios asiste normalmente, variable para simulaciones).
- **Capacidad_Biometrica:** 5 est/min (Outflow bajo disponibilidad).
- **Capacidad_Manual:** 2 est/min (Outflow de respaldo cuando falla biométrico).
- **Tiempo_reposicion:** 5 Minutos (Latencia de la interrupción).
- **Stock_inicial:** 100 Platos.
- **Stock_Seguridad:** 10 Platos (Buffer para reducir tiempo de reposición).
- **Personal_presente:** 1 (Binario: 1 = hay personal, 0 = no hay).
- **Costo_etico:** 0.5 (Adimensional, 0 = nadie se avergüenza, 1 = todos se avergüenzan).
- **Factor_colado:** 0.5 (Peso de la frustración sobre los colados).
- **Tasa_falla_biometrica:** 0.1 (Probabilidad de fallo por minuto).
- **Factor_reduccion_frustracion:** 10.0 (Reducción de frustración por atención efectiva).
- **Factor_escala_frustracion:** 10.0 (Divisor para escalar frustración en colados).
- **Tasa_decaimiento_frustracion:** 0.1 (Decaimiento natural de la frustración, 10% por minuto).
- **Frustracion_maxima:** 1000.0 (Cap máximo para evitar explosión de frustración).
- **Tiempo_cierre:** 240 Minutos (Horario de cierre del comedor).
- **TIME_STEP:** 0.125 min (Intervalo de simulación para precisión en bloqueos).

### Distribución de Llegadas (Distribución por Tramos)
La tasa de llegada varía según la hora del día:
- **t < 30 min:** 20% de Tasa_Llegada_base (llegada lenta al abrir)
- **30 <= t < 60 min:** 70% de Tasa_Llegada_base (pre-pico)
- **60 <= t < 90 min:** 100% de Tasa_Llegada_base (pico máximo a las 12pm)
- **t >= 90 min:** 50% de Tasa_Llegada_base (va bajando después del pico)

Donde t = tiempo en minutos desde la apertura (0 = 11am).

---

## 2. Análisis de Profundización (Deep Dive): Lógica FSM + Comportamiento Emergente

Para resolver el "Deadlock Dinámico" (donde la cola se estanca), el modelo se implementó como una **Máquina de Estados Finitos (FSM)** integrada en un sistema de ecuaciones diferenciales, donde la conducta de colarse surge como comportamiento emergente del fallo técnico.

### Estados del Sistema
1. **Estado 1 (SERVING):** `Stock_comida > 0` y `Reposicion_activa = 0`. El sistema opera en régimen normal.
2. **Estado 2 (DEPLETED):** `Stock_comida <= 0`. Transición inmediata al modo de recuperación.
3. **Estado 3 (REPLENISHING):** `Reposicion_activa > 0`. La salida se bloquea (`Salida = 0`) y la entrada se corta al llegar a Beneficiarios para permitir el vaciado real posterior.
4. **Estado 4 (CERRADO):** `TIME >= Tiempo_cierre`. La entrada se corta (`Entrada = 0`), la cola se vacía completamente hasta 0.

### Arquetipo: Soluciones Contraproducentes
- (+) Demora -> (+) Frustración -> (+) Colados -> (+) Tiempo_fila
- El fallo técnico genera conducta disruptiva que agrava el problema original

---

## 3. Diagramas de Causalidad (Bucles)

### Bucle de Refuerzo (Caos):
```
Demora -> Frustración -> Colados -> +Demora
```
El empeoramiento del problema aumenta la frustración, lo que incrementa los colados, lo que vuelve a empeorar la demora.

### Bucle de Balance (Suministro):
```
Entrega -> Stock -> Necesidad de reposición
```
Cuando se entrega comida, el stock baja, lo que eventualmente requiere reposición.

### Bucle de Refuerzo (Fallo):
```
Falla biométrica -> Digitación manual -> Ausencia de personal -> Paro de flujo
```
Las fallas en el sistema biométrico generan trabajo adicional para procesar entradas manualmente, lo que puede llevar a ausencia de personal y eventualmente a un paro del servicio.

---

## 4. Arquitectura del Modelo (Python Puro con Integración Euler)

El modelo se implementa en **Python puro** usando integración Euler con `TIME_STEP = 0.125 min`. Esta aproximación es más simple y robusta para manejar las discontinuidades de la FSM que los solvers de paso variable.

### Stocks Principales
- **Cola_actual:** Beneficiarios esperando actualmente en la fila (máximo = Beneficiarios = 800)
- **Stock_comida:** Platos disponibles
- **Reposicion_activa:** Indicador de si hay proceso de reposición en curso (0 o 1 normalizado)
- **Frustracion:** Nivel acumulado de frustración por demoras (con cap máximo de 1000)
- **Total_atendidos:** Contador acumulado de personas atendidas

### Ecuación Principal de Stock
```python
dCola = (Tasa_Llegada + Tasa_Colados) - Tasa_Atencion
```

### Distribución de Llegadas
```python
def distribucion_llegadas(t):
    if t < 30:     factor = 0.2
    elif t < 60:   factor = 0.7
    elif t < 90:   factor = 1.0
    else:          factor = 0.5
    return Tasa_Llegada_base * factor * Tasa_asistencia
```

### Lógica de Control de Estados (FSM)
```python
if tiempo >= Tiempo_cierre:
    return CERRADO
if reposicion_activa > 0 or stock_comida <= 0:
    return REPLENISHING
return SERVING
```

### Flujo de Salida (Con Consistencia Física)
```python
Tasa_Atencion = MIN(Capacidad_Biometrica * Personal, Cola_actual / TIME_STEP)
```
Esto asegura que no se atienda más de lo que hay en la cola.

### Flujo de Colados (Con Límite Físico)
```python
tasa_colados = Costo_etico * (Frustracion / Factor_escala_frustracion) * Factor_colado
tasa_colados = MIN(tasa_colados, Cola_actual / TIME_STEP)
```
Los colados nunca pueden superar la población físicamente presente en la cola.

### Ecuación de Frustración (Con Decaimiento Natural y Cap)
```python
dFrustracion = Demora - (Tasa_Atencion * Factor_reduccion_frustracion) - (Frustracion * Tasa_decaimiento_frustracion)
if Frustracion >= Frustracion_maxima:
    dFrustracion = MIN(0, dFrustracion)
```
La frustración se calma con el tiempo (decaimiento del 10% por minuto) y tiene un cap máximo de 1000 para evitar explosión en escenarios extremos.

### Lógica de Cierre del Comedor
Cuando `TIME >= Tiempo_cierre`:
- La tasa de entrada base se vuelve 0
- Los colados también cesan (no hay a quien colarse)
- La cola continúa vaciándose a través de la salida normal hasta llegar a 0
- El modelo termina la simulación con la cola completamente vacía

### Lógica de Falla Biométrica
```python
Falla_actual = IF THEN ELSE(RANDOM() < Tasa_falla_biometrica, 1, 0)
Personal_activo = MAX(0, Personal - Falla_actual)
```

---

## 5. Pruebas de Consistencia

### Consistencia Dimensional
- Todas las tasas se miden en `estudiantes/minuto`
- Los stocks se miden en `estudiantes`
- `Cola_actual / TIME_STEP` da `estudiantes/min` ✓

### Consistencia Física (Evitar Negativos)
```python
Tasa_Atencion = MIN(Capacidad_Biometrica * Personal, Cola_actual / TIME_STEP)
```
Esto asegura que no se atienda más de lo que hay en la cola.

### Pruebas de Robustez
El modelo ha sido sometido a pruebas de condiciones extremas:
- **Llegada masiva (100 est/min):** La cola satura en el límite de beneficiarios sin errores matemáticos
- **Sin personal (Capacidad = 0):** La cola crece hasta el máximo, stock no se consume, sin división por cero
- **Sensibilidad de Costo Ético:** Variaciones en el costo ético muestran impacto significativo en la tasa de colados

---

## 6. Escenarios y Políticas

### Escenario A (Normal): Flujo estándar de estudiantes.
Parámetros base: Beneficiarios = 800, Tasa_Llegada_base = 9, Tasa_asistencia = 0.8

### Escenario B (Crítico): Semana de parciales con mayor afluencia
- Tasa_Llegada_base = 20 est/min
- Tasa_asistencia = 0.95

### Política 1 (Logística): Stock de seguridad
- Reduce tiempo de reposición de 5 a 2 minutos
- Implementación: `Tiempo_reposicion = 2`
- Impacto esperado: Menos tiempo bloqueado, colas más cortas

### Política 2 (Tecnológica): Doble biométrico
- Duplica la capacidad biométrica
- Implementación: `Capacidad_Biometrica = 10`
- Impacto esperado: Vaciamiento de cola el doble de rápido

### Política 3 (Social): Campañas de cultura ciudadana
- Aumenta el costo ético (más gente se cohíbe de colarse)
- Implementación: `Costo_etico = 0.9`
- Impacto esperado: Menos colados, flujo más ordenado

### Política 4 (Logística + Tecnológica): Combinación P1 + P2
- Reposición rápida + mayor capacidad de atención
- Implementación: `Tiempo_reposicion = 2` y `Capacidad_Biometrica = 10`

### Política 5 (Integral): Combinación P1 + P2 + P3
- Reposición rápida + mayor capacidad + cultura ciudadana
- Implementación: `Tiempo_reposicion = 2`, `Capacidad_Biometrica = 10`, `Costo_etico = 0.9`

---

## 7. Referencias

1. Hidayana, R. A., & Yohandoko, S. L. O. (2024). Analysis of queueing systems in fast food restaurants using the M/M/c model.
2. Mandlhate, M., et al. (2025). O impacto dos gargalos na eficiência de distribuição de refeições em restaurantes universitários.
3. Meadows, D. H. (2008). Thinking in Systems: A Primer.
4. Prieto, S. (2026). Notas de Clase: Dinámica de Sistemas e Ingeniería de Sistemas. Universidad del Magdalena.
5. Sterman, J. D. (2000). Business Dynamics: Systems Thinking and Modeling for a Complex World.
6. Zhu, J., et al. (2025). Neural architecture of social punishment: Insights from a queue-jumping scenario.
7. Wang, C., et al. (2026). Towards a more resilient and cost-efficient fresh agri-food supply chain.
