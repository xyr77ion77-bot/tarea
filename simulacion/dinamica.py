#!/usr/bin/env python3
"""Nivel B · análisis dinámico del pórtico 2D (períodos, modos y espectro).

Lo que pidió el usuario en el punto 1 de la auditoría (nivel A + B):

  1. **Masas sísmicas por nudo** con el mismo peso sísmico del cuaderno
     (D + 0,5L en cubierta, pasarela y peso propio real de cada barra).
  2. **Autovalores y autovectores** con los GDL de giro condensados estáticamente
     (tienen masa nula: la condensación de Guyan es exacta) y el método de Jacobi
     sobre A = M^(-1/2)·K·M^(-1/2).
  3. **Modos**: período T i, factor de participación Γ i y masa efectiva de cada modo
     (la suma de las masas efectivas da el 100 % de la masa).
  4. **Espectro** evaluado en T 1 con los parámetros del cuaderno (COVENIN 1756-1:2019 §7;
     el cuaderno usó la ordenada de la meseta para T a = 0,44 s).
  5. **Cortante basal modal** contra el cortante estático del cuaderno (V 0 = C·W).

Escribe `modal.json` y `datos2.js` (window.MODAL) para el visor.
"""
import json
import math
import pathlib
import sys

AQUI = pathlib.Path(__file__).parent
sys.path.insert(0, str(AQUI))
import modelo as MOD            # noqa: E402
import solver2d as S            # noqa: E402

G = 981.0                       # cm/s² (kg·s²/cm · cm/s² = kg)


# ---------------------------------------------------------------------------
# masas sísmicas
# ---------------------------------------------------------------------------
def masas(m, factor_L=0.5):
    """Peso sísmico por nudo (kg): D + 0,5L + pasarela + peso propio real."""
    c, g = MOD.c, MOD.g
    q_techo = (c["D"] + c["colgadas"] + factor_L * c["L"]) * g["S"]
    q_pas = c["pp_pasarela"]
    pesos = {n["n"]: 0.0 for n in m["nodos"]}
    for n in m["nodos"]:
        nom = n["n"]
        if nom[0] in "ei" and nom[1:].isdigit():
            k = int(nom[1:])                       # panel 0..8 (misma trib. horizontal)
            pesos[nom] += (q_techo if nom[0] == "e" else q_pas) * m["trib"][k]
    for e in m["elementos"]:
        w = m["secciones"][e["sec"]]["w"] * e["L"] / 100.0
        pesos[m["nodos"][e["a"]]["n"]] += w / 2.0
        pesos[m["nodos"][e["b"]]["n"]] += w / 2.0
    return pesos, sum(pesos.values())


# ---------------------------------------------------------------------------
# autovalores (Jacobi cíclico sobre matriz simétrica)
# ---------------------------------------------------------------------------
def jacobi(A, tol=1e-11, itmax=120):
    n = len(A)
    a = [row[:] for row in A]
    V = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for _ in range(itmax):
        off = math.sqrt(sum(a[i][j] ** 2 for i in range(n) for j in range(n) if i != j))
        if off < tol:
            break
        for p in range(n - 1):
            for q in range(p + 1, n):
                if abs(a[p][q]) < 1e-18:
                    continue
                th = (a[q][q] - a[p][p]) / (2.0 * a[p][q])
                t = (1 if th >= 0 else -1) / (abs(th) + math.sqrt(th * th + 1.0))
                cc = 1.0 / math.sqrt(1 + t * t)
                ss = t * cc
                for k in range(n):
                    akp, akq = a[k][p], a[k][q]
                    a[k][p] = cc * akp - ss * akq
                    a[k][q] = ss * akp + cc * akq
                for k in range(n):
                    apk, aqk = a[p][k], a[q][k]
                    a[p][k] = cc * apk - ss * aqk
                    a[q][k] = ss * apk + cc * aqk
                for k in range(n):
                    vkp, vkq = V[k][p], V[k][q]
                    V[k][p] = cc * vkp - ss * vkq
                    V[k][q] = ss * vkp + cc * vkq
    val = [a[i][i] for i in range(n)]
    vec = [[V[j][i] for j in range(n)] for i in range(n)]   # vec[i] = columna i (autovector)
    orden = sorted(range(n), key=lambda i: val[i])
    return [val[i] for i in orden], [vec[i] for i in orden]


