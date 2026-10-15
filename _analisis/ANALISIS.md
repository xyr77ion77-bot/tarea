# Análisis de los documentos escaneados

**Archivos analizados**

| Archivo | Páginas | Páginas impresas | Tamaño |
|---|---|---|---|
| `Fundaciones y Muros_cap 1.pdf` | 55 | 11 – 65 | 2,4 MB |
| `Fundaciones y Muros_cap 8.pdf` | 29 | 246 – 274 | 1,0 MB |

Fecha de trabajo: 14 de octubre de 2026.

---

## 1. Qué son estos documentos

**Fuente identificada.** Son escaneos del libro **«Suelos, Fundaciones y Muros» de María Graciela Fratelli**
(572 págs., en español). La coincidencia es exacta con el índice publicado de la obra y se confirma
dentro del propio texto:

- El PDF «cap 1» arranca con el título **CAPITULO 1 – Características de los Suelos** (pág. 11 del libro).
- El PDF «cap 8» arranca con **CAPITULO 8 – Fundaciones Directas Aisladas y Continuas** (pág. 246),
  que es el capítulo 8 del índice de la obra.

**Ficha técnica de los archivos**

| Característica | Valor |
|---|---|
| Tipo | PDF con imágenes, **sin capa de texto** (0 caracteres extraíbles) |
| Imagen por página | 2240 × 1680 px, 1 bit (blanco y negro), filtro CCITT/PNG |
| Resolución efectiva | ≈ 200 dpi (por eso las líneas finas de las figuras se ven “entrecortadas”) |
| Productor | PDFium (los PDF se generaron el mismo día, 2026-10-14, con el nombre “Fundaciones y Muros_cap N”) |
| Marcas de escaneo | líneas punteadas verticales de calibración en el margen izquierdo y recuadros negros de calibración en algunas páginas |
| Índice / marcadores / formularios | ninguno |

**Observación importante sobre el alcance real de cada archivo.** El archivo llamado «cap 1» **no contiene
sólo el capítulo 1**: trae los capítulos 1 y 2 completos y el inicio del 3.

| Contenido | Páginas del libro |
|---|---|
| CAPÍTULO 1 – Características de los Suelos | 11 – 35 |
| CAPÍTULO 2 – El Comportamiento de los Suelos | 36 – 64 |
| CAPÍTULO 3 – Exploración del Subsuelo (sólo el arranque, §3.1) | 65 |

El archivo «cap 8» sí está recortado exactamente en el capítulo 8 (246 – 274).

---

## 2. Cómo se analizó (y qué se generó)

Como los PDF no tienen texto, se hizo un **OCR completo** y se reconstruyó el orden de lectura. Todo el
material de trabajo quedó en la carpeta `_analisis/`:

```
_analisis/
├── ANALISIS.md                     ← este informe
├── indice_paginas.csv              ← correspondencia página PDF ↔ página del libro
├── hojas_contacto/                 ← vistas en miniatura de todas las páginas (control visual)
├── texto/
│   ├── cap1_libro_pag011-065.txt   ← texto continuo, capítulos 1–2 y arranque del 3
│   ├── cap8_libro_pag246-274.txt   ← texto continuo del capítulo 8
│   └── paginas/                    ← 84 archivos, uno por página (texto ya reordenado)
├── datos_ocr/                      ← 84 archivos JSON con las cajas OCR (x, y, texto, confianza)
└── scripts/
    ├── ocr_paginas.py              ← paso 1: OCR a 200 dpi
    ├── agrupar_lineas.py           ← paso 2: reordenar cajas en líneas legibles
    └── unir_capitulo.py            ← paso 3: unir páginas en texto continuo por capítulo
```

Reproducible con:

```bash
cd _analisis
python3 scripts/ocr_paginas.py cap1 && python3 scripts/ocr_paginas.py cap8
python3 scripts/agrupar_lineas.py cap1 && python3 scripts/agrupar_lineas.py cap8
python3 scripts/unir_capitulo.py cap1 && python3 scripts/unir_capitulo.py cap8
```
(requiere `pymupdf`, `pillow`, `numpy`, `rapidocr-onnxruntime`)

**Detalle técnico que condicionó la calidad del texto:** el escaneo está inclinado ~1–2°. Eso hace que los
rectángulos envolventes de líneas contiguas se solapen y, si se ordenan sin más, se mezclan renglones
(lo que producía pasajes aparentemente sin sentido en el primer intento). La solución fue agrupar por el
**centro vertical** de cada caja, que es exacto, con una tolerancia derivada del paso de línea.

**Límites de esta transcripción (importante antes de citar).**
- El texto es OCR **sin corregir**: aparecen confusiones típicas (`1`↔`l`↔`I`, `rn`↔`m`, `0`↔`o`,
  `F1gura` por `Figura`, `s1` por `si`, etc.). Los párrafos se entienden, pero no deben copiarse literalmente.
- Las **fórmulas, tablas y figuras** están muy degradadas (subíndices, fracciones, radicales y columnas
  se pierden o se desordenan). Para tablas y ecuaciones debe usarse el PDF original.
- El orden de lectura dentro de páginas con figuras de varias columnas puede quedar alterado.

---

## 3. Mapa de contenido con páginas

### Capítulo 1 – Características de los Suelos (págs. 11–35)

