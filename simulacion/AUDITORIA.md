# Auditoría de la petición — «Quiero hacer una simulación en 2D»

**Petición textual:** *«…haz un subdirectorio donde tengas los archivos para la petición siguiente:
Quiero hacer una simulación en 2d … para ver las cargas en acción, movimiento lateral, etc.
Audita mi petición y haz preguntas.»*

Este documento hace tres cosas, en este orden: **(1)** traduce la petición a un problema de
ingeniería concreto, **(2)** audita los datos de entrada contra la norma y el cuaderno de cálculo,
y **(3)** declara las hipótesis, los resultados ya obtenidos y **las decisiones que faltan**
(preguntas al final, §9). El visor `index.html` que acompaña este documento es un **prototipo
del nivel A** (estático animado) construido con el mismo solver auditado.

> **Alcance entregado:** un pórtico transversal (uno de los 7 iguales) resuelto como modelo de
> barras 2D por rigidez directa, con 5 casos: servicio, rotura 1,2D+1,6L, sismo R = 6, sismo R = 2
> y rotura **sin tirante**, más el **nivel dinámico** (`dinamica.py`: masas sísmicas, autovalores,
> período fundamental `T₁`, modo de vibración, espectro de diseño evaluado en `T₁` y oscilación en
> el tiempo). El sismo estático usa las fuerzas laterales del cuaderno (`V_col` por pilar) y el
> dinámico el modo fundamental de la estructura real; los dos quedan comparados en el visor.
> El nivel C (los 7 pórticos en 3D) queda descartado por decisión del usuario (§9).

---

## 1. Qué significa «simulación 2D para ver las cargas en acción»

La petición se descompone en cuatro capacidades verificables:

| # | Lo que se quiere ver | Traducción técnica | ¿Se puede hoy con los datos del proyecto? |
|---|----------------------|--------------------|-------------------------------------------|
| 1 | Las **cargas en acción** (aplicación paso a paso) | fuerzas nodales del caso de carga, dibujadas sobre la geometría | **Sí** — las cargas salen del cuaderno (`q_techo`, `q_pas`, `V_col`) |
| 2 | El **movimiento lateral** (deformada) | desplazamientos nodales `u`, `v`, `θ` del sistema `K·d = F` | **Sí** — es el resultado central del solver |
| 3 | El **estado interno** (axiales, momentos, D/C) | esfuerzos de extremo de barra por `k·d − f` en coordenadas locales | **Sí** |
| 4 | El **comportamiento en el tiempo** (vibración sísmica) | análisis modal: `T₁`, modo, espectro de diseño, oscilación | **Sí** — `dinamica.py` (masas sísmicas, Jacobi con condensación de giros, espectro evaluado en `T₁`) |

Lo que la petición **no** puede cubrir y conviene decir desde el principio: una simulación 2D de un
pórtico no reproduce torsión de la planta, ni el diafragma de cubierta, ni el sismo en la dirección
longitudinal (esa dirección la toman los arriostramientos HEB 200), ni la interacción con el suelo.
Está listado con detalle en §5.

## 2. Auditoría de los datos de entrada

### 2.1 Lo que ya existe (cuaderno `cuaderno/calculos.py`, 13 bloques)

Geometría: `L = 17,60 m`, `h = 8,50 m` (pilar en ménsula), flecha del arco `f = 2,50 m`,
doble cordón separado `d = 0,80 m`, ángulo de arranque `θ = 63,437°`, longitud de arco
`L_arco = 18,532 m`, separación entre pórticos `S = 4,10 m`, 7 pórticos iguales.

Cargas y materiales: `D = 23,0 kg/m²` (lámina 5,5 + correas 7,5 + cielo raso 10,0),
`L = 100 kg/m²` (público, COVENIN 2002), cargas colgadas 15,0 kg/m², peso propio de planilla
`35 + 25 = 60 kg/m`; `q_serv = 625,8 kg/m`, `q_u = 914,96 kg/m` por pórtico;
`E = 2,1·10⁶ kg/cm²`, `Fy = 2 530 kg/cm²`.

Sismo (COVENIN 1756‑1:2019 §7, nivel de diseño ND3): `AA = 0,345`, `AV = 0,669`,
`TC = 0,809 s`, `Ta = 0,44 s`, `φ = 0,9625`, `C = φ·Ad`, `Ad = 2,4·AA/R`,
`Cd = 4,25` (§9.4), `R = 6` (planilla original) y `R = 2` (Tipo IV, §3.5.4),
`W = 54,59 t` para los 7 pórticos (`W_pórtico = 7,80 t`), `V_col = 0,518 t` (R = 6) y
`1,554 t` (R = 2) por pilar, `δ_lim = 0,020·h = 17,0 cm`.

