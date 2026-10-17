#!/usr/bin/env python3
"""Genera cuaderno.html (archivo único, sin recursos externos) desde calculos.py."""
import pathlib
import hcom
from hcom import page
import sec_a, sec_b, sec_c, sec_d

TITULO = "Cuaderno de cálculos — Auditorio UPT Barlovento «Argelia Laya» (Higuerote)"

partes = [
    sec_a.portada(),
    sec_a.sec_datos(),
    sec_a.ej1(),
    sec_a.ej2(),
    sec_a.ej3(),
    sec_b.ej4(),
    sec_b.ej5(),
    sec_b.ej6(),
    sec_b.ej7(),
    sec_b.ej8(),
    sec_c.ej9(),
    sec_c.ej10(),
    sec_c.ej11(),
    sec_d.ej12(),
    sec_d.ej13(),
    sec_d.planilla(),
    sec_d.conclusiones(),
    sec_d.anexos(),
    sec_d.anexo_b(),
]

html = page(TITULO, "\n".join(partes))
salida = pathlib.Path(__file__).with_name("cuaderno.html")
salida.write_text(html, encoding="utf-8")
print(f"escrito {salida}  ({len(html) / 1024:.0f} kB)")