| § | Título | Pág. libro |
|---|---|---|
| 1.1 | Generalidades sobre suelos y rocas | 11 |
| 1.2 | La mecánica de suelos | 12 |
| 1.3 | Propiedades físicas de los suelos | 13 |
| 1.4 | Densidad, porosidad e índice de vacíos | 13 |
| 1.5 | Tamaño de los granos | 19 |
| 1.6 | Forma de las partículas | 22 |
| 1.7 | Textura y color | 23 |
| 1.8 | Consistencia. Los límites de Atterberg | 24 |
| 1.9 | Clasificación de suelos en ingeniería | 30 |

Tablas: 1.1 y 1.2 (pesos específicos relativos, págs. 15–16), 1.3 (tamices, pág. 19), 1.4 (clasificación
por tamaño, pág. 20), 1.5 (límites de Atterberg, pág. 24), 1.6 (límites por mineral arcilloso, pág. 25),
1.7 (consistencia según índice de fluidez, pág. 27), 1.8 (actividad de Skempton, pág. 29), 1.9 (densidad
relativa de arenas, pág. 32).
Figuras: 1.1 (estructura de un suelo mixto, pág. 14), 1.2 (curva granulométrica, pág. 21), 1.3–1.5 (forma de
partículas y angulosidad, págs. 22–23), 1.6 (límite líquido, pág. 26), 1.7 (diagrama de plasticidad, pág. 28).
Ejemplos resueltos: 1.1 (pág. 16), 1.2 (18), 1.3 (18), 1.4 (19), 1.5 (20, granulometría por tamices),
1.6 (29, índices y actividad), 1.7 (30).

### Capítulo 2 – El Comportamiento de los Suelos (págs. 36–64) *(incluido en el archivo «cap 1»)*

| § | Título | Pág. libro |
|---|---|---|
| 2.1 | Generalidades | 36 |
| 2.2 | La presencia del agua en los suelos | 36 |
| 2.3 | La permeabilidad | 39 |
| 2.4 | La capilaridad | 41 |
| 2.5 | La compresibilidad | 42 |
| 2.6 | Los asentamientos | 47 |
| 2.7 | La retracción y expansión | 58 |
| 2.8 | La licuefacción del suelo | 62 |
| 2.9 | La acción de las heladas y deshielos | 64 |

Tablas: 2.1 (permeabilidad, pág. 41), 2.2 (asentamientos tolerables, pág. 51), 2.3 (asentamientos máximos
admisibles, pág. 51), 2.4 (índice de plasticidad ↔ expansividad, pág. 58), 2.5 (% cambio de volumen ↔
expansividad, pág. 59).
Figuras: 2.1 (tipos de agua en el suelo, pág. 38), 2.2 y 2.3 (permeabilidad, págs. 39–40), 2.4 (capilaridad,
pág. 41), 2.5 (consolidómetro, pág. 43), 2.6 (curvas de consolidación, pág. 44), 2.7 (arcilla normal vs.
preconsolidada, pág. 45), 2.8 y 2.9 (asentamiento–presión, pág. 48), 2.10 y 2.11 (asentamiento absoluto y
diferencial, pág. 49), 2.12 (distorsión angular admisible, pág. 51), 2.13 (factor de tiempo, pág. 53),
2.14 (distorsión vs. asentamiento, pág. 54), 2.15–2.18 (suelos expansivos, págs. 59–61), 2.19 (Niigata,
pág. 62), 2.20 (heladas, pág. 64).
Ejemplos resueltos: 2.1 (pág. 45), 2.2 (47), 2.3 (54, asentamientos y consolidación), 2.4 (56),
2.5–2.7 (57, asentamiento en arenas, N del SPT), 2.8 (58, efecto del nivel freático).

### Capítulo 3 – Exploración del Subsuelo (pág. 65) *(sólo el arranque)*

| § | Título | Pág. libro |
|---|---|---|
| 3.1 | Investigaciones exploratorias | 65 |

### Capítulo 8 – Fundaciones Directas Aisladas y Continuas (págs. 246–274)

| § | Título | Pág. libro |
|---|---|---|
| 8.1 | Generalidades | 246 |
| — | Pedestales · Vigas de riostra · Bases de concreto sin armar | 249–252 |
| 8.2 | Bases aisladas | 249 |
| 8.3 | Bases aisladas cuadradas | 252 |
| 8.4 | Bases aisladas rectangulares | 264 |
| 8.5 | Bases continuas para muros | 267 |
| 8.6 | Bases continuas para una fila de columnas | 269 |

Tablas: 8.1 (factor de mayoración ν según profundidad, pág. 253), 8.2 a 8.6 (prediseño de bases cuadradas
para σ adm = 1 / 1,5 / 2 / 2,5 / 3 Kg/cm², págs. 258–262).
Figuras: 8.1 (tipos de fundaciones directas, pág. 247), 8.2 (pedestales, 249), 8.3 (vigas de riostra, 250),
8.4 (bases sin armar, 251), 8.5 (perfiles de bases cuadradas, 252), 8.6 (planos críticos, 253), 8.7 y 8.8
(punzonado, 263), 8.9 (soluciones alternas: nervios, pedestal troncopiramidal, 265), 8.10 (bases continuas
para muros, 267), 8.11–8.13 (base corrida bajo fila de columnas, 269–271).
Ejemplos resueltos: 8.1 (pág. 255, base cuadrada centrada), 8.2 (265, base rectangular), 8.3 (268, base
continua de muro de mampostería), 8.4 (272, base continua para 4 columnas con viga rigidizadora).

---

## 4. Resumen de contenido

### 4.1 Capítulo 1 — Características de los Suelos

