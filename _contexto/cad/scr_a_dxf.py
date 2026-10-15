#!/usr/bin/env python3
"""Convierte un script de AutoCAD (.scr con _LINE / _ARC / _TEXT / _-LAYER) a DXF.

Motivo: el .scr depende del idioma, del separador decimal y de la regla
"línea en blanco = Enter" (la causa del error «comando M inválido»). El DXF no
tiene ninguno de esos problemas: se abre en AutoCAD 2018 con ARCHIVO > ABRIR.

Uso:
    python3 scr_a_dxf.py CT01.scr CT01.dxf
    python3 scr_a_dxf.py CT01.scr CT01.dxf --png CT01_preview.png
"""
import argparse
import math
import os
import sys

import ezdxf
from ezdxf.addons.drawing import matplotlib as ezmpl


def leer_scr(ruta):
    """Devuelve (capas, entidades) con el subconjunto de comandos que usamos."""
    lineas = [l.strip() for l in open(ruta, encoding="ascii", errors="replace")]
    capas, entidades = {}, []
    capa_actual = "0"
    i = 0
    while i < len(lineas):
        cmd = lineas[i].upper().lstrip("_-")
        if cmd == "LAYER":
            # _-LAYER / _M nombre / _C color nombre / [_S nombre]
            j = i + 1
            while j < len(lineas) and lineas[j].strip():
                op = lineas[j].upper().lstrip("_-")
                if op == "M" and j + 1 < len(lineas):
                    capa_actual = lineas[j + 1].strip()
                    capas.setdefault(capa_actual, 7)
                    j += 2
                elif op == "C" and j + 2 < len(lineas):
                    color = int(float(lineas[j + 1]))
                    nombre = lineas[j + 2].strip()
                    capas[nombre] = color
                    j += 3
                elif op == "S" and j + 1 < len(lineas):
                    capa_actual = lineas[j + 1].strip()
                    capas.setdefault(capa_actual, 7)
                    j += 2
                else:
                    j += 1
            i = j
            continue
        if cmd == "LINE" and i + 2 < len(lineas):
            p1 = punto(lineas[i + 1])
            p2 = punto(lineas[i + 2])
            entidades.append(("LINE", capa_actual, p1, p2))
            i += 3
            continue
        if cmd == "ARC" and i + 3 < len(lineas):
            p1 = punto(lineas[i + 1])
            p2 = punto(lineas[i + 2])   # punto intermedio (aprox. clave)
            p3 = punto(lineas[i + 3])
            entidades.append(("ARC", capa_actual, p1, p2, p3))
            i += 4
            continue
        if cmd == "TEXT" and i + 4 < len(lineas):
            p = punto(lineas[i + 1])
            altura = float(lineas[i + 2])
            rot = float(lineas[i + 3])
            texto = lineas[i + 4]
            entidades.append(("TEXT", capa_actual, p, altura, rot, texto))
            i += 5
            continue
        i += 1
    return capas, entidades


def punto(t):
    x, y = t.replace(" ", "").split(",")[:2]
    return (float(x), float(y))


def circulo_por_tres_puntos(p1, p2, p3):
    """Centro, radio y ángulos (inicio, fin) del arco que pasa por p1-p2-p3."""
    ax, ay = p1
    bx, by = p2
    cx, cy = p3
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay)
          + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx)
          + (cx**2 + cy**2) * (bx - ax)) / d
    r = math.hypot(ax - ux, ay - uy)
    a1 = math.degrees(math.atan2(ay - uy, ax - ux))
    a2 = math.degrees(math.atan2(cy - uy, cx - ux))
    # el punto medio debe quedar sobre el arco: elegimos el sentido que lo contiene
    am = math.degrees(math.atan2(by - uy, bx - ux))
    if not en_arco(a1, am, a2):
        a1, a2 = a2, a1
    return (ux, uy), r, a1 % 360, a2 % 360


def en_arco(a1, am, a2):
    a1, am, a2 = a1 % 360, am % 360, a2 % 360
    if a1 <= a2:
        return a1 <= am <= a2
    return am >= a1 or am <= a2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scr")
    ap.add_argument("dxf")
    ap.add_argument("--png", default=None)
    args = ap.parse_args()

    capas, entidades = leer_scr(args.scr)
    doc = ezdxf.new("R2010", setup=True)
    for nombre, color in capas.items():
        doc.layers.add(nombre, color=color)
    msp = doc.modelspace()

    informe = []
    for e in entidades:
        tipo, capa = e[0], e[1]
        if tipo == "LINE":
            msp.add_line(e[2], e[3], dxfattribs={"layer": capa})
        elif tipo == "ARC":
            (ux, uy), r, a1, a2 = circulo_por_tres_puntos(e[2], e[3], e[4])
            informe.append((capa, e[2], e[4], (ux, uy), r))
            msp.add_arc(center=(ux, uy), radius=r, start_angle=a1,
                        end_angle=a2, dxfattribs={"layer": capa})
        elif tipo == "TEXT":
            msp.add_text(e[5], height=e[3],
                         dxfattribs={"layer": capa, "rotation": e[4]}).set_placement(e[2])

    doc.saveas(args.dxf)
    print(f"DXF escrito: {args.dxf}")
    print(f"  capas: {', '.join(f'{k}(ACI {v})' for k, v in capas.items())}")
    print(f"  entidades: {len(entidades)}")

    print("\n  Verificación geométrica de los arcos (3 puntos -> centro y radio):")
    for capa, p1, p3, centro, r in informe:
        print(f"   · capa {capa}: extremos {p1} y {p3}")
        print(f"     centro = ({centro[0]:.4f}, {centro[1]:.4f}) m   radio = {r:.4f} m")

    if args.png:
        from ezdxf.addons.drawing import Frontend, RenderContext
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(16, 10))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor("#0d0d0d")
        ctx = RenderContext(doc)
        Frontend(ctx, ezmpl.MatplotlibBackend(ax)).draw_layout(
            doc.modelspace(), finalize=True)
        fig.savefig(args.png, dpi=140, facecolor="#0d0d0d")
        print(f"\n  Vista previa PNG: {args.png}")


if __name__ == "__main__":
    main()
