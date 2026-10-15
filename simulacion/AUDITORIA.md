# Auditoría de la petición — «simulación en 2D para ver las cargas en acción, movimiento lateral, etc.»

**Qué se pidió.** Una simulación 2D del pórtico del auditorio para *ver* las cargas actuando y el
movimiento lateral de la estructura, con la posibilidad de auditar la petición y hacer preguntas
antes de construir.

**Qué hay en este subdirectorio.** Un modelo de barras en dos dimensiones del pórtico transversal
(un pórtico de los 7 iguales), resuelto con un solver de rigidez directa escrito desde cero, con
verificación contra fórmulas cerradas, animación de las cargas paso a paso y análisis dinámico
modo-espectral con el espectro del cuaderno. **Nada está dibujado «a ojo»**: cada número del visor
sale de `solver2d.py` (estático) o `dinamica.py` (dinámico), y los dos leen su materia prima de
`../cuaderno/calculos.py`.

---

## 1. Qué se puede y qué no se puede modelar con lo que ya está calculado

| Pieza de la petición | ¿Se puede? | Con qué |
|---|---|---|
| Cargas actuando sobre la estructura (paso a paso) | **Sí** | casos D+L, 1,2D+1,6L, sismo R6/R2 y el escenario sin tirante, con las áreas tributarias reales de `calculos.py` |
| Movimiento lateral (deriva y oscilación) | **Sí** | desplazamientos por nudo del solver; oscilación con el período y el modo calculados en `dinamica.py` |
| Comparar **R = 6 contra R = 2** lado a lado | **Sí** | dos escenas gemelas con la misma amplificación y el mismo instante |
| Escenario **sin tirante** con las dos hipótesis de empuje | **Sí** | `sin_tirante` del modelo 2D + la comprobación del cuaderno con H en la cabeza del pilar |
| Período fundamental, modo de vibración, espectro | **Sí** | `dinamica.py`: autovalores por Jacobi con los giros condensados, participación y masa efectiva |
| 3D (los 7 pórticos, torsión, arriostramientos longitudinales) | **No** | hacen falta masas y rigideces de losa larga; queda como **nivel C**, descartado por ahora |
| Video o informe PDF | **No lo pedido** | la salida es el visor HTML, autocontenido |

## 2. El modelo adoptado

* **Geometría.** Un pórtico transversal: dos columnas HEB 300 de 8,50 m **empotradas en la base y en
  voladizo** hasta la cabeza, y el arco de la cercha de doble cordón 2×IPE 160 apoyado en las
  cabezas **mediante articulación** (rótula), tal como lo describe el diseño (§3.5.4 del chat del
  proyecto: «columnas en voladizo con arco articulado»). El tirante de cabeza (Φ1‑1/2″) cierra el
  arco a nivel de la línea de arranques.
* **22 nudos y 44 barras.** 2 columnas HEB 300, 16 tramos de cordón (8 del extradós y 8 del intradós,
  cada uno 2×IPE 160), 2×8 diagonales IPE 160 en X y 7 montantes IPE 120, más el tirante.
  Los perfiles y pesos salen de `SECCIONES` en `modelo.py`, nunca del aire.
* **Cargas.** Áreas tributarias reales de cada nudo (9 áreas para el cordón, reparto de la pasarela
  al cordón inferior) más el **peso propio real de los perfiles** (el cuaderno usa 60 kg/m; el
  modelo usa los perfiles reales, ver §5).
* **Casos.** `servicio` (D+L), `mayorada` (1,2D+1,6L), `sismo_R6`, `sismo_R2` (1,2D+0,5L+S) y
  `sin_tirante` (1,2D+1,6L sin el tirante de cabeza).

## 3. Verificación del solver (antes de creerle a cualquier número)

| Comprobación | Teoría | Solver | Error |
|---|---|---|---|
| Pilar en voladizo Δ = P·h³/(3EI) | 2,00576 cm | 2,00576 cm | 0,00 % |
| Viga apoyada δ = 5wL⁴/(384EI) | 0,87051 cm | 0,87051 cm | 0,00 % |
| Arco funicular con tirante T = qL²/(8f) | 13.520,4 kg | 13.520,4 kg | 0,00 % |
| Equilibrio vertical ΣR = ΣF | 20.189,6 kg | 20.189,6 kg | 0,00 % |
| Reparto del empuje (arco + pilares + tirante como resortes) | 362,69 / 12.181,85 kg | 362,6897 / 12.181,85 kg | 6 cifras |
| **Nivel B:** T₁ del autovalor contra 2π√(m/k) | 0,9179 s | 0,8752 s | 4,9 % |

La última fila no es un error del programa: la fórmula 2π√(m/k) con `k = 2·3EI/h³` desprecia la
flexibilidad de corte del pilar y la masa repartida a lo largo del arco; el autovalor las incluye.

