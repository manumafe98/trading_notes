
La **Manipulación de Liquidez** se basa en la misma lógica que el resto de modelos de liquidez:

- El precio busca liquidez
- La liquida
- Y reacciona a partir de ese punto

> La diferencia con la manipulación del rango asiático **no está en la lógica**, sino en que aquí **no dependemos necesariamente del rango asiático**.

Este modelo se utiliza cuando la manipulación:

- Se produce **fuera del rango asiático**
- O ataca **puntos de liquidez concretos del gráfico**

---

## Horarios operativos

Este modelo se trabaja **únicamente** en los horarios de mayor actividad institucional:

- **14:00 – 17:00 (hora España)** Apertura de Nueva York

Es en estas franjas cuando:

- Aumenta el volumen
- Se producen los movimientos relevantes
- Aparecen las manipulaciones de liquidez

> Fuera de estos horarios, **no se opera este modelo**.

---

## Lógica del modelo

Lo que buscamos es **que el precio liquide un punto importante del gráfico**.

No trabajamos rangos concretos. No trabajamos patrones aislados. Trabajamos **barridos de liquidez claros**.

El proceso es siempre el mismo:

1. El precio se dirige a un punto relevante
2. Liquida la liquidez acumulada
3. Esperamos confirmación
4. Ejecutamos la entrada

---

## Puntos de liquidez que tenemos en cuenta

Los puntos de liquidez que tenemos en cuenta para la estrategia se explican en [[Jerarquías de Liquidez]]

---

## Tipo de entrada del modelo

### Nasdaq

- [[Inverse Fair Value Gap|iFVG]] en temporalidad de 5/3 o 1 minuto
- [[Balanced Price Range|BPR]]
- Rotura de estructura y [[Fair Value Gap|FVG]] 

> Para la entrada de iFVG entramos a mercado con confirmación de ruptura del mismo o en Limit en retesteo

---

## Dirección del trade

- No seguimos la tendencia por sí sola
- No operamos por sesgo macro

> **Nos guiamos por la liquidez que el precio está atacando.**

La dirección del trade debe tener sentido en función de:

- El punto de liquidez que se liquida
- El horario en el que ocurre
- La reacción del precio tras esa liquidez

---

## Reglas generales del modelo

### ✅ Hacer

- Operar solo en horarios válidos
- Trabajar con puntos de liquidez claros
- Esperar confirmación del precio
- Ejecutar solo tras la manipulación

### ❌ No hacer

- No anticipar entradas
- No operar fuera de horario
- No forzar trades sin liquidez clara
