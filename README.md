# tarea

## Presentación web «Los juegos del sacrificio»

Estilo holográfico rojo inspirado en el diagrama con el que Tengen explica el
juego (Jujutsu Kaisen): fondo negro con retícula roja, banners hexagonales de
borde doble, líneas de conexión con glow, esfera central pulsante, subtítulos
estilo anime y barra de pestañas/ progreso como un reproductor.

- **Archivo:** `presentacion/index.html` (8 diapositivas, reveal.js empaquetado localmente, sin internet)
- **Contenido:** portada · Tengen (figura vectorial) · diagrama de nodos · reglas · cita · cronograma · reverso del Gokumonkyō · cierre
- **Navegación:** flechas/espacio del teclado, pestañas numeradas arriba, barra roja de progreso abajo (el botón ⤢ entra en pantalla completa)

```bash
cd presentacion
python3 -m http.server 8000    # abrir http://localhost:8000
# o simplemente abrir index.html en el navegador
```

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
