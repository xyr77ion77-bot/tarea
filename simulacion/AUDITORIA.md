# Auditoría de la petición — «simulación en 2D para ver las cargas en acción y el movimiento lateral»

> Documento de trabajo del subdirectorio `simulacion/`. Audita la petición **antes** de invertir
> en la simulación completa: qué se puede hacer ya con los datos del cuaderno, qué falta, qué
> decisiones hay que tomar y qué se armó y verificó en esta primera entrega parcial.
> Fecha: 2026-10-15 · Estructura: auditorio UPT Barlovento «Argelia Laya», Higuerote.

---

## 0 · Resumen

| Punto | Estado |
|---|---|
| Subdirectorio propio para la petición | `simulacion/` (este directorio) |
| Datos de entrada | se leen de `../cuaderno/calculos.py` — **no se recalcula nada a mano** |
| Modelo 2D | pórtico plano transversal, 22 nudos, 44 barras, 56 GDL libres |
| Solver | rigidez directa en Python puro (sin `numpy`): barras de pórtico y bielas articuladas |
| Verificación | 4 comprobaciones contra fórmulas cerradas (error 0,00 %) + 1 comprobación de resortes con coincidencia a 4 cifras |
| Primera corrida | 5 casos de carga (servicio, rotura, sismo R = 6, sismo R = 2, sin tirante) |
| Visor animado | `index.html` (cargas, deformada, axiales y deriva) |
| Preguntas al usuario | §8 — 5 puntos, se responden antes de programar lo que falta |

---

## 1 · La petición, traducida a un modelo

«Una simulación en 2D para ver las cargas en acción, movimiento lateral, etc.» se puede leer como
tres cosas distintas, que cuestan cosas distintas:

| Nivel | Qué muestra | Qué exige |
|---|---|---|
| A · **Estático animado** | la deformada real de cada caso, las cargas entrando, la deriva lateral, los axiales con color | nada nuevo: los datos y las secciones ya están |
| B · **Dinámico** | modo y período de vibración, oscilación en el tiempo ante un sismo, amplificación | matriz de masas, período T, registro o espectro de diseño (COVENIN 1756‑1:2019 §7), más tiempo de cómputo |
| C · **3D / los 7 pórticos** | torsión, diafragma de cubierta, arriostramiento longitudinal, "el edificio entero" | modelo espacial completo, ~600 nudos: conviene un programa matricial externo (el solver propio se vuelve impráctico) |

En esta entrega se armó y verificó el **nivel A** completo. Los niveles B y C son ampliaciones
que se cuelgan del mismo modelo (ver §8 y §9).

---

## 2 · Materia prima: qué ya existe y qué falta

### 2.1 Lo que ya está calculado y sirve tal cual (de `cuaderno/calculos.py`)

| Dato | Valor | Uso en la simulación |
|---|---|---|
| Geometría | L = 17,60 m; f = 2,50 m; d = 0,80 m; h = 8,50 m; S = 4,10 m; 7 pórticos | nudos del arco |
| R_sup / R_inf / θ | 16,738 / 15,938 m / 31,7187° (semiángulo) | 9 nudos por cordón a igual ángulo |
| Cargas | D = 23; colgadas = 15; L = 100 kg/m²; PP 60 kg/m | q por caso |
| Sismo | AA = 0,345; Ad = 0,138 (R = 6) / 0,414 (R = 2); Cd = 4,25; V_col = 517,9 / 1.553,7 kg | fuerza lateral en la cabeza del pilar |
| Secciones | HEB 300; 2×IPE 160 (cordones, A = 40,2 cm²); IPE 160 (diagonales); IPE 120 (montantes); Ø1‑1/2″ (tirante) | áreas, inercias, pesos |
| Empuje | H_u = 14.171 kg = q_u·L²/(8f) | comparación con el modelo |
| Deriva límite | 17,0 cm (el del cuaderno) | semáforo del visor |

### 2.2 Lo que falta (y que el modelo no puede inventar)