**Suelo vs. roca (§1.1).** El suelo es el producto del desgaste o desintegración de las rocas por agentes
atmosféricos y procesos físico-químicos; se define como todo depósito de partículas minerales y orgánicas
disgregadas pero íntimamente asociadas, del manto rocoso de la litosfera. Las rocas sólo se excavan con
taladros, cuñas o explosivos. No hay frontera neta: suelos consolidados se transforman en rocas y rocas
meteorizadas en suelos. El texto fija tres papeles del suelo en ingeniería civil: **base de apoyo** de las
edificaciones, **masa o talud** que debe ser contenido y **material de construcción**.

**Mecánica de suelos (§1.2).** Ciencia que investiga la naturaleza y el comportamiento de la masa de
suelo; especialidad de la geomecánica (rocas + suelos), distinta de la mecánica de sólidos y de fluidos.
Recuento histórico: Coulomb (1773), Rankine (1885), y luego Klöger (Alemania), Boussinesq (Francia) y
**Karl Terzaghi** (Alemania/EE. UU.) como fundadores de la disciplina moderna. Subraya que el terreno bajo
cada construcción es único y que el problema debe enfocarse como **interacción suelo–bases–superestructura**.

**Propiedades físicas y relaciones fundamentales (§1.3–1.4).** Las propiedades se listan (composición,
densidad/porosidad/índice de vacíos, tamaño y forma de partículas, textura y color, consistencia y humedad,
permeabilidad y capilaridad, compresibilidad, capacidad portante, retracción y expansión). Se desarrollan
las relaciones volumétricas y de pesos con su notación:

- volúmenes: V = V_s + V_a + V_w ; pesos: W = W_s + W_w (el peso del aire se desprecia)
- relación de vacíos e = V_v / V_s (ec. 1.3)
- porosidad n = (V_v / V) × 100 (ec. 1.4) y las equivalencias e ↔ n (ec. 1.5)
- contenido de humedad w = (W_w / W_s) × 100 (ec. 1.6)
- grado de saturación S = (V_w / V_v) × 100 (ec. 1.7)
- densidades y pesos específicos: γ (ec. 1.8), γ seco (1.9), γ sumergido (1.10), γ del agua (1.11),
  peso específico relativo de la masa G (1.12) y de los sólidos G_s (1.13)

  (La ec. 1.8 se lee como «ρ = M / …» en el escaneo, donde el denominador —el volumen— queda cortado.
  Por el contexto debe ser ρ = M/V; conviene confirmarlo en el original.)

Idea de diseño que ancla el capítulo: **la capacidad portante aumenta cuando la relación de vacíos y la
porosidad disminuyen**.

**Tamaño de los granos (§1.5).** Granulometría por tamices calibrados (U.S.A. Standard, de 4″ a N.° 200 =
0,075 mm; ver Tabla 1.3) y por sedimentación (ensayo hidrométrico) por debajo de 0,075 mm. Curva de
distribución (Fig. 1.2) con los tres casos típicos: graduación discontinua (A), bien graduado (B) y
uniforme (C). Tabla 1.4 fija los rangos: piedras de boleo > 300 mm, canto rodado 80–300, grava gruesa
20–80, grava fina 5–20, arena gruesa 2–5, arena mediana 0,5–2, arena fina 0,075–0,5, limos 0,002–0,075,
arcillas < 0,002 mm (2 μ). Dato local: las arenas naturales comunes en Venezuela tienen ~4 % de granos más
finos que 0,075 mm.

**Forma de las partículas (§1.6).** Índices de redondez I_r (ec. 1.14), esfericidad I_e (ec. 1.15) y
equivalente (ec. 1.16), planeidad I_p (ec. 1.17) y alargamiento I_a (ec. 1.18). Consecuencias mecánicas:
granos redondeados resisten mejor el desmenuzamiento y las cargas estáticas; los de cantos vivos se
quiebran por concentración de esfuerzos pero resisten mejor el desplazamiento; las partículas laminares
(arcillas, micas) se orientan horizontalmente y crean **planos preferenciales de deslizamiento**,
peligrosos en terraplenes y laderas.

**Textura y color (§1.7).** Textura: rugosas, lisas, estriadas, picadas, pulidas. El color sólo es
informativo en muestras inalteradas: rojizo → óxidos de hierro no hidratados (bien drenado); negro y marrón
oscuro → materia orgánica; amarillos → hierro hidratado (mal drenaje); blanco → sílice y cal.

**Consistencia y límites de Atterberg (§1.8).** Estados líquido, plástico, semisólido y sólido, separados
por el límite líquido (LL), el límite plástico (LP) y el límite de retracción (LR). Se explican los ensayos
de la taza de Casagrande (cierre de la ranura a los 25 golpes), del bastoncito de 0,3 cm y del mercurio
para la retracción. Se definen además el índice de plasticidad IP = LL − LP (ec. 1.20), el índice de fluidez
IL = (w_N − LP)/IP (ec. 1.21), el índice de retracción (ecs. 1.22–1.23) y la **actividad de Skempton**
A = IP/c (ec. 1.24), con la clasificación: A ≤ 1 caolinita (baja), 1 < A ≤ 4 illita (mediana), A > 4
montmorillonita (alta). Dato práctico: la mayoría de los suelos arcillosos venezolanos tiene LL entre 40 y
60 %; la capacidad portante de un suelo con límite plástico **varía con el régimen de lluvias**, por lo que
se recomienda adoptar el menor valor admisible o drenar.

