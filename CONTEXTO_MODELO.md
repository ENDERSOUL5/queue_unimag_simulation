# Contexto del Modelo - Comedor Unimagdalena
**Fecha:** 24 Abril 2026
**Estado:** En desarrollo - Problema de lógica REPLENISHING sin resolver

---

## Descripción del Problema Real

Un comedor universitario donde:
1. Estudiantes hacen fila para almorzar
2. Hay un stock de comida (50 platos inicialmente)
3. Cuando se agota la comida, se detiene la atención por 10 minutos (reposición)
4. Durante la reposición, la fila sigue creciendo (nadie puede ser atendido)
5. Después de los 10 minutos, la comida se recarga y la atención vuelve a funcionar

---

## Variables Principales

| Variable | Descripción |
|----------|-------------|
| Cola_actual | Estudiantes esperando en la fila |
| Stock_comida | Platos disponibles |
| Beneficiarios | Total de estudiantes con derecho (150) |
| Total_atendidos | Estudiantes que ya recibieron almuerzo |
| Reposicion_activa | Flag que indica si hay reposición en curso (0=no, >0=sí) |
| Tiempo_reposicion | Duración de la reposición (10 min) |
| Capacidad_Biometrica | Personas atendidas por minuto (6 est/min) |
| TIME_STEP | Intervalo de simulación (0.125 min) |

---

## Estados del Sistema (FSM)

1. **SERVING**: Operation normal - hay comida y se atiende
2. **REPLENISHING**: Stock agotado - nadie es atendido, se espera reposición
3. **CERRADO**: El comedor cierra a los 240 minutos

---

## Flujos

```
dCola/dt = Tasa_llegada + Tasa_colados - Tasa_atencion
dStock/dt = Llegada_comida - Tasa_atencion
dReposicion/dt = Inicia cuando stock<=0, decrementa durante Tiempo_reposicion
dAtendidos/dt = Tasa_atencion (cuando se atiende)
```

---

## Problema Identificado

### El problema
Cuando `Stock_comida` llega a 0, el sistema debería:
1. Entrar en estado REPLENISHING
2. Bloquear atención (tasa_atencion = 0)
3. Mantener stock = 0 durante 10 minutos
4. Al terminar los 10 min, recargar stock = 50
5. Volver a SERVING y retomar atención

### Lo que está pasando actualmente
El stock se recarga sin entrar en REPLENISHING, o el tiempo de reposición es incorrecto.

**Observación del usuario:**
```
t=20.000  Cola=0.300  Stock=2.300   SERVING   ← Stock bajo de 2.3
t=22.500  Cola=1.650  Stock=47.750  SERVING   ← Stock subió a 47.75 SIN entrar REPLENISHING
```

---

## Archivos Principales

- `/home/endersoul/sim_unimag/src/modelos.py` - Ecuaciones y lógica FSM
- `/home/endersoul/sim_unimag/src/simulacion.py` - Integración Euler
- `/home/endersoul/sim_unimag/src/parametros.py` - Parámetros configurables
- `/home/endersoul/sim_unimag/analizar_datos.py` - Script para analizar resultados
- `/home/endersoul/sim_unimag/debug_stock.py` - Debug en detalle

---

## Historial de Intentos de Corrección

### Intento 1
- Cambiar `dReposicion = -1.0` a `dReposicion = -1.0 / Tiempo_reposicion`
- Resultado: No cambió el comportamiento

### Intento 2
- Modificar `obtener_estado()` para incluir `stock_comida <= 0` como condición de REPLENISHING
- Resultado: Causó parpadeo entre estados

### Intento 3
- En `calcular_flux()` poner `llegada_comida = 0` en REPLENISHING
- Resultado: Stock se mantiene en 0 pero no entra en REPLENISHING

### Intento 4
- Recargar stock con condición: `if y[2] <= 0 and y[1] <= 0: y[1] = Stock_inicial`
- Resultado: Stock se recarga pero sin pasar por REPLENISHING

---

## Recomendación para Nueva Sesión

Empezar con lógica simplificada:
1. Cuando stock <= 0, iniciar REPLENISHING directamente
2. REPLENISHING dura exactamente Tiempo_reposicion pasos
3. Durante REPLENISHING: stock = 0, tasa_atencion = 0
4. Al terminar REPLENISHING: stock = Stock_inicial, retomar atención

Verificar con datos simples primero antes de agregar complejidad.