| Falta | Consecuencia en la simulación |
|---|---|
| **Estudio de mecánica de suelos** | no se puede modelar la interacción suelo–estructura ni la rigidez horizontal de la zapata (se supone base empotrada). El giro de la zapata bajo sismo añadiría deriva. |
| **Rigidez real de las conexiones** | el modelo supone cordones continuos (rígido) y diagonales/montantes articulados (rótula). Las cartelas soldadas reales quedan en un punto intermedio. |
| **Rigidez de la placa base** | la placa de 45×45×25 mm con 8 pernos Ø3/4″ trabaja con el mortero de nivelación: se supuso **empotramiento** en la base. Si se modela como apoyo articulado, la deriva aumenta (el pórtico se vuelve más flexible). |
| **Diafragma de cubierta** | define si el arco puede «abrirse» lateralmente o no (§5.3). Es la hipótesis que más pesa en el resultado «sin tirante». |
| **Posición real de la pasarela** | en el modelo la carga de pasarela (25 kg/m) cuelga del cordón inferior; si va sobre la clave, el empuje cambia poco pero el cordón inferior trabaja distinto. |
| **Viento** | excluido por el profesor; si se pidiera, es una fuerza lateral más (q_z = 47,2 kg/m², W = 138,6 kg/m). |
| **Planos definitivos** | el tirante de cabeza todavía no aparece en los planos (bandera del cuaderno). |

---

## 3 · El modelo que se armó

### 3.1 Hipótesis (todas declaradas en `modelo.py` y en el visor)

1. **Pórtico plano transversal tipo** de los 7 iguales (se toma 1/7 del cortante basal).
2. **Arco articulado** a la cabeza del pilar: es la clasificación del proyecto — sistema Tipo IV
   «columnas en voladizo con arco articulado», COVENIN 1756‑1:2019 §3.5.4, R = 2, Ωo = 1,5, Cd = 2.
   Se modela con un enlace que comparte los desplazamientos y deja libres los giros (rótula).
3. **Geometría del arco igual a la del diseño**: 9 nudos por cordón a igual ángulo (8 paneles),
   doble cordón 2×IPE 160, montantes IPE 120 de 0,80 m descontando el ángulo, diagonales IPE 160
   **en X (San Andrés)** en cada panel.
4. **Cordones y pilares**: elementos de pórtico (nudos continuos, transmiten momento).
   **Montantes, diagonales y tirante**: bielas articuladas (igual que el cálculo del cuaderno).
5. **Peso propio con las secciones reales** del catálogo (§5.3), no con el PP de la planilla.
6. Análisis **lineal elástico de primer orden**; la armadura se supone capaz de tomar el empuje
   en cualquier sentido, salvo el tirante, que se retira si sale comprimido.

### 3.2 Cómo se verificó el solver (antes de creerle a cualquier número)

| Comprobación | Fórmula cerrada | Solver | Error |
|---|---|---|---|
| Pilar en voladizo | Δ = P·h³/(3EI) = 2,006 cm | 2,006 cm | 0,00 % |
| Viga simplemente apoyada (correa IPN 140, q = 284,69 kg/m) | δ = 5wL⁴/(384EI) = 0,871 cm | 0,871 cm | 0,00 % |
| Arco funicular biarticulado con tirante | T = q·L²/(8f) = 13.520 kg | 13.520 kg | 0,00 % |
| Equilibrio vertical (caso de rotura) | ΣR = ΣF = 20.190 kg | 20.190 kg | 0,00 % |

Y una verificación independiente del reparto del empuje, con la analogía de resortes en
paralelo (arco + pilares + tirante):

- Empuje del arco con arranques fijos: **H₀ = 17.883 kg**
- Rigidez de aplanamiento del arco: **k_a = 12.473 kg/cm**
- Pilar en voladizo: **k_p = 3EI/h³ = 258 kg/cm** · Tirante: **k_t = 2EA/L = 27.205 kg/cm**
- Sin tirante: H = H₀·k_p/(k_a + k_p) = **362,7 kg** → el solver da **362,7 kg**
- Con tirante: T = H₀·k_t/(k_a + k_t + k_p) = **12.181,9 kg** → el solver da **12.181,9 kg**