**Clasificación en ingeniería (§1.9).** Rocas (ígneas, metamórficas, sedimentarias y el proceso de
meteorización mecánica/química), canto rodado, gravas, arenas (suelos no cohesivos, con cohesión aparente
por tensión superficial cuando están húmedas), limos, **loess** (limos transportados por el viento, porosos
y colapsables al humedecerse; grandes extensiones en Rusia, Siberia, Nueva Zelanda y la pampa argentina),
arcillas (minerales arcillosos: montmorillonita, illita, caolinita, bentonita, clorita, vermiculita; la
montmorillonita es la responsable de la retracción y expansión), suelos orgánicos (turba, humus, fangos) y
suelos de relleno (deben compactarse y ensayarse antes de confiarles capacidad resistente).

### 4.2 Capítulo 2 — El Comportamiento de los Suelos

**Agua en el suelo (§2.2).** Distingue el agua infiltrata o percolada, el agua capilar (continua y
discontinua), el agua libre o gravitacional, y rodeando las partículas el agua higroscópica, pelicular y la
humedad de poros. El **nivel freático** es la cota superior del agua libre: su ascenso y descenso estacional
modifica la capacidad portante, provoca inundaciones en sótanos, subpresiones en losas y baja drásticamente
la resistencia al corte. Trata también las aguas **colgadas** y **artesianas** y el fenómeno de “ebullición”
del fondo de excavaciones.

**Permeabilidad (§2.3).** Flujo laminar en los poros, ley de **Darcy** Q = k·i·A·t (ecs. 2.1–2.2), con
validez para suelos granulares y gradientes i < 5. Factores: composición, relación de vacíos, tamaño y
distribución de granos, textura, compactación y saturación. Ensayos in situ por bombeo en pozos en círculo
(5–15 m) e in vitro con el permeámetro de Darcy. Velocidad real vs. ficticia (ecs. 2.3–2.6, con v_s = v/n).
Tabla 2.1: grava y arena gruesa > 10⁻¹ cm/s (muy permeable), arena mediana ~10⁻²–10⁻³, arena fina limosa
~10⁻³–10⁻⁵, limo 10⁻⁵–10⁻⁷, arcilla prácticamente impermeable. Criterio de presas de tierra: permeables
k ≥ 10⁻³ cm/s, impermeables k ≤ 10⁻⁶ cm/s. La montmorillonita de sodio es el mineral menos permeable y se
usa como aditivo impermeabilizante.

**Capilaridad (§2.4).** Ascensión en tubos capilares, h_c = 4T_s·cos α /(γ·D) (ec. 2.7), tensión superficial
del agua ≈ 0,075 g/m (ec. 2.8). En suelos la altura capilar es inversamente proporcional al tamaño de los
vacíos: de pocos centímetros en arena gruesa a más de 25 m en arcillas. Efectos: incrementa el peso efectivo
y otorga cohesión aparente a los granos gruesos (arena húmeda moldeable); desaparece al saturarse el suelo.

**Compresibilidad y consolidación (§2.5).** Al cargar, el suelo reduce su índice de vacíos; en suelos
saturados poco permeables el agua debe ser expulsada lentamente: **consolidación**, cuya teoría se debe a
Terzaghi. Ensayo en el **consolidómetro** (Fig. 2.5), curvas de consolidación (Fig. 2.6) y coeficiente de
compresibilidad C_v como pendiente de la curva e–log σ (ec. 2.10). Para arcillas normalmente consolidadas
Skempton da C_v = 0,009 (LL − 10) (ec. 2.11); para rocas porosas y suelos micáceos C_v = 0,75(e − a)
(ec. 2.12). Se distingue arcilla **normalmente consolidada** (la que nunca soportó cargas mayores que la
sobrecarga efectiva actual) de **preconsolidada** (mejor suelo de fundación: mayor capacidad portante y
asentamientos reducidos), con el método gráfico S–Z para decidirlo en laboratorio (Fig. 2.7).

**Asentamientos (§2.6).** Compresión inmediata (expulsión de gas), primaria (agua) y secundaria (a esfuerzo
constante, medida a las 24 h). Asentamientos **uniformes** (poco frecuentes, críticos para ductos y
tanques) y **no uniformes**: rotación de cuerpo rígido y deformaciones locales por descensos diferenciales
Δ = Δ_máx − Δ_mín (ec. 2.13). Casos citados: hundimiento del valle de México, **Torre de Pisa** (3 m al sur
y 1,2 m al norte), **catedral de México** (torres descendidas más de 1,5 m, fondo del templo hasta ~3 m,
colapso acelerado por la extracción de agua y las vibraciones del metro) y casos en Bogotá. Se dan las
**Tablas 2.2 y 2.3** de asentamientos tolerables y la **distorsión angular θ = Δ/L** (Fig. 2.12), insistiendo
en que el destino de la edificación, la ductilidad del material y la hiperestaticidad del esquema definen
los límites admisibles. Fórmulas de cálculo: asentamiento por consolidación Δ = H·(e₀ − e)/(1 + e₀)
(ec. 2.14), tiempo de consolidación t = (T·H²)/C_v (ec. 2.15), y para arenas el asentamiento en función del
N del SPT, Δ = (5q/N)·(2B/(30 + B)) (ec. 2.16) con corrección por nivel freático α (ec. 2.17).