Comprobaciones: 28 filas D/C (26 cumplen / 2 no).

### 2.2 Peso propio real — el hallazgo más importante de la auditoría

La planilla usa `pp_cercha = 35 kg/m` y `pp_pasarela = 25 kg/m`. Con los perfiles del plano
(2×IPE 160 en los dos cordones, IPE 160 en las diagonales en X, IPE 120 en los montantes)
el peso propio **calculado** de la cercha es:

| Grupo | Barras | kg |
|-------|--------|----|
| Cordones 2×IPE 160 | 16 | 1 173,6 |
| Diagonales IPE 160 | 16 | 621,1 |
| Montantes IPE 120 | 9 | 80,2 |
| Tirante Ø1-1/2″ | 1 | 157,5 |
| **Cercha (sin pasarela)** | **42** | **2 032,4 kg** |
| ÷ longitud de arco 18,532 m | | **109,7 kg/m** |

Sumando la pasarela (25 kg/m) el peso propio real es **134,7 kg/m contra 60 kg/m de la planilla:
2,24 veces (+124 %)**. Consecuencias cuantificadas en el modelo 2D: la carga de servicio pasa de
625,8 a **719 kg/m** (+15 %), la de rotura de 915 a **1 010 kg/m** (+10 %), la flecha por peso
propio del arco crece 18 % y el **peso sísmico** pasa de 7,80 a **10,81 t por pórtico** (+39 %).
El rótulo del cuaderno ya fue corregido en el commit `b04f6fc`; **queda pendiente decidir si se
recalcula la planilla completa con el PP real** (§9, pregunta 4).

### 2.3 Datos que faltan (no están en el expediente)

| Falta | Por qué importa en la simulación | Cómo se puede suplir |
|-------|----------------------------------|----------------------|
| Estudio de mecánica de suelos (EMS) | rigidez y amortiguamiento del suelo: hoy el modelo supone **apoyo empotrado** en la base | hipótesis declaradas (σ_adm = 1,5 kg/cm², NF = 1,50 m) y análisis de sensibilidad |
| Detalle real de las conexiones (nudos con cartelas soldadas) | el modelo supone cordones continuos (nudo rígido) y diagonales articuladas | comparar con el caso «todo articulado» (envolvente) |
| Detalle de la placa base y anclajes | el empotramiento perfecto es una idealización; la rigidez real es finita | ya existe el cálculo de placa/pernos del cuaderno |
| Posición real de la pasarela | ¿cuelga del cordón inferior en todo el ancho? ¿tiene barandas? | confirmar con el plano (hoy: 25 kg/m colgando del cordón inferior) |
| Masas no estructurales (cielo raso, instalaciones, luces) | entran en el peso sísmico `W` | ya contabilizadas como `D` |

## 3. Modelo 2D adoptado (hipótesis declaradas)

### 3.1 Geometría y elementos

22 nudos, **44 barras**: 2 pilares HEB 300 (8,50 m), 16 segmentos de cordón 2×IPE 160
(extradós en arco de circunferencia, intradós a distancia constante `d = 0,80 m`),
16 diagonales IPE 160 en X (San Andrés), 9 montantes IPE 120 y 1 tirante Ø1-1/2″.
Las coordenadas de la cercha se generan con **el mismo ángulo por panel** que usó el cuaderno
(9 nudos por cordón), no con una parábola ideal: la geometría del diseño no es funicular, y eso
es precisamente lo que produce los momentos flectores en los cordones.

### 3.2 Vínculos

* Base de los pilares: **empotrada** (3 GDL restringidos en cada uno).
* Apoyo del arco sobre la cabeza del pilar: **articulación** — comparten `u` y `v`, con giro
  libre. Es lo declarado en el chat del proyecto (§3.5.4: «columnas en voladizo con arco articulado»).
* Tirante: barra articulada en sus dos extremos; se comprueba que trabaje **sólo a tracción**
  (si en un caso aparece comprimido, se repite el análisis sin él).

### 3.3 Cargas

Cargas verticales nodales por área tributaria **real** de cada nudo (mitad de panel a cada lado,
medida sobre la proyección horizontal de 17,60 m), aplicadas en los nudos del cordón superior
(`q_techo`) y del inferior (`q_pas`). El peso propio de cada barra se reparte 50/50 entre sus dos
nudos (en las bielas y en los cordones) o como viga biempotrada si la barra es un pilar.
Sísmicas: `V_col` horizontal aplicada en las dos cabezas de pilar, ambas **en el mismo sentido**
(es un pórtico, no un par de fuerzas).

