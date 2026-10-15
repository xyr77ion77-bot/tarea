#!/usr/bin/env python3
"""Paso 2: reordena las cajas OCR en líneas legibles, una página por archivo.

Uso:
    python3 scripts/agrupar_lineas.py cap1      # o cap8

Por qué no basta con ordenar por la caja envolvente: el escaneo está inclinado
~1-2°, de modo que las envolventes alineadas al eje de líneas contiguas se
solapan y dos renglones distintos se mezclan. El *centro vertical* de cada
envolvente, en cambio, es exacto, así que se agrupa por ese centro con una
tolerancia derivada del paso de línea (mediana de las diferencias de centros).

En cada línea, los bloques separados por un hueco horizontal grande (p. ej. dos
columnas o el texto junto a una figura) se separan con "   |   ".
"""
import glob
import json
import os
import statistics
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = os.path.join(RAIZ, "datos_ocr")
SALIDA = os.path.join(RAIZ, "texto", "paginas")

HUECO_COLUMNA = 120  # px a 200 dpi (~1,5 cm en el original)
HUECO_PALABRA = 4    # px


def agrupar(items):
    if not items:
        return []
    for it in items:
        it["yc"] = (it["y0"] + it["y1"]) / 2.0
    items.sort(key=lambda d: d["yc"])
    centros = [it["yc"] for it in items]
    difs = [b - a for a, b in zip(centros, centros[1:]) if b - a > 4]
    paso = statistics.median(difs) if difs else 12.0
    tol = max(4.0, 0.42 * paso)

    grupos = []
    for it in items:
        mejor, mejor_d = None, None
        for g in grupos:
            d = abs(it["yc"] - g["yc"])
            if d <= tol and (mejor_d is None or d < mejor_d):
                mejor, mejor_d = g, d
        if mejor is None:
            grupos.append({"yc": it["yc"], "items": [it]})
        else:
            mejor["items"].append(it)
            mejor["yc"] = sum(x["yc"] for x in mejor["items"]) / len(mejor["items"])
    grupos.sort(key=lambda g: g["yc"])

    lineas = []
    for g in grupos:
        g["items"].sort(key=lambda d: d["x0"])
        piezas, actual, prev = [], [], None
        for it in g["items"]:
            if prev is not None and it["x0"] - prev["x1"] > HUECO_COLUMNA:
                piezas.append(actual)
                actual = []
            actual.append(it)
            prev = it
        if actual:
            piezas.append(actual)
        textos = []
        for pieza in piezas:
            partes = []
            for i, it in enumerate(pieza):
                t = it["txt"].strip()
                if not t:
                    continue
                if partes:
                    partes.append(" " if it["x0"] - pieza[i - 1]["x1"] > HUECO_PALABRA else "")
                partes.append(t)
            textos.append("".join(partes))
        lineas.append({"yc": g["yc"],
                       "x0": min(d["x0"] for d in g["items"]),
                       "x1": max(d["x1"] for d in g["items"]),
                       "texto": "   |   ".join(textos)})
    return lineas


def main(tag):
    os.makedirs(SALIDA, exist_ok=True)
    archivos = sorted(glob.glob(os.path.join(ENTRADA, f"{tag}_pdf_*.json")))
    for ruta in archivos:
        datos = json.load(open(ruta, encoding="utf-8"))
        lineas = agrupar([dict(it) for it in datos["items"]])
        destino = os.path.join(SALIDA, f"{tag}_libro_{datos['pagina_libro']:03d}.txt")
        with open(destino[:-4] + ".lineas.json", "w", encoding="utf-8") as fh:
            json.dump({"pagina_libro": datos["pagina_libro"], "lineas": lineas},
                      fh, ensure_ascii=False)
        with open(destino, "w", encoding="utf-8") as fh:
            fh.write(f"# {tag} · página del libro {datos['pagina_libro']} "
                     f"(página {datos['pagina_pdf']} del PDF)\n")
            for ln in lineas:
                sangria = "  " if ln["x0"] > 400 else ""
                fh.write(sangria + ln["texto"] + "\n")
    print(f"[{tag}] {len(archivos)} páginas reordenadas")


if __name__ == "__main__":
    main(sys.argv[1])