**Retracción y expansión (§2.7).** Causas de expansión: recuperación elástica de los granos, atracción del
agua por los minerales arcillosos, repulsión eléctrica entre partículas y expansión del aire de los poros.
La **montmorillonita** puede aumentar su volumen hasta 1.500 %, la illita ~350 % y la caolinita casi nada.
Clasificación por IP (Tabla 2.4: 0–14 baja, 15–25 media, 26–40 crítica, >40 muy crítica) y por porcentaje de
cambio de volumen (Tabla 2.5: 0–10 baja, 11–20 media, 21–30 crítica, >30 muy crítica). Zonas expansivas
citadas: sur de África, Egipto, Israel, **Venezuela (región de Coro, por su alto contenido de
montmorillonita)**, España, México y el oeste de EE. UU. Daños típicos: levantamiento de pisos, rotura de
losas, fisuración de muros, tuberías obstruidas, hasta colapso del edificio. Cuatro estrategias: **evitar,
controlar, resistir o impedir** la expansión (aislar con cámara de aire bajo placa, drenes perimetrales,
distancias mínimas a árboles de 6 m y espera de 1 año antes de construir, cimentaciones con cavidades,
conexiones flexibles, cajones rígidos, o sobrecarga de edificios altos y pesados). Cierra con la
advertencia de que el costo de reparación suele superar el costo inicial de la obra.

**Licuefacción (§2.8).** Pérdida súbita de resistencia de suelos no cohesivos sueltos saturados o arcillas
sensibles por vibración, impacto o cortante localizado, con exceso de presión hidráulica en los poros. Casos:
hinca de pilotes, explosiones y sismos. Ejemplos históricos: **Niigata (Japón, 1964)** — edificios que
colapsaron o se hundieron, cráteres de arena, gente evacuando caminando sobre las fachadas inclinadas—,
**Puerto Montt (Chile, 1960)**, **Valdivia (1963)**, **Alaska (1964 y 1966)** y el flujo deslizante de
**Kansu (China, 1920)** sobre loess, que cubrió unos 10.000 km². Aplicación directa: los muros de contención
con relleno licuable y las tablestacas ancladas en el mar son los casos críticos.

**Heladas y deshielos (§2.9).** Al congelarse, el agua aumenta ~10 % su volumen y provoca movimientos
diferenciales; al deshelarse aparece un lodo que ablanda el suelo. La cota de congelamiento suele estar a
menos de 1,2 m en zonas no excesivamente frías: **fundar por debajo de esa cota**. En arcillas, el nivel
freático alto favorece la formación de **lentes de hielo**. Soluciones: sustituir la capa superficial por
suelo granular compactado, aditivos químicos (p. ej. polifosfatos de sodio), capas aislantes de asfalto o
geotextiles impermeables. En **zonas de permahielo** (Alaska, Antártida, Groenlandia, parte de Canadá y
Rusia; el estrato congelado puede alcanzar 300 m, con una “zona activa” que se descongela en verano) se
recomienda usar pilotes prefabricados de concreto o madera, cuidando que el calor de las tuberías de
calefacción no derrita el hielo bajo las fundaciones.

### 4.3 Capítulo 8 — Fundaciones Directas Aisladas y Continuas

**Generalidades (§8.1).** Fundaciones **directas** son las que se apoyan en toda el área de su base sobre
el terreno, en un estrato **no mayor a 5 m** de profundidad, con asentamientos moderados. Clasificación
(Fig. 8.1): aisladas, continuas (corridas), combinadas, conectadas y placas de fundación. Se materializan
normalmente en concreto armado y, por excepción, en concreto simple o ciclópeo. Detalles constructivos:
capa de concreto pobre de 10 a 15 cm (o piedra y arena apisonadas) antes de vaciar la base; concreto pobre
de 150–200 kg de cemento por m³; excavar los últimos 20 cm inmediatamente antes de vaciar. El diseño se
divide en dos etapas: **análisis** (forma y dimensiones en planta, con cargas de servicio y esfuerzos
admisibles) y **diseño** (altura útil, cantidad y distribución del acero, con cargas mayoradas y
resistencias minoradas).

Criterio de combinación de cargas:
1. combinación más desfavorable **sin** sismo → no superar el esfuerzo admisible;
2. combinación **con** sismo → no superar el esfuerzo admisible incrementado en **33 %**;
   además, el área traccionada de la base no puede superar el **25 %** de la superficie de contacto.
Siempre se busca que el baricentro de las cargas coincida con el de la base; en bases excéntricas se
verifica a deslizamiento y volcamiento (remite al Capítulo 15).

**Pedestales, vigas de riostra y bases sin armar (§8.2, págs. 249–252).** Los pedestales son
ensanchamientos en la base de las columnas: reparten mejor la carga, reducen momentos flectores y cortantes
en la zapata y dan estabilidad al conjunto; se vacían con las bases y su altura suele estar entre 1 y 1,5 m.
Las **vigas de riostra** encadenan las bases en dos direcciones ortogonales (obligatorias en zona sísmica),
forman un retículo que impide desplazamientos laterales y rigidizan el conjunto. Secciones mínimas: 25 cm de
lado si van encofradas (recubrimiento ≥ 4 cm) y **40 cm** de lado si se vacían directamente en zanja. Se
arman con un mínimo de 4 barras longitudinales en los vértices (Φ mínimo 1/2″) y estribos Φ 3/8″. Su
armadura debe cumplir las ecuaciones 8.1 a 8.6, que incluyen la tracción por encadenado (Φ A_s = 0,15 P_u),
la esbeltez/pandeo (ec. 8.3) y las cuantías mínimas. Las **bases de concreto sin armar** son dados de gran
altura con β = 50–60°, en las que la tracción se mantiene bajo f_t = 0,1 f_c′.

