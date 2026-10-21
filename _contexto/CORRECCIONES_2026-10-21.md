# Auditoría de las correcciones recibidas (2026-10-21)

**Qué llegó.** Tres bloques de texto (lectura de la imagen 3D del profesor, cierre de
fundaciones + coordinación puertas/arriostramientos, y la «Sección 6. Fundaciones»
completa) y el PDF `DISEÑO DE ESTRUCTURAS.pdf` del Ing. Ivan Laine (29 págs.),
que es la fuente del método de clase usado en las correcciones.

**Conclusión en una línea.** Las correcciones están bien calculadas en lo numérico,
pero **no son un parche: cambian el sistema estructural en las dos direcciones, los
materiales y la combinación de carga**. Aplicarlas tal cual invalida parte del
cuaderno y de las dos simulaciones, y además contradicen dos decisiones que el
usuario ya había tomado (vanos arriostrados y sistema transversal). Por eso se
auditan primero y se pregunta antes de reescribir el cálculo.

---

## 1. Verificación numérica de las correcciones (lo que está bien)

| Afirmación de la corrección | Comprobación con las fórmulas del proyecto | Resultado |
|---|---|---|
| Diagonal HEB 200: φPn = 38,9 t (λ = 177–180, longitud total) | `phi_flex` del cuaderno, L = 9,13 m: λ = 180, φPn = **39,3 t** (en régimen elástico no depende de Fy) | ✔ coincide |
| Riostra: As = 0,15·Pu/(φ·Fy) = 0,50 cm² (Pu = 9,83 t) | 0,15×9.830/(0,7×4.200) = **0,50 cm²**; es el bloque «VIGAS DE RIOSTRA» de Laine (pág. 10: φAsFy > 0,1–0,15 Pu, φ = 0,7) | ✔ y fuente verificada en el PDF |
| Zapata: As_mín = 14·B·d/Fy = 13,65 cm² (gobierna) | 14×130×31,5/4.200 = **13,65 cm²**; Laine pág. 9: As_mín = 14·b·d/Fy | ✔ |
| Zapata: d por flexión = √(Mu/(μ·f'c·B)) = 3,1 cm con μ = 0,1448 | μ = 0,1448 es el valor de Laine (págs. 8–9, sección dúctil w = 0,18, Ju = 0,894); da 3,1 cm ✔ (gobierna el d práctico, 31,5 cm) | ✔ |
| Riostra normativa: máx(AA/4·P, 10 %·P) | 0,345/4×P vs 0,10·P → gobierna el 10 % (≈ 1,0 t) | ✔ |
| Zapata 1,30: q_máx servicio 9,13 y sísmica 12,81 t/m² ≤ 15 | Internamente consistentes con P_s = 10,56 t y e vs B/6 + área real triangular | ✔ (con sus cargas, ver §3) |

## 2. Inconsistencias *dentro* de las propias correcciones

1. **Dos zapatas distintas.** El bloque 1 adopta 1,20×1,20 m con Ø5/8"@15 y Pu = 9,7 t;
   la Sección 6 adopta **1,30×1,30 m con Ø5/8"@12 y Pu = 9,83 t**. Hay que quedarse con
   una (se propone la Sección 6, que es la versión formal y posterior).
2. **El sistema longitudinal se describe de dos maneras.** El bloque 1 dice «longitudinal:
   columnas en voladizo Tipo IV + diafragma de techo, R = 2»; la Sección 6 y el bloque 2
   suponen **cruces verticales también en las fachadas** (parejas axiales ΔP = 2,71 t que
   llegan a las zapatas). Las dos cosas no pueden gobernar a la vez: si hay cruces en
   fachada, el sistema longitudinal es arriostrado (III‑b), no voladizo.
3. **Fy = 3.500 kg/cm²** aparece en la conexión por capacidad (Ry·Fy·Ag = 30,1 t) y en el
   chat («acero A52 Fy = 3.500»), pero el cuaderno calcula todo el acero con **Fy = 2.530**.
   Con 2.530, la conexión por capacidad sería 1,1×2.530×78,1 = **21,7 t**, no 30,1 t.

## 3. Conflictos con el proyecto actual (cuaderno + simulaciones)

| Tema | Proyecto actual (repo) | Corrección | Impacto si se aplica |
|---|---|---|---|
| Combinación de gravedad | 1,2CP + 1,6CV (q_u = 915 kg/m) | **1,4CP + 1,6CV** (cátedra) → q_u ≈ 958 kg/m (+4,7 %) | Cambian cercha, tirante, columna, placa y zapata: hay que correr de nuevo todo el cuaderno |
| f'c del concreto | **210 kg/cm²** | **250 kg/cm²** | Zapata, pedestal y aplastamiento; también las citas del Cap. 8 del libro que usaban 210 |
| Fy de perfiles | **2.530 kg/cm²** (A52 equiv. A36) | **3.500 kg/cm²** en la conexión por capacidad | Todas las D/C de acero del cuaderno y de las simulaciones bajarían; hay que decidir un solo Fy |
| Zapata | 1,50×1,50×0,40, Ø1/2"@15, As_mín = 0,002·b·h = 8 cm²/m | 1,30×1,30×0,40, Ø5/8"@12, As_mín (Laine) = 13,65 cm² | La zapata actual es más grande pero con menos acero: con el criterio de Laine el acero Ø1/2"@15 (8,5 cm²/m) **no cumpliría** el mínimo de 13,65 cm² |
| Pedestal | 40×40, 4Ø3/4" | 0,60×0,70, 4Ø5/8" + Ø3/8"@15; 6 pernos Ø1" A687 | Cambia P‑03 y el detalle de placa base |
| Riostra | 40×40, 6Ø3/4", en el modelo toma también el empuje H; transversal entre zapatas opuestas | **25×40, 4Ø1/2" + Ø3/8"@20, solo longitudinal**; transversal la suple la losa (§13.4.4.c) | Cambia el resumen de fundaciones y elimina el «par de riostras» sísmico actual |
| Deslizamiento | FS = 0,42 ✗ contra H = 14,17 t sin tirante (hipótesis vieja) | φ·μf·N = 3,38 t ≥ V = 1,13 t ✔ (momento de base casi nulo por el arriostramiento) | El ✗ desaparece **solo si** se acepta el cambio de sistema (con tirante y sin momento de base); hay que documentarlo así |
| **Sistema transversal** | Pórtico en voladizo Tipo IV, R = 2: Δ = 25,57/29,76 cm **✗** (el hallazgo central de la simulación) | **Testeros arriostrados Tipo III‑b** (cruces en vanos exteriores, 2 columnas intermedias en X = ±4,40 m, vano central libre para la puerta), R = 4,5 | Es el cambio mayor: la resistencia transversal se concentra en los testeros y el diafragma de techo trae el corte de los pórticos interiores. El modelo 2D transversal actual (un pórtico interior tipo) dejaría de representar el sistema; haría falta el modelo del testero + diafragma |
| **Sistema longitudinal** | Simulación Y recién hecha: cruces en **los 6 vanos** (decisión del usuario, 2026‑10‑17) | Cruces solo en **vanos 2, 3 y 5** (puertas/celosías en 1, 4 y 6), simétrico; cruces de techo Ø1" solo a tracción en bahías 2, 3, 5 + bordes | Hay que rehacer el nivel Y con 3 vanos arriostrados por fachada; con vanos desiguales las dos hipótesis de diafragma **ya no coinciden** (el reparto cambia), que era justo el resultado anterior |
| Puertas vs arriostramiento | Sin coordinación explícita en planos | Regla: vano con puerta no lleva cruz; nota en P‑01 y plano P‑02 de arriostramientos | Nuevo entregable de coordinación (tabla de vanos por fachada y testero) |

## 4. Qué se puede aplicar sin ambigüedad (si el usuario lo confirma)

- La **Sección 6 de Fundaciones con el método de Laine** (área con γ, e vs B/6 y área real,
  μ = 0,1448, As = Mu/(φFy·Ju·d), As_mín = 14Bd/Fy, riostra As = 0,15Pu/(φFy) + momento por
  rigidez), adoptando la versión 1,30×1,30 y Pu con 1,4CP + 1,6CV.
- La **regla de coordinación puertas/arriostramiento** y sus tablas de vanos.
- El **diafragma de techo con tirantes Ø1" solo a tracción** como arriostramiento de
  diafragma (§8.2.4.2), distinto del sistema vertical (que sí trabaja a tracción y compresión).

## 5. Lo que NO se debe aplicar sin decidir antes

1. El cambio de **sistema transversal** (testeros arriostrados): rehace el análisis sísmico
   transversal, el modelo 2D y el hallazgo de la deriva que no cumple.
2. Los **materiales** (f'c 250, Fy 3.500): tocan todos los D/C del expediente.
3. Los **vanos 2, 3, 5** contra la decisión anterior de arriostrar los 6 vanos.
4. La combinación **1,4CP + 1,6CV** aplicada a todo el cuaderno (no solo a la zapata).

---

## 6. Decisiones del usuario (2026-10-21) y aplicación

| Pregunta | Decisión |
|---|---|
| Alcance | **Solo la Sección 6 de Fundaciones** por ahora (+ riostra y coordinación de puertas); el sistema estructural y las simulaciones no se rehacen en esta pasada |
| Materiales | **Los de cátedra: f'c = 250 kg/cm²** (aplicado ya, solo afecta a las fundaciones) y **Fy = 3.500 kg/cm²** para perfiles (queda adoptado como decisión; su recálculo global de D/C de acero queda pendiente, junto con el sistema nuevo) |
| Vanos de fachada | **Cruces solo en los vanos 2, 3 y 5** (puertas/celosías en 1, 4 y 6) — decisión adoptada; el nivel Y de la simulación (6 vanos) queda por rehacer cuando se aplique el sistema completo |
| Sistema transversal | **Testeros arriostrados Tipo III-b** (corrección) — decisión adoptada; el modelo transversal actual (voladizo Tipo IV) queda vigente en el cuaderno/simulación hasta el recálculo global, con la divergencia declarada |

**Aplicado en esta pasada (cuaderno, cálculo 11 y 12):**
- `calculos.py`: FC 210 → **250**; zapata **1,30×1,30×0,40** (d = 31,5 cm), pedestal **0,60×0,70**;
  combinación de cátedra **U = 1,4CP + 1,6CV** para la fundación (P_u = 9,82 t); presión de diseño
  con P_u de cátedra; flexión con **μ = 0,1448** y **As_mín = 14·B·d/Fy = 13,65 cm²** (Laine);
  acero **Ø5/8"@12 con gancho estándar** (la barra recta no cabe: L_d = 56 cm > 27,5 cm disponibles;
  con gancho l_dh = 22,2 cm ✔ — la corrección original decía «55 < 122 cm», que no se reproduce);
  presiones con excentricidad (e vs B/6, área real: σ_máx sismo = 12,9 t/m², levantamiento 1,5 %);
  deslizamiento sísmico §13.5.4 ✔ (3,44 t ≥ 1,09 t), manteniendo la bandera del deslizamiento
  **sin tirante** (FS = 0,38 ✗) como prueba de que el tirante es obligatorio.
- Riostra **25×40, 4Ø1/2" + Ø3/8"@20, solo longitudinal** (As = 0,50 tracción + 1,26 flexión =
  1,76 cm²; gobierna lo constructivo); la transversal la suple la losa (§13.4.4.c), declarado.
- `sec_c.py`, `sec_d.py`, `sec_a.py`, `svg.py`: texto, planilla (renglones 15–22 y 27–29),
  índice y figuras (zapata y riostra) actualizados; `cuaderno.html` regenerado.

**Pendiente (cuando se ordene el recálculo global):** sistema transversal de testeros con sus
columnas intermedias y diafragma de techo, nivel Y con vanos 2, 3, 5, Fy = 3.500 en todos los
D/C de acero, combinación 1,4CP + 1,6CV en la superestructura y los planos P‑01/P‑02/P‑03.