Coincidencia a cuatro cifras: el modelo matricial y el modelo de resortes dicen lo mismo.

---

## 4 · Resultados de la primera corrida (un pórtico de los 7)

| Caso | q [kg/m] | T tirante | H en pilar | M base pilar | Δ tope | Cd·Δ vs 17 cm |
|---|---|---|---|---|---|---|
| Servicio D+L | 590,8 + PP | 8,48 t | 0,08 t | 0,68 t·m | 0,31 cm | 1,33 cm ✓ |
| Rotura 1,2D+1,6L | 873,0 + PP | 12,18 t | 0,12 t | 0,98 t·m | 0,45 cm | 1,90 cm ✓ |
| Sismo R = 6 | 1,2D+0,5L + S | 6,68 t | 0,45 t | 3,86 t·m | 1,76 cm | 7,48 cm ✓ |
| Sismo R = 2 | 1,2D+0,5L + S | 6,68 t | 1,49 t | 12,67 t·m | 5,77 cm | **24,53 cm ✗** |
| Rotura **sin tirante** | 1,2D+1,6L | 0 | 0,36 t | 3,08 t·m | 1,41 cm | 5,97 cm ✓ · **pero el cordón superior llega a −45,05 t y su D/C es 1,11 ✗** (ver §5.3) |

---

## 5 · Auditoría: lo que el modelo confirma, corrige y descubre

### 5.1 Lo que **confirma** (el cuaderno está bien)

| Verificación | Cuaderno | Modelo 2D | Lectura |
|---|---|---|---|
| Empuje al tirante | 14,17 t | 12,18 t | el cuaderno es **16 % conservador** para el tirante |
| Deriva R = 6 | 8,52 cm ≤ 17 ✓ | 7,48 cm ≤ 17 ✓ | cumple en los dos |
| **Deriva R = 2** | 25,57 cm ✗ | **24,53 cm ✗** | **la bandera roja se confirma** |
| Momento en la base del pilar R = 2 | 13,21 t·m (D/C 0,378) | 12,67 t·m | coincide |
| «El tirante anula el empuje» | frase del chat del proyecto | el tirante toma el **96,8 %** del empuje; el pilar el 1 % | **se confirma y se cuantifica** |

### 5.2 Lo que **corrige** (el cuaderno es conservador)

| Elemento | Cuaderno | Modelo 2D | Por qué cambia |
|---|---|---|---|
| Cordón de la cercha | N = 29,52 t → D/C 0,725 | N = 19,74 t → D/C 0,485 | el cuaderno usó el momento de **viga biempotrada** (q_u·L²/12) para el par de fuerzas del cordón; el arco biarticulado real tiene momentos menores |
| Diagonal IPE 160 | N = 12,33 t → D/C 0,667 | N = 3,54 t → D/C 0,19 | el cuaderno tomó la reacción vertical R_u como cortante del panel: **faltó descontar la componente del empuje**, S = V·cosφ − H·senφ = 2.182 kg → N = S/(2·senβ) = 3,34 t (el modelo da 3,54 t) |
| Tirante | D/C 0,546 | D/C 0,47 | efecto conjunto de lo anterior |
| Montante | D/C 0,027 | D/C 0,091 | al revés: el modelo pide **3,4× más** (sigue holgado). Además el montante del arranque mide 0,94 m, no 0,80 m |

Los aprovechamientos D/C que calcula el propio modelo (con las capacidades φPn del cuaderno) son,
para el caso de rotura con tirante: cordón 0,485 · diagonal 0,191 · montante 0,091 · tirante 0,469 ·
pilar 0,061. El montante del modelo es el único que supera al del cuaderno, y sigue muy holgado.