**Bases aisladas cuadradas (§8.3).** Perfiles habituales: planas y troncopiramidales (también troncocónicas
y escalonadas; normalmente se construyen sin encofrado). El predimensionado usa cargas de servicio
mayoradas por el factor **ν** para incluir peso propio de la base y del relleno, Tabla 8.1:

| Profundidad de apoyo H | ν |
|---|---|
| H ≤ 1,5 m | 1,15 |
| 1,5 < H ≤ 3 m | 1,20 |
| 3 < H ≤ 5 m | 1,30 |

A_req = ν·P/σ_adm (ec. 8.7) y B = √A, redondeando por exceso a múltiplos de 5 cm. El peso específico
equivalente del conjunto base + hueco se toma ≈ **2.100 kg/m³** (promedio entre concreto 2.400–2.500 y suelo
1.700–2.000). El diseño toma la reacción ficticia σ_u = P_u/A (ec. 8.8) y verifica:

- momento por flexión en los planos tangentes a la cara de la columna (ec. 8.9);
- **corte simple** a la distancia d de la cara, V_u = σ_u·B·c (ecs. 8.10–8.11), resistido sólo por el
  concreto: v_c = 0,53√f_c′ con φ = 0,85 (ec. 8.12);
- **punzonado** en el perímetro crítico a d/2 (ecs. 8.14–8.16), con v_c = 1,06√f_c′ (ec. 8.17);
  en bases aisladas **suele ser el punzonado el que controla**;
- **aplastamiento** columna–zapata (ecs. 8.20–8.21, con √(A₂/A₁) ≤ 2);
- acero por flexión (ec. 8.22) y acero mínimo de la Sección 7.7.

Recomendaciones prácticas de armado: 4 barras por metro (s/25 cm), 5 por metro (s/20), 8 por metro
(s/12,5) y 10 por metro (s/10), sin bajar de 10 cm ni pasar de 25 cm de separación; barras en dos
direcciones ortogonales; recubrimiento lateral de 7 cm en los extremos.

**Tablas 8.2 a 8.6 — prediseño de bases cuadradas.** Cinco tablas con σ_adm = 1; 1,5; 2; 2,5 y 3 kg/cm²
para f_c′ ≥ 210 kg/cm², que dan directamente dimensiones B, altura útil d, carga última P_u, presión última
σ_u, momento último M_u y el acero por metro según f_y = 2.800, 3.000, 3.500 y 4.200 kg/cm².

**Ejemplo 8.1 (base cuadrada centrada).** CP = 156 t, CV = 84 t, columna de 60 cm, f_c′ = 250 kg/cm²,
f_y = 3.500, σ_adm = 2,5 kg/cm², H = 2,1 m, γ_s = 1.800 kg/m³. Resultado: ν = 1,2 → A_req = 115.200 cm² →
**B = 3,40 m**; d = 30 cm no cumple a corte, se adopta **d = 55 cm (h = 65 cm)**; punzonado
v_u = 14,88 < 16,76 kg/cm² (cumple); aplastamiento cumple; acero 66,7 cm² → **5/8″ c/10 cm** (19,8 cm²/m);
longitudes de desarrollo 36,8 cm y 46,75 cm < 133 cm disponibles. El ejemplo continúa con el **diseño de
las vigas de riostra** (luz libre 4 m, sección 40 × 40 cm, acero 8 Φ 3/4″, estribos 3/8″ c/20 cm).

**Bases aisladas rectangulares (§8.4).** Sólo se admiten cargas centradas si **B_x/B_y ≥ 0,5** (ec. 8.33);
cuando se excede esa relación hay que combinar la base con fundaciones vecinas para eliminar la flexión
excesiva en la dirección larga. Se calculan alturas útiles independientes para cada eje crítico de momentos
(ecs. 8.36–8.38) y se toma la mayor como d. Corte simple en los planos 1-1 y 2-2 (ecs. 8.39–8.42) y
punzonado con perímetro b_o = 2(b_x + b_y + 2d) (ec. 8.43). Distribución del acero: el de la dirección larga
se reparte uniformemente en todo el ancho; el de la **dirección corta se concentra en la banda centrada** de
ancho igual al lado menor, con A_s2 = 2A_sy/(β + 1) (ecs. 7.66 y 7.67), y el resto se reparte fuera de la
banda. Cuando hay que limitar la altura sin armadura a corte, se proponen alternativas (Fig. 8.9): nervios
longitudinales (viga T), **pedestal troncopiramidal** que ensancha la columna, y bases con nervios
transversales y diagonales — todas encarecen el acero y exigen encofrado.

**Ejemplo 8.2 (base rectangular).** CP = 125 t, CV = 85 t, columna 65 × 50 cm, B_x fijado por construcción
en 2,8 m, H = 3,2 m, σ_adm = 2 kg/cm², f_c′ = 280, f_y = 4.200. Resultado: ν = 1,3 → A_req = 13,65 m² →
**B_x × B_y = 2,8 × 4,9 m** (relación 1,75 < 2, correcto); P_u = 1,4CP + 1,7CV = **319,5 t** →
σ_u = 2,33 kg/cm²; d = 55 cm cumple corte simple (7,85 y 3 kg/cm² < 8,67) y punzonado
(13,79 < 17,73 kg/cm²); acero 3/4″ c/10 cm en x y 1/2″ c/10 cm en la banda central en y.