## 4. Resultados (un pórtico de los 7)

| Caso | T tirante | H en el pilar | M base | Δ lateral | Cd·Δ (≤ 17 cm) |
|---|---|---|---|---|---|
| Servicio | 8,48 t | 0,08 t | 0,68 t·m | — (aplanamiento 0,31 cm) | no aplica |
| Rotura | 12,18 t | 0,12 t | 0,98 t·m | — (aplanamiento 0,45 cm) | no aplica |
| Sismo R = 6 | 6,68 t | 0,58 t | 4,94 t·m | 2,006 cm | **8,52 cm ✓** |
| Sismo R = 2 | 6,68 t | 1,62 t | 13,75 t·m | 6,017 cm | **25,57 cm ✗** |
| Sin tirante | — | 0,36 t | 3,08 t·m | — | cordón D/C **1,11 ✗** |

Nivel B (masas sísmicas reales, 10,81 t por pórtico contra 7,80 t de la planilla):

| Magnitud | Cuaderno (estático) | Nivel B (dinámico) |
|---|---|---|
| Período fundamental | — | T₁ = 0,875 s (f = 1,14 Hz), Γ₁ = 1,001, 90,8 % de la masa |
| Ordenada espectral | Ad(Ta) = 0,1380 | Ad(T₁) = 0,1276 (T₁ > TC: rama descendente) |
| Cortante basal por pórtico | 1,04 t | 1,21 t (+17 %, por el peso sísmico real) |
| Deriva Cd·δ (R = 6) | 8,52 cm ✓ | 9,92 cm ✓ |
| Deriva Cd·δ (R = 2) | 25,57 cm ✗ | 29,76 cm ✗ |

## 5. Hallazgos de la auditoría (lo que el modelo 2D añade al cuaderno)

1. **El peso propio real duplica la planilla.** La cercha pesa 2.032 kg (109,7 kg/m de arco) más la
   pasarela de 25 kg/m = **134,7 kg/m** contra 60 kg/m de la planilla: **+124 %**. El peso sísmico
   por pórtico pasa de 7,80 t a 10,81 t (+39 %) y con él sube el cortante basal y la deriva.
2. **El reparto del corte entre pilares no es 50/50.** Los pilares son iguales, pero el arco
   articulado no es simétrico respecto al sismo (el tirante trabaja a distinta tracción): el pilar
   derecho se lleva 581 kg contra 454 kg del izquierdo (R = 6) y 1.617 contra 1.490 kg (R = 2).
   Gobierna el derecho, con M = 4,94 t·m y D/C 0,151 (cuaderno 0,148).
3. **La deriva del cuaderno es correcta.** Con el arco articulado y las dos columnas iguales, el
   arco se traslada como cuerpo rígido y cada pilar trabaja como ménsula pura: la rigidez lateral
   `k = 2·3EI/h³ = 516,4 kg/cm` reproduce el desplazamiento del cuaderno a 4 cifras. No es una
   coincidencia, es la mecánica del sistema.
4. **El sismo R = 2 no cumple por deriva** (25,57 cm contra 17 cm) y arrastra al perno de anclaje
   Φ1″ de la placa base (D/C 1,087) y al deslizamiento de la zapata. El pilar, en cambio, tiene
   D/C 0,381: **gobierna la deriva, no la resistencia**.
5. **El aplanamiento del arco bajo carga gravitatoria** mueve las cabezas de los pilares
   ±0,245 cm (0,49 cm entre ambas) y el tirante toma 8,48 t en servicio. Por eso la deriva sísmica
   se mide **sólo con el campo lateral**: mezclar los dos campos da un desplazamiento neto
   (1,760 cm en el pilar izquierdo, 2,251 cm en el derecho para R = 6) que no es la deriva.
6. **Sin el tirante la estructura cambia de mecanismo.** La cercha se apoya en las cabezas de los
   pilares (no en el suelo): sin tirante, el arco empuja hacia afuera y las cabezas se separan
   porque el pilar en voladizo es muy flexible lateralmente (k = 258 kg/cm por pilar). El modelo da
   H ≈ 0,36 t y el pilar queda holgado (D/C 0,116), pero **el cordón superior se sobrecarga**
   (D/C 1,106 ✗) porque la cercha pierde la acción de arco y trabaja como viga curva.
7. **Dos hipótesis de empuje sin tirante, y son opuestas.** El cuaderno comprobó el pilar con
   H = 14,17 t en la cabeza (M = H·h ≈ 120 t·m, D/C 3,18 ✗), que es el caso «el apoyo no se
   separa». El modelo 2D con la cabeza libre da H = 0,36 t y M = 3,08 t·m. La verdad está entre las
   dos y depende de la rigidez del diafragma de cubierta y de la cimentación. **Recomendación:** el
   tirante de cabeza se ejecuta (D/C 0,546 con H = 14,17 t) y ninguna de las dos fallas aparece.
