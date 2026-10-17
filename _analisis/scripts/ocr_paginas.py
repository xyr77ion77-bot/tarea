#!/usr/bin/env python3
"""Paso 1 del pipeline: OCR de un PDF escaneado página por página.

Uso:
    python3 scripts/ocr_paginas.py cap1        # o cap8

Requisitos: pymupdf, pillow, numpy, rapidocr-onnxruntime.
Salida: datos_ocr/<tag>_pdf_NNN.json  con las cajas de texto reconocidas
        (coordenadas en px a 200 dpi sobre un render de 2550x3300).

Los PDF de origen son escaneos de 1 bit (una imagen PNG por página); se renderiza
a 200 dpi, resolución más que suficiente porque el original está a ~200 dpi.

El OCR se ejecuta con la detección y el reconocimiento de RapidOCR; el resultado
viene en polígonos ligeramente rotados (el escaneo está inclinado ~1°), por eso
sólo se conservan las coordenadas de la caja envolvente y el centro vertical.
"""
import json
import os
import sys
import time

import numpy as np
import pymupdf
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = "/tmp/arena-coding-uploads"
SALIDA = os.path.join(RAIZ, "datos_ocr")
DPI = 200

DOCS = {
    "cap1": ("Fundaciones y Muros_cap 1.pdf", 10),   # pdf 1 = libro 11
    "cap8": ("Fundaciones y Muros_cap 8.pdf", 245),  # pdf 1 = libro 246
}


def main(tag):
    archivo, offset = DOCS[tag]
    ocr = RapidOCR()
    doc = pymupdf.open(os.path.join(ENTRADA, archivo))
    os.makedirs(SALIDA, exist_ok=True)
    for i, page in enumerate(doc):
        destino = os.path.join(SALIDA, f"{tag}_pdf_{i+1:03d}.json")
        if os.path.exists(destino):
            print(f"[{tag}] página {i+1} ya procesada", flush=True)
            continue
        t0 = time.time()
        pix = page.get_pixmap(dpi=DPI)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        res, _ = ocr(np.array(img))
        items = []
        for x0, y0, x1, y1, txt, score in res or []:
            items.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1,
                          "txt": txt, "score": float(score)})
        with open(destino, "w", encoding="utf-8") as fh:
            json.dump({"archivo": tag, "pagina_pdf": i + 1,
                       "pagina_libro": i + 1 + offset, "items": items},
                      fh, ensure_ascii=False)
        print(f"[{tag}] página {i+1}/{len(doc)} en {time.time()-t0:.1f}s "
              f"({len(items)} cajas)", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
