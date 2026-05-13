Son indicadores que suavizan la acción del precio para mostrar la tendencia en un número de periodos determinado.  
El periodo (ej. 20) corresponde al marco temporal del gráfico, salvo que se configure manualmente.

![[indicador_medias_moviles.png]]

---

## SMA – Media Móvil Simple

Calcula el promedio aritmético de los precios en un periodo determinado.  
Ejemplo con **20 días**:

SMA(20) = (P1 + P2 + ... + P20) / 20

---

## EMA – Media Móvil Exponencial

Da más peso a los precios recientes.  
Se calcula usando un factor de suavizado **k**:

EMA(t) = (Pt × k) + (EMA(t-1) × (1 - k))

donde:  
k = 2 / (n + 1)  
para n = 20 → k = 2 / 21 ≈ 0.095

---

👉 Diferencia clave: la **SMA** trata todos los precios por igual, mientras que la **EMA** reacciona más rápido a los cambios recientes.
