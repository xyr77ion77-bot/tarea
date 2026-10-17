#!/usr/bin/env python3
"""Simulación del eje Y (longitudinal): fachada arriostrada, R = 4,5 contra R = 2
y diafragma rígido contra flexible.

Decisiones del usuario (2026-10-17): elevación 2D de fachada, los 6 vanos
arriostrados en X (HEB 200), comparación R = 4,5 / R = 2, y las dos hipótesis
de diafragma (rígido / flexible).

Método: el mismo solver verificado (`solver2d.Modelo`) sobre el modelo de
`modelo_y.py`; análisis modal por Jacobi con los GDL sin masa condensados
(Guyan), igual que `dinamica.py`; espectro del cuaderno (COVENIN 1756-1:2019 §7,
forma meseta 2,4·AA/R hasta TC y rama TC/T) evaluado en el T₁ longitudinal.

Par (R, Cd) longitudinal: Tabla 15 para arriostramientos concéntricos da
R = 4,5 y Cd = 3,75. Al bajar R a 2 (decisión conservadora del proyecto) se
conserva Cd = 3,75 para la deriva, y se declara así.

Una sola fachada: masa y cortante = mitad del total (dos fachadas iguales,
sin torsión — limitante declarada del alcance 2D).

Escribe `resultados_y.json` y `datos_y.js` (window.EJEY) para el visor.
"""
import json
import math
import pathlib
import sys

AQUI = pathlib.Path(__file__).parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "cuaderno"))
import calculos  # noqa: E402
import modelo as MOD       # noqa: E402  (transversal, para la masa sísmica real)
import modelo_y as MY      # noqa: E402
import solver2d as S       # noqa: E402
import dinamica as D       # noqa: E402  (jacobi y ad_espectro reutilizados)

GRAV = 981.0
CD_Y = 3.75                       # Cd longitudinal (Tabla 15, arriostrado concéntrico)
DERIVA_LIM = 0.02 * MY.H_CM       # 17 cm, misma referencia del cuaderno (0,02·h)
RS = (4.5, 2.0)
NOM_R = {4.5: "sismo_R45", 2.0: "sismo_R2"}


# --------------------------------------------------------------------------- #
#  masas y sistema reducido (Guyan), genérico para la fachada
# --------------------------------------------------------------------------- #
def masas_y(m, W_fachada):
    """Peso sísmico por nudo (kg): la masa de cubierta de cada pórtico va a su
    cabeza de pilar (W_fachada/7) más el peso propio de las barras del modelo."""
    pesos = {n["n"]: 0.0 for n in m["nodos"]}
    for i in range(MY.NP):
        pesos[f"t{i}"] += W_fachada / MY.NP
    for e in m["elementos"]:
        w = m["secciones"][e["sec"]]["w"] * e["L"] / 100.0
        pesos[m["nodos"][e["a"]]["n"]] += w / 2.0
        pesos[m["nodos"][e["b"]]["n"]] += w / 2.0
    return pesos


def sistema_y(m, pesos):
    Me = S.Modelo(m, "vacio", g_pp=0.0)
    Me.resolver()
    K, dof = Me.K, Me.dof
    masa = [0.0] * Me.ndof
    for i, n in enumerate(m["nodos"]):
        mi = pesos[n["n"]] / GRAV
        masa[dof[i][0]] += mi
        masa[dof[i][1]] += mi
    libres = [i for i in range(Me.ndof) if i not in Me.apoyos]
    t = [i for i in libres if masa[i] > 0]
    r = [i for i in libres if masa[i] <= 0]
    Ktt = [[K[i][j] for j in t] for i in t]
    if r:
        Ktr = [[K[i][j] for j in r] for i in t]
        Krr = [[K[i][j] for j in r] for i in r]
        Krt = [[K[i][j] for j in t] for i in r]
        inv = []
        for j in range(len(r)):
            e = [1.0 if i == j else 0.0 for i in range(len(r))]
            inv.append(S.gauss([row[:] for row in Krr], e))
        inv = [[inv[j][i] for j in range(len(r))] for i in range(len(r))]
        Kc = [[Ktt[i][j] - sum(Ktr[i][k] * sum(inv[k][l] * Krt[l][j] for l in range(len(r)))
                               for k in range(len(r))) for j in range(len(t))]
              for i in range(len(t))]
    else:
        Krr, Krt, Kc = [], [], Ktt
    return dict(K=Kc, mt=[masa[i] for i in t], t=t, r=r, Krr=Krr, Krt=Krt,
                dof=dof, ndof=Me.ndof)