# ---------------------------------------------------------------------------
# sistema reducido (condensación estática de los GDL sin masa)
# ---------------------------------------------------------------------------
def sistema(m, tirante=True, articulado=True):
    cero = dict(m["casos"]["servicio"], Fv={}, Fh={}, g_pp=0.0, label="masas")
    mm = dict(m, casos={"e": cero})
    Me = S.Modelo(mm, "e", tirante=tirante, articulado=articulado, g_pp=0.0)
    Me.resolver()
    K, dof = Me.K, Me.dof
    pesos, W = masas(m)
    masa = [0.0] * Me.ndof
    for i, n in enumerate(m["nodos"]):
        mi = pesos[n["n"]] / G
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
        Krr, Krt = [], []
        Kc = Ktt
    return dict(K=Kc, mt=[masa[i] for i in t], t=t, r=r, Krr=Krr, Krt=Krt, dof=dof,
                pesos=pesos, W=W, ndof=Me.ndof, masa=masa)


# ---------------------------------------------------------------------------
# modos
# ---------------------------------------------------------------------------
def modos(m, nmax=6, **kw):
    si = sistema(m, **kw)
    K, mt, t, r = si["K"], si["mt"], si["t"], si["r"]
    n = len(t)
    raiz = [1.0 / math.sqrt(x) for x in mt]
    A = [[raiz[i] * K[i][j] * raiz[j] for j in range(n)] for i in range(n)]
    val, vec = jacobi(A)
    dof_u = set(si["dof"][j][0] for j in range(len(m["nodos"])))     # GDL horizontales
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
    autos.sort(key=lambda d: d["omega"])          # del período mayor al menor
    return autos[:nmax], si


# ---------------------------------------------------------------------------
# espectro
# ---------------------------------------------------------------------------
def ad_espectro(T, R, s=None):
    """Ordenada espectral Ad(T) con los parámetros del cuaderno: meseta 2,4·AA/R hasta
    T C y rama descendente (T C/T) después. La ordenada de la meseta es exactamente la
    que usó la memoria del proyecto (Ad = 2,4·AA/R) evaluada en T a = 0,44 s."""
    s = s or MOD.s
    meseta = 2.4 * s["AA"] / R
    return meseta if T <= s["TC"] else meseta * s["TC"] / T


def campos_modales(m, si, lateral, pesos, ad, s=None):
    """Campo de desplazamientos del modo fundamental, elástico e inelástico (Cd·Δ).

    Para un modo i con masa generalizada M*i, participación Γ i y espectro Ad(T i):
        Sd = φ·Ad·g/ω²  (desplazamiento espectral de diseño, elástico)
        d(x) = Γ i · φ i(x) · Sd          (desplazamiento modal elástico)
        Δ = Cd · d                        (desplazamiento de diseño, §9.4)
    """
    s = s or MOD.s
    phi, gem = lateral["phi"], lateral["gamma"]
    Sd = s["phi_esp"] * ad * G / lateral["omega"] ** 2
    campo_el, campo_inel, fuerza = [], [], []
    for i, n in enumerate(m["nodos"]):
        u, v = gem * phi[si["dof"][i][0]] * Sd, gem * phi[si["dof"][i][1]] * Sd
        campo_el.append(dict(u=u, v=v))
        campo_inel.append(dict(u=s["Cd"] * u, v=s["Cd"] * v))
        fuerza.append(dict(n=n["n"], F=gem * phi[si["dof"][i][0]] * pesos[n["n"]] * Sd
                           * lateral["omega"] ** 2 / G))
    return dict(Sd=Sd, campo_el=campo_el, campo_inel=campo_inel, fuerza=fuerza)


def m_nodo(m, nombre):
    for i, n in enumerate(m["nodos"]):
        if n["n"] == nombre:
            return i
    raise KeyError(nombre)