### 5.3 Lo que **descubre** (nuevo, y hay que decidir qué hacer con ello)

1. **El caso «sin tirante» falla, pero por otro motivo del que dice el cuaderno.
   El tirante es imprescindible: se demuestra por partida doble.**
   El cuaderno supone que el empuje completo H = 14,17 t llega a la cabeza del pilar
   → M = H·h = **120,5 t·m** → D/C 3,18 ✗. El modelo 2D permite además un segundo escenario,
   con el arranque libre de desplazarse:

   | Escenario | Qué pasa con el pilar | Qué pasa con la cercha |
   |---|---|---|
   | (B) arranque restringido (diafragma de cubierta, apoyo rígido) → el arco conserva su empuje | H ≈ 14–17 t al pilar → M ≈ 120–150 t·m → **D/C ≈ 3,2 ✗** (y la zapata desliza, FS 0,42 ✗) | trabaja como arco: N_cordón ≈ 20 t, D/C 0,49 ✓ |
   | (A) arranque libre (el 2D sin tirante) → el arco se abre 1,4 cm y pierde el empuje | H = 0,36 t → M = 3,08 t·m → D/C 0,12 ✓ | **pierde la acción de arco y trabaja como viga curva**: N_cordón sup = **−45,05 t → D/C 1,11 ✗** y diagonales 11,7 t (D/C 0,63) |

   Es decir: **sin tirante no hay escenario que cumpla** — o falla el pilar (B) o falla la
   propia cercha (A). Con el tirante, en cambio, el conjunto pasa con holgura (D/C ≤ 0,49).
   La conclusión del cuaderno («el tirante anula el empuje») queda **reforzada** por el modelo:
   no es sólo una comodidad para la fundación, es lo que mantiene al arco en régimen de arco.
   El reparto exacto de por qué el pilar sólo recibe 1 % del empuje con el tirante está en §3.2
   (resortes en paralelo: k_arco = 12,5 t/cm contra k_pilar = 0,26 t/cm).
2. **El peso propio real de la cercha es ~3 veces el de la planilla.**
   Con los perfiles del catálogo: cordones 2×IPE 160 = 63,3 kg/m; diagonales = 33,5 kg/m;
   montantes = 4,3 kg/m; tirante = 8,5 kg/m → **cercha ≈ 101 kg/m** (109,7 kg/m con el tirante)
   contra los **35 kg/m** de la planilla. Con la pasarela: **135 kg/m reales contra 60 kg/m** (+124 %).
   Efecto: el peso sísmico W sube ~18 % → V₀ sube ~18 % → la deriva R = 6 pasa de 8,5 a ~10 cm
   (sigue cumpliendo) y la de R = 2 empeora (ya no cumplía). El cuaderno ya había advertido que
   el PP estaba subestimado; el modelo le pone el número.
3. **El arranque del arco condiciona el modelo entero.** El pilar apenas participa del empuje
   (1 %); su papel real es tomar el sismo lateral como ménsula. Eso valida la clasificación
   Tipo IV y explica por qué la deriva y el momento de la base son los que gobiernan el diseño
   transversal.
4. **Efectos de segundo orden (P‑Δ):** con N_pilar = 6,13 t y Δ = 5,77 cm (R = 2),
   M_PΔ = N·Δ ≈ 0,35 t·m ≈ 3 % del momento de primer orden. No cambia conclusiones, conviene
   declararlo.

---

## 6 · Limitaciones del modelo 2D (lo que NO captura)

1. **Torsión y diafragma**: un pórtico plano no ve la torsión accidental ni la acción del
   diafragma de cubierta (COVENIN 1756‑1:2019 §9.4.5.2 exige el 6 % de excentricidad accidental).
2. **Flexión local del cordón entre correas**: en el modelo la carga entra sólo en los nudos;
   las 13 correas intermedias producen flexión local en el cordón (el cuaderno tampoco la revisa).