def modos_y(m, pesos, nmax=6):
    si = sistema_y(m, pesos)
    K, mt, t, r = si["K"], si["mt"], si["t"], si["r"]
    n = len(t)
    raiz = [1.0 / math.sqrt(x) for x in mt]
    A = [[raiz[i] * K[i][j] * raiz[j] for j in range(n)] for i in range(n)]
    val, vec = D.jacobi(A)
    dof_u = set(si["dof"][j][0] for j in range(len(m["nodos"])))
    autos = []
    for idx in range(n):
        if val[idx] <= 1e-9:
            continue
        omega = math.sqrt(val[idx])
        phit = [vec[idx][j] * raiz[j] for j in range(n)]
        esc = max(abs(x) for x in phit)
        phit = [x / esc for x in phit]
        phir = []
        if r:
            rhs = [sum(si["Krt"][a][j] * phit[j] for j in range(n)) for a in range(len(r))]
            phir = [-v for v in S.gauss([row[:] for row in si["Krr"]], rhs)]
        phi = [0.0] * si["ndof"]
        for k, i in enumerate(t):
            phi[i] = phit[k]
        for k, i in enumerate(r):
            phi[i] = phir[k]
        m_mod = sum(mt[k] * phit[k] ** 2 for k in range(n))
        r1 = sum(mt[k] * phit[k] for k in range(n) if t[k] in dof_u)
        gamma = r1 / m_mod if m_mod else 0.0
        autos.append(dict(T=2 * math.pi / omega, omega=omega, m_mod=m_mod,
                          gamma=gamma, m_eff=gamma ** 2 * m_mod, phi=phi))
    autos.sort(key=lambda d: d["omega"])
    si["masa_u"] = sum(mt[k] for k in range(n) if t[k] in dof_u)
    return autos[:nmax], si


# --------------------------------------------------------------------------- #
#  capacidades (mismas fórmulas del cuaderno)
# --------------------------------------------------------------------------- #
def capacidades():
    A_d = MY.SECCIONES["HEB 200"]["A"]
    L_d = math.hypot(MY.S_CM, MY.H_CM)
    lam_d = L_d / MY.DIAG["r_min"]
    _, phiFcr_d = calculos.phi_flex(lam_d)
    A_c = MY.SECCIONES["HEB 300 (eje débil)"]["A"]
    lam_c = MY.H_CM / MY.COL["r_iy"]
    _, phiFcr_c = calculos.phi_flex(lam_c)
    return dict(
        diag_tension=0.9 * calculos.FY_ACERO * A_d,          # kg (fluencia, §E? tracción)
        diag_compresion=phiFcr_d * A_d,                      # kg (pandeo, longitud total)
        lam_diag=lam_d,
        col_phiPn=phiFcr_c * A_c,                            # kg
        col_phiMn=0.9 * MY.COL["Zy"] * calculos.FY_ACERO,    # kg·cm (eje débil, Zpl,y)
        lam_col=lam_c)