### 3.4 Casos analizados

| Caso | Combinación | Tirante |
|------|-------------|---------|
| `servicio` | D + L | sí |
| `mayorada` | 1,2D + 1,6L (con el PP real mayorado) | sí |
| `sismo_R6` | 1,2D + 0,5L + S (R = 6) | sí |
| `sismo_R2` | 1,2D + 0,5L + S (R = 2, Tipo IV) | sí |
| `sin_tirante` | 1,2D + 1,6L, sin el tirante de cabeza | no |

### 3.5 Lo que el modelo **no** incluye

1. **Torsión y diafragma de cubierta**: el pórtico es 2D; que las 7 cerchas se muevan igual es una
   hipótesis, no un resultado.
2. **Dirección longitudinal**: la toman los arriostramientos HEB 200 en los vanos 2–5 (fuera de este modelo).
3. **No linealidad**: análisis lineal elástico. No hay P‑Δ (efecto de segundo orden), ni
   plastificación, ni pandeo local, ni abolladura; el pandeo de barras **sí** se comprueba en el D/C
   con las capacidades del cuaderno (`φPn`).
4. **Suelo**: base empotrada; no hay asentamientos diferenciales ni rigidez de fundación.
5. **Viento**: excluido por indicación del profesor.
6. **Estado tensional inicial** (montaje, temperatura, descimbrado).

---

## 4. Verificación del programa (por qué se puede confiar en los números)

Antes de usar el solver sobre la estructura real se resolvieron cuatro problemas con solución
cerrada y una comprobación mecánica independiente del empuje:

| Prueba | Cerrado | Solver | Error |
|--------|---------|--------|-------|
| Columna en voladizo, `Δ = P·h³/(3EI)` | 2,00576 cm | 2,00576 cm | 0,00 % |
| Viga apoyada, `δ = 5wL⁴/(384EI)` | 0,87051 cm | 0,87051 cm | 0,00 % |
| Arco funicular con tirante, `T = qL²/(8f)` | 13 520,4 kg | 13 520,4 kg | 0,00 % |
| Equilibrio vertical, `ΣR = ΣF` | 20 189,6 kg | 20 189,6 kg | 0,00 % |

**Comprobación independiente del empuje (analogía de resortes en serie).** Para el arco biarticulado:
empuje con arranques fijos `H₀ = 17 883 kg`, rigidez de aplanamiento del arco `k_a = 12 473 kg/cm`,
rigidez de los dos pilares `k_p = 258,2 kg/cm`, rigidez del tirante `k_t = EA/L` para el alargamiento
total `= 27 205 kg/cm`. Entonces:

* sin tirante, el empuje se limita por el desplazamiento de las cabezas:
  `H = H₀·k_p/(k_a + k_p) = 362,69 kg` → **el solver da 362,6897 kg**;
* con tirante: `T = H₀·k_t/(k_a + k_t + k_p) = 12 181,85 kg` → **el solver da 12 181,85 kg**.

La coincidencia es de 6 a 8 cifras significativas con un procedimiento que no comparte código con el
solver: eso descarta errores de armado de la matriz o de interpretación de los vínculos.

---

## 5. Resultados de la auditoría (lo que encontró el modelo)

### 5.1 Los 5 casos (un pórtico de los 7)

| Caso | T tirante | H en el pilar | M base pilar | Δ lateral | Cd·Δ (lím 17 cm) | D/C máx |
|------|-----------|---------------|--------------|-----------|------------------|---------|
| Servicio D+L | 8,48 t | 0,08 t | 0,68 t·m | 0,31 cm (aplanamiento del arco, no sismo) | — | 0,337 |
| Rotura 1,2D+1,6L | **12,18 t** | 0,12 t | 0,98 t·m | 0,45 cm (aplanamiento) | — | 0,485 |
| Sismo R = 6 | 6,68 t | 0,46 t | 3,86 t·m | **2,006 cm** | **8,52 cm ✓** | 0,266 |
| Sismo R = 2 | 6,68 t | 1,49 t | 12,67 t·m | **6,017 cm** | **25,57 cm ✗** | 0,353 |
| Rotura sin tirante | — | 0,36 t | 3,08 t·m | 1,40 cm (aplanamiento) | — | **1,106 ✗** (cordón) |

