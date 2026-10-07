# tarea

## Plantilla de presentación (PowerPoint)

Este repositorio contiene un script en Python que genera una plantilla de
presentación `.pptx` con 10 diapositivas de ejemplo: portada, índice,
introducción, objetivos, desarrollo, resultados (con gráfico), datos clave
(con tabla), conclusiones y cierre.

### Requisitos

- Python 3.10 o superior
- `pip install python-pptx`

### Uso

```bash
python generar_presentacion.py              # crea presentacion.pptx
python generar_presentacion.py mi_tema.pptx # nombre personalizado
```

### Personalización

Edita la sección **CONFIGURACIÓN** al inicio de `generar_presentacion.py`:

- `TITULO`, `SUBTITULO`, `AUTOR`, `FECHA`, `CONTACTO`
- `COLORES`: paleta de la presentación
- El contenido de cada diapositiva está en las funciones `diapositiva_*`

El archivo `presentacion.pptx` incluido ya está generado por si prefieres
editar directamente en PowerPoint.
