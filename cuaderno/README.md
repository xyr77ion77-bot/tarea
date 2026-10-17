# Cuaderno de cálculos — Auditorio UPT Barlovento «Argelia Laya»

Documento HTML autocontenido (sin internet, sin librerías) con **todos los cálculos**
del auditorio, presentados paso a paso como un examen: geometría del doble arco,
cargas, análisis global, sismo, correas, cercha, soldadura, columnas, placa base,
tirante, **zapatas aisladas**, riostras, losa y graderío, más la planilla general
de demanda/capacidad y las figuras SVG (fuerzas, DFC/DMF, zapata, columna, viga,
soldadura y gráfico D/C).

## Archivos

| Archivo | Qué es |
|---|---|
| `cuaderno.html` | **el cuaderno** (archivo único, se abre con doble clic) |
| `calculos.py` | los 13 bloques de cálculo; fuente única de todos los números |
| `svg.py` | las 9 figuras SVG, generadas con los números de `calculos.py` |
| `hcom.py`, `sec_a.py`…`sec_d.py` | CSS, plantillas y texto del cuaderno |
| `gen_html.py` | regenera `cuaderno.html` |

## Cómo se usa

```bash
python3 calculos.py     # imprime la planilla completa en texto (comprobación rápida)
python3 gen_html.py     # regenera cuaderno.html
```

Si se cambia un dato de entrada en `calculos.py`, se vuelve a ejecutar `gen_html.py`
y el cuaderno y la planilla se actualizan: no hay cifras escritas a mano en el HTML.