3. **Conexiones**: se supone rótula en las bielas y nudo rígido en los cordones; las cartelas
   reales son intermedias. Sin detalle de conexión no se puede afinar.
4. **Suelo**: base empotrada; sin EMS no hay rigidez de zapata, ni giro de fundación, ni deriva
   de fundación.
5. **Dirección longitudinal**: los arriostramientos en X (vanos 2 a 5, HEB 200) no están en este
   modelo; la simulación 2D que se pidió es del pórtico transversal.
6. **Viento, temperatura, sismo vertical, imperfecciones y montaje**: fuera de alcance declarado.
7. **No linealidad**: no se modela el pandeo real de las diagonales comprimidas ni la plasticidad.
   El cálculo lineal reparte la fuerza entre las dos diagonales de la X por igual.

---

## 7 · Datos que faltan para completar (§8 los pregunta)

1. ¿Se confirman los perfiles de la cercha del modelo (2×IPE 160 / IPE 160 / IPE 120) contra el
   plano, y se acepta el peso propio real de 101 kg/m en lugar de 35 kg/m?
2. ¿El tirante de cabeza se ejecuta? (bandera del cuaderno: no está en los planos)
3. ¿Qué hipótesis se adopta para el empuje sin tirante: la conservadora (H al pilar, M = 120 t·m)
   o la del modelo (aplanamiento, M = 3 t·m)?
4. ¿Nivel B (dinámico) y/o C (3D) se quieren, o basta A?
5. ¿Salida: página HTML animada (ya está), video/GIF para la exposición, informe en PDF?

---

## 8 · Preguntas para el usuario

1. **Alcance**: ¿nivel A (estático animado), A+B (agregar modo y período de vibración con
   oscilación en el tiempo) o A+B+C (los 7 pórticos en 3D)?
2. **Hipótesis sísmica**: ¿R = 6, R = 2, o los dos comparados lado a lado? (recordar:
   el proyecto adoptó R = 2 en ambas direcciones; R = 6 es la planilla original y es el caso
   que hace no cumplir la deriva)
3. **Tirante y arranque**: ¿el tirante se ejecuta? y ¿se adopta la hipótesis conservadora
   (empuje completo al pilar) o la del modelo (aplanamiento) para el caso sin tirante?
4. **Salida**: ¿HTML animado, o además video/GIF e informe?
5. **Datos**: ¿se confirman los perfiles del catálogo y el peso propio real? ¿dónde cuelga
   la pasarela: cordón inferior o clave?

---

## 9 · Ruta de trabajo propuesta (según las respuestas)

| Fase | Contenido | Estado |
|---|---|---|
| 1 | Modelo + solver verificado + 5 casos + visor animado | **entregado** |
| 2 | Respuestas → ajustes de hipótesis (tirante, PP real, pasarela, base articulada/empotrada) | siguiente |
| 3 | Nivel B: matriz de masas, autovalores (T₁), oscilación en el tiempo con el espectro de COVENIN 1756‑1:2019 §7 | opcional |
| 4 | Nivel C: 3D de los 7 pórticos + diafragma + arriostramiento longitudinal | opcional |
| 5 | Video/GIF + informe de resultados para la memoria | opcional |

---

## 10 · Cómo se corre

```bash
cd simulacion
python3 modelo.py      # escribe modelo.json (geometría, cargas, casos)
python3 solver2d.py    # verifica, resuelve los 5 casos y escribe resultados.json + datos.js
python3 -m http.server 8001 --bind 0.0.0.0   # visor: http://localhost:8001/index.html
```

Los números de partida salen de `../cuaderno/calculos.py`; si el cuaderno cambia, basta volver a
correr `solver2d.py` para que la simulación quede sincronizada.

**Bibliografía citada:** COVENIN 1756‑1:2019 (sismo), COVENIN 1618‑98 / NTF 1618‑2 (acero),
COVENIN 810‑1998 (salidas), Fratelli, M. G., *Suelos, Fundaciones y Muros* (fundaciones).
