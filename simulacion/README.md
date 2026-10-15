# `simulacion/` — simulación 2D del pórtico del auditorio

Subdirectorio de la petición «**simulación en 2D para ver las cargas en acción, movimiento
lateral, etc.**» del auditorio UPT Barlovento «Argelia Laya» (Higuerote).

Aquí no se inventa ningún dato: **todo sale de `../cuaderno/calculos.py`** (el módulo del
cuaderno de cálculo). Si el cuaderno cambia, basta volver a correr `solver2d.py` y la
simulación queda sincronizada.

## Archivos

| Archivo | Qué es |
|---|---|
| `AUDITORIA.md` | **auditoría de la petición**: qué se puede modelar con lo ya calculado, qué falta, qué decisiones hay que tomar, limitaciones y las preguntas para el usuario |
| `modelo.py` | arma el modelo 2D (22 nudos, 44 barras): geometría del arco según el diseño, secciones, cargas por caso, articulación arco–pilar. Escribe `modelo.json` |
| `solver2d.py` | **solver propio** de pórtico plano por rigidez directa (barras de pórtico + bielas articuladas, Python puro: no requiere `numpy`). Verifica, corre los 5 casos y escribe `resultados.json` + `datos.js` |
| `modelo.json` | geometría, secciones, cargas y casos (generado) |
| `resultados.json` | desplazamientos por nudo, axiales, momentos, deriva y D/C de los 5 casos (generado) |
| `datos.js` | `modelo.json` + `resultados.json` embebidos para el visor (generado) |
| `index.html` · `app.js` | **visor animado**: cargas, deformada amplificada, axiales con color, deriva y momentos en los pilares |

## Cómo se corre

```bash
cd simulacion
python3 modelo.py      # 22 nudos, 44 barras, 5 casos
python3 solver2d.py    # verifica y resuelve; escribe resultados.json + datos.js
python3 -m http.server 8001 --bind 0.0.0.0     # abrir http://localhost:8001/
```

El visor también funciona abriendo `index.html` desde el disco (no necesita servidor).

## Casos de carga que trae

| Clave | Combinación |
|---|---|
| `servicio` | D + L (sin mayorar) |
| `mayorada` | 1,2D + 1,6L |
| `sismo_R6` | 1,2D + 0,5L + S (R = 6, Cd = 4,25) |
| `sismo_R2` | 1,2D + 0,5L + S (R = 2, Cd = 4,25) |
| `sin_tirante` | 1,2D + 1,6L sin el tirante de cabeza |

## Verificación del solver (antes de creerle a cualquier número)

| Comprobación | Teoría | Solver | Error |
|---|---|---|---|
| Pilar en voladizo Δ = P·h³/(3EI) | 2,006 cm | 2,006 cm | 0,00 % |
| Viga apoyada δ = 5wL⁴/(384EI) | 0,871 cm | 0,871 cm | 0,00 % |
| Arco funicular con tirante T = qL²/(8f) | 13.520 kg | 13.520 kg | 0,00 % |
| Equilibrio vertical ΣR = ΣF | 20.190 kg | 20.190 kg | 0,00 % |
| Reparto del empuje (arco + pilar + tirante como resortes) | 362,7 kg / 12.181,9 kg | 362,7 / 12.181,9 kg | 4 cifras |

## Resultados de la primera corrida (un pórtico de los 7)

| Caso | T tirante | H en pilar | M base | Δ tope | Cd·Δ ≤ 17 cm |
|---|---|---|---|---|---|
| Servicio | 8,48 t | 0,08 t | 0,68 t·m | 0,31 cm | 1,33 cm ✓ |
| Rotura | 12,18 t | 0,12 t | 0,98 t·m | 0,45 cm | 1,90 cm ✓ |
| Sismo R = 6 | 6,68 t | 0,45 t | 3,86 t·m | 1,76 cm | 7,48 cm ✓ |
| Sismo R = 2 | 6,68 t | 1,49 t | 12,67 t·m | 5,77 cm | **24,53 cm ✗** |
| Sin tirante | — | 0,36 t | 3,08 t·m | 1,41 cm | cordón D/C 1,11 ✗ |

Conclusiones y comparación elemento por elemento con el cuaderno en `AUDITORIA.md`.

**Pendiente:** las 5 respuestas del usuario (alcance, hipótesis sísmica, tirante, salida y
datos) que están al final de `AUDITORIA.md` para completar niveles B (dinámico) y C (3D).