def correr(verboso=True):
    m = MOD.construir()
    s = MOD.s
    autos, si = modos(m, nmax=8)
    W = si["W"]
    lateral = max(autos, key=lambda d: d["m_eff"])
    T1 = lateral["T"]
    I_COL = MOD.SECCIONES["HEB 300"]["I"]
    k_lat = 2 * 3 * MOD.E * I_COL / (850.0 ** 3)          # 2 pilares en voladizo (HEB 300)
    T_teo = 2 * math.pi * math.sqrt((W / G) / k_lat)
    phi_techo = 0.5 * (lateral["phi"][si["dof"][m_nodo(m, "top_i")][0]]
                       + lateral["phi"][si["dof"][m_nodo(m, "top_d")][0]])
    esp = {}
    for R in (6, 2):
        ad1 = ad_espectro(T1, R)
        ad_a = ad_espectro(s["Ta"], R)
        camp = campos_modales(m, si, lateral, si["pesos"], ad1)
        d_el = abs(camp["campo_el"][m_nodo(m, "top_i")]["u"])
        esp[R] = dict(R=R, Ad_T1=ad1, Ad_Ta=ad_a, en_meseta=T1 <= s["TC"],
                      C_T1=s["phi_esp"] * ad1, C_Ta=s["phi_esp"] * ad_a,
                      Sa_T1_cms2=s["phi_esp"] * ad1 * G,
                      Sd_el=camp["Sd"],
                      delta_el=d_el, delta_inel=abs(camp["campo_inel"][m_nodo(m, "top_i")]["u"]),
                      V0_cuaderno=s["casos"][R]["V0"] * 1000.0,
                      V0_cuaderno_portico=s["casos"][R]["V0"] * 1000.0 / MOD.g["nport"],
                      V_modal=lateral["m_eff"] * s["phi_esp"] * ad1 * G,
                      delta_e_cuaderno=s["casos"][R]["delta_e"],
                      delta_cuaderno=s["Cd"] * s["casos"][R]["delta_e"],
                      Cd=s["Cd"], deriva_lim=s["casos"][R]["delta_lim"],
                      campo_el=camp["campo_el"], campo_inel=camp["campo_inel"],
                      fuerza=camp["fuerza"])
    # curva del espectro (una sola vez, la forma es la del cuaderno)
    curva = []
    for i in range(0, 121):
        T = 0.02 + i * 3.0 / 120
        curva.append([round(T, 4)] + [round(ad_espectro(T, R), 5) for R in (6, 2)])
    salida = dict(
        W=W, g=G, masa_total=W / G, masa_1er_modo=lateral["m_eff"],
        pesos_nodo=[dict(n=n["n"], kg=si["pesos"][n["n"]]) for n in m["nodos"]],
        modos=[dict(n=i + 1, T=d["T"], f=1 / d["T"], omega=d["omega"], gamma=d["gamma"],
                    m_mod=d["m_mod"], m_ef=d["m_eff"], porc=100 * d["m_eff"] / (W / G),
                    phi=[dict(u=d["phi"][si["dof"][j][0]], v=d["phi"][si["dof"][j][1]])
                         for j in range(len(m["nodos"]))])
               for i, d in enumerate(autos)],
        T1=T1, T1_teorico=T_teo, k_lateral=k_lat, phi_techo=phi_techo, Ta=s["Ta"], TC=s["TC"],
        AA=s["AA"], AV=s["AV"], Cd=s["Cd"], phi_esp=s["phi_esp"], espectro=esp, curva=curva,
        masa_acumulada=sum(d["m_eff"] for d in autos) / (W / G),
        nota_forma_espectral="adoptada del cuaderno: 2,4·AA/R hasta TC y rama descendente TC/T",
    )
    (AQUI / "modal.json").write_text(json.dumps(salida, indent=1, ensure_ascii=False), encoding="utf-8")
    (AQUI / "datos2.js").write_text(
        "// Generado por dinamica.py — no editar a mano.\n"
        "window.MODAL = " + json.dumps(salida, ensure_ascii=False) + ";\n", encoding="utf-8")
    if verboso:
        print(f"· peso sísmico del pórtico  W = {W:9,.0f} kg".replace(",", " "))
        print(f"· T1 = {T1:.3f} s   (teórico 2π√(m/k), k = 2·3EI/h³ = {k_lat:.0f} kg/cm: {T_teo:.3f} s)")
        print(f"· φ en la cabeza de pilar = {phi_techo:.4f}  (normalizado al máximo del modo)")
        for i, d in enumerate(autos[:5]):
            print(f"   modo {i + 1}: T = {d['T']:6.3f} s   f = {1 / d['T']:5.2f} Hz   "
                  f"Γ = {d['gamma']:6.3f}   masa efectiva X = {100 * d['m_eff'] / (W / G):5.1f} %")
        print(f"   masa efectiva acumulada (8 modos) = {100 * salida['masa_acumulada']:.1f} %")
        for R in (6, 2):
            e = esp[R]
            print(f"   R = {R}: Ad(T1) = {e['Ad_T1']:.4f} vs Ad(Ta) = {e['Ad_Ta']:.4f} → "
                  f"V modal = {e['V_modal'] / 1000:6.2f} t vs V0 cuaderno = "
                  f"{e['V0_cuaderno'] / 1000:6.2f} t (por pórtico {e['V0_cuaderno_portico'] / 1000:5.2f} t)")
            print(f"          δ elástica = {e['delta_el']:.2f} cm (cuaderno {e['delta_e_cuaderno']:.2f}) → "
                  f"Δ = Cd·δ = {e['delta_inel']:.2f} cm (cuaderno {e['delta_cuaderno']:.2f}, "
                  f"límite {e['deriva_lim']:.0f} cm)")
        print("· escrito modal.json y datos2.js")
    return salida


if __name__ == "__main__":
    correr()
