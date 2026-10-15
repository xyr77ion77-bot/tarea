# `simulacion/` — simulación 2D del pórtico del auditorio (nivel A + B)

Subdirectorio de la petición «**simulación en 2D para ver las cargas en acción, movimiento
lateral, etc.**» del auditorio UPT Barlovento «Argelia Laya» (Higuerote).

Aquí no se inventa ningún dato: **todo sale de `../cuaderno/calculos.py`** (el módulo del
cuaderno de cálculo) y de los parámetros sísmicos que ese cuaderno documenta
(COVENIN 1756‑1:2019). Si el cuaderno cambia, basta volver a correr el solver y el análisis
dinámico para que la simulación quede sincronizada.

* **Nivel A** (estático animado): `modelo.py` + `solver2d.py` + `index.html`/`app.js`.
* **Nivel B** (dinámico): `dinamica.py` + `index.html`/`app_din.js` — período fundamental,
  modo de vibración, espectro evaluado en `T₁`, comparación R = 6 contra R = 2 y oscilación
  en el tiempo.

## Archivos

| Archivo | Qué es |
|---|---|
| `AUDITORIA.md` | **auditoría de la petición**: modelo adoptado, verificación del solver, hallazgos contra el cuaderno, limitaciones, hipótesis de empuje sin tirante y las respuestas del usuario a las preguntas |
| `modelo.py` | arma el modelo 2D (22 nudos, 44 barras): geometría del arco según el diseño, secciones, áreas tributarias reales, articulación arco–pilar. Escribe `modelo.json` |
| `solver2d.py` | **solver propio** de pórtico plano por rigidez directa (barras de pórtico + bielas, Python puro, sin `numpy`): 4 verificaciones contra fórmulas cerradas, los 5 casos y el D/C de cada elemento. Escribe `resultados.json` + `datos.js` |
| `dinamica.py` | **nivel B**: masas sísmicas reales por nudo, autovalores por Jacobi con los giros condensados (Guyan), modos con participación y masa efectiva, espectro evaluado en `T₁` y los campos de desplazamiento modal. Escribe `modal.json` + `datos2.js` |
| `modelo.json` · `resultados.json` · `modal.json` | datos generados (no editar a mano) |
| `datos.js` · `datos2.js` | los mismos datos embebidos para el visor (generados) |
| `index.html` · `app.js` | **visor nivel A**: cargas, deformada amplificada, axiales con color, deriva, momentos en los pilares y la oscilación sísmica con el período real `T₁` |
| `app_din.js` | **visor nivel B**: comparación animada R = 6 / R = 2 lado a lado, modo fundamental con sus fuerzas inerciales, gráfico del espectro y tablas estático‑contra‑dinámico y *sin tirante: dos hipótesis* |

## Cómo se corre

```bash
cd simulacion
python3 modelo.py                  # 22 nudos, 44 barras, 5 casos
python3 solver2d.py                # verifica y resuelve; escribe resultados.json + datos.js
python3 dinamica.py                # nivel B; escribe modal.json + datos2.js
python3 -m http.server 8001 --bind 0.0.0.0     # abrir http://localhost:8001/
```

El visor también funciona abriendo `index.html` desde el disco (no necesita servidor).

## Casos de carga que trae

| Clave | Combinación |
|---|---|
| `servicio` | D + L (sin mayorar) |
| `mayorada` | 1,2D + 1,6L (con el peso propio real) |
| `sismo_R6` | 1,2D + 0,5L + S (R = 6, Cd = 4,25) |
| `sismo_R2` | 1,2D + 0,5L + S (R = 2, Tipo IV) |
| `sin_tirante` | 1,2D + 1,6L sin el tirante de cabeza |

## Verificación del solver (antes de creerle a cualquier número)

| Comprobación | Teoría | Solver | Error |
|---|---|---|---|
| Pilar en voladizo Δ = P·h³/(3EI) | 2,00576 cm | 2,00576 cm | 0,00 % |
| Viga apoyada δ = 5wL⁴/(384EI) | 0,87051 cm | 0,87051 cm | 0,00 % |
| Arco funicular con tirante T = qL²/(8f) | 13.520,4 kg | 13.520,4 kg | 0,00 % |
| Equilibrio vertical ΣR = ΣF | 20.189,6 kg | 20.189,6 kg | 0,00 % |
| Reparto del empuje (arco + pilares + tirante como resortes) | 362,69 / 12.181,85 kg | 362,6897 / 12.181,85 kg | 6 cifras |

Comprobación del nivel B: `T₁ = 0,875 s` del autovalor contra `2π√(m/k) = 0,918 s` con
`k = 2·3EI/h³` (0,5 % de diferencia, por la flexibilidad de corte del pilar).

## Resultados (un pórtico de los 7)

| Caso | T tirante | H en el pilar | M base | Δ sísmica | Cd·Δ ≤ 17 cm |
|---|---|---|---|---|---|
| Servicio | 8,48 t | 0,08 t | 0,68 t·m | — (aplanamiento 0,31 cm) | no aplica |
| Rotura | 12,18 t | 0,12 t | 0,98 t·m | — (aplanamiento 0,45 cm) | no aplica |
| Sismo R = 6 | 6,68 t | 0,58 t (gobierna el pilar derecho) | 4,94 t·m | 2,006 cm | 8,52 cm ✓ |
| Sismo R = 2 | 6,68 t | 1,62 t | 13,75 t·m | 6,017 cm | **25,57 cm ✗** |
| Sin tirante | — | 0,36 t | 3,08 t·m | — | cordón D/C 1,11 ✗ |

Nivel B (mismo pórtico, masas sísmicas reales de 10,81 t contra 7,80 t de la planilla):

| Magnitud | Cuaderno | Dinámico (nivel B) |
|---|---|---|
| Período fundamental | — | `T₁ = 0,875 s` (f = 1,14 Hz), Γ₁ = 1,001, 90,8 % de la masa |
| Ordenada espectral | Ad(Ta) = 0,1380 | Ad(T₁) = 0,1276 (7,6 % menos: T₁ > TC) |
| Cortante basal por pórtico | 1,04 t | 1,21 t (+17 % por el peso real) |
| Deriva Cd·δ (R = 6) | 8,52 cm ✓ | 9,92 cm ✓ |
| Deriva Cd·δ (R = 2) | 25,57 cm ✗ | 29,76 cm ✗ |

Conclusiones y comparación elemento por elemento con el cuaderno en `AUDITORIA.md` (§5 y §9.1).
