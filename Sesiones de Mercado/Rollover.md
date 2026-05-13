
El **rollover** es el momento en el que el mercado Forex:

- Cierra el **día contable**
- Aplica o cobra el **swap** (intereses por mantener posiciones abiertas)
- Transiciona del día actual al siguiente

📌 **Referencia fija del mercado:**

> El rollover ocurre a las **17:00 hora de Nueva York (NY)**.

Este horario **no cambia nunca**. Lo que cambia es cómo se ve desde otros países.

---

## 2️⃣ ¿Qué pasa en el mercado durante el rollover?

Alrededor del rollover suelen ocurrir estas cosas:

- 🔴 **Fuerte expansión del spread**
- 🔴 **Baja liquidez**
- 🔴 Movimientos erráticos
- 🔴 Stops barridos aunque el precio no haya llegado "realmente"

Esto sucede porque:

- Europa ya cerró
- EE. UU. termina su día
- Asia recién empieza (Sídney abre, pero con poca participación)

A este período se lo suele llamar:

> **"Dead zone del rollover"**

---

## 3️⃣ Rollover y [[DST]]

Argentina **NO usa DST**, por lo que mantiene **GMT-3 todo el año**.

👉 Cuando EE. UU. cambia su horario, el rollover se ve **una hora antes o después** en Argentina.

---

## 4️⃣ Horario del rollover en Argentina

### 🔴 EE. UU. **sin DST** (aprox. noviembre → marzo)

- Nueva York: GMT-5
- Argentina: GMT-3
- Diferencia: **2 horas**

👉 **Rollover en Argentina: 19:00 hs**

---

### 🟢 EE. UU. **con DST** (aprox. marzo → noviembre)

- Nueva York: GMT-4
- Argentina: GMT-3
- Diferencia: **1 hora**

👉 **Rollover en Argentina: 18:00 hs**

---

## 5️⃣ Ventana crítica del spread

El spread **no salta instantáneamente**. La expansión y normalización siguen un patrón observable:

### 📊 Observación real (Enero 2025)

**Timeline del comportamiento del spread:**

- **18:35 hs** → Los spreads empezaron a aumentar masivamente
- **19:00 hs** → Rollover oficial (17:00 NY)
- **20:00 hs** → Spreads mejoraron, pero seguían altos
- **20:05 hs** → Spreads completamente normalizados

**Conclusión:** La ventana crítica real duró aproximadamente **1 hora y 35 minutos** (18:35 - 20:10).

---

### Regla práctica (Argentina)

| Estado de EE. UU. | Rollover oficial | Inicio expansión | Normalización completa | Ventana total de riesgo |
| ----------------- | ---------------- | ---------------- | ---------------------- | ----------------------- |
| Sin DST           | 19:00            | ~18:30           | ~20:30                 | 18:30 – 20:30 (2h)      |
| Con DST           | 18:00            | ~17:30           | ~19:30                 | 17:30 – 19:30 (2h)      |

⚠️ **Nota importante:** Estos horarios pueden variar ligeramente según:

- El broker
- La liquidez del día específico
- El par que estés operando

---

## 6️⃣ Ejemplos reales de expansión del spread

Las siguientes capturas muestran el **comportamiento real del spread** antes y después del rollover:

### 📊 Antes del rollover

![[spreads_pre_rollover.png]]

Esta captura muestra los spreads durante un horario de **liquidez normal**, antes de que comience la ventana crítica del rollover. Los valores son los típicos que verías durante las sesiones de Londres o Nueva York.

---

### 📊 Después del rollover

![[spread_post_rollover.png]]

Esta segunda captura fue tomada **después del pico de expansión**, mostrando spreads que ya están normalizándose o completamente normalizados.

---

### ⚠️ Implicaciones prácticas

**Ejemplo con EURUSD:**

Si tu SL técnico está a:

- **20 pips** del precio actual (200 puntos)
- Spread normal: **2.6 pips** (26 puntos)
- Durante el rollover el spread salta a: **15 pips** (150 puntos)

**Tu SL puede ejecutarse sin que el precio "real" lo toque**, porque el Ask o Bid se desplazaron por la expansión del spread, no por movimiento genuino del mercado.

Por eso el colchón de rollover es crítico: no es una protección contra el movimiento del precio, sino contra **la expansión temporal del spread**.

---

## 7️⃣ Consideraciones antes de decidir mantener una operación abierta

Antes del rollover preguntate:

- ¿El trade está **muy cerca del SL**?
- ¿El SL está en **break-even** o con poco margen?
- ¿El setup es de **swing / intradía extendido**?
- ¿El swap afecta significativamente mi ganancia potencial?
- ¿Mi SL tiene suficiente **colchón** para sobrevivir la expansión del spread?

Si el SL está muy ajustado, el riesgo principal es **el spread**, no el precio.

---

## 8️⃣ Uso de MT5 + Position Sizer para gestionar el rollover

### 🔹 Concepto clave

- MT5 calcula el riesgo en **puntos**, no en pips
- El Position Sizer muestra:
    - Puntos
    - Pips (indirectamente)
    - USD de riesgo

📌 En la mayoría de pares Forex modernos:

- **1 pip = 10 puntos** (pares con 5 o 3 decimales)

**Ejemplo práctico:**

- Si tu SL está a 162 puntos = 16.2 pips
- Un colchón de 250 puntos = 25 pips adicionales
- SL temporal: 412 puntos = 41.2 pips

---

## 9️⃣ Estrategia práctica: colchón de rollover

### Paso 1 – Identificar el SL técnico

Ejemplo:

- SL técnico: **-162 puntos** (≈ 16.2 pips)
- Riesgo: **$100 USD**

---

### Paso 2 – Definir el colchón según el par

El colchón debe ajustarse a la **liquidez del par**:

|Tipo de par|Ejemplos|Colchón sugerido|
|---|---|---|
|Mayores (alta liquidez)|EURUSD, GBPUSD, USDJPY|200-250 puntos (20-25 pips)|
|Menores|AUDUSD, NZDUSD, USDCAD|250-300 puntos (25-30 pips)|
|Exóticos/Cruzados|AUDNZD, NZDJPY, EURAUD|300-350 puntos (30-35 pips)|

**Criterios adicionales:**

- Si tu SL ya tiene **respiración técnica** (no está pegado a un nivel exacto): colchón menor
- Si tu SL está **muy ajustado** (breakeven, nivel clave preciso): colchón mayor
- En días de **alta volatilidad** (datos macro, noticias): considerar aumentar el colchón 20-30%

**Colchón estándar recomendado: 250 puntos (25 pips)**

---

### Paso 3 – Ajustar SL temporalmente

Ejemplo con **EURUSD** (par mayor):

```
SL técnico = 162 puntos
Colchón rollover = 250 puntos
SL temporal = 162 + 250 = 412 puntos
```

Mientras arrastrás el SL en MT5:

- Mirás los **puntos** (412)
- Confirmás el **USD adicional de riesgo** (por ejemplo, pasa de $100 a $254)
- Anotás mentalmente: "Vuelvo a 162 puntos después del rollover"

**No necesitás calcular el valor del pip** - el Position Sizer ya lo hace por vos.

---

## 🔟 ¿Cuándo mover y cuándo volver a ajustar?

### 🔁 Días de semana

**Timeline basado en observación real (horario actual Argentina - EE. UU. sin DST):**

- 🟡 **18:25 hs** → Ampliar SL con colchón de 250 puntos
- 🔴 **18:35 - 20:10 hs** → VENTANA CRÍTICA - no tocar nada
- 🟢 **20:15 hs** → Verificar normalización del spread visualmente
- 🟢 **20:25 hs** → Reajustar SL al nivel técnico original

**Cuando EE. UU. tenga DST (horario de verano) - ver [[DST]]:**

```
17:15 hs → Ampliar SL con colchón
17:35 - 19:10 hs → VENTANA CRÍTICA - no tocar nada
19:15 hs → Verificar normalización
19:20 hs → Reajustar SL al nivel técnico
```

⚠️ **Regla de oro:** Siempre esperá **al menos 10 minutos** después de que veas los spreads normalizados antes de reajustar tu SL. Mejor pecar de precavido.

> Nota: con DST restar 1 hora los pasos anteriores

---

### 🔁 Fin de semana

- **Viernes:** mismo criterio que un día normal
    - Considerar si vale la pena mantener la posición por el swap de triple día (miércoles a jueves generalmente)
- **Domingo:**
    - Esperar apertura de Sídney (alrededor de 22:00 hs Argentina, sin DST)
    - Esperar **30-60 minutos** de estabilización del mercado
    - Verificar que los spreads estén normalizados
    - **Solo entonces** reajustar SL al nivel técnico

⚠️ La apertura del domingo suele tener **gaps** (saltos de precio). Si tu posición abrió el viernes, revisa primero si el precio gapeó cerca de tu SL antes de hacer ajustes.