En los casos sísmicos la deriva que se compara es la del campo **sólo lateral** (`Fh`), porque el
campo gravitatorio ya desplaza las cabezas hacia afuera: el arco se aplana y separa las dos cabezas
**±0,245 cm** (0,49 cm entre ambas) tomando el empuje el tirante. El desplazamiento *neto* de la
cabeza izquierda en el sismo R = 6 es por eso 1,760 cm (los 2,006 hacia +x menos los 0,245 del
aplanamiento inicial) y el de la derecha 2,251 cm. Mezclar los dos campos subestimaría la deriva.

### 5.2 Modelo 2D contra cuaderno (D/C del mismo criterio)

| Elemento | Cuaderno | Modelo 2D | Lectura |
|----------|----------|-----------|---------|
| Tirante Ø1-1/2″ | 0,546 (T_u = 14,17 t) | **0,469** (12,18 t) | el cuaderno queda del lado seguro (el tirante toma también parte del empuje del peso propio) |
| Cordón 2×IPE 160 | 0,725 (N = 29,52 t) | **0,485** (19,74 t) | el modelo de viga biempotrada del cuaderno es conservador |
| Diagonal IPE 160 | 0,667 (S = 12,33 t) | **0,191** (3,54 t) | el cuaderno **no descontó** `H·senφ`; la fórmula correcta es `S = R·cosφ − H·senφ` = 2,18 → 3,34 t |
| Montante IPE 120 | 0,027 (0,69 t) | **0,091** (2,34 t) | el modelo pide 3,4 veces más; sigue cumpliendo con holgura |
| Pilar HEB 300, R = 6 | 0,148 | **0,151** | coinciden (el modelo 2 % arriba) |
| Pilar HEB 300, R = 2 | 0,378 | **0,381** | coinciden (el modelo 1 % arriba) |
| Deriva R = 6 | 8,52 cm ✓ | **8,52 cm ✓ (idéntica)** | el modelo reproduce la fórmula de la ménsula a 4 cifras |
| Deriva R = 2 | 25,57 cm ✗ | **25,57 cm ✗ (idéntica)** | **confirma la bandera roja** |

Que las derivas coincidan *exactamente* tiene explicación: con el arco **articulado** y los dos
pilares iguales, cuando las dos cabezas se desplazan lo mismo el arco se **traslada rígido** y no
aporta rigidez lateral; las columnas trabajan como ménsulas puras. El modelo da
`k_lat = 516,4 kg/cm` contra `2·3EI/h³ = 516,8 kg/cm` de la fórmula cerrada (0,08 % de diferencia,
que es la deformación por corte del pilar). Por eso el sismo del cuaderno y el del modelo coinciden
en la deriva y en el momento de la base.

**El corte sísmico no se reparte por igual entre los dos pilares.** En la combinación
1,2D + 0,5L + S conviven dos campos: el del sismo, que es **traslación pura** (los dos pilares
empujan igual), y el gravitatorio, que es **simétrico-espejo** (el arco se aplana y separa las
cabezas: −0,245 cm a la izquierda y +0,245 cm a la derecha, con el tirante tomando ese empuje).
El resultado, después de resolver el sistema acoplado por el tirante, es un reparto desigual del
corte: **454,5 kg en el pilar izquierdo y 581,3 kg en el derecho** (R = 6), 1 490 y 1 617 kg (R = 2).
La suma reproduce exactamente la fuerza aplicada (1 035,8 y 3 107,4 kg: equilibrio horizontal exacto)
y gobierna el pilar derecho: `M_base = 4,94 t·m` (R = 6) y 13,75 t·m (R = 2), un 12 % y un 4 % por
encima del `V_col·h` del cuaderno (4,40 y 13,21 t·m). El D/C del pilar **sí coincide** con el del
cuaderno porque el cuaderno también usa la columna como ménsula pura con la carga de servicio
equivalente: 0,151 contra 0,148 (R = 6) y 0,381 contra 0,378 (R = 2).

### 5.3 La hipótesis «sin tirante» no es única (hallazgo importante)

El cuaderno calcula el pilar **sin tirante** suponiendo que todo el empuje `H_u = 14,17 t` llega a la
cabeza del pilar (de ahí `M = H·h ≈ 120 t·m` y D/C de la columna ≈ **3,18**: no cumple). Esa
hipótesis supone que los arranques del arco **no pueden separarse**. El modelo 2D, en cambio,
deja que los arranques se separen libremente (el arco está simplemente apoyado sobre las cabezas
de los pilares): el empuje se cae a 0,36 t, los pilares casi no reciben momento (3,08 t·m) y,
en cambio, **la cercha trabaja como viga curva**: el cordón superior llega a −45,1 t con
**D/C = 1,106 (no cumple)**. Las dos hipótesis son los dos extremos:

