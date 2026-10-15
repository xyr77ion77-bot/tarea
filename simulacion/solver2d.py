#!/usr/bin/env python3
"""Solver de pórtico plano (Python puro, sin numpy) y casos de carga del auditorio.

Método de la rigidez directa con dos tipos de elemento:
  · frame  → 6 GDL (u, v, θ por extremo), Euler-Bernoulli, con reparto consistente
             de la carga uniforme (peso propio) como viga doblemente empotrada.
  · truss  → biela articulada (sólo fuerza axial), peso propio repartido 50/50.

Los nudos del arco y la cabeza del pilar se unen con un **enlace de articulación**
(comparten u y v; cada uno conserva su giro): así se modela el «arco articulado»
del sistema Tipo IV de COVENIN 1756-1:2019 §3.5.4 (pilares en voladizo).

Corre 4 comprobaciones contra fórmulas cerradas antes de resolver el pórtico y
escribe `resultados.json` + `datos.js` (modelo + resultados) para la vista HTML.
"""
import json
import math
import pathlib
import sys

AQUI = pathlib.Path(__file__).parent
sys.path.insert(0, str(AQUI))
import modelo as MOD  # noqa: E402


# ---------------------------------------------------------------------------
# utilidades numéricas
# ---------------------------------------------------------------------------
def gauss(A, b):
    """Resuelve A·x = b por eliminación de Gauss con pivoteo parcial."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-13:
            raise ValueError(f"sistema singular en la columna {col}")
        M[col], M[piv] = M[piv], M[col]
        p = M[col][col]
        for r in range(col + 1, n):
            f = M[r][col] / p
            if f:
                for cc in range(col, n + 1):
                    M[r][cc] -= f * M[col][cc]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = M[r][n] - sum(M[r][c] * x[c] for c in range(r + 1, n))
        x[r] = s / M[r][r]
    return x


def k_frame(E, A, I, L):
    ea, ei = E * A, E * I
    return [[ea / L, 0, 0, -ea / L, 0, 0],
            [0, 12 * ei / L ** 3, 6 * ei / L ** 2, 0, -12 * ei / L ** 3, 6 * ei / L ** 2],
            [0, 6 * ei / L ** 2, 4 * ei / L, 0, -6 * ei / L ** 2, 2 * ei / L],
            [-ea / L, 0, 0, ea / L, 0, 0],
            [0, -12 * ei / L ** 3, -6 * ei / L ** 2, 0, 12 * ei / L ** 3, -6 * ei / L ** 2],
            [0, 6 * ei / L ** 2, 2 * ei / L, 0, -6 * ei / L ** 2, 4 * ei / L]]


def k_truss(E, A, L):
    ea = E * A / L
    return [[ea, 0, -ea, 0], [0, 0, 0, 0], [-ea, 0, ea, 0], [0, 0, 0, 0]]


def rot6(c, s):
    return [[c, s, 0, 0, 0, 0], [-s, c, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
            [0, 0, 0, c, s, 0], [0, 0, 0, -s, c, 0], [0, 0, 0, 0, 0, 1]]


def rot4(c, s):
    return [[c, s, 0, 0], [-s, c, 0, 0], [0, 0, c, s], [0, 0, -s, c]]


def matmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(m)) for j in range(p)] for i in range(n)]


def matvec(A, v):
    return [sum(A[i][k] * v[k] for k in range(len(v))) for i in range(len(A))]


def transp(A):
    return [list(col) for col in zip(*A)]


def carga_local(w, L, c, s):
    """Fuerzas nodales locales de una carga w (kg/cm) vertical hacia abajo.

    Reparto consistente (viga doblemente empotrada): q·L/2 en cada nudo y
    ±q·L²/12 de momento de empotramiento.
    """
    qx, qy = -w * s, -w * c                            # componentes en ejes locales
    return [qx * L / 2, qy * L / 2, qy * L ** 2 / 12.0,
            qx * L / 2, qy * L / 2, -qy * L ** 2 / 12.0]


# ---------------------------------------------------------------------------
# modelo → sistema
# ---------------------------------------------------------------------------
class Modelo:
    def __init__(self, m, caso, tirante=True, articulado=True, g_pp=None):
        self.m = m
        self.caso = m["casos"][caso]
        self.con_tirante = tirante
        self.articulado = articulado
        self.nodos = m["nodos"]
        self.pos = {n["n"]: i for i, n in enumerate(self.nodos)}
        self.g_pp = self.caso["g_pp"] if g_pp is None else g_pp
        self._dof()
        self.apoyos = set()
        for nn in m["apoyo"]["nudos"]:
            self.apoyos.update(self.dof[self.pos[nn]])
        self.ndof = self.nlibre

    def _dof(self):
        """Numeración de GDL considerando los enlaces arco–pilar."""
        enl = {e["a"]: e for e in self.m.get("enlaces", [])}
        self.dof, libre = {}, 0
        for i, n in enumerate(self.nodos):
            if n["n"] in enl:
                e = enl[n["n"]]
                j = self.pos[e["b"]]
                assert j < i, "el nudo destino del enlace debe numerarse antes"
                if e["tipo"] == "articulacion" and self.articulado:
                    self.dof[i] = (self.dof[j][0], self.dof[j][1], libre)
                    libre += 1                              # giro propio del arco (rótula)
                else:
                    self.dof[i] = self.dof[j]               # nudo rígido: comparten todo
            else:
                self.dof[i] = (libre, libre + 1, libre + 2)
                libre += 3
        self.nlibre = libre

    def resolver(self):
        m = self.m
        K = [[0.0] * self.ndof for _ in range(self.ndof)]
        F = [0.0] * self.ndof
        info = {}
        for e in m["elementos"]:
            if not self.con_tirante and e["n"] == "tirante de cabeza":
                continue
            i, j = e["a"], e["b"]
            p1, p2 = self.nodos[i], self.nodos[j]
            dx, dy = p2["x"] - p1["x"], p2["y"] - p1["y"]
            L = math.hypot(dx, dy)
            c, s = dx / L, dy / L
            sec = m["secciones"][e["sec"]]
            w = sec["w"] * self.g_pp / 100.0            # kg/m → kg/cm
            if e["tipo"] == "frame":
                kl, T = k_frame(m["E"], sec["A"], sec["I"], L), rot6(c, s)
                gd = self.dof[i] + self.dof[j]
                fl = carga_local(w, L, c, s)            # locales
                fg = matvec(transp(T), fl)              # globales
                kg = matmul(matmul(transp(T), kl), T)
            else:
                kl, T = k_truss(m["E"], sec["A"], L), rot4(c, s)
                gd = (self.dof[i][0], self.dof[i][1], self.dof[j][0], self.dof[j][1])
                fg = [0.0, -w * L / 2, 0.0, -w * L / 2]  # peso propio 50/50 en global
                fl = matvec(T, fg)
                kg = matmul(matmul(transp(T), kl), T)
            info[e["i"]] = dict(gd=gd, kl=kl, T=T, L=L, c=c, s=s, e=e, fl=fl, fg=fg)
            for r, gr in enumerate(gd):
                for cc, gc in enumerate(gd):
                    K[gr][gc] += kg[r][cc]
                F[gr] += fg[r]
        for nn, val in self.caso["Fv"].items():
            F[self.dof[self.pos[nn]][1]] += val
        for nn, val in self.caso["Fh"].items():
            F[self.dof[self.pos[nn]][0]] += val
        self.F = F
        libre = [i for i in range(self.ndof) if i not in self.apoyos]
        Kred = [[K[i][j] for j in libre] for i in libre]
        for r in range(len(libre)):
            if abs(Kred[r][r]) < 1e-9:
                Kred[r][r] = 1.0                        # GDL sin rigidez (nudo articulado)
        x = gauss(Kred, [F[i] for i in libre])
        self.d = [0.0] * self.ndof
        for r, i in enumerate(libre):
            self.d[i] = x[r]
        self.K = K
        self.R = [sum(K[i][j] * self.d[j] for j in range(self.ndof)) - F[i]
                  if i in self.apoyos else 0.0 for i in range(self.ndof)]
        self.el_info = info
        return self.d

    def despl(self, nombre):
        return tuple(self.d[g] for g in self.dof[self.pos[nombre]])

    def esfuerzos(self):
        out = {}
        for i, inf in self.el_info.items():
            e, gd = inf["e"], inf["gd"]
            dg = [self.d[g] for g in gd]
            dl = matvec(inf["T"], dg)
            n_ = len(gd)
            p = [sum(inf["kl"][r][cc] * dl[cc] for cc in range(n_)) - inf["fl"][r]
                 for r in range(n_)]
            if e["tipo"] == "frame":
                out[i] = dict(n=e["n"], tipo="frame", sec=e["sec"], L=inf["L"],
                              N=-p[0], M1=p[2], M2=p[5], Vy1=p[1], Vy2=p[4])
            else:
                out[i] = dict(n=e["n"], tipo="truss", sec=e["sec"], L=inf["L"],
                              N=-p[0], M1=0.0, M2=0.0, Vy1=0.0, Vy2=0.0)
        self.esf = out
        return out


# ---------------------------------------------------------------------------
# comprobaciones contra fórmulas cerradas
# ---------------------------------------------------------------------------
def _columna_voladizo():
    h, I, P = 850.0, 25170.0, 517.9
    m = dict(E=MOD.E, nodos=[dict(n="b", x=0.0, y=0.0), dict(n="t", x=0.0, y=h)],
             elementos=[dict(i=0, tipo="frame", a=0, b=1, sec="HEB 300", n="c", L=h)],
             secciones={"HEB 300": dict(A=149.1, I=I, w=0.0)},
             apoyo=dict(nudos=["b"]), enlaces=[],
             casos={"t": dict(Fv={}, Fh={"t": P}, g_pp=0.0, label="")})
    M = Modelo(m, "t")
    M.resolver()
    return M.d[3], P * h ** 3 / (3 * MOD.E * I)


def _viga_apoyada(nel=8):
    """Viga simplemente apoyada con q = 284,69 kg/m (carga de la correa IPN 140)."""
    L, q, I = 410.0, 284.69, 573.0
    nodos = [dict(n=f"n{k}", x=k * L / nel, y=0.0) for k in range(nel + 1)]
    el = [dict(i=k, tipo="frame", a=k, b=k + 1, sec="IPN 140", n=f"e{k}", L=L / nel)
          for k in range(nel)]
    m = dict(E=MOD.E, nodos=nodos, elementos=el,
             secciones={"IPN 140": dict(A=18.2, I=I, w=q)},
             apoyo=dict(nudos=["n0"]), enlaces=[],
             casos={"t": dict(Fv={}, Fh={}, g_pp=1.0, label="")})
    ap = Modelo(m, "t")
    ap.apoyos = {ap.dof[0][0], ap.dof[0][1], ap.dof[nel][1]}     # apoyo simple + rodillo
    ap.resolver()
    return -ap.despl(f"n{nel // 2}")[1], 5 * (q / 100.0) * L ** 4 / (384 * MOD.E * I)


def _arco_funicular(nel=16):
    """Arco parabólico biarticulado (bielas) con tirante: debe salir T = q·L²/(8f)."""
    L, f, q, A = 1760.0, 250.0, 8.7296, 40.2         # kg/cm, kg/cm²
    nodos = [dict(n=f"n{k}", x=k * L / nel, y=4 * f * (k * L / nel) * (L - k * L / nel) / L ** 2)
             for k in range(nel + 1)]
    el = [dict(i=k, tipo="truss", a=k, b=k + 1, sec="biela", n=f"e{k}", L=0.0)
          for k in range(nel)]
    el.append(dict(i=nel, tipo="truss", a=0, b=nel, sec="biela", n="tirante", L=L))
    caso = dict(Fv={f"n{k}": -q * L / nel for k in range(nel + 1)}, Fh={}, g_pp=0.0, label="")
    m = dict(E=MOD.E, nodos=nodos, elementos=el,
             secciones={"biela": dict(A=A, I=1000.0, w=0.0)},
             apoyo=dict(nudos=["n0"]), enlaces=[], casos={"t": caso})
    ar = Modelo(m, "t")
    ar.apoyos = {ar.dof[0][0], ar.dof[0][1], ar.dof[nel][1]}     # biarticulado
    ar.resolver()
    return ar.esfuerzos()[nel]["N"], q * L ** 2 / (8 * f)


def _equilibrio(caso="mayorada"):
    m = MOD.salida(verboso=False)
    M = Modelo(m, caso)
    M.resolver()
    Rv = abs(sum(M.R[g] for g in sorted(M.apoyos)))
    Fv = sum(-M.F[g] for g in range(M.ndof))           # Σ de las cargas verticales bajando
    return Rv, Fv


def comprobaciones(verboso=True):
    res = []
    for nombre, par in (("columna en voladizo    Δ = P·h³/(3EI)", _columna_voladizo()),
                        ("viga apoyada           δ = 5wL⁴/(384EI)", _viga_apoyada()),
                        ("arco funicular c/tirante      T = qL²/(8f)", _arco_funicular()),
                        ("equilibrio vertical    ΣR = ΣF", _equilibrio())):
        calc, teo = par
        err = abs(calc - teo) / abs(teo) * 100
        res.append(dict(nombre=nombre, calculado=calc, teorico=teo, error=err))
        if verboso:
            print(f"  {'✓' if err < 5 else '✗'} {nombre}: FE {calc:12,.3f} vs teoría {teo:12,.3f}"
                  f"   (error {err:5.2f} %)".replace(",", " "))
    return res

def verificacion_empuje(m):
    """Comprueba el reparto del empuje H con la analogía de resortes en paralelo.

    El arco es un resorte de aplanamiento k_a (empuje por cm de apertura de los
    arranques); el pilar es un resorte de ménsula k_p = 3EI/h³ y el tirante un
    resorte k_t = 2EA/L (por arranque, midiendo la elongación total). Con H0 = el
    empuje del arco con los arranques fijos:
        sin tirante:  H  = H0·k_p/(k_a + k_p)
        con tirante:  T  = H0·k_t/(k_a + k_t + k_p)
    """
    P = 1000.0
    arch, enl, ap = m["elementos"], m["enlaces"], m["apoyo"]
    m2 = dict(m, elementos=[e for e in arch if "pilar" not in e["n"]], enlaces=[],
              apoyo=dict(nudos=["e0", "e8"],
                         tipo="articulado"),
              casos=dict(m["casos"]))
    # (a) empuje con los arranques fijos
    mA = Modelo(m2, "mayorada", tirante=False)
    mA.apoyos = {mA.dof[mA.pos["e0"]][0], mA.dof[mA.pos["e0"]][1],
                 mA.dof[mA.pos["e8"]][0], mA.dof[mA.pos["e8"]][1]}
    mA.resolver()
    H0 = abs(mA.R[mA.dof[mA.pos["e0"]][0]])
    # (b) rigidez de aplanamiento
    caso = dict(m2["casos"]["mayorada"])
    caso.update(Fv={}, Fh={"e0": -P, "e8": P}, g_pp=0.0)
    m3 = dict(m2, casos={"t": caso})
    mB = Modelo(m3, "t", tirante=False)
    mB.apoyos = {mB.dof[mB.pos["e0"]][1], mB.dof[mB.pos["e8"]][1]}
    mB.resolver()
    k_a = 2 * P / (mB.despl("e8")[0] - mB.despl("e0")[0])
    h, I, A, L = 850.0, 25170.0, 11.4, 1760.0
    k_p, k_t = 3 * m["E"] * I / h ** 3, 2 * m["E"] * A / L
    res = correr(verboso=False, datos_js=False) if False else None
    return dict(H0=H0, k_a=k_a, k_p=k_p, k_t=k_t,
                H_sin_tirante=H0 * k_p / (k_a + k_p),
                T_con_tirante=H0 * k_t / (k_a + k_t + k_p))


# ---------------------------------------------------------------------------
# casos del pórtico
# ---------------------------------------------------------------------------
def campos_extra(m, nom, tir):
    """Campos de desplazamiento separados: sólo gravedad y sólo sismo (para animar)."""
    campos = {}
    for clave, mod in (("grav", dict(Fh={}, Fv=m["casos"][nom]["Fv"])),
                       ("lat", dict(Fv={}, Fh=m["casos"][nom]["Fh"], g_pp=0.0))):
        mm = dict(m, casos={**{k: m["casos"][k] for k in [nom]},
                            "e_" + clave: dict(m["casos"][nom], **mod)})
        Mc = Modelo(mm, "e_" + clave, tirante=tir)
        Mc.resolver()
        campos[clave] = [dict(zip(("u", "v", "th"), Mc.despl(n["n"]))) for n in m["nodos"]]
    return campos


def pesos_propios(m):
    """Peso propio real del modelo por grupo de barras, comparado con la planilla."""
    grupos = {}
    for e in m["elementos"]:
        w = m["secciones"][e["sec"]]["w"] * e["L"] / 100.0
        k = ("cordones 2×IPE 160" if "cordón" in e["n"] else
             "diagonales IPE 160" if "diagonal" in e["n"] else
             "montantes IPE 120" if "montante" in e["n"] else
             "tirante Ø1-1/2″" if "tirante" in e["n"] else "pilares HEB 300")
        g = grupos.setdefault(k, dict(n=0, kg=0.0))
        g["n"] += 1
        g["kg"] += w
    cercha = sum(g["kg"] for k, g in grupos.items() if k != "pilares HEB 300")
    L = m["geometria"]["L_arco"]
    return dict(grupos=grupos, cercha_kg=cercha, cercha_kg_m=cercha / L,
                pasarela_kg_m=m["casos"]["mayorada"]["q_pas"] / 1.2,
                planilla_kg_m=60.0, real_kg_m=cercha / L + m["casos"]["mayorada"]["q_pas"] / 1.2)


def correr(verboso=True, datos_js=True):
    m = MOD.salida(verboso=False)
    if verboso:
        print("· comprobaciones del solver (contra fórmulas cerradas):")
    comps = comprobaciones(verboso)
    if verboso:
        print("· casos de carga (un pórtico de los 7 iguales):")
    resultados = {"casos": {}, "comprobaciones": comps}
    idx = {e["n"]: e["i"] for e in m["elementos"]}
    ref = m["referencia"]["de_cuaderno"]
    for nom in m["casos"]:
        tir = m["casos"][nom].get("tirante", True)
        M = Modelo(m, nom, tirante=tir)
        M.resolver()
        esf = M.esfuerzos()
        tir_n = esf[idx["tirante de cabeza"]]["N"] if tir else 0.0
        if tir and tir_n < 0:                          # el tirante no trabaja a compresión
            M = Modelo(m, nom, tirante=False)
            M.resolver()
            esf = M.esfuerzos()
            tir_n = 0.0
        nodos = [{**dict(n=n["n"], x=n["x"], y=n["y"]),
                  **dict(zip(("u", "v", "th"), M.despl(n["n"])))} for n in m["nodos"]]
        # aprovechamientos D/C del modelo (capacidades del cuaderno)
        phiC = MOD.R["cercha"]["phiPn_cordon"]
        phiD = MOD.R["cercha"]["phiPn_diag"]
        phiM = MOD.R["cercha"]["phiPn_montante"]
        phiT = MOD.R["tirante"]["phiPn"]
        phiP, phiMn = MOD.R["columna"]["phiPn"] * 1000.0, MOD.R["columna"]["phiMn"] * 1000.0
        mx = lambda txt: max([abs(e["N"]) for e in esf.values() if txt in e["n"]] or [0.0])
        pil = idx["pilar izquierdo"]
        M_base = abs(esf[pil]["M1"])                   # kg·cm en la base del pilar
        _pc = abs(esf[pil]["N"]) / MOD.R["columna"]["phiPn"] / 1000.0
        _pr = M_base / 100.0 / (MOD.R["columna"]["phiMn"] * 1000.0)   # kg·m / (t·m→kg·m)
        col_dc = _pc / 2 + _pr if _pc < 0.2 else _pc + 8.0 / 9.0 * _pr
        cd, lim = ref["Cd"], ref["deriva_lim_cm"]
        deriva = abs(M.despl("e0")[0])
        R = m["casos"][nom]["R"]
        resultados["casos"][nom] = dict(
            label=m["casos"][nom]["label"], R=R, nodos=nodos,
            tirante_N=tir_n, deriva=deriva, deriva_amplificada=cd * deriva,
            deriva_lim=lim, deriva_ok=cd * deriva <= lim,
            H_arco=tir_n + abs(esf[pil]["Vy1"]),
            M_base=M_base / 100.0, V_base=abs(esf[pil]["Vy1"]), N_pilar=abs(esf[pil]["N"]),
            axial={str(i): round(e["N"], 1) for i, e in esf.items()},
            momento={str(i): round(e["M1"] / 100.0, 2) for i, e in esf.items()},
            momento2={str(i): round(e["M2"] / 100.0, 2) for i, e in esf.items()},
            peso_propio=sum(m["secciones"][e["sec"]]["w"] * e["L"] / 100.0
                            for e in m["elementos"]),
            q_total=m["casos"][nom]["q_techo"] + m["casos"][nom]["q_pas"],
            dc=dict(cordon=mx("cordón") / phiC, diagonal=mx("diagonal") / phiD,
                    montante=mx("montante") / phiM, tirante=abs(tir_n) / phiT,
                    pilar=col_dc),
        )
        if m["casos"][nom]["Fh"]:                      # caso sísmico: animación
            resultados.setdefault("oscilacion", {})[nom] = campos_extra(m, nom, tir)
        elif False:
            pass
        if verboso:
            ok = "OK" if cd * deriva <= lim else f"NO CUMPLE (lím {lim:g} cm)"
            print(f"  {nom:12s} T tirante = {tir_n / 1000:7.2f} t | H en pilar = {abs(esf[pil]['Vy1']) / 1000:7.2f} t"
                  f" | M base = {M_base / 100 / 1000:7.2f} t·m | Δ tope = {deriva:6.3f} cm"
                  f" | Cd·Δ = {cd * deriva:6.2f} cm  {ok}")
    resultados["verificacion_empuje"] = verificacion_empuje(m)
    resultados["pesos_propios"] = pesos_propios(m)
    resultados["verificacion_empuje"]["H_sin_tirante_solver"] = \
        resultados["casos"]["sin_tirante"]["V_base"]
    resultados["verificacion_empuje"]["T_con_tirante_solver"] = \
        resultados["casos"]["mayorada"]["tirante_N"]
    resultados["comparacion_cuaderno"] = dict(
        H_u=ref["H_u"], tirante_T_u=ref["tirante_T_u"], q_u=ref["q_u"],
        V_col=ref["V_col"], M_base_cantil=ref["M_base_cantil"], delta_e=ref["delta_e"],
        nota="valores de cuaderno/calculos.py (fórmula q·L²/8f, ménsula 3EI/h³)")
    (AQUI / "resultados.json").write_text(json.dumps(resultados, indent=1, ensure_ascii=False),
                                          encoding="utf-8")
    if datos_js:
        js = ("// Generado por solver2d.py — no editar a mano.\n"
              "window.MODELO = " + json.dumps(m, ensure_ascii=False) + ";\n"
              "window.RESULTADOS = " + json.dumps(resultados, ensure_ascii=False) + ";\n")
        (AQUI / "datos.js").write_text(js, encoding="utf-8")
        if verboso:
            print(f"· escrito resultados.json y datos.js ({len(js) / 1024:.0f} kB)")
    return resultados


if __name__ == "__main__":
    correr()
