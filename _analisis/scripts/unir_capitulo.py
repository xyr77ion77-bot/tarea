#!/usr/bin/env python3
"""Paso 3: une las páginas reordenadas en un texto continuo por capítulo.

Uso:
    python3 scripts/unir_capitulo.py cap1
    python3 scripts/unir_capitulo.py cap8

Reglas:
- descarta el número de página suelto del encabezado;
- un bloque propio para viñetas, títulos, encabezados de sección, fórmulas,
  pies de figura/tabla y encabezados de ejemplo;
- une líneas sucesivas de un mismo párrafo: una línea que arranca en el margen
  izquierdo continúa el párrafo anterior, una línea indentada inicia párrafo
  nuevo (así están compuestos los originales mecanografiados).
"""
import glob
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = os.path.join(RAIZ, "texto", "paginas")

VINETA = re.compile(r"^\s*(-|•|\*|[a-z]\)|[0-9]\)|\([a-z0-9]+\))\s")
SECCION = re.compile(r"^[0-9]+\.[0-9]+")
TITULO = re.compile(r"^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9 ,\.\-'\(\)]{5,}$")
PIE = re.compile(r"(Figura|F1gura|TABLA|Tabla|EJEMPLO|EJEMPL0|Secci[oó]n)\s?\d")


def es_inicio(t):
    if len(t) < 95 and SECCION.match(t):
        return True
    return bool(VINETA.match(t) or TITULO.match(t) or PIE.search(t))


def es_formula(t):
    return "   |   " in t or "=" in t


def unir(paginas):
    parrafos, buf = [], []
    for pagina in paginas:
        for ln in pagina["lineas"]:
            t = ln["texto"].strip()
            if not t:
                continue
            if re.fullmatch(r"[0-9]{1,3}", t):      # número de página
                continue
            if es_inicio(t) or es_formula(t):
                if buf:
                    parrafos.append(" ".join(buf)); buf = []
                parrafos.append(t)
                continue
            izquierda = ln["x0"] < 300
            if buf and izquierda:
                buf.append(t)
            elif buf:
                parrafos.append(" ".join(buf)); buf = [t]
            else:
                buf = [t]
    if buf:
        parrafos.append(" ".join(buf))
    return parrafos


def main(tag):
    archivos = sorted(glob.glob(os.path.join(ENTRADA, f"{tag}_libro_*.lineas.json")))
    paginas = [json.load(open(a, encoding="utf-8")) for a in archivos]
    parrafos = unir(paginas)
    ini = paginas[0]["pagina_libro"]
    fin = paginas[-1]["pagina_libro"]
    salida = os.path.join(RAIZ, "texto", f"{tag}_libro_pag{ini:03d}-{fin:03d}.txt")
    with open(salida, "w", encoding="utf-8") as fh:
        fh.write(f"# {tag} · texto continuo, páginas {ini}-{fin} del libro "
                 f"(OCR automático, sin corregir)\n")
        for t in parrafos:
            fh.write(t + "\n")
    print(f"{salida}: {len(parrafos)} bloques de {len(archivos)} páginas")


if __name__ == "__main__":
    main(sys.argv[1])