**Bases continuas para muros (§8.5).** Pueden ser de concreto sin armar (sólo cargas reducidas, p. ej.
paredes de mampostería sin sobrecargas importantes) o armadas, para las que se recomienda
d = (B − b)/4 (ec. 8.44). La reacción del suelo se supone uniforme; el acero principal se coloca
perpendicular al muro y en la dirección paralela sólo se dispone acero de retracción y temperatura. El
ancho requerido es B = ν·P/σ_adm (ec. 8.45). Momentos de diseño por metro de ancho (ec. 8.47) y verificación
sólo **a corte simple** a la distancia d (ecs. 8.49–8.50). Se recomienda una **viga de encadenado** que
conecte todas las bases de muros y columnas en dos direcciones, con mínimo 4 Φ 5/8″ y estribos Φ 3/8″ con
s ≤ 25 cm.

**Ejemplo 8.3 (base continua de muro de mampostería).** CP = 6 t/m, CV = 4,4 t/m, muro de 30 cm,
f_c′ = 210, f_y = 2.800, σ_adm = 1 kg/cm², γ_s = 1.700, H = 0,75 m. Resultado: ν = 1,15 → B_req = 120 cm →
**B = 1,2 m**; P_u = 15,88 t/m; d = 25 cm (h = 35 cm) cumple corte (2 < 7,68 kg/cm²); el acero calculado
(3,2 cm²/m) es menor que el mínimo → **5/8″ c/25 cm en ambas direcciones**.

**Bases continuas para una fila de columnas (§8.6).** Se comportan como vigas sobre fundación elástica. Se
cita el resultado de Stuttgart y Netzel: la concentración de presiones bajo la base crece con la
deformabilidad de la zapata y la rigidez del suelo, mientras las solicitaciones de flexión disminuyen al
aumentar la rigidez del suelo. Criterio de rigidez con la rigidez relativa 4E_cI/(K·B) (ec. 8.51) y la
separación entre columnas S:

- **Caso I — base rígida**: S ≤ (π/4)·L_e aproximadamente (ec. 8.52, con variantes 8.53 y el límite 8.54
  s ≤ 1,75 L_e). Es aceptable suponer distribución uniforme o lineal de presiones si las cargas de columnas
  adyacentes y las luces no difieren en más del 20 %; los momentos y cortantes se obtienen por estática.
- **Caso II — base flexible**: S mayor (ecs. 8.55–8.56) → diseñar como viga sobre fundación elástica
  (remite a bibliografía) o con métodos aproximados: diagrama trapecial de presiones bajo cada columna
  (σ = K·Δ, ec. 6.16), prolongando la base en las columnas de borde una distancia a ≈ … (ec. 8.57) y
  verificando σ_adm.
En todos los casos se colocan vigas de enlace para rigidizar, y en bases corridas bajo una fila de columnas
—de ancho B limitado— **no se verifica punzonado**, sólo flexión y corte simple.

**Ejemplo 8.4 (base continua para 4 columnas).** Columnas de 40 cm con CP = 62/66/70/74 t y CV = 48/46/52/42 t,
f_c′ = 220, f_y = 3.000, σ_adm = 3 kg/cm² (arena firme de granulometría mediana), H = 3 m → ν = 1,3.
ΣP = 460 t → A_req = 20 m² → **L = 10 m, B = 2 m**; P_u = 700,4 t → σ_u = 3,5 kg/cm². Con d = 30 cm la
base resultó **flexible** (L_e = 120 cm < S), por lo que se optó por rigidizarla con una **viga de
encadenado** que sobresale del plano superior (I = 1.791.903 cm⁴; L_e = 168 cm; s + b = 304 cm cumple).
Se obtienen los diagramas envolventes de momentos (M_u máx = 48,23 t·m) y cortes, y se diseña la viga
(máx 61,5 cm < 65 cm), con acero superior 6 Φ 1″ (30,42 cm²) e inferior 6 Φ 1″, estribos cerrados 5/8″
c/15 cm y el acero transversal de la losa 7/8″ c/25 cm.

---

## 5. Valores y criterios de referencia rápida

| Tema | Valor en el texto |
|---|---|
| Fundación directa | apoyo en estrato a ≤ 5 m de profundidad |
| Mayoración de cargas (diseño) | 1,4 CP + 1,7 CV |
| Esfuerzo admisible del suelo con sismo | + 33 % |
| Área traccionada admisible (con sismo) | ≤ 25 % del área de contacto |
| Peso específico equivalente base + relleno | ≈ 2.100 kg/m³ |
| Peso específico del concreto | 2.400 – 2.500 kg/m³ |
| Peso específico del suelo | 1.700 – 2.000 kg/m³ |
| Capa de concreto pobre bajo la base | 10 – 15 cm (150–200 kg cemento/m³) |
| Viga de riostra encofrada | 25 × 25 cm, recubrimiento ≥ 4 cm |
| Viga de riostra vaciada en zanja | 40 × 40 cm |
| Armado mínimo de riostra | 4 Φ 1/2″ + estribos Φ 3/8″ |
| Separación práctica de barras en la base | 10 a 25 cm |
| Corte simple del concreto (φ = 0,85) | v_c = 0,53 √f_c′ |
| Punzonado del concreto (φ = 0,85) | v_c = 1,06 √f_c′ |
| Relación √(A₂/A₁) en aplastamiento | ≤ 2 |
| Relación de lados en bases rectangulares | B_x/B_y ≥ 0,5 |
| Relación L/h en vigas de enlace rígidas | ≤ 6 |
| γ del agua | 1.000 kg/m³ |