# --------------------------------------------------------------------------- #
def correr(verboso=True):
    s = MOD.s
    m_tr = MOD.construir()
    _, W_portico = D.masas(m_tr)               # masa sísmica real por pórtico (nivel B)
    W_total = W_portico * MOD.g["nport"]       # los 7 pórticos: W del edificio
    W_f = W_total / 2.0                        # una de las dos fachadas
    cap = capacidades()
    phi_esp = s["phi_esp"]

    # rigidez teórica de la fachada (fórmula cerrada, para verificar el solver):
    L_d = math.hypot(MY.S_CM, MY.H_CM)
    cos_t = MY.S_CM / L_d
    k_vano = 2 * MY.E * MY.SECCIONES["HEB 200"]["A"] / L_d * cos_t ** 2   # cruz en X
    k_teorica = 6 * k_vano + MY.NP * 3 * MY.E * MY.SECCIONES["HEB 300 (eje débil)"]["I"] / MY.H_CM ** 3

    salida = dict(W_total=W_total, W_fachada=W_f, Cd=CD_Y, deriva_lim=DERIVA_LIM,
                  AA=s["AA"], TC=s["TC"], phi_esp=phi_esp,
                  k_teorica=k_teorica, capacidades=cap,
                  decisiones=dict(alcance="elevación 2D de una fachada (sin torsión)",
                                  vanos="los 6 vanos arriostrados en X (HEB 200)",
                                  R="4,5 (Tabla 15) comparado con R = 2",
                                  diafragma="rígido y flexible comparados"),
                  diafragmas={})

    for diaf in ("rigido", "flexible"):
        V_est = {R: phi_esp * (2.4 * s["AA"] / R) * W_f for R in RS}
        m = MY.construir(diaf, fuerzas={NOM_R[R]: V_est[R] for R in RS})
        pesos = masas_y(m, W_f)
        autos, si = modos_y(m, pesos)
        lateral = max(autos, key=lambda d: d["m_eff"])
        T1 = lateral["T"]
        bloque = dict(T1=T1, k_teorica=k_teorica,
                      modos=[dict(n=i + 1, T=d["T"], porc=100 * d["m_eff"] / si["masa_u"])
                             for i, d in enumerate(autos)],
                      masa_modelo=si["masa_u"] * GRAV,
                      espectro={})
        for R in RS:
            # --- estático equivalente (solver, cargas nodales V/7 en cabezas)
            Me = S.Modelo(m, NOM_R[R], g_pp=0.0)
            Me.resolver()
            esf = Me.esfuerzos()
            drift = sum(Me.despl(f"t{i}")[0] for i in range(MY.NP)) / MY.NP
            diags = [e for e in esf.values() if "diagonal" in e["n"]]
            N_t = max([e["N"] for e in diags] or [0.0])
            N_c = min([e["N"] for e in diags] or [0.0])
            cols = [e for e in esf.values() if e["n"].startswith("pilar")]
            M_col = max(abs(e["M1"]) for e in cols) / 1e5          # t·m
            N_col = max(abs(e["N"]) for e in cols) / 1000.0        # t
            pc = N_col * 1000.0 / cap["col_phiPn"]
            pr = M_col * 1e5 / cap["col_phiMn"]
            dc_col = (pc / 2 + pr) if pc < 0.2 else (pc + 8.0 / 9.0 * pr)
            # --- modal (modo 1, espectro en T1)
            ad = D.ad_espectro(T1, R)
            Sd = phi_esp * ad * GRAV / lateral["omega"] ** 2
            campo_el, campo_inel, fuerza = [], [], []
            for i, n in enumerate(m["nodos"]):
                uu = lateral["gamma"] * lateral["phi"][si["dof"][i][0]] * Sd
                vv = lateral["gamma"] * lateral["phi"][si["dof"][i][1]] * Sd
                campo_el.append(dict(u=uu, v=vv))
                campo_inel.append(dict(u=CD_Y * uu, v=CD_Y * vv))
                fuerza.append(dict(n=n["n"], F=lateral["gamma"]
                                   * lateral["phi"][si["dof"][i][0]] * pesos[n["n"]]
                                   * Sd * lateral["omega"] ** 2 / GRAV))
            d_el = max(abs(campo_el[MY.NP + i]["u"]) for i in range(MY.NP))
            bloque["espectro"][str(R)] = dict(
                R=R, Ad_T1=ad, Ad_meseta=2.4 * s["AA"] / R, en_meseta=T1 <= s["TC"],
                V_estatico=V_est[R], V_modal=lateral["m_eff"] * phi_esp * ad * GRAV,
                k_solver=V_est[R] / drift, drift_estatica=drift,
                delta_el=d_el, delta_inel=CD_Y * d_el,
                deriva_ok=CD_Y * d_el <= DERIVA_LIM,
                N_diag_tension=N_t, N_diag_compresion=N_c,
                dc_diag=max(N_t / cap["diag_tension"], abs(N_c) / cap["diag_compresion"]),
                M_col=M_col, N_col=N_col, dc_col=dc_col,
                campo_el=campo_el, campo_inel=campo_inel, fuerza=fuerza)
        bloque["error_k"] = abs(bloque["espectro"]["2.0"]["k_solver"] - k_teorica) / k_teorica * 100
        bloque["nodos"] = m["nodos"]
        bloque["elementos"] = m["elementos"]
        salida["diafragmas"][diaf] = bloque

    # reparto por vano con cada hipótesis de diafragma (para la tabla del visor)
    for diaf, bloque in salida["diafragmas"].items():
        for R in RS:
            V = bloque["espectro"][str(R)]["V_estatico"]
            bloque.setdefault("reparto", {})[str(R)] = dict(
                por_vano=V / 6.0,
                criterio=("por rigidez (6 vanos iguales → V/6)" if diaf == "rigido"
                          else "por área tributaria (6 vanos iguales → V/6)"))

    (AQUI / "resultados_y.json").write_text(json.dumps(salida, indent=1, ensure_ascii=False),
                                            encoding="utf-8")
    (AQUI / "datos_y.js").write_text(
        "// Generado por eje_y.py — no editar a mano.\n"
        "window.EJEY = " + json.dumps(salida, ensure_ascii=False) + ";\n", encoding="utf-8")
    if verboso:
        print(f"· peso sísmico total W = {W_total:,.0f} kg → por fachada {W_f:,.0f} kg"
              .replace(",", " "))
        print(f"· rigidez teórica de la fachada k = {k_teorica:,.0f} kg/cm "
              f"(cruz en X por vano {k_vano:,.0f} + pilares eje débil)".replace(",", " "))
        for diaf, b in salida["diafragmas"].items():
            e2 = b["espectro"]["2.0"]
            print(f"· diafragma {diaf:9s}: T1 = {b['T1']:.3f} s | k solver = "
                  f"{e2['k_solver']:,.0f} kg/cm (error vs fórmula {b['error_k']:.2f} %)"
                  .replace(",", " "))
            for R in RS:
                e = b["espectro"][str(R)]
                print(f"    R = {R}: Ad(T1) = {e['Ad_T1']:.4f} | V fachada = "
                      f"{e['V_estatico'] / 1000:6.2f} t | Δ = Cd·δ = {e['delta_inel']:6.2f} cm "
                      f"({'✓' if e['deriva_ok'] else '✗'} ≤ {DERIVA_LIM:.0f}) | "
                      f"diag. máx {max(e['N_diag_tension'], -e['N_diag_compresion']) / 1000:6.2f} t "
                      f"D/C {e['dc_diag']:.3f} | pilar D/C {e['dc_col']:.3f}")
        print("· escrito resultados_y.json y datos_y.js")
    return salida


if __name__ == "__main__":
    correr()