| Hipótesis | Qué supone | Resultado | D/C que gobierna |
|-----------|-----------|-----------|------------------|
| Arranque **restringido** (cuaderno) | los apoyos no se separan (diafragma de cubierta rígido, fricción, riostras) | `H = 14,17 t` → `M_base ≈ 120 t·m` | pilar **3,18 ✗** |
| Arranque **libre** (modelo 2D) | los apoyos se separan sin resistencia (sólo `k_p = 258 kg/cm` de los pilares) | `H = 0,36 t` | cordón **1,106 ✗** |

Conclusión de la auditoría: **el tirante no es un elemento de confort, es el elemento que cierra el
camino de carga más desfavorable**. Si se ejecuta, el empuje se queda dentro de la cercha
(`T = 12,18 t` de rotura) y todo cumple salvo la deriva de R = 2. Si no se ejecuta, **alguna de las
dos cosas va a fallar** (o el pilar o el cordón), y cuál de las dos gobierna depende de la rigidez
del diafragma de cubierta y del rozamiento en las fundaciones, que hoy no están cuantificados
(§9, pregunta 3).

### 5.4 Otras observaciones

1. **La deriva de R = 2 no cumple** (24,53 cm contra 17 cm) con el modelo 2D y con el cuaderno:
   es un problema del **criterio de diseño (R)**, no del modelo.
2. **Deslizamiento de la zapata** (FS = 0,42 ✗ en la planilla): ese FS se calculó con la hipótesis de
   empuje sin tirante (`H = 14,17 t`). Con el tirante ejecutado el empuje que llega a la fundación es
   de 0,12–1,49 t y el FS deja de ser crítico. **Los dos números no son comparables: hay que declarar
   la hipótesis de empuje con la que se calculó cada uno.**
3. **Perno Φ1″ a tracción con R = 2: D/C 1,087 ✗** — el modelo 2D no cambia ese resultado (es placa base).
4. **Asentamiento**: 0,447 cm elástico contra 2,50 cm admisible; sin EMS, es una estimación.
5. **Diagonal con la fórmula correcta**: la demanda baja de 12,33 a 3,54 t, pero la longitud real de
   panel (2,88 m en los vanos extremos contra 2,45 m supuestos) sube la esbeltez de 133 a ≈157;
   sigue cumpliendo, aunque conviene recalcular `φFcr` con la longitud real.
6. **El arco se aplana con la carga vertical** y separa las cabezas de los pilares ±0,245 cm
   (0,49 cm entre ambas, con el tirante tomando 8,48 t de servicio). No es un efecto sísmico, pero
   sí una razón más para ejecutar el tirante: sin él ese aplanamiento crece hasta donde lo permita
   la cercha (el cordón llega a −45,1 t).
7. **La deriva del cuaderno está bien calculada**, no es una coincidencia: la ménsula en voladizo
   `δ = P·h³/(3EI)` reproduce exactamente el comportamiento del pórtico con arco articulado cuando
   las dos cabezas se mueven igual (§5.2).

---

## 6. Cómo se usa el prototipo entregado

```bash
cd simulacion
python3 modelo.py && python3 solver2d.py     # regenera modelo.json, resultados.json, datos.js
python3 dinamica.py                          # regenera modal.json, datos2.js (nivel B)
python3 -m http.server 8001                  # o abrir index.html directamente
```

El visor tiene dos bloques:

* **Nivel A (estático animado).** Elegir el caso, **aplicar las cargas paso a paso** (animación),
  ver la deformada amplificada —con el contorno sin deformar en trazo discontinuo—, leer los
  axiales por color y grosor, ver los momentos de los pilares, la deriva en centímetros y el D/C
  de cada elemento contra el del cuaderno. En los casos sísmicos el botón **⇄ Oscilar sismo**
  pone la estructura a vibrar con el **período real `T₁`** y el modo fundamental; el selector de
  velocidad permite verlo a cámara lenta (×1/4 o ×1/10) y el interruptor **amplitud de diseño ×Cd**
  decide si la oscilación se dibuja con el desplazamiento elástico δ o con el de diseño
  Δ = Cd·δ.
