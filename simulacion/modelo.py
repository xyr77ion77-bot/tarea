#!/usr/bin/env python3
"""Modelo 2D del pórtico del auditorio — datos de partida para la simulación.

Toma TODOS los datos de `../cuaderno/calculos.py` (no inventa números) y arma el
modelo de pórtico plano que se usa en la simulación: nudos, elementos, secciones,
cargas y casos. Escribe `modelo.json`, que consume `solver2d.py`.

Ejes: x horizontal (luz de 17,60 m), y vertical hacia arriba. Longitudes en cm,
fuerzas en kg (momentos kg·cm).

Hipótesis del modelo (todas declaradas en AUDITORIA.md):
  1. Pórtico plano transversal tipo, de los 7 iguales; sin torsión ni diafragma.
  2. **Arco articulado** a la cabeza del pilar (COVENIN 1756-1:2019 §3.5.4,
     Tipo IV) → el pilar trabaja en voladizo y el empuje H se va al tirante.
  3. Geometría de la cercha exactamente como la del diseño (geo["nudos"]):
     9 nudos por cordón a **igual ángulo** (8 paneles), cordones 2×IPE 160,
     montantes IPE 120 de 0,80 m, diagonales IPE 160 **en X (San Andrés)**.
  4. Cordones y pilares: elementos de pórtico (nudos continuos). Montantes,
     diagonales y tirante: bielas articuladas (como el cálculo del cuaderno).
  5. Peso propio calculado con las secciones reales (≈73 kg/m de cercha) en vez
     del PP = 60 kg/m de la planilla original.
"""
import json
import math
import pathlib
import sys

AQUI = pathlib.Path(__file__).parent
sys.path.insert(0, str(AQUI.parent / "cuaderno"))
import calculos  # noqa: E402

R = calculos.calcular()
g, c, a, s = R["geo"], R["cargas"], R["global"], R["sismo"]
E = calculos.E_ACERO           # kg/cm²
GAMMA = 7850.0                 # kg/m³ (acero)

# Catálogo europeo (kg/m y cm²/cm⁴ de la tabla de perfiles)
SECCIONES = {
    "HEB 300":   dict(A=149.1, I=25170.0, w=117.0, perfil="HEB 300"),
    "2xIPE 160": dict(A=2 * 20.1, I=2 * 869.0, w=2 * 15.8, perfil="IPE 160 ×2"),
    "IPE 160":   dict(A=20.1, I=869.0, w=15.8, perfil="IPE 160"),
    "IPE 120":   dict(A=13.2, I=318.0, w=10.4, perfil="IPE 120"),
    "Ø1-1/2″":   dict(A=11.40, I=1e-3, w=8.95, perfil="barra roscada Ø1-1/2″"),
}
NODO_A_SECCION = {"columna": "HEB 300", "cordon": "2xIPE 160", "diagonal": "IPE 160",
                  "montante": "IPE 120", "tirante": "Ø1-1/2″"}


def nudos_cercha():
    """Nudos del arco con la geometría exacta del diseño (igual ángulo por panel)."""
    L, d, f = g["L"], g["d"], g["f"]
    R_sup, th = g["R_sup"], math.radians(g["th_medio_grados"])   # 31,7187° = semiángulo
    dphi = th / 4                                                # 4 paneles por semi-arco
    filas = []
    for k in range(-4, 5):
        phi = k * dphi
        x = L / 2 + R_sup * math.sin(phi)
        ye = R_sup * (math.cos(phi) - math.cos(th))
        yi = ye - d / math.cos(phi)
        filas.append(dict(k=k, phi=math.degrees(phi), x=x, ye=ye, yi=yi))
    return filas


