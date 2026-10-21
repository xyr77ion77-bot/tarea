"""Figuras SVG del cuaderno — todos los números vienen de calculos.py.

Sin librerías externas: cada figura es un <svg> cuyas clases CSS están definidas
en el propio cuaderno (ver CSS_FIG en gen_html.py), de modo que el HTML final es
autocontenido y se abre sin internet.
"""
import math


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def fmt(x, d=1):
    """Número con coma decimal y punto de millar (convención venezolana)."""
    s = f"{x:,.{d}f}"
    return s.replace(",", "\u00a0").replace(".", ",").replace("\u00a0", ".")


class Sc:
    """Mapea coordenadas de mundo (x a la derecha, y hacia arriba) al SVG."""

    def __init__(self, xmin, xmax, ymin, ymax, x0, y0, x1, y1):
        k = min((x1 - x0) / (xmax - xmin), (y1 - y0) / (ymax - ymin))
        self.k = k
        self.cx = (x0 + x1) / 2 - k * (xmin + xmax) / 2
        self.cy = (y0 + y1) / 2 + k * (ymin + ymax) / 2

    def X(self, x):
        return self.cx + self.k * x

    def Y(self, y):
        return self.cy - self.k * y


class CV:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.a = []
        self._uid = 0

    # --- primitivas -------------------------------------------------------
    def raw(self, s):
        self.a.append(s)
        return self

    def uid(self, base):
        self._uid += 1
        return f"{base}{self._uid}"

    def line(self, x1, y1, x2, y2, cls="ln"):
        self.raw(f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
        return self

    def pline(self, pts, cls="ln"):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.raw(f'<polyline class="{cls}" points="{p}"/>')
        return self

    def polygon(self, pts, cls="poly"):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.raw(f'<polygon class="{cls}" points="{p}"/>')
        return self

    def rect(self, x, y, w, h, cls="ln"):
        self.raw(f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{abs(w):.1f}" '
                 f'height="{abs(h):.1f}"/>')
        return self

    def circle(self, x, y, rr, cls="dot"):
        self.raw(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}"/>')
        return self

    def text(self, x, y, s, cls="tx", rot=None, anchor=None):
        at = f' text-anchor="{anchor}"' if anchor else ""
        rt = f' transform="rotate({rot:.1f} {x:.1f} {y:.1f})"' if rot is not None else ""
        self.raw(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}"{at}{rt}>{esc(s)}</text>')
        return self

    def lines(self, x, y, textos, cls="txs", anchor=None, dy=12.5):
        for i, s in enumerate(textos):
            self.text(x, y + i * dy, s, cls, anchor=anchor)
        return self

    def arrow(self, x1, y1, x2, y2, cls="ln", s=6.0, fill=None):
        self.line(x1, y1, x2, y2, cls)
        ang = math.atan2(y2 - y1, x2 - x1)
        f = fill or "#1f2937"
        pa = (x2 - s * math.cos(ang - 0.38), y2 - s * math.sin(ang - 0.38))
        pb = (x2 - s * math.cos(ang + 0.38), y2 - s * math.sin(ang + 0.38))
        self.raw(f'<polygon points="{pa[0]:.1f},{pa[1]:.1f} {x2:.1f},{y2:.1f} '
                 f'{pb[0]:.1f},{pb[1]:.1f}" fill="{f}"/>')
        return self

    def hatch(self, x1, y1, x2, y2, cls="thin", step=9):
        """Achurado a 45° recortado al rectángulo (suelo, concreto pobre…)."""
        xa, xb = min(x1, x2), max(x1, x2)
        ya, yb = min(y1, y2), max(y1, y2)
        i = self.uid("cl")
        self.raw(f'<defs><clipPath id="{i}"><rect x="{xa:.1f}" y="{ya:.1f}" '
                 f'width="{xb - xa:.1f}" height="{yb - ya:.1f}"/></clipPath></defs>')
        w, h = xb - xa, yb - ya
        ls = []
        for j in range(int((w + h) / step) + 2):
            x0 = xa - h + j * step
            ls.append(f'<line x1="{x0:.1f}" y1="{yb:.1f}" x2="{x0 + h:.1f}" y2="{ya:.1f}"/>')
        self.raw(f'<g class="{cls}" clip-path="url(#{i})">{"".join(ls)}</g>')
        return self

    def dimx(self, xa, xb, y, label, cls="dim", ext=5.0, tick=6.0, above=True):
        self.line(xa, y, xb, y, cls)
        self.line(xa, y - ext, xa, y + ext, cls)
        self.line(xb, y - ext, xb, y + ext, cls)
        self.raw(f'<polygon points="{xa:.1f},{y:.1f} {xa + tick:.1f},{y - 2.4:.1f} '
                 f'{xa + tick:.1f},{y + 2.4:.1f}" fill="#0e7490"/>')
        self.raw(f'<polygon points="{xb:.1f},{y:.1f} {xb - tick:.1f},{y - 2.4:.1f} '
                 f'{xb - tick:.1f},{y + 2.4:.1f}" fill="#0e7490"/>')
        self.text((xa + xb) / 2, y - 5 if above else y + 13, label, "txdim")
        return self

    def dimy(self, ya, yb, x, label, cls="dim", ext=5.0, tick=6.0, side="left"):
        self.line(x, ya, x, yb, cls)
        self.line(x - ext, ya, x + ext, ya, cls)
        self.line(x - ext, yb, x + ext, yb, cls)
        self.raw(f'<polygon points="{x:.1f},{ya:.1f} {x - 2.4:.1f},{ya + tick:.1f} '
                 f'{x + 2.4:.1f},{ya + tick:.1f}" fill="#0e7490"/>')
        self.raw(f'<polygon points="{x:.1f},{yb:.1f} {x - 2.4:.1f},{yb - tick:.1f} '
                 f'{x + 2.4:.1f},{yb - tick:.1f}" fill="#0e7490"/>')
        self.text(x - 6 if side == "left" else x + 6, (ya + yb) / 2 + 3.5, label, "txdim",
                  anchor="end" if side == "left" else "start")
        return self

    def leader(self, x1, y1, x2, y2, textos, cls="txs", anchor="start"):
        self.line(x1, y1, x2, y2, "thin")
        if isinstance(textos, str):
            textos = [textos]
        self.lines(x2, y2, textos, cls, anchor=anchor)
        return self

    def title(self, s, x=14, y=20):
        return self.text(x, y, s, "txb", anchor="start")

    def out(self, cls="fig", aria=""):
        head = (f'<svg class="{cls}" viewBox="0 0 {self.W} {self.H}" '
                f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(aria)}">')
        return head + "".join(self.a) + "</svg>"


# =============================================================================
# 1 · PÓRTICO DE DOBLE ARCO — geometría y cargas
# =============================================================================
def fig_portico(r, w=780, h=430):
    g, c = r["geo"], r["cargas"]
    cv = CV(w, h)
    sc = Sc(-2.8, g["L"] + 2.8, -1.5, g["h"] + g["f"] + 2.5, 44, 30, w - 150, h - 58)
    L, d, hh, f, R = g["L"], g["d"], g["h"], g["f"], g["R_sup"]

    def u_ye(u):
        return (f - R) + math.sqrt(max(R ** 2 - u ** 2, 0.0))

    def u_yi(u):
        ph = math.asin(min(1.0, abs(u) / R))
        return u_ye(u) - d / math.cos(ph)

    cv.rect(sc.X(-2.8), sc.Y(0), sc.k * (L + 5.6), sc.k * 1.5, "ground")
    cv.hatch(sc.X(-2.8), sc.Y(-1.0), sc.X(L + 2.8), sc.Y(0), step=10)
    cv.line(sc.X(-2.8), sc.Y(0), sc.X(L + 2.8), sc.Y(0), "ln")

    for xc in (0.0, L):                                    # columnas HEB 300
        cv.rect(sc.X(xc - 0.15), sc.Y(hh), sc.k * 0.30, sc.k * hh, "steelbox")
        cv.text(sc.X(xc), sc.Y(hh / 2), "HEB 300", "txs", rot=-90)

    us = [(-L / 2 + i * L / 16.0) for i in range(17)]
    cv.pline([(sc.X(L / 2 + u), sc.Y(hh + u_ye(u))) for u in us], "steel")
    cv.pline([(sc.X(L / 2 + u), sc.Y(hh + u_yi(u))) for u in us], "steel")
    nd = g["nudos"]
    for i in range(len(nd) - 1):                          # celosía en cruz
        for sgn in (1, -1):
            ua = -L / 2 + (nd[i]["x"] if sgn > 0 else -nd[i]["x"])
            ub = -L / 2 + (nd[i + 1]["x"] if sgn > 0 else -nd[i + 1]["x"])
            cv.line(sc.X(L / 2 + ua), sc.Y(hh + u_ye(ua)), sc.X(L / 2 + ub), sc.Y(hh + u_yi(ub)), "thin")
            cv.line(sc.X(L / 2 + ua), sc.Y(hh + u_yi(ua)), sc.X(L / 2 + ub), sc.Y(hh + u_ye(ub)), "thin")
    for nd_ in nd:
        for sgn in (1, -1):
            u = nd_["x"] if sgn > 0 else -nd_["x"]
            cv.circle(sc.X(L / 2 + u), sc.Y(hh + u_ye(u)), 2.6, "dot")
            cv.circle(sc.X(L / 2 + u), sc.Y(hh + u_yi(u)), 2.6, "dot")

    for i in range(13):                                   # correas
        u = -L / 2 + g["paso_correa"] * i * (L / g["L_arco"])
        cv.circle(sc.X(L / 2 + u), sc.Y(hh + u_ye(u) + 0.17), 1.8, "dot2")

    for i in range(15):                                   # carga repartida
        u = -L / 2 + i * L / 14.0
        y0 = hh + u_ye(u) + 1.35
        cv.arrow(sc.X(L / 2 + u), sc.Y(y0), sc.X(L / 2 + u), sc.Y(hh + u_ye(u) + 0.10), "qload", s=5)
    cv.text(sc.X(L / 2 - 1.2), sc.Y(hh + f + 2.15),
            f"q u = {fmt(c['q_u'], 2)} kg/m   (1,2D + 1,6L + 1,2·PP)", "txb", anchor="middle")

    cv.dimx(sc.X(0), sc.X(L), sc.Y(-0.72), f"L = {fmt(L, 2)} m")
    cv.dimy(sc.Y(0), sc.Y(hh), sc.X(-1.7), f"h = {fmt(hh, 2)} m")
    cv.dimy(sc.Y(hh + u_yi(0)), sc.Y(hh + u_ye(0)), sc.X(-4.1), f"d = {fmt(d, 2)}")
    cv.line(sc.X(L / 2), sc.Y(hh + f), sc.X(L / 2), sc.Y(hh + f + 1.8), "thin")
    cv.line(sc.X(-2.8), sc.Y(hh + f), sc.X(L / 2), sc.Y(hh + f), "thin")
    cv.arrow(sc.X(L / 2 - 0.55), sc.Y(hh + f + 1.1), sc.X(L / 2 - 0.55), sc.Y(hh + 0.6), "dim", s=5, fill="#0e7490")
    cv.text(sc.X(L / 2 - 0.85), sc.Y(hh + f + 1.2), f"f = {fmt(f, 2)} m", "txdim", anchor="end")
    cv.leader(sc.X(L / 2 + 0.9), sc.Y(hh + u_ye(0) - 0.1), sc.X(L + 1.3), sc.Y(hh + f + 1.5),
              ["2×IPE 160 — cordón superior (extradós)", "2×IPE 160 — cordón inferior (intradós)",
               f"R sup = {fmt(g['R_sup'], 3)} m   |   R inf = {fmt(g['R_inf'], 3)} m",
               f"θ = {fmt(g['th_grados'], 3)}°   |   L arco = {fmt(g['L_arco'], 3)} m",
               f"paso de correas = {fmt(g['paso_correo'] if 'paso_correo' in g else g['paso_correa'], 3)} m"])
    cv.circle(sc.X(0), sc.Y(hh), 3.0, "dot3")
    cv.circle(sc.X(L), sc.Y(hh), 3.0, "dot3")
    cv.title("Pórtico tipo de doble arco (7 en total, separación S = 4,10 m)")
    return cv.out(aria="Pórtico de doble arco: geometría y cargas")


# =============================================================================
# 2 · CUERPO LIBRE DEL PÓRTICO
# =============================================================================
def fig_cuerpolibre(r, w=780, h=320):
    g, a, c = r["geo"], r["global"], r["cargas"]
    cv = CV(w, h)
    sc = Sc(-4.2, g["L"] + 4.2, -1.4, g["h"] + g["f"] + 1.9, 36, 34, w - 36, h - 52)
    L = g["L"]
    cv.rect(sc.X(-0.3), sc.Y(0), sc.k * 0.6, sc.k * g["h"], "steelbox")
    cv.arrow(sc.X(-0.3), sc.Y(1.7), sc.X(-3.3), sc.Y(1.7), "Harrow", s=8)
    cv.lines(sc.X(-3.5), sc.Y(1.9), [f"H u = {fmt(a['H_u'] / 1000, 2)} t", "empuje del arco"],
             "txb", anchor="end")
    cv.arrow(sc.X(0), sc.Y(-0.2), sc.X(0), sc.Y(-1.15), "Harrow", s=7)
    cv.text(sc.X(0.2), sc.Y(-1.05), f"R u = {fmt(a['R_u'] / 1000, 2)} t", "txb", anchor="start")
    u = [(-L / 2 + i * L / 8.0) for i in range(9)]
    ye = [(g["f"] - g["R_sup"]) + math.sqrt(g["R_sup"] ** 2 - uu ** 2) for uu in u]
    cv.pline([(sc.X(L / 2 + uu), sc.Y(g["h"] + yy)) for uu, yy in zip(u, ye)], "ln2")
    cv.text(sc.X(L / 2), sc.Y(g["h"] + g["f"] + 1.5), f"q u = {fmt(c['q_u'], 2)} kg/m", "txb")
    for i in range(9):
        cv.arrow(sc.X(L / 2 + u[i]), sc.Y(g["h"] + ye[i] + 1.25),
                 sc.X(L / 2 + u[i]), sc.Y(g["h"] + ye[i] + 0.12), "qload", s=5)
    xm = L / 2
    cv.line(sc.X(xm - 6.4), sc.Y(g["h"] + 0.15), sc.X(xm - 6.4), sc.Y(g["h"] + g["f"] - 0.1), "thin")
    cv.line(sc.X(xm + 1.1), sc.Y(g["h"] + 0.15), sc.X(xm + 1.1), sc.Y(g["h"] + 1.1), "thin")
    cv.arrow(sc.X(xm), sc.Y(g["h"] + 0.15), sc.X(xm), sc.Y(g["h"] + 1.05), "Npar", s=7, fill="#b91c1c")
    cv.arrow(sc.X(xm + 1.1), sc.Y(g["h"] + 1.05), sc.X(xm + 1.1), sc.Y(g["h"] + 0.15), "Npar", s=7,
             fill="#b91c1c")
    cv.dimy(sc.Y(g["h"] + 0.15), sc.Y(g["h"] + g["f"] - 0.1), sc.X(xm - 6.4), "d = 0,80", side="left")
    cv.text(sc.X(xm + 1.9), sc.Y(g["h"] + 1.15), f"N u = M u / d = {fmt(a['N_u'] / 1000, 2)} t (par de fuerzas)",
            "txr", anchor="start")
    cv.lines(sc.X(-3.5), sc.Y(-0.75),
             ["Esquema de cálculo: arco sobre columnas en voladizo.",
              "H u por la fórmula del arco triarticulado (predimensionado),",
              "los momentos por la viga biempotrada equivalente (fig. siguiente)."],
             "txs", anchor="start")
    cv.title("Cuerpo libre del pórtico tipo — acciones mayoradas (1,2D + 1,6L + 1,2·PP)")
    return cv.out(aria="Cuerpo libre del pórtico: empuje, reacción y par de fuerzas")


# =============================================================================
# 3 · DFC Y DMF DE LA VIGA BIEMPOTRADA EQUIVALENTE
# =============================================================================
def fig_dfcdmf(r, w=780, h=380):
    a, c, g = r["global"], r["cargas"], r["geo"]
    cv = CV(w, h)
    Le, qu, Ru, Me = g["L"], c["q_u"], a["R_u"], a["M_u"]
    Mm = a["M_mid"]

    def M(x):
        return -Me + qu * Le * x / 2.0 - qu * x ** 2 / 2.0

    def V(x):
        return Ru - qu * x

    x0, x1 = 76, w - 44
    sx = (x1 - x0) / Le
    cv.title("Diagramas de la viga biempotrada equivalente de luz L = 17,60 m (q u = 914,96 kg/m)")
    # ---- DFC ----
    y0 = 118
    cv.line(x0 - 26, y0, x1 + 26, y0, "ln2")
    cv.polygon([(x0, y0)] + [(x0 + sx * i * Le / 40, y0 - (V(i * Le / 40) / Ru) * 60)
                             for i in range(41)] + [(x1, y0)], "dfcfill")
    cv.pline([(x0, y0)] + [(x0 + sx * i * Le / 40, y0 - (V(i * Le / 40) / Ru) * 60)
                           for i in range(41)] + [(x1, y0)], "dfc")
    cv.circle(x0, y0, 3.4, "dot")
    cv.circle(x1, y0, 3.4, "dot")
    cv.text(x0 - 10, y0 - 62, f"+{fmt(Ru / 1000, 2)} t", "txs", anchor="start")
    cv.text(x1 - 6, y0 + 78, f"−{fmt(Ru / 1000, 2)} t", "txs", anchor="end")
    cv.text(x0 - 8, y0 + 4, "A", "txb", anchor="end")
    cv.text(x1 + 8, y0 + 4, "B", "txb", anchor="start")
    cv.text(14, 34, "Fuerza cortante  V(x) = R u − q u·x   [t]", "txb", anchor="start")
    cv.text(x0 + sx * Le / 2, y0 + 66, "V = 0 en x = L/2 = 8,80 m", "txdim")
    # ---- DMF ----
    y0b = 302
    e = 58.0 / Me
    cv.line(x0 - 26, y0b, x1 + 26, y0b, "ln2")
    cv.polygon([(x0, y0b)] + [(x0 + sx * i * Le / 40, y0b + M(i * Le / 40) * e)
                              for i in range(41)] + [(x1, y0b)], "dmffill")
    cv.pline([(x0, y0b)] + [(x0 + sx * i * Le / 40, y0b + M(i * Le / 40) * e)
                            for i in range(41)] + [(x1, y0b)], "dmf")
    for xx in (0.0, Le):
        cv.line(x0 + sx * xx, y0b, x0 + sx * xx, y0b - Me * e, "ln2")
    cv.text(x0 + sx * 0.12, y0b - Me * e - 8, f"M − = q u L²/12 = {fmt(Me / 1000, 2)} t·m",
            "txs", anchor="start")
    cv.text(x1 - sx * 0.12, y0b - Me * e - 8, f"M − = {fmt(Me / 1000, 2)} t·m", "txs", anchor="end")
    cv.text(x0 + sx * Le / 2, y0b + Mm * e + 16, f"M + = q u L²/24 = {fmt(Mm / 1000, 2)} t·m", "txs")
    cv.text(14, 218, "Momento flector  M(x) = −q u L²/12 + q u L·x/2 − q u x²/2   [t·m]",
            "txb", anchor="start")
    cv.dimx(x0, x1, y0b + 92, f"L = {fmt(Le, 2)} m")
    return cv.out(aria="Diagramas de fuerza cortante y momento flector")


# =============================================================================
# 4 · ZAPATA — PLANTA Y CORTE
# =============================================================================
def fig_zapata(r, w=780, h=460):
    z = r["zapata"]
    cv = CV(w, h)
    B, hz, ac, rec = z["B"], z["hz"], z["a_col"], z["rec"]
    Bc, hzc, acc = B * 100, hz * 100, ac * 100
    cv.title("Zapata aislada del pórtico — geometría adoptada, armado y secciones críticas")

    # ---------------- planta ----------------
    sc = Sc(-20, 178, -34, 168, 26, 50, 354, 400)
    cv.rect(sc.X(0), sc.Y(Bc), sc.k * Bc, sc.k * Bc, "conc")
    x, barras = rec * 100, 0
    while x <= Bc - rec * 100 + 0.1:
        cv.line(sc.X(x), sc.Y(rec * 100), sc.X(x), sc.Y(Bc - rec * 100), "bar")
        barras += 1
        x += z["s_adop"]
    y = rec * 100
    while y <= Bc - rec * 100 + 0.1:
        cv.line(sc.X(rec * 100), sc.Y(y), sc.X(Bc - rec * 100), sc.Y(y), "bar")
        y += z["s_adop"]
    cv.rect(sc.X((Bc - acc) / 2), sc.Y((Bc + acc) / 2), sc.k * acc, sc.k * acc, "colbox")
    cv.text(sc.X(Bc / 2), sc.Y(Bc / 2 - 2), "pedestal", "txs")
    cv.text(sc.X(Bc / 2), sc.Y(Bc / 2 - 13), "0,60×0,70", "txs")
    bo = acc + z["d"]
    cv.rect(sc.X((Bc - bo) / 2), sc.Y((Bc + bo) / 2), sc.k * bo, sc.k * bo, "dash")
    cv.dimx(sc.X(0), sc.X(Bc), sc.Y(-12), f"B = {fmt(B, 2)} m")
    cv.dimy(sc.Y(Bc), sc.Y(Bc - rec * 100), sc.X(Bc + 9), "7,5", side="right")
    cv.lines(sc.X(8), sc.Y(20), [f"b o = 2[(a+d)+(b+d)] = {fmt(z['b_o'], 0)} cm — perímetro crítico"],
             "txdim", anchor="start")
    cv.line(sc.X(Bc / 2), sc.Y(24), sc.X(Bc / 2), sc.Y(Bc / 2 - bo / 2), "thin")
    cv.lines(sc.X(Bc / 2), sc.Y(-26), ["PLANTA — malla inferior Ø5/8″ @ 12 cm en ambos sentidos, con gancho"],
             "txb")
    cv.lines(30, 424, [f"Predimensionado por presión: A req = γ·P/σ adm = {fmt(z['A_req'], 3)} m² "
                       f"→ B req = {fmt(z['B_req'], 2)} m",
                       f"Se adopta B = {fmt(B, 2)} m por criterio constructivo (pedestal 0,60×0,70 + "
                       f"borde); malla con gancho estándar, l dh = {fmt(z['Ld_gancho'], 1)} cm"], "txs", anchor="start")

    # ---------------- corte ----------------
    sc2 = Sc(-72, 218, -84, 142, 424, 50, w - 26, 400)
    cv.rect(sc2.X(0), sc2.Y(hzc), sc2.k * Bc, sc2.k * hzc, "conc")
    cv.rect(sc2.X(-10), sc2.Y(0), sc2.k * (Bc + 20), sc2.k * 10, "poor")
    cv.hatch(sc2.X(-10), sc2.Y(10), sc2.X(Bc + 10), sc2.Y(0), step=5)
    cv.rect(sc2.X((Bc - acc) / 2), sc2.Y(120), sc2.k * acc, sc2.k * (120 - hzc), "conc")
    cv.text(sc2.X(Bc / 2), sc2.Y(108), "pedestal 0,60×0,70", "txs", anchor="middle")
    cv.hatch(sc2.X(-72), sc2.Y(120), sc2.X(0), sc2.Y(hzc), step=9)
    cv.hatch(sc2.X(Bc), sc2.Y(120), sc2.X(218), sc2.Y(hzc), step=9)
    cv.line(sc2.X(-72), sc2.Y(120), sc2.X(-6), sc2.Y(120), "ln")
    cv.line(sc2.X(Bc + 6), sc2.Y(120), sc2.X(218), sc2.Y(120), "ln")
    cv.text(sc2.X(-70), sc2.Y(126), "N.T.", "txs", anchor="start")
    cv.line(sc2.X(-72), sc2.Y(-30), sc2.X(218), sc2.Y(-30), "nf")
    cv.text(sc2.X(-70), sc2.Y(-26), "N.F. = 1,50 m (dato municipal)", "txnf", anchor="start")
    yy = rec * 100
    cv.line(sc2.X(rec * 100), sc2.Y(yy), sc2.X(Bc - rec * 100), sc2.Y(yy), "bar")
    cv.circle(sc2.X(rec * 100), sc2.Y(yy), 2.6, "dot3")
    cv.circle(sc2.X(Bc - rec * 100), sc2.Y(yy), 2.6, "dot3")
    cv.dimy(sc2.Y(yy), sc2.Y(hzc), sc2.X(6), f"d = {fmt(z['d'], 1)} cm")
    xs = Bc / 2 - acc / 2 - z["c_corte"]
    cv.line(sc2.X(xs), sc2.Y(hzc), sc2.X(xs), sc2.Y(0), "scut")
    cv.line(sc2.X(xs), sc2.Y(0), sc2.X(xs), sc2.Y(-30), "scut")
    for xa in range(8, int(Bc), 18):
        cv.arrow(sc2.X(xa), sc2.Y(-22), sc2.X(xa), sc2.Y(-11), "pl", s=4.5, fill="#b45309")
    cv.line(sc2.X(-10), sc2.Y(-22), sc2.X(Bc + 10), sc2.Y(-22), "pl")
    cv.text(sc2.X(-70), sc2.Y(-44), f"σ s = {fmt(z['q_serv_kgcm'], 3)} kg/cm² ≤ σ adm = 1,50 kg/cm² "
            "(servicio)", "txdim", anchor="start")
    cv.text(sc2.X(-70), sc2.Y(-58), f"Sección crítica de corte a d = {fmt(z['c_corte'], 1)} cm del "
            "borde (trazo rojo)", "txdim", anchor="start")
    cv.dimy(sc2.Y(0), sc2.Y(120), sc2.X(196), "1,20", side="left")
    cv.text(sc2.X(10), sc2.Y(33), f"h = {fmt(hz, 2)} m", "txs", anchor="start")
    cv.text(sc2.X(-70), sc2.Y(-72), f"D f = {fmt(z['D_f'], 2)} m — concreto pobre 10 cm "
            "(pág. 247); excavación 1,30 m", "txs", anchor="start")
    cv.lines(sc2.X(170), sc2.Y(140), ["CORTE A–A"], "txb")
    return cv.out(aria="Zapata aislada: planta y corte con secciones críticas")


# =============================================================================
# 5 · COLUMNA HEB 300, PLACA BASE Y PERNOS
# =============================================================================
def fig_placa(r, w=780, h=430):
    b, s = r["placa"], r["sismo"]
    cv = CV(w, h)
    Lo, sp = b["lado"], b["s_pernos"]
    cv.title("Columna HEB 300: placa base 45×45 cm, pernos de anclaje y transferencia de momentos")
    # ---------------- planta ----------------
    sc = Sc(-17, 62, -14, 61, 30, 56, 350, 396)
    cv.rect(sc.X(0), sc.Y(Lo), sc.k * Lo, sc.k * Lo, "placa")
    cv.rect(sc.X(7.5), sc.Y(37.5), sc.k * 30, sc.k * 30, "colbox")
    cv.text(sc.X(Lo / 2), sc.Y(Lo / 2 + 2), "HEB 300", "txs")
    cv.text(sc.X(Lo / 2), sc.Y(Lo / 2 - 9), "(30×30)", "txs")
    for dy in (-1, 1):
        for dx in (-3, -1, 1, 3):
            cv.circle(sc.X(Lo / 2 + dx * 4.75), sc.Y(Lo / 2 + dy * (sp / 2 + 3.2)), 3.6, "bolt")
    cv.dimx(sc.X(0), sc.X(Lo), sc.Y(-8), f"{fmt(Lo, 0)} × {fmt(Lo, 0)} cm")
    cv.dimy(sc.Y(Lo / 2 - sp / 2 - 3.2), sc.Y(Lo / 2 + sp / 2 + 3.2), sc.X(-8),
            f"s = {fmt(sp, 1)} cm", side="left")
    cv.lines(sc.X(Lo / 2), sc.Y(-20), ["PLANTA — placa t = 25 mm, 8 pernos Ø3/4″ (4 por lado)"],
             "txb")
    # ---------------- elevación ----------------
    sc2 = Sc(-100, 110, -34, 190, 396, 56, w - 26, 396)
    cv.rect(sc2.X(-22.5), sc2.Y(2.5), sc2.k * 45, sc2.k * 2.5, "placa")
    cv.rect(sc2.X(-15), sc2.Y(170), sc2.k * 30, sc2.k * 167.5, "steelfill")
    cv.line(sc2.X(-15), sc2.Y(2.5), sc2.X(-15), sc2.Y(170), "steel")
    cv.line(sc2.X(15), sc2.Y(2.5), sc2.X(15), sc2.Y(170), "steel")
    cv.line(sc2.X(-0.55), sc2.Y(2.5), sc2.X(-0.55), sc2.Y(170), "ln2")
    cv.line(sc2.X(0.55), sc2.Y(2.5), sc2.X(0.55), sc2.Y(170), "ln2")
    cv.line(sc2.X(-15), sc2.Y(170), sc2.X(15), sc2.Y(170), "steel")
    cv.text(sc2.X(0), sc2.Y(120), "HEB 300", "txs", rot=-90)
    for xb in (-sp / 2, sp / 2):
        cv.line(sc2.X(xb), sc2.Y(2.5), sc2.X(xb), sc2.Y(-16), "bolt")
        cv.line(sc2.X(xb - 1.6), sc2.Y(-13.5), sc2.X(xb + 1.6), sc2.Y(-13.5), "bolt")
        cv.circle(sc2.X(xb), sc2.Y(2.5), 3.0, "bolt")
    cv.rect(sc2.X(-20), sc2.Y(0), sc2.k * 40, sc2.k * 12, "conc")
    cv.hatch(sc2.X(-20), sc2.Y(0), sc2.X(20), sc2.Y(-12), step=6)
    cv.text(sc2.X(0), sc2.Y(-24), "pedestal 0,60×0,70", "txs")
    cv.dimy(sc2.Y(2.5), sc2.Y(170), sc2.X(-46), f"h = {fmt(r['geo']['h'], 2)} m", side="left")
    cv.dimy(sc2.Y(-sp / 2 - 3.2), sc2.Y(sp / 2 + 3.2), sc2.X(26), f"s = {fmt(sp, 1)}", side="right")
    cv.text(sc2.X(40), sc2.Y(46), f"z = 0,90·s = {fmt(b['z_pernos'] * 100, 1)} cm", "txs", anchor="start")
    cv.arrow(sc2.X(70), sc2.Y(150), sc2.X(18), sc2.Y(150), "Harrow", s=7)
    cv.lines(sc2.X(74), sc2.Y(154), [f"V col = {fmt(s['casos'][6]['V_col'], 3)} t",
                                     f"M base = {fmt(s['casos'][6]['M_base'], 2)} t·m"],
             "txs", anchor="start")
    cv.leader(sc2.X(20), sc2.Y(4), sc2.X(52), sc2.Y(-26),
              ["placa t = 25 mm",
               f"T perno = {fmt(b['casos']['Sismo R = 6']['T_perno'] / 1000, 2)} t (Ø3/4″)"],
              "txs", anchor="start")
    cv.lines(sc2.X(0), sc2.Y(184), ["ELEVACIÓN"], "txb")
    return cv.out(aria="Placa base y pernos de anclaje de la columna HEB 300")


# =============================================================================
# 6 · DETALLE DE SOLDADURA DE FILETE
# =============================================================================
def fig_soldadura(r, w=780, h=340):
    t, wd = r["cercha"], r["soldadura"]
    cv = CV(w, h)
    cv.title("Juntas soldadas — filete de 6 mm con electrodo E70XX (cartela del nudo de apoyo)")
    # --- junta: cartela horizontal + diagonal apoyada, con filetes a ambos lados ---
    sc = Sc(-3, 34, -3, 20, 40, 46, 400, 186)
    cv.rect(sc.X(-2.5), sc.Y(0.6), sc.k * 37, sc.k * 1.2, "conc")
    cv.polygon([(sc.X(9), sc.Y(1.8)), (sc.X(17.5), sc.Y(1.8)), (sc.X(12.5), sc.Y(16)),
                (sc.X(6.5), sc.Y(16))], "steelbox2")
    cv.polygon([(sc.X(9), sc.Y(1.8)), (sc.X(9.6), sc.Y(1.8)), (sc.X(9.0), sc.Y(3.4))], "weld")
    cv.polygon([(sc.X(16.9), sc.Y(1.8)), (sc.X(17.5), sc.Y(1.8)), (sc.X(17.5), sc.Y(3.4))], "weld")
    cv.text(sc.X(19), sc.Y(13), "diagonal 2×IPE 160", "txs", anchor="start")
    cv.text(sc.X(-2.4), sc.Y(2.6), f"cartela t = {fmt(t['espesor_gusset'], 1)} cm", "txs", anchor="start")
    cv.leader(sc.X(20), sc.Y(2.6), sc.X(26), sc.Y(7),
              ["cordón de filete de 6 mm", f"φR n = {fmt(wd['phiRn_cm'], 0)} kg/cm por cordón"],
              "txdim", anchor="start")
    cv.text(sc.X(15), sc.Y(-2), "longitud de cordón = 9 cm a cada lado", "txdim", anchor="middle")
    # --- sección ampliada del filete ---
    cv.lines(40, 210, ["Sección ampliada del filete (las dos planchas y el cordón)"], "txs", anchor="start")
    sc2 = Sc(-0.6, 5.0, -0.6, 2.3, 60, 224, 400, 326)
    cv.rect(sc2.X(-0.4), sc2.Y(0.6), sc2.k * 3.6, sc2.k * 0.6, "conc")
    cv.rect(sc2.X(1.6), sc2.Y(2.3), sc2.k * 0.6, sc2.k * 1.7, "steelbox2")
    cv.polygon([(sc2.X(1.6), sc2.Y(0.6)), (sc2.X(1.0), sc2.Y(0.6)), (sc2.X(1.6), sc2.Y(1.2))], "weld")
    cv.polygon([(sc2.X(2.2), sc2.Y(0.6)), (sc2.X(2.8), sc2.Y(0.6)), (sc2.X(2.2), sc2.Y(1.2))], "weld")
    cv.arrow(sc2.X(3.15), sc2.Y(0.6), sc2.X(3.15), sc2.Y(1.2), "dim", s=5, fill="#0e7490")
    cv.text(sc2.X(3.3), sc2.Y(1.15), f"pata = {fmt(wd['leg'] * 10, 1)} mm", "txdim", anchor="start")
    cv.text(sc2.X(3.3), sc2.Y(0.75), f"garganta = 0,707·pata", "txdim", anchor="start")
    cv.text(sc2.X(3.3), sc2.Y(0.45), f"= {fmt(wd['garganta'] * 10, 2)} mm", "txdim", anchor="start")
    cv.line(sc2.X(3.25), sc2.Y(0.9), sc2.X(2.35), sc2.Y(0.62), "thin")
    cv.line(sc2.X(3.25), sc2.Y(1.05), sc2.X(2.8), sc2.Y(0.9), "thin")
    # --- tabla de longitudes ---
    x0 = 470
    cv.lines(x0, 74, ["Longitudes de cordón requeridas y adoptadas"], "txb", anchor="start")
    cv.text(x0, 100, "junta", "txs", anchor="start")
    cv.text(x0 + 182, 100, "D/C", "txs", anchor="start")
    cv.text(x0 + 222, 100, "nec.", "txs", anchor="start")
    cv.text(x0 + 272, 100, "adop.", "txs", anchor="start")
    filas = [("Diagonal — 2 cordones de 9 cm", f"{fmt(wd['L_diag_nec'], 2)} cm",
              f"{fmt(wd['L_diag_adop'], 0)} cm", wd["dc_diag"]),
             ("Cordón del arco — 4 cordones de 20 cm", f"{fmt(wd['L_cordon_nec'], 2)} cm",
              f"{fmt(wd['L_cordon_adop'], 0)} cm", wd["dc_cordon"]),
             ("Placa base — 4 de 30 cm", "—", "120 cm", wd["dc_placa"])]
    for i, (nom, nec, ado, dc) in enumerate(filas):
        y = 130 + i * 36
        cv.text(x0, y, nom, "txs", anchor="start")
        cv.text(x0 + 182, y, fmt(dc, 2), "txdc" if dc <= 1 else "txbad", anchor="start")
        cv.text(x0 + 222, y, nec, "txs", anchor="start")
        cv.text(x0 + 272, y, ado, "txs", anchor="start")
    cv.text(x0, 258, f"L mín = 4·pata = {fmt(wd['Lmin'], 1)} cm por cordón   |   E70XX, "
            f"F EXX = 4 920 kg/cm²", "txdim", anchor="start")
    cv.text(x0, 280, f"φ = 0,75   |   φR n = 0,75·0,6·F EXX·garganta = "
            f"{fmt(wd['phiRn_cm'], 0)} kg/cm", "txdim", anchor="start")
    return cv.out(aria="Detalle de soldadura de filete de 6 mm")


# =============================================================================
# 7 · VIGA DE RIOSTRA — SECCIÓN Y ARMADO
# =============================================================================
def fig_riostra(r, w=780, h=250):
    ri = r["riostra"]
    cv = CV(w, h)
    b, hh = ri["b"], ri["h"]
    cv.title("Viga de riostra 25×40 cm (solo longitudinal) entre zapatas — sección y armado")
    sc = Sc(-16, 56, -14, 56, 150, 46, 330, h - 24)
    cv.rect(sc.X(0), sc.Y(hh), sc.k * b, sc.k * hh, "conc")
    cv.rect(sc.X(4), sc.Y(hh - 4), sc.k * (b - 8), sc.k * (hh - 8), "stirrup")
    for dx in (-6, 6):
        cv.circle(sc.X(b / 2 + dx), sc.Y(hh - 7.5), 4.4, "bar2")
        cv.circle(sc.X(b / 2 + dx), sc.Y(7.5), 4.4, "bar2")
    cv.dimx(sc.X(0), sc.X(b), sc.Y(-8), f"{fmt(b, 0)} cm")
    cv.dimy(sc.Y(0), sc.Y(hh), sc.X(-9), f"{fmt(hh, 0)} cm", side="left")
    cv.leader(sc.X(4), sc.Y(hh / 2), sc.X(74), sc.Y(hh / 2 + 6),
              [f"estribo Ø3/8″ @ {fmt(ri['s_estribo'], 0)} cm",
               f"s ≤ mín[25 ; 16 d b] = {fmt(ri['s_max'], 1)} cm"], "txs", anchor="start")
    cv.lines(400, 62, ["Acero longitudinal: 4 Ø1/2″ (2 arriba y 2 abajo) — solo longitudinal",
                       f"A s adoptado = {fmt(ri['A_s_adop'], 2)} cm²   |   A s requerido = {fmt(ri['A_s_req'], 2)} cm²",
                       f"· tracción Laine 0,15 P u/(0,7 f y) = {fmt(ri['A_s_81'], 2)} cm²",
                       f"· flexión del momento concurrente = {fmt(ri['A_s_flex'], 2)} cm²",
                       "· transversal: la losa sobre terreno suple la riostra (§13.4.4.c)"],
             "txs", anchor="start")
    cv.text(400, 216, "En el sentido transversal no hay riostra: interconexión por la losa "
            "sobre terreno (1,05 m ≤ 1,50 m).", "txdim", anchor="start")
    return cv.out(aria="Sección de la viga de riostra con su armado")


# =============================================================================
# 8 · GRADERÍO Y LOSA SOBRE TERRENO
# =============================================================================
def fig_graderio(r, w=780, h=290):
    lo, z = r["losa"], r["zapata"]
    cv = CV(w, h)
    cv.title("Graderío y losa sobre terreno — corte esquemático del macizo de relleno")
    sc = Sc(-0.6, 9.6, -1.3, 3.0, 40, 52, w - 40, h - 30)
    x = 0.0
    for i in range(5):
        hh = 0.75 * (i + 1) / 5.0
        cv.rect(sc.X(x), sc.Y(hh), sc.k * 1.8, sc.k * hh, "macizo")
        cv.rect(sc.X(x), sc.Y(hh + 0.20), sc.k * 1.8, sc.k * 0.20, "conc")
        x += 1.75
    cv.rect(sc.X(-0.6), sc.Y(0.20), sc.k * 0.6, sc.k * 0.20, "conc")
    cv.hatch(sc.X(-0.6), sc.Y(0.0), sc.X(9.0), sc.Y(-1.3), step=10)
    cv.line(sc.X(-0.6), sc.Y(0.0), sc.X(9.0), sc.Y(0.0), "ln")
    cv.text(sc.X(4.2), sc.Y(2.75), f"Losa sobre terreno h = {fmt(lo['h'], 2)} m — malla Ø1/2″ @ "
            f"{fmt(lo['s_adop'], 0)} cm", "txb")
    cv.text(sc.X(4.2), sc.Y(2.45), f"A s,mín = 0,002·b·h = {fmt(lo['As_min'], 2)} cm²/m   |   "
            f"adoptado {fmt(lo['As_adop'], 2)} cm²/m", "txs")
    cv.dimx(sc.X(0), sc.X(9.0), sc.Y(-0.45), "graderío: 5 filas de 1,75 m con contrahuella 0,15 m")
    cv.dimy(sc.Y(0), sc.Y(0.75), sc.X(9.3), "macizo 0,75 m", side="right")
    cv.text(sc.X(0.1), sc.Y(-0.95), f"σ bajo el macizo = γ c · h = {fmt(lo['sigma_macizo'], 2)} t/m²  "
            f"≤  σ adm = {fmt(z['sigma_adm'] / 1000, 1)} t/m²", "txdim", anchor="start")
    return cv.out(aria="Corte del graderío y la losa sobre terreno")


# =============================================================================
# 9 · GRÁFICO DE BARRAS DE DEMANDA/CAPACIDAD
# =============================================================================
def fig_dc(r, w=780, h=None):
    filas = r["dc"]
    h = h or (58 + 29 * len(filas) + 44)
    cv = CV(w, h)
    x0, x1 = 322, w - 74
    esc_ = (x1 - x0) / 1.6
    top = 62
    for i, (nom, v, ok) in enumerate(filas):
        y = top + i * 29
        cv.text(x0 - 12, y + 11, nom, "txs", anchor="end")
        cv.rect(x0, y, x1 - x0, 15, "track")
        wv = min(v, 1.6) * esc_
        cv.rect(x0, y, wv, 15, "barok" if ok else "barbad")
        cv.text(x0 + wv + 8, y + 11.5, fmt(v, 2), "txdc" if ok else "txbad", anchor="start")
    ylim = top + len(filas) * 29 - 6
    cv.line(x0 + 1.0 * esc_, top - 12, x0 + 1.0 * esc_, ylim, "lim")
    cv.text(x0 + 1.0 * esc_, top - 18, "1,00", "txlim")
    for frac in (0.5, 1.0, 1.5):
        cv.line(x0 + frac * esc_, top - 12, x0 + frac * esc_, ylim, "grid")
        cv.text(x0 + frac * esc_, ylim + 17, fmt(frac, 2), "txs")
    cv.text(x0 - 12, top - 16, "renglón de la planilla", "txb", anchor="end")
    cv.text(x0 + 1.0 * esc_ + 4, top - 16, "D/C", "txlim", anchor="start")
    cv.title("Relación demanda/capacidad de cada renglón de la planilla (línea roja: D/C = 1,00)")
    return cv.out(aria="Gráfico de barras de demanda/capacidad")


def todas(r):
    return [("fig-portico", fig_portico(r), "Pórtico tipo: geometría del doble arco y cargas de diseño."),
            ("fig-cl", fig_cuerpolibre(r), "Cuerpo libre: empuje H u, reacción R u y par de fuerzas N u = M u/d."),
            ("fig-dfc", fig_dfcdmf(r), "Fuerza cortante y momento flector de la viga biempotrada equivalente."),
            ("fig-zapata", fig_zapata(r), "Zapata aislada: planta, corte y secciones críticas."),
            ("fig-placa", fig_placa(r), "Columna HEB 300 con placa base y pernos de anclaje."),
            ("fig-soldadura", fig_soldadura(r), "Soldadura de filete de 6 mm en la cartela del nudo de apoyo."),
            ("fig-riostra", fig_riostra(r), "Viga de riostra 25×40 cm solo longitudinal: armado y estribos."),
            ("fig-graderio", fig_graderio(r), "Graderío, losa sobre terreno y macizo de relleno."),
            ("fig-dc", fig_dc(r), "Resumen gráfico demanda/capacidad de todos los renglones.")]