---

## 6. Puntos a verificar antes de citar (erratas y dudas detectadas)

Estas observaciones salen de comparar el texto con la bibliografía estándar y de revisar los pasajes donde
el propio escaneo es dudoso. **No son correcciones al libro**: son puntos que conviene confirmar en el
original antes de usarlos en un trabajo.

1. **Límites de Atterberg.** El libro dice «el físico sueco A. Atterberg estableció en **1946**…». La
   atribución histórica habitual es **Albert Atterberg**, químico/agrónomo sueco, hacia **1911**. Verificado
   a 400 dpi: el escaneo dice claramente 1946, pero probablemente convenga citar 1911.
2. **Permeabilidad: el pasaje del orden de magnitud de k (§2.3).** Se lee «Los suelos muy porosos, como las
   arenas gruesas y las gravas, tienen un valor de k de menores a 10⁻⁸ cm/seg», mientras la Tabla 2.1 de la
   misma sección asigna **> 10⁻¹ cm/s** a grava y arena gruesa. La tabla es coherente con el resto del texto;
   el pasaje del párrafo está mal transcrito por el OCR (los superíndices se pierden) o mal resuelto en la
   edición. **Verificar ese párrafo directamente en el PDF (pág. 40) antes de citarlo.**
3. **Referencias cruzadas del capítulo 8.** Casi todas las referencias internas del capítulo 8 apuntan a
   secciones de otros capítulos con su numeración original:
   - §6.4 (distribución de presiones de contacto) y §6.5 + **Tabla 6.4** (módulo de balastro K),
   - §7.1 (módulo de elasticidad del concreto), §7.3 y Tabla 7.5 (mayoración de cargas), §7.4 (vigas T y
     armadura de paramento), §7.6 (longitud de desarrollo y empalmes), §7.7 (acero mínimo), §7.8
     (envolventes), §7.11 (aplastamiento), Tabla 7.2, Tabla 7.3, Tabla 7.4, Tabla 7.7, Tabla 7.9, Tabla 7.12,
   - §3.5 (SPT), §6.16 (σ = K·Δ), §10.6 (placas de fundación), §4.12 y §4.16 (mejoramiento de suelos),
     §14.7 (estabilidad de taludes),
     **Capítulo 15** (empuje de tierras y muros) y §16.5 (fundaciones especiales).
   Como esos capítulos no vienen en los archivos entregados, varias fórmulas y criterios del capítulo 8
   quedan citados pero no desarrollados. **Se recomienda conseguir los capítulos 4, 6, 7, 10, 14, 15 y 16
   para poder aplicar el capítulo 8 completo.**
4. **Fórmulas clave del capítulo 8.** Las ecuaciones 8.3 (pandeo de la riostra), 8.7 (A_req), 8.19 (altura
   útil inicial por flexión) y 8.44 (d = (B − b)/4) aparecen fragmentadas en el escaneo. Deben tomarse del
   PDF original, no del texto OCR.
5. **Tablas 8.2 a 8.6.** Son tablas densas de 5 columnas numéricas; el OCR mezcla filas y columnas. Están
   completas y legibles en el PDF (págs. 258–262) pero no deben usarse desde la transcripción.
6. **Valores del Ejemplo 8.1.** Con B ≈ 340 cm se adoptó A = 115.600 cm² (B = 340 cm daría 115.600 exacto
   si B = 340). Verificar la coherencia de los redondeos (A_req = 115.200 cm² → B ≈ 339,4 → 340 cm). Las
   cifras internas son consistentes salvo por los residuos de redondeo propios del ejemplo.
7. **Tabla 1.6 (límites por mineral arcilloso).** Los valores de LL, LP, IP y LR están correctos en el
   escaneo, pero la fila de la montmorillonita con Fe# (tras 5 ciclos de humectación y secado) aparece
   incompleta en el OCR. Confirmar en el original.
8. **Nota de composición del libro.** El capítulo 8 remite a secciones de los capítulos 6, 7, 10, 15 y 16
   (distribución de esfuerzos, diseño estructural en concreto armado, placas de fundación, muros de
   contención, fundaciones especiales). Para aplicar el capítulo 8 completo hacen falta esos capítulos, que
   no vienen en los archivos entregados. Lo mismo vale para el Capítulo 3: sólo está la primera página.

---

## 7. Sugerencias de siguientes pasos

- **Corregir la transcripción** de las secciones que interesen (especialmente fórmulas y tablas del cap. 8)
  contra el PDF, y guardarlas como apuntes de estudio.
- **Extraer las tablas 8.2–8.6 a CSV/XLSX** usándolas como prediseño de zapatas cuadradas (σ_adm = 1 a
  3 kg/cm²), lo que resulta directamente aplicable en oficina técnica.
- **Armar un resumen de fórmulas** del capítulo 8 (numeración 8.1 a 8.57) con su rango de validez.
- **Preparar material de estudio o una presentación** (el repositorio ya tiene una plantilla de
  presentación y una presentación web en `presentacion/`) a partir de estos dos capítulos.
- Si se consiguen los capítulos 3 a 7 y 9 a 16 del mismo escaneo, el mismo pipeline de `_analisis/scripts/`
  los procesa sin cambios (sólo hay que ajustar el desplazamiento entre página de PDF y página del libro).