def construir(g_pp=None):
    L, d, h = g["L"], g["d"], g["h"]
    filas = nudos_cercha()
    nodos, nd = [], {}

    def nodo(nombre, x, y, tipo="libre"):
        nd[nombre] = len(nodos)
        nodos.append(dict(n=nombre, x=round(x * 100, 2), y=round(y * 100, 2), tipo=tipo))

    nodo("base_i", 0.0, 0.0, "apoyo")
    nodo("base_d", L, 0.0, "apoyo")
    nodo("top_i", 0.0, h, "pilar")
    nodo("top_d", L, h, "pilar")
    for k, fi in enumerate(filas):
        nodo(f"e{k}", fi["x"], h + fi["ye"], "cordon")
    for k, fi in enumerate(filas):
        nodo(f"i{k}", fi["x"], h + fi["yi"], "cordon")

    elementos = []

    def add(tipo, na, nb, sec, nombre):
        p1, p2 = nodos[nd[na]], nodos[nd[nb]]
        elementos.append(dict(i=len(elementos), tipo=tipo, a=nd[na], b=nd[nb], sec=sec, n=nombre,
                              L=round(math.dist((p1["x"], p1["y"]), (p2["x"], p2["y"])), 2)))

    add("frame", "base_i", "top_i", NODO_A_SECCION["columna"], "pilar izquierdo")
    add("frame", "base_d", "top_d", NODO_A_SECCION["columna"], "pilar derecho")
    for k in range(8):
        add("frame", f"e{k}", f"e{k+1}", NODO_A_SECCION["cordon"], f"cordón superior P{k+1}")
        add("frame", f"i{k}", f"i{k+1}", NODO_A_SECCION["cordon"], f"cordón inferior P{k+1}")
        add("truss", f"e{k}", f"i{k+1}", NODO_A_SECCION["diagonal"], f"diagonal ↗ P{k+1}")
        add("truss", f"i{k}", f"e{k+1}", NODO_A_SECCION["diagonal"], f"diagonal ↘ P{k+1}")
    for k in range(9):
        add("truss", f"e{k}", f"i{k}", NODO_A_SECCION["montante"], f"montante {k}")
    add("truss", "e0", "e8", NODO_A_SECCION["tirante"], "tirante de cabeza")

    # articulación del arco a la cabeza del pilar: se comparten los desplazamientos
    enlaces = [dict(a="e0", b="top_i", tipo="articulacion"),
               dict(a="e8", b="top_d", tipo="articulacion")]

    # ---- cargas por nudo (kg): techo sobre el cordón superior, pasarela sobre el inferior
    trib = [0.0] * 9
    for k in range(8):
        dx = filas[k + 1]["x"] - filas[k]["x"]
        trib[k] += dx / 2
        trib[k + 1] += dx / 2
    trib = [round(t, 4) for t in trib]                 # en m de proyección horizontal
    S = g["S"]
    defs = {
        "servicio": dict(
            q_techo=(c["D"] + c["colgadas"] + c["L"]) * S, q_pas=c["pp_pasarela"],
            g_pp=1.0, R=None,
            label="Servicio: D + L (sin mayorar)"),
        "mayorada": dict(
            q_techo=1.2 * (c["D"] + c["colgadas"]) * S + 1.6 * c["L"] * S,
            q_pas=1.2 * c["pp_pasarela"], g_pp=1.2, R=None,
            label="Rotura: 1,2D + 1,6L (con mayoración del PP real)"),
        "sismo_R6": dict(
            q_techo=1.2 * (c["D"] + c["colgadas"]) * S + 0.5 * c["L"] * S,
            q_pas=1.2 * c["pp_pasarela"], g_pp=1.2, R=6,
            label="Sismo R = 6: 1,2D + 0,5L + S"),
        "sismo_R2": dict(
            q_techo=1.2 * (c["D"] + c["colgadas"]) * S + 0.5 * c["L"] * S,
            q_pas=1.2 * c["pp_pasarela"], g_pp=1.2, R=2,
            label="Sismo R = 2 (Tipo IV): 1,2D + 0,5L + S"),
        "sin_tirante": dict(
            q_techo=1.2 * (c["D"] + c["colgadas"]) * S + 1.6 * c["L"] * S,
            q_pas=1.2 * c["pp_pasarela"], g_pp=1.2, R=None, tirante=False,
            label="Rotura SIN tirante: el empuje H llega al pilar"),
    }
    casos = {}
    for nom, k in defs.items():
        if g_pp is not None:
            k["g_pp"] = g_pp
        Fv = {f"e{i}": -k["q_techo"] * trib[i] for i in range(9)}
        for i in range(9):
            Fv[f"i{i}"] = -k["q_pas"] * trib[i]
        Fh = {}
        V_col = 0.0
        if k["R"]:
            V_col = s["casos"][k["R"]]["V_col"] * 1000.0            # kg, corte por pilar
            Fh["top_i"] = V_col
            Fh["top_d"] = V_col
        casos[nom] = dict(label=k["label"], Fv=Fv, Fh=Fh, g_pp=k["g_pp"],
                          tirante=k.get("tirante", True), V_col=V_col, R=k["R"],
                          q_techo=k["q_techo"], q_pas=k["q_pas"])

    modelo = dict(
        unidades=dict(longitud="cm", fuerza="kg", momento="kg·cm", carga="kg/m"),
        E=E, gamma=GAMMA, nodos=nodos, elementos=elementos, secciones=SECCIONES,
        enlaces=enlaces, casos=casos, trib=trib,
        apoyo=dict(nudos=["base_i", "base_d"], tipo="empotrado"),
        geometria=dict(L=g["L"], f=g["f"], d=g["d"], h=g["h"], S=S, nport=g["nport"],
                       L_arco=g["L_arco"], th_medio_grados=g["th_medio_grados"],
                       h_clave=g["h_clave"]),
        referencia=dict(
            de_cuaderno=dict(
                H_u=a["H_u"], R_u=a["R_u"], M_u=a["M_u"], N_u=a["N_u"], q_u=c["q_u"],
                W_total=c["W_total"], W_portico=c["W_portico"],
                tirante_T_u=R["tirante"]["T_u"], tirante_dc=R["tirante"]["dc"],
                V_col={6: s["casos"][6]["V_col"] * 1000, 2: s["casos"][2]["V_col"] * 1000},
                delta_e={6: s["casos"][6]["delta_e"], 2: s["casos"][2]["delta_e"]},
                M_base_cantil={6: s["casos"][6]["M_base"] * 1000.0,
                               2: s["casos"][2]["M_base"] * 1000.0},
                deriva_lim_cm=s["casos"][6]["delta_lim"],
                Cd=s["Cd"], dc_columna={6: R["columna"]["casos"]["Sismo R = 6 (planilla original)"]["inter"],
                                        2: R["columna"]["casos"]["Sismo R = 2 (Tipo IV)"]["inter"]},
                dc_columna_sin_tirante=R["columna"]["casos"]["Sin tirante (H al apoyo)"]["inter"],
                dc_cordon=R["cercha"]["dc_cordon"], dc_diagonal=R["cercha"]["dc_diag"],
                dc_montante=R["cercha"]["dc_montante"],
                dc_correa=R["correa"]["dc_x"], flecha_correa=R["correa"]["flecha"],
                flecha_correa_lim=R["correa"]["flecha_lim"],
                perno_R6=dict(T_perno=R["placa"]["casos"]["Sismo R = 6"]["T_perno"],
                              diam=R["placa"]["casos"]["Sismo R = 6"]["perno"],
                              dc=R["placa"]["casos"]["Sismo R = 6"]["T_perno"] / R["placa"]["casos"]["Sismo R = 6"]["cap_34"],
                              ok=R["placa"]["casos"]["Sismo R = 6"]["ok"]),
                perno_R2=dict(T_perno=R["placa"]["casos"]["Sismo R = 2"]["T_perno"],
                              dc=R["placa"]["casos"]["Sismo R = 2"]["T_perno"] / R["placa"]["casos"]["Sismo R = 2"]["cap_1"],
                              ok=R["placa"]["casos"]["Sismo R = 2"]["ok"]),
                zapata=dict(P_serv=R["zapata"]["P_serv"], P_u=R["zapata"]["P_u"],
                            q_serv=R["zapata"]["q_serv"], q_u=R["zapata"]["q_u"],
                            s_elast=R["zapata"]["s_elast"], s_lim=R["zapata"]["s_lim"],
                            H_sin_tirante=R["zapata"]["H_sin_tirante"],
                            F_roce=R["zapata"]["F_roce"], FS_desliz=R["zapata"]["FS_desliz"],
                            desliza_ok=R["zapata"]["desliza_ok"]),
            ),
            nota="valores del cuaderno (cuaderno/calculos.py) para comparar"),
    )
    return modelo


def salida(verboso=True):
    m = construir()
    (AQUI / "modelo.json").write_text(json.dumps(m, indent=1, ensure_ascii=False), encoding="utf-8")
    if verboso:
        print(f"nudos: {len(m['nodos'])}  elementos: {len(m['elementos'])}  casos: {len(m['casos'])}")
        print("escrito modelo.json")
    return m


if __name__ == "__main__":
    m = salida()
    print("nudos del arco (x, y desde el nivel de apoyo del arco, m):")
    for fi in nudos_cercha():
        print(f"  k={fi['k']:+d}  phi={fi['phi']:7.3f}°  x={fi['x']:7.3f}  ye={fi['ye']:6.3f}  yi={fi['yi']:7.3f}")