8. **La zapata de la planilla puede estar sobredimensionada en carga vertical y subdimensionada en
   deslizamiento** según la hipótesis de empuje que se adopte (FS = 0,42 con H = 14,17 t).

## 6. Límites del nivel B y del modelo 2D

* Es un **pórtico plano**: no hay torsión, ni los 7 pórticos trabajando juntos, ni el diafragma de
  cubierta (nivel C).
* El análisis dinámico es **modo-espectral con un solo modo** (el primero concentra el 90,8 % de la
  masa); no es una integración paso a paso en el tiempo ni un análisis con registros sísmicos.
* La oscilación del visor usa el **período real T₁ = 0,875 s** y la amplitud del desplazamiento de
  diseño, pero es una **visualización**: la respuesta real de un sismo es irregular, no armónica.
* La aceleración de la gravedad, los módulos y las resistencias son los del cuaderno (E = 2,1·10⁶
  kg/cm², `calculos.py`); no se recalibró nada.
* No hay estudio de mecánica de suelos: los resortes de la cimentación son hipótesis declaradas
  (AUDITORIA del cuaderno), no resultados de ensayos.

## 7. Archivos

| Archivo | Contenido |
|---|---|
| `AUDITORIA.md` | este documento |
| `modelo.py` | arma nudos, barras, secciones, áreas tributarias y casos de carga |
| `solver2d.py` | solver de rigidez directa (barras de pórtico y bielas), comprobaciones y D/C |
| `dinamica.py` | análisis dinámico: masas sísmicas, autovalores (Jacobi + Guyan), modos y espectro |
| `modelo.json`, `resultados.json`, `modal.json` | datos generados (no editar a mano) |
| `datos.js`, `datos2.js` | esos datos embebidos para el visor (generados) |
| `index.html`, `app.js` | visor animado del nivel A (estático) |
| `app_din.js` | visor del nivel B: R = 6 contra R = 2, modo, espectro y tablas |
| `README.md` | guía rápida |

## 8. Cómo se usa el visor

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

## 9. Preguntas y respuestas

### 9.1 Respuestas del usuario (2026-10-15)

| Pregunta | Respuesta |
|---|---|
| Alcance | **A + B** (estático animado + dinámico: período, modo de vibración y oscilación con el espectro COVENIN 1756‑1:2019 §7). El nivel C (3D, 7 pórticos) queda descartado por ahora |
| Sismo | **R = 6 y R = 2 lado a lado**, comparados |
| Tirante | **Sí se ejecuta**; el visor muestra además el escenario **sin tirante** con las dos hipótesis de empuje y sus D/C |
| Datos de plano | Cordones **2×IPE 160** y **pasarela de 25 kg/m** colgando del cordón inferior → PP real ≈ 135 kg/m |
| Salida | **Solo el visor HTML** (sin video ni informe PDF) |

### 9.2 Preguntas que siguen abiertas (para el nivel C o para el expediente)

1. **¿Se modela el nivel C?** Hacen falta las masas y rigideces de la losa de cubierta y del
   arriostramiento longitudinal (HEB 200 en los vanos 2–5) para mirar torsión y los 7 pórticos.
2. **¿Qué hipótesis de empuje se adopta en el expediente?** Hay que decidir si el tirante se
   considera elemento estructural principal (recomendado, D/C 0,546) o si se documenta el escenario
   sin él y se redimensiona el cordón y la cimentación.
3. **¿Se corrigen los dos ✗ de la planilla con R = 2** (perno Φ1″ de la placa base y deslizamiento
   de la zapata) o se documentan como incumplimientos del escenario R = 2?
4. **¿Se revisa el peso propio de la planilla (60 kg/m) a la luz del real (134,7 kg/m)?** Afecta
   al sismo, a la zapata y a las reacciones de la cercha.
5. **¿Hace falta el registro del tirante en los planos** (P‑01/CL‑01) y la nota de que sin él el
   cordón no cumple? Es la recomendación directa del punto 7 de §5.

## 10. Ruta de trabajo (lo que se hizo, en orden)

1. Auditar la petición y hacer las preguntas (§9.1) → respuestas del usuario.
2. Armar el modelo 2D leyendo `calculos.py` (nada duplicado a mano).
3. Escribir el solver y **verificarlo** contra cuatro fórmulas cerradas y el reparto del empuje (§3).
4. Correr los 5 casos, comparar con el cuaderno y anotar los hallazgos (§5).
5. Escribir `dinamica.py`: masas reales, autovalores, modos, espectro y campos de desplazamiento.
6. Construir el visor (nivel A animado + nivel B con R = 6 / R = 2, modo, espectro y tablas).
7. Redactar esta auditoría y publicar todo en el repositorio (rama `arena/d5d7b5b7-tarea`, PR #1).
