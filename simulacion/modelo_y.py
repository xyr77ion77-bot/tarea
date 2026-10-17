#!/usr/bin/env python3
"""Modelo 2D del eje Y (dirección longitudinal) — elevación de UNA fachada.

Lo que pidió el usuario tras la auditoría de limitantes (2026-10-17):
  · alcance: elevación 2D de la fachada longitudinal (no 3D, sin torsión);
  · vanos arriostrados: **los 6 vanos** (también los extremos) con cruces en X HEB 200;
  · R comparado: **R = 4,5 (Tabla 15, Tipo III-b) contra R = 2** (conservador);
  · diafragma de cubierta en **dos hipótesis**: rígido y flexible.

Geometría: 7 pilares HEB 300 de 8,50 m cada 4,10 m (longitud total 24,60 m),
empotrados en la base. En este plano los pilares flexionan sobre su **eje débil**
(Iy = 8 563 cm⁴, no los 25 170 cm⁴ del pórtico transversal). Las cabezas se unen
con la correa-colector longitudinal IPN 140 y cada vano lleva una cruz de
San Andrés HEB 200 (bielas). Se modela **una de las dos fachadas**: por simetría
(sin torsión) cada una recibe la mitad del cortante basal y de la masa.

Hipótesis declaradas (ver AUDITORIA.md, sección del nivel Y):
  1. Fachada plana: no hay torsión ni reparto en planta (las dos fachadas iguales).
  2. Diafragma rígido = colector axialmente rígido (A × 1000); flexible = correa
     IPN 140 real como colector axial. La geometría y las cruces no cambian.
  3. Las cruces trabajan como bielas (tracción y compresión); la capacidad a
     compresión se verifica con la longitud total de la diagonal (sin contar
     con la conexión en el cruce, criterio conservador).
  4. Solo acción lateral: la gravedad ya está resuelta en el pórtico transversal;
     aquí el peso propio de las barras no se mayoró ni se aplica (g_pp = 0).
"""
import json
import math
import pathlib
import sys

AQUI = pathlib.Path(__file__).parent
sys.path.insert(0, str(AQUI.parent / "cuaderno"))
sys.path.insert(0, str(AQUI))
import calculos  # noqa: E402
import modelo as MOD  # noqa: E402  (pórtico transversal: geometría y espectro)

E = calculos.E_ACERO
G = MOD.g                       # geometría del cuaderno (S, h, nport, Ltot)
NP = G["nport"]                 # 7 pórticos
S_CM = G["S"] * 100.0           # 410 cm entre pilares
H_CM = G["h"] * 100.0           # 850 cm

# Catálogo (cm², cm⁴, kg/m). HEB 200: perfil del arriostramiento del chat (HEB 200 en X).
SECCIONES = {
    "HEB 300 (eje débil)": dict(A=149.1, I=8563.0, w=117.0, perfil="HEB 300 (Iy)"),
    "IPN 140 (colector)":  dict(A=18.2, I=573.0, w=14.3, perfil="IPN 140"),
    "HEB 200":             dict(A=78.1, I=2003.0, w=61.3, perfil="HEB 200"),
}
# capacidad del pilar sobre el eje débil (para el D/C de eje_y.py)
COL = dict(r_iy=7.58, Zy=946.0)          # HEB 300: iy y Zpl,y de catálogo
DIAG = dict(r_min=math.sqrt(2003.0 / 78.1))   # HEB 200: r = √(Iy/A) = 5,06 cm


def construir(diafragma="flexible", fuerzas=None):
    """Arma la elevación de fachada. `fuerzas`: dict {nombre_caso: V_total_fachada_kg}."""
    nodos, nd = [], {}

    def nodo(nombre, x, y, tipo="libre"):
        nd[nombre] = len(nodos)
        nodos.append(dict(n=nombre, x=round(x, 2), y=round(y, 2), tipo=tipo))

    for i in range(NP):
        nodo(f"b{i}", i * S_CM, 0.0, "apoyo")
    for i in range(NP):
        nodo(f"t{i}", i * S_CM, H_CM, "pilar")

    secciones = {k: dict(v) for k, v in SECCIONES.items()}
    if diafragma == "rigido":
        secciones["IPN 140 (colector)"]["A"] *= 1000.0   # colector axialmente rígido

    elementos = []

    def add(tipo, na, nb, sec, nombre):
        p1, p2 = nodos[nd[na]], nodos[nd[nb]]
        elementos.append(dict(i=len(elementos), tipo=tipo, a=nd[na], b=nd[nb], sec=sec,
                              n=nombre,
                              L=round(math.dist((p1["x"], p1["y"]), (p2["x"], p2["y"])), 2)))

    for i in range(NP):
        add("frame", f"b{i}", f"t{i}", "HEB 300 (eje débil)", f"pilar E{i + 1}")
    for i in range(NP - 1):
        add("frame", f"t{i}", f"t{i + 1}", "IPN 140 (colector)", f"colector vano {i + 1}")
        add("truss", f"b{i}", f"t{i + 1}", "HEB 200", f"diagonal ↗ vano {i + 1}")
        add("truss", f"t{i}", f"b{i + 1}", "HEB 200", f"diagonal ↘ vano {i + 1}")

    casos = {}
    for nom, V in (fuerzas or {}).items():
        casos[nom] = dict(label=f"Sismo longitudinal {nom} (una fachada, V = {V:,.0f} kg)"
                          .replace(",", " "),
                          Fv={}, Fh={f"t{i}": V / NP for i in range(NP)},
                          g_pp=0.0, R=None, V_fachada=V)
    casos.setdefault("vacio", dict(label="sin cargas (masas)", Fv={}, Fh={}, g_pp=0.0, R=None))

    return dict(
        unidades=dict(longitud="cm", fuerza="kg", momento="kg·cm"),
        E=E, nodos=nodos, elementos=elementos, secciones=secciones, enlaces=[],
        casos=casos, diafragma=diafragma,
        apoyo=dict(nudos=[f"b{i}" for i in range(NP)], tipo="empotrado"),
        geometria=dict(Ltot=G["Ltot"], S=G["S"], h=G["h"], nport=NP, vanos=NP - 1,
                       L_diag=round(math.hypot(S_CM, H_CM), 2)),
        nota="una de las dos fachadas longitudinales; V y masa = mitad del total (sin torsión)")


def salida(verboso=True):
    m = construir("flexible")
    (AQUI / "modelo_y.json").write_text(json.dumps(m, indent=1, ensure_ascii=False),
                                        encoding="utf-8")
    if verboso:
        print(f"eje Y: {len(m['nodos'])} nudos, {len(m['elementos'])} elementos "
              f"({m['geometria']['vanos']} vanos arriostrados en X, HEB 200)")
        print("escrito modelo_y.json (variante flexible; la rígida la genera eje_y.py)")
    return m


if __name__ == "__main__":
    salida()