* **Nivel B (dinámico).** Dos paneles animados **R = 6 contra R = 2** con la misma amplificación y
  el mismo instante de tiempo (la diferencia que se ve es la del sismo, no la del dibujo), el
  **modo fundamental** con sus fuerzas inerciales, el **espectro de diseño** con `Ta`, `TC` y `T₁`
  marcados, y dos tablas: *estático contra dinámico* y *sin tirante: las dos hipótesis de empuje*.

Los datos que dibuja **no están estimados a ojo**: todos vienen de `resultados.json` y
`modal.json`. Las flechas verticales son las cargas nodales del caso (por área tributaria real),
las horizontales el corte sísmico por pilar y las rosadas del modo son `Γ·m·φ`.

## 7. Archivos del subdirectorio

| Archivo | Contenido |
|---------|-----------|
| `AUDITORIA.md` | este documento |
| `modelo.py` | arma nudos, barras, secciones, áreas tributarias y casos de carga |
| `solver2d.py` | solver de rigidez directa (barras de pórtico y bielas), comprobaciones y D/C |
| `dinamica.py` | análisis dinámico: masas sísmicas, autovalores (Jacobi + Guyan), modos y espectro |
| `modelo.json`, `resultados.json`, `modal.json` | datos generados (no editar a mano) |
| `datos.js`, `datos2.js` | esos datos embebidos para el visor (generados) |
| `index.html`, `app.js` | visor animado del nivel A (estático) |
| `app_din.js` | visor del nivel B: R = 6 contra R = 2, modo, espectro y tablas |
| `README.md` | guía rápida |

## 8. Riesgos de interpretación (para no usar mal el visor)

1. La deformada se dibuja **amplificada** ×N (el movimiento real es de centímetros): sin ese factor
   no se vería nada. El factor está siempre rotulado.
2. La simulación es un **modelo de barras lineal**, no un ensayo: no reproduce plasticidad,
   inestabilidad local ni daño.
3. Los colores del axial son proporcionales al máximo **de ese caso**, no comparables entre casos.
4. Los resultados son de **un pórtico de los 7**; todo lo longitudinal está fuera.
5. Nada de esto sustituye la memoria de cálculo ni la firma de un profesional; el expediente sigue
   siendo académico y **no válido para permisología** mientras no exista el EMS.

## 9. Decisiones que se consultaron (y lo que se respondió)

Las cinco preguntas de la auditoría se enviaron al usuario el **15‑10‑2026** y quedaron respondidas
así:

| # | Pregunta | Respuesta | Efecto en el trabajo |
|---|----------|-----------|----------------------|
| 1 | Alcance: nivel A, A+B o A+B+C | **A + B** (estático animado + dinámico: período, modo y oscilación con el espectro COVENIN 1756‑1:2019 §7) | nivel C (3D) descartado por ahora |
| 2 | Hipótesis sísmica | **R = 6 y R = 2 lado a lado**, comparadas | el visor muestra las dos a la vez |
| 3 | Tirante | **Sí se ejecuta**, pero hay que mostrar también el escenario **sin tirante con sus dos hipótesis de empuje** | §5.3 va al visor con los dos D/C juntos |
| 4 | Peso propio | **Datos del plano confirmados**: cordones 2×IPE 160 y pasarela de 25 kg/m colgando del cordón inferior → PP real 134,7 kg/m contra 60 de la planilla | el modelo 2D ya usa el PP real; el recálculo de la planilla queda para otra entrega |
| 5 | Salida | **Sólo el visor HTML** (sin video ni informe PDF) | todo se entrega dentro de `index.html` |

### 9.1 El nivel B en una línea

Con las masas sísmicas reales (D + 0,5L + pasarela + peso propio, 10,81 t por pórtico) el modo
fundamental de traslación es **T₁ = 0,875 s** (f = 1,14 Hz), con factor de participación
**Γ₁ = 1,001** y **90,8 %** de la masa efectiva en la dirección horizontal: es un modo de traslación
puro, sin torsión (el modelo es 2D). El período queda **por encima de `TC = 0,809 s`**, es decir en la
rama descendente del espectro: la ordenada de diseño `Ad(T₁) = 2,4·AA/R·(TC/T₁)` es 7,5 % menor que la
que usó el cuaderno evaluando la meseta en `Ta = 0,44 s`. El cortante basal modal por pórtico resulta
**1,21 t** contra 1,04 t del cuaderno (+17 %): el aumento viene del peso sísmico real (+39 %) menos el
efecto favorable del período. La oscilación del visor usa ese período, ese modo y esa ordenada.

