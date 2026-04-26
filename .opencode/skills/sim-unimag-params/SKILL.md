---
name: sim-unimag-params
description: Reglas de parametrizacion para el proyecto de simulacion del Comedor Unimagdalena. Garantiza que todos los parametros numericos del modelo vivan en src/parametros.py y no haya valores hardcodeados en la logica ni las graficas.
---

# Skill: Parametrizacion - Comedor Unimagdalena

## Contexto
Este es un modelo de Dinamica de Sistemas para el comedor de la Universidad del Magdalena, escrito en Python puro con integracion Euler.

## Reglas de Oro

### 1. Fuente autoritativa de parametros
- `src/parametros.py` es el **unico** lugar donde deben definirse constantes numericas, tasas, factores, umbrales y parametros de escala del modelo.
- Si un valor numerico aparece en cualquier otro archivo (`src/modelos.py`, `src/simulacion.py`, `src/graficar.py`, scripts auxiliares), **debe provenir** del diccionario `PARAMETROS` importado desde `src.parametros`.

### 2. Prohibicion absoluta de hardcodes
- **NUNCA** escribir valores literales como `150`, `10.0`, `50`, `300`, `0.125`, `240`, `0.2`, `0.7`, `1.0`, `0.5`, `10.0` (escala de frustracion), etc., directamente en la logica del modelo o en las graficas.
- **NUNCA** usar `frustracion / 10.0`, `factor = 0.2`, `y = 50` ni ninguna constante magica. Todo debe leerse de `PARAMETROS`.

### 3. Patron obligatorio
- Siempre importar: `from .parametros import PARAMETROS` (o `from src.parametros import PARAMETROS` en scripts de raiz).
- Acceder a los valores asi: `p = PARAMETROS; valor = p["Clave"];`
- En f-strings de graficas: `f'Etiqueta ({PARAMETROS["Clave"]})'`

### 4. Parametro no existe? Agregarlo primero
- Si necesitas un nuevo factor, divisor o constante, **primero** anadelo al diccionario `PARAMETROS` en `src/parametros.py` con un nombre descriptivo.
- Luego, y solo entonces, usalo en la logica.

### 5. Graficas sin valores fijos
- Las lineas de referencia (`ax.axhline`, `ax.axvline`, `ax.axhspan`) deben usar `PARAMETROS["..."]` en lugar de numeros literales.
- Ejemplo correcto:
  ```python
  ax.axhline(y=PARAMETROS["Beneficiarios"], color="red", linestyle="--",
             label=f'Beneficiarios ({PARAMETROS["Beneficiarios"]})');
  ax.axhline(y=PARAMETROS["Stock_inicial"], color="blue", linestyle=":",
             label=f'Stock inicial ({PARAMETROS["Stock_inicial"]})');
  ```

### 6. Escalas magicas parametrizadas
- Cualquier divisor o factor de escala (ej. `frustracion / 10.0`, `cola / 100`) debe parametrizarse como:
  ```python
  "Factor_escala_frustracion": 10.0,
  ```
- Y usarse asi: `frustracion / p["Factor_escala_frustracion"]`

### 7. Estilo del proyecto
- Codigo y comentarios en **espanol**.
- Indentacion: **2 espacios**.
- Punto y coma (`;`) al final de cada statement.

### 8. Pipeline principal vs scripts alternativos
- El **pipeline principal** es: `main.py` -> `src/parametros.py` -> `src/modelos.py` -> `src/simulacion.py` -> `src/graficar.py`.
- No crear ni mantener scripts alternativos con logica duplicada ni con sus propios diccionarios de parametros.
- Si un script auxiliar (ej. `analizar_datos.py`) necesita leer parametros, debe importarlos desde `src.parametros`.

## Verificacion antes de entregar cambios
Antes de considerar una tarea terminada, revisar que:
1. No haya numeros literales en la logica nueva (buscar `[0-9]+\.[0-9]+` o valores enteros sospechosos).
2. Todo parametro nuevo este en `src/parametros.py`.
3. Las graficas usen `PARAMETROS` para lineas de referencia.
