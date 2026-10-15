#!/usr/bin/env python3
"""Cálculos del Auditorio UPT Barlovento «Argelia Laya» (Higuerote).

Todos los números del cuaderno salen de aquí: ninguna cifra se escribe a mano
en el HTML. Unidades: kg, cm, m, s.  Sistema: kg/cm² para tensiones.

Referencias usadas en el texto (ver Anexo A del cuaderno):
  · Fratelli, M. G. — «Suelos, Fundaciones y Muros», capítulo 8, págs. 246–274.
  · COVENIN 1618-98 (acero estructural, estados límites) y COVENIN-MINDUR 2002-88.
  · COVENIN 1756-1:2019 (sismo) y COVENIN 810-1998 (medios de escape).
  · COVENIN-MINDUR 2003-86 (viento) — acción excluida por decisión docente.
"""
import math

# ----------------------------------------------------------------------------
# MATERIALES Y CONSTANTES
# ----------------------------------------------------------------------------
E_ACERO = 2.1e6          # kg/cm²
FY_ACERO = 2530.0        # kg/cm²  (acero A52 SIDOR, equivalente A36)
FU_ACERO = 4100.0        # kg/cm²
FC = 210.0               # kg/cm²  concreto
FY_BARRA = 4200.0        # kg/cm²  ADN 420 (grado 60)
GAMMA_C = 2400.0         # kg/m³   concreto armado
GAMMA_S = 1800.0         # kg/m³   suelo húmedo
GAMMA_EQ = 2100.0        # kg/m³   masa equivalente base+relleno (libro, pág. 253)
FEXX = 4920.0            # kg/cm²  electrodo E70XX
G = 9.81

# Perfiles (SIDOR / catálogo DIN)
PERFILES = {
    "IPE 120": dict(A=13.2, Ix=318, Wx=53.0, Zx=60.7, ix=4.90, Iy=27.7, Wy=8.65, iy=1.45, g=10.4, h=12.0),
    "IPE 160": dict(A=20.1, Ix=869, Wx=109.0, Zx=124.0, ix=6.58, Iy=68.3, Wy=18.3, iy=1.84, g=15.8, h=16.0),
    "IPN 140": dict(A=18.2, Ix=573, Wx=81.9, Zx=95.4, ix=5.61, Iy=44.9, Wy=12.3, iy=1.57, g=14.3, h=14.0),
    "HEB 300": dict(A=149.1, Ix=25170, Wx=1679.0, Zx=1869.0, ix=12.99, Iy=8563, Wy=570.9, iy=7.58, g=117.0, h=30.0),
}

# barras: diámetro nominal (plg), área (cm²), diámetro (cm)
BARRAS = {
    "3/8": (0.71, 0.952),
    "1/2": (1.27, 1.270),
    "5/8": (1.98, 1.588),
    "3/4": (2.85, 1.905),
    "7/8": (3.87, 2.222),
    "1":   (5.07, 2.540),
}


def barra(d, n=1):
    return BARRAS[d][0] * n


def phi_flex(lam):
    """φPn para compresión según AISC 360 §E3 (acero A52, Fy = 2 530)."""
    lim = 4.71 * math.sqrt(E_ACERO / FY_ACERO)
    if lam <= lim:
        fe = math.pi ** 2 * E_ACERO / lam ** 2
        fcr = 0.658 ** (FY_ACERO / fe) * FY_ACERO
    else:
        fe = math.pi ** 2 * E_ACERO / lam ** 2
        fcr = 0.877 * fe
    return fcr, 0.90 * fcr


# ----------------------------------------------------------------------------
def calcular():
    R = {}

    # =========================================================================
    # 1 · GEOMETRÍA
    # =========================================================================
    g = dict(L=17.60, f=2.50, d=0.80, h=8.50, Ltot=24.60, S=4.10, nport=7)
    g["f_L"] = g["f"] / g["L"]
    g["d_L"] = g["d"] / g["L"]
    g["h_clave"] = g["h"] + g["f"]
    g["h_media"] = g["h"] + g["f"] / 2.0
    # radio del extradós por los tres puntos (apoyos y clave)
    g["R_sup"] = (g["L"] / 2) ** 2 / (2 * g["f"]) + g["f"] / 2
    g["R_inf"] = g["R_sup"] - g["d"]
    g["y0"] = g["f"] - g["R_sup"]                      # centro del arco
    g["th_medio"] = math.asin((g["L"] / 2) / g["R_sup"])   # semiapertura
    g["th"] = 2 * g["th_medio"]
    g["th_grados"] = math.degrees(g["th"])
    g["th_medio_grados"] = math.degrees(g["th_medio"])
    g["L_arco"] = g["R_sup"] * g["th"]
    g["L_inf"] = g["R_inf"] * g["th"]
    g["n_paneles"] = 8
    g["ds"] = g["L_arco"] / g["n_paneles"]
    g["alfa_apoyo"] = g["th_medio_grados"]
    g["n_correas"] = 13
    g["paso_correa"] = g["L_arco"] / 12.0
    g["nudos"] = []
    for i in range(5):
        ph = i * g["th"] / 8
        x = g["R_sup"] * math.sin(ph)
        y = g["y0"] + math.sqrt(g["R_sup"] ** 2 - x ** 2)
        y_int = y - g["d"] / math.cos(ph)
        g["nudos"].append(dict(i=i, phi=math.degrees(ph), x=x, ye=y, yi=y_int))
    R["geo"] = g

    # =========================================================================
    # 2 · CARGAS Y COMBINACIONES
    # =========================================================================
    c = dict(lamina=5.5, correas=7.5, cielo=10.0, colgadas=15.0, L=100.0,
             pp_cercha=35.0, pp_pasarela=25.0)
    c["D"] = c["lamina"] + c["correas"] + c["cielo"]
    c["PP"] = c["pp_cercha"] + c["pp_pasarela"]
    c["q_serv"] = (c["D"] + c["L"] + c["colgadas"]) * g["S"]
    c["q_serv_total"] = c["q_serv"] + c["PP"]
    c["q_u"] = (1.2 * (c["D"] + c["colgadas"]) + 1.6 * c["L"]) * g["S"] + 1.2 * c["PP"]
    c["q_u_cubierta"] = 1.2 * (c["D"] + c["colgadas"]) + 1.6 * c["L"]
    # peso sísmico
    c["W_cub"] = c["D"] + c["colgadas"] + 0.5 * c["L"]
    c["W_lineal"] = c["W_cub"] * g["S"] + c["PP"]
    c["W_portico"] = c["W_lineal"] * g["L_arco"]
    c["W_total"] = c["W_portico"] * g["nport"]
    R["cargas"] = c

    # =========================================================================
    # 3 · ANÁLISIS GLOBAL DEL PÓRTICO
    # =========================================================================
    a = dict()
    a["R_u"] = c["q_u"] * g["L"] / 2
    a["R_serv"] = c["q_serv_total"] * g["L"] / 2
    a["H_u"] = c["q_u"] * g["L"] ** 2 / (8 * g["f"])
    a["M_u"] = c["q_u"] * g["L"] ** 2 / 12.0          # extremos, viga biempotrada equivalente
    a["M_mid"] = c["q_u"] * g["L"] ** 2 / 24.0        # centro de la luz, misma viga
    a["N_u"] = a["M_u"] / g["d"]                      # par de fuerzas separadas d
    a["N_apoyo"] = math.hypot(a["H_u"], a["R_u"])
    a["p_pilar_u"] = 1.2 * PERFILES["HEB 300"]["g"] * g["h"] / 1000.0   # t
    a["P_u_zapata"] = a["R_u"] / 1000.0 + a["p_pilar_u"]                # t
    a["p_pilar_serv"] = PERFILES["HEB 300"]["g"] * g["h"] / 1000.0      # t
    a["P_serv_zapata"] = a["R_serv"] / 1000.0 + a["p_pilar_serv"]       # t
    R["global"] = a

    # =========================================================================
    # 4 · SISMO (COVENIN 1756-1:2019)
    # =========================================================================
    s = dict(AA=0.345, AV=0.669, TC=0.809, Ta=0.44, phi_esp=0.9625, Cd=4.25)
    s["V_stat"] = 1.0  # reservado
    s["casos"] = {}
    for Rr in (6, 2):
        d = dict(R=Rr)
        d["Ad"] = 2.4 * s["AA"] / Rr
        d["C"] = s["phi_esp"] * d["Ad"]
        d["Cmin"] = s["AA"] / Rr
        d["V0"] = d["C"] * c["W_total"] / 1000.0            # t
        d["V_portico"] = d["V0"] / g["nport"]               # t
        d["V_col"] = d["V_portico"] / 2                     # t
        d["M_base"] = d["V_col"] * g["h"]                   # t·m (columna en ménsula)
        # deriva elástica de una columna en voladizo
        P = d["V_col"] * 1000.0
        H = g["h"] * 100.0
        d["delta_e"] = P * H ** 3 / (3 * E_ACERO * PERFILES["HEB 300"]["Ix"])
        d["delta_lim"] = 0.020 * H
        d["Delta"] = s["Cd"] * d["delta_e"]
        d["deriva_ok"] = d["Delta"] <= d["delta_lim"]
        s["casos"][Rr] = d
    # par de vuelco llevado por las riostras entre zapatas opuestas
    for Rr in (6, 2):
        s["casos"][Rr]["dP_riostra"] = 2 * s["casos"][Rr]["M_base"] / g["L"]
    R["sismo"] = s

    # =========================================================================
    # 5 · CORREAS (vigas de cubierta) — IPN 140
    # =========================================================================
    v = dict(perfil="IPN 140")
    p = PERFILES[v["perfil"]]
    v["tributaria"] = g["paso_correa"]
    v["q_serv"] = (c["D"] + c["colgadas"] + c["L"]) * v["tributaria"] + p["g"]
    v["q_u"] = (1.2 * (c["D"] + c["colgadas"]) + 1.6 * c["L"]) * v["tributaria"] + 1.2 * p["g"]
    al = math.radians(g["alfa_apoyo"])
    v["alfa"] = g["alfa_apoyo"]
    v["q_n_u"] = v["q_u"] * math.cos(al)      # normal a la cubierta (eje fuerte)
    v["q_t_u"] = v["q_u"] * math.sin(al)      # tangencial (eje débil)
    v["q_n_serv"] = v["q_serv"] * math.cos(al)
    v["Mx_u"] = v["q_n_u"] * g["S"] ** 2 / 8
    v["My_u"] = v["q_t_u"] * g["S"] ** 2 / 8
    v["V_u"] = v["q_n_u"] * g["S"] / 2
    v["Mcx"] = 0.9 * FY_ACERO * p["Wx"] / 100.0       # kg·m
    v["Mcz"] = 0.9 * FY_ACERO * p["Wy"] / 100.0
    v["dc_x"] = v["Mx_u"] / v["Mcx"]
    v["dc_z"] = v["My_u"] / v["Mcz"]
    v["dc_biaxial"] = v["dc_x"] + v["dc_z"]
    v["dc_arriostrada"] = v["dc_x"]
    v["flecha"] = 5 * (v["q_n_serv"] / 100.0) * (g["S"] * 100) ** 4 / (384 * E_ACERO * p["Ix"])
    v["flecha_lim"] = g["S"] * 100 / 300.0
    v["flecha_ok"] = v["flecha"] <= v["flecha_lim"]
    v["tau_u"] = v["V_u"] / (0.9 * 0.6 * FY_ACERO * (0.56 * (p["h"] - 2 * 0.86)))
    R["correa"] = v

    # =========================================================================
    # 6 · CERCHA DE DOBLE ARCO
    # =========================================================================
    t = dict()
    t["N_cordon"] = a["N_u"]
    t["N_cordon_corona"] = a["H_u"]
    pc = PERFILES["IPE 160"]
    t["A_cordon"] = 2 * pc["A"]
    t["L_pandeo_cordon"] = g["ds"] * 100
    t["lam_cordon"] = 1.0 * t["L_pandeo_cordon"] / pc["iy"]
    t["Fcr_cordon"], t["phiFcr_cordon"] = phi_flex(t["lam_cordon"])
    t["phiPn_cordon"] = t["phiFcr_cordon"] * t["A_cordon"]
    t["dc_cordon"] = t["N_cordon"] / t["phiPn_cordon"]
    t["phiPn_traccion"] = 0.9 * FY_ACERO * t["A_cordon"]
    t["dc_traccion"] = t["N_cordon"] / t["phiPn_traccion"]
    # diagonal del panel extremo
    t["beta_diag"] = math.degrees(math.atan2(g["d"], g["ds"]))
    t["L_diag"] = math.hypot(g["ds"], g["d"]) * 100
    t["N_diag_total"] = a["R_u"] / math.sin(math.radians(t["beta_diag"]))
    t["N_diag"] = t["N_diag_total"] / 2          # dos diagonales por panel (cruz de San Andrés)
    t["lam_diag"] = 1.0 * t["L_diag"] / pc["iy"]
    t["Fcr_diag"], t["phiFcr_diag"] = phi_flex(t["lam_diag"])
    t["phiPn_diag"] = t["phiFcr_diag"] * pc["A"]
    t["dc_diag"] = t["N_diag"] / t["phiPn_diag"]
    # montantes
    pm = PERFILES["IPE 120"]
    t["L_montante"] = g["d"] * 100
    t["lam_montante"] = 1.0 * t["L_montante"] / pm["iy"]
    t["N_montante"] = v["q_u"] * g["S"] / 2      # reacción de la correa sobre el cordón
    t["Fcr_montante"], t["phiFcr_montante"] = phi_flex(t["lam_montante"])
    t["phiPn_montante"] = t["phiFcr_montante"] * pm["A"]
    t["dc_montante"] = t["N_montante"] / t["phiPn_montante"]
    # gusset del nudo de apoyo
    t["A_gusset"] = a["H_u"] / (0.66 * FY_ACERO)
    t["espesor_gusset"] = 1.2      # cm
    t["lado_gusset_min"] = math.sqrt(t["A_gusset"])
    t["cartela"] = (20, 35)        # cm (adoptada)
    R["cercha"] = t

    # =========================================================================
    # 7 · SOLDADURA (COVENIN 1618-98 §21 / AISC 360 §J2)
    # =========================================================================
    w = dict(leg=0.6)
    w["garganta"] = 0.707 * w["leg"]
    w["phiRn_cm"] = 0.75 * 0.6 * FEXX * w["garganta"]        # kg/cm de cordón
    w["Lmin"] = 4 * w["leg"]
    w["L_diag_nec"] = t["N_diag"] / w["phiRn_cm"]
    w["L_diag_adop"] = 18.0
    w["L_cordon_nec"] = t["N_cordon"] / (4 * w["phiRn_cm"])
    w["L_cordon_adop"] = 20.0
    w["dc_diag"] = t["N_diag"] / (w["L_diag_adop"] * w["phiRn_cm"])
    w["dc_cordon"] = t["N_cordon"] / (4 * w["L_cordon_adop"] * w["phiRn_cm"])
    w["perim_columna"] = 4 * 30.0                             # 4 cordones de 30 cm en las alas
    w["dc_placa"] = a["P_u_zapata"] * 1000 / (w["perim_columna"] * w["phiRn_cm"])
    R["soldadura"] = w

    # =========================================================================
    # 8 · COLUMNA HEB 300
    # =========================================================================
    k = dict(Kx=2.0)
    hb = PERFILES["HEB 300"]
    k["lam_x"] = k["Kx"] * g["h"] * 100 / hb["ix"]
    k["Fcr_x"], k["phiFcr_x"] = phi_flex(k["lam_x"])
    k["phiPn"] = k["phiFcr_x"] * hb["A"] / 1000.0         # t
    k["P_u"] = a["P_u_zapata"]
    k["dc_carga"] = k["P_u"] / k["phiPn"]
    k["phiMn"] = 0.9 * FY_ACERO * hb["Wx"] / 1e5          # t·m
    k["casos"] = {}
    for nombre, M, nota in (
            ("Sin tirante (H al apoyo)", a["H_u"] * g["h"] / 1000.0,
             "si el empuje del arco llega a la cabeza del pilar"),
            ("Sismo R = 2 (Tipo IV)", s["casos"][2]["M_base"],
             "columnas en ménsula, R = 2"),
            ("Sismo R = 6 (planilla original)", s["casos"][6]["M_base"],
             "pórticos de acero ND3, R = 6")):
        pc_ = k["P_u"] / k["phiPn"]
        pr_ = M / k["phiMn"]
        inter = pc_ + 8.0 / 9.0 * pr_ if pc_ >= 0.2 else pc_ / 2 + pr_
        k["casos"][nombre] = dict(M=M, pc=pc_, pr=pr_, inter=inter, ok=inter <= 1.0, nota=nota)
    R["columna"] = k

    # tirante de cabeza (anula el empuje del arco)
    ti = dict(diam=1.5, A=11.40)
    ti["T_u"] = a["H_u"]
    ti["phiPn"] = 0.9 * FY_ACERO * ti["A"]
    ti["dc"] = ti["T_u"] / ti["phiPn"]
    ti["sigma"] = ti["T_u"] / ti["A"]
    ti["ok"] = ti["dc"] <= 1.0
    ti["w"] = ti["A"] * 7.85 / 10.0                      # kg/m (7,85 g/cm³ = 7,85 kg/m por cm²... /10)
    ti["sag"] = ti["w"] * g["L"] ** 2 / (8.0 * ti["T_u"])   # m
    ti["sigma_serv"] = (c["q_serv_total"] * g["L"] ** 2 / (8 * g["f"])) / ti["A"]
    R["tirante"] = ti

    # =========================================================================
    # 9 · PLACA BASE Y PERNOS
    # =========================================================================
    b = dict(lado=45.0, t=2.5, m=(45 - 30) / 2, n_pernos=8, s_pernos=31.6)
    sigma_placa = a["P_u_zapata"] * 1000 / b["lado"] ** 2
    b["sigma"] = sigma_placa
    b["M_placa"] = sigma_placa * b["m"] ** 2 / 2
    b["t_nec"] = math.sqrt(4 * b["M_placa"] / (0.9 * FY_ACERO)) * 10   # mm
    b["z_pernos"] = b["s_pernos"] * 0.90 / 100.0             # brazo del par, en m
    b["a_perno"] = 9.0                                       # cm del perno a la cara de la columna
    b["casos"] = {}
    for Rr, nom in ((6, "Sismo R = 6"), (2, "Sismo R = 2")):
        d = dict(R=Rr)
        d["M"] = s["casos"][Rr]["M_base"]
        d["T_par"] = d["M"] * 1000 / b["z_pernos"]            # kg (par tracción-compresión)
        d["T_total"] = max(0.0, d["T_par"] - a["P_u_zapata"] * 1000 / 2)
        d["T_perno"] = d["T_total"] / (b["n_pernos"] / 2)
        d["cap_34"] = 0.75 * barra("3/4") * FY_ACERO
        d["cap_1"] = 0.75 * barra("1") * FY_ACERO
        d["perno"] = ("3/4" if d["T_perno"] <= d["cap_34"] else
                      "1" if d["T_perno"] <= d["cap_1"] else "—")
        d["ok"] = d["T_perno"] <= d["cap_1"]
        # espesor de placa por flexión con el par sísmico: franja = ancho del ala (30 cm)
        d["b_franja"] = 30.0
        d["t_nec"] = math.sqrt(6 * d["T_perno"] * b["a_perno"] / (0.9 * FY_ACERO * d["b_franja"])) * 10
        b["casos"][nom] = d
    b["T_perno"] = b["casos"]["Sismo R = 6"]["T_perno"]
    b["T_perno_R2"] = b["casos"]["Sismo R = 2"]["T_perno"]
    b["V_perno"] = s["casos"][6]["V_col"] * 1000 / b["n_pernos"]
    b["V_perno_R2"] = s["casos"][2]["V_col"] * 1000 / b["n_pernos"]
    b["cumple_34"] = b["casos"]["Sismo R = 6"]["ok"]
    b["tirante"] = R["tirante"]["dc"]
    R["placa"] = b

    # =========================================================================
    # 10 · ZAPATA AISLADA (diseño por gravedad + verificación sísmica)
    # =========================================================================
    z = dict(sigma_adm=15000.0, D_f=1.20, B=1.50, hz=0.40, rec=0.075,
             a_col=0.40, v=1.15)
    z["sigma_adm_sismo"] = z["sigma_adm"] * 1.33
    P_serv = a["P_serv_zapata"] * 1000.0
    z["P_serv"] = P_serv
    z["A_req"] = z["v"] * P_serv / z["sigma_adm"]
    z["B_req"] = math.sqrt(z["A_req"])
    z["B_adop"] = z["B"]
    z["A"] = z["B"] ** 2
    z["d"] = z["hz"] * 100 - z["rec"] * 100          # cm
    # pesos propios
    z["W_zapata"] = z["B"] ** 2 * z["hz"] * GAMMA_C
    z["W_pedestal"] = z["a_col"] ** 2 * (z["D_f"] - z["hz"]) * GAMMA_C
    z["W_tierra"] = (z["B"] ** 2 - z["a_col"] ** 2) * (z["D_f"] - z["hz"]) * GAMMA_S
    z["W_total"] = z["W_zapata"] + z["W_pedestal"] + z["W_tierra"]
    z["P_tot_serv"] = P_serv + z["W_total"]
    z["q_serv"] = z["P_tot_serv"] / z["A"]                    # kg/m²
    z["q_serv_kgcm"] = z["q_serv"] / 10000.0
    z["u_serv"] = z["q_serv"] / z["sigma_adm"]
    z["u_serv_ok"] = z["q_serv"] <= z["sigma_adm"]
    # diseño a rotura
    z["P_u"] = a["P_u_zapata"] * 1000.0
    z["q_u"] = z["P_u"] / z["A"]
    # corte simple
    z["c_corte"] = (z["B"] - z["a_col"]) / 2 * 100 - z["d"]
    z["c_corte"] = max(z["c_corte"], 0.0)
    z["V_corte"] = z["q_u"] * z["B"] * (z["c_corte"] / 100.0)
    z["v_corte"] = z["V_corte"] / (0.85 * (z["B"] * 100) * z["d"])
    z["v_c_corte"] = 0.53 * math.sqrt(FC)
    z["corte_ok"] = z["v_corte"] <= z["v_c_corte"]
    # punzonado
    z["b_o"] = 4 * (z["a_col"] * 100 + z["d"])
    z["V_punz"] = z["P_u"] - z["q_u"] * (z["a_col"] + z["d"] / 100.0) ** 2
    z["v_punz"] = z["V_punz"] / (0.85 * z["b_o"] * z["d"])
    z["v_c_punz"] = 1.06 * math.sqrt(FC)
    z["punz_ok"] = z["v_punz"] <= z["v_c_punz"]
    # flexión
    z["c_flex"] = (z["B"] - z["a_col"]) / 2
    z["M_u"] = z["q_u"] * z["B"] * z["c_flex"] ** 2 / 2      # kg·m
    z["As_flex"] = z["M_u"] * 100 / (0.9 * FY_BARRA * 0.9 * z["d"])
    z["As_min"] = 0.002 * 100 * (z["hz"] * 100)
    z["As_req"] = max(z["As_flex"], z["As_min"])
    z["gobierna"] = "mínimo" if z["As_min"] >= z["As_flex"] else "flexión"
    # separaciones y acero adoptado
    z["s_adop"] = 15.0
    z["As_adop"] = barra("1/2") * 100 / z["s_adop"]
    z["acero_ok"] = z["As_adop"] >= z["As_req"]
    # longitud de desarrollo
    ab, db = BARRAS["1/2"]
    z["Ld1"] = 1.4 * 0.06 * ab * FY_BARRA / math.sqrt(FC)
    z["Ld2"] = 1.4 * 0.006 * db * FY_BARRA
    z["Ld"] = max(z["Ld1"], z["Ld2"])
    z["Ld_disp"] = (z["B"] - z["a_col"]) / 2 * 100 - z["rec"] * 100
    z["Ld_ok"] = z["Ld"] <= z["Ld_disp"]
    z["B_req_Ld"] = (z["a_col"] * 100 + 2 * (z["Ld"] + z["rec"] * 100)) / 100.0   # ancho mínimo por Ld
    # aplastamiento columna-pedestal y pedestal-zapata
    z["Pn_col"] = 0.7 * 0.85 * FC * (z["a_col"] * 100) ** 2 / 1000.0
    z["Pn_base"] = 2 * z["Pn_col"]
    z["apl_ok"] = z["Pn_col"] * 1000 >= z["P_u"]
    # verificación sísmica con el par de riostras
    z["P_sismo"] = 0.9 * (a["R_serv"] / 1000.0 + a["p_pilar_serv"]) * 1000.0
    z["P_sismo_total"] = z["P_sismo"] + z["W_total"] + s["casos"][2]["dP_riostra"] * 1000.0
    z["q_sismo"] = z["P_sismo_total"] / z["A"]
    z["u_sismo"] = z["q_sismo"] / z["sigma_adm_sismo"]
    z["sismo_ok"] = z["q_sismo"] <= z["sigma_adm_sismo"]
    # pedestal 40×40 (de 0,50 a 1,20 m): se arma como columna corta, ρ mín = 0,005
    z["ped_As_min"] = 0.005 * 40.0 * 40.0               # 8,0 cm²
    z["ped_As"] = barra("3/4", 4)                       # 4 Φ3/4" = 11,40 cm²
    z["ped_ok"] = z["ped_As"] >= z["ped_As_min"]
    # deslizamiento sin tirante
    z["H_sin_tirante"] = a["H_u"]
    z["F_roce"] = 0.5 * z["P_tot_serv"]
    z["desliza_ok"] = z["F_roce"] >= z["H_sin_tirante"]
    z["FS_desliz"] = z["F_roce"] / z["H_sin_tirante"]
    # asentamiento elástico estimado (arcilla blanda supuesta)
    Es = 150.0     # kg/cm² (hipótesis, sin EMS)
    z["Es"] = Es
    z["nu_suelo"] = 0.5
    z["s_elast"] = z["q_serv_kgcm"] * (z["B"] * 100) * (1 - 0.5 ** 2) * 1.12 / Es  # cm
    z["s_lim"] = 2.5    # cm (Tabla 2.3, estructuras rígidas de concreto armado)
    z["s_ok"] = z["s_elast"] <= z["s_lim"]
    R["zapata"] = z

    # =========================================================================
    # 11 · VIGA DE RIOSTRA
    # =========================================================================
    ri = dict(b=40.0, h=40.0)
    ri["Ac"] = ri["b"] * ri["h"]
    ri["P_carga"] = z["P_u"] / 1000.0                   # t, carga mayorada de la columna más cargada
    ri["A_s_81"] = 0.15 * ri["P_carga"] * 1000 / (0.7 * FY_BARRA)
    ri["A_s_min1"] = 0.01 * ri["Ac"]
    ri["A_s_min2"] = 0.15 * ri["Ac"] * FC / FY_BARRA
    ri["A_s_min"] = max(0.01 * ri["Ac"], 0.15 * ri["Ac"] * FC / FY_BARRA)
    ri["A_s_H"] = a["H_u"] / (0.9 * FY_BARRA)           # si la riostra toma el empuje H
    ri["A_s_adop"] = barra("3/4", 6)
    ri["A_s_req"] = max(ri["A_s_81"], ri["A_s_min"], ri["A_s_H"])
    ri["acero_ok"] = ri["A_s_adop"] >= ri["A_s_req"]
    ri["s_estribo"] = 20.0
    ri["s_max"] = min(30.0, 12 * BARRAS["3/4"][1])
    ri["estribo_ok"] = ri["s_estribo"] <= ri["s_max"]
    ri["V_zapata_par"] = s["casos"][2]["dP_riostra"]
    R["riostra"] = ri

    # =========================================================================
    # 12 · LOSA SOBRE TERRENO Y MACIZO DEL GRADERÍO
    # =========================================================================
    lo = dict(L=500.0, h=0.20, q_macizo=0.0)
    lo["As_min"] = 0.002 * 100 * (lo["h"] * 100)
    lo["barra"] = "1/2"
    lo["s_adop"] = 20.0
    lo["As_adop"] = barra("1/2") * 100 / lo["s_adop"]
    lo["losa_ok"] = lo["As_adop"] >= lo["As_min"]
    lo["sigma_macizo"] = GAMMA_C * 0.75 / 1000.0 * 10000 / 10000.0   # t/m² con h_media 0,75
    lo["sigma_macizo"] = 2.4 * 0.75
    lo["h_max_macizo"] = 1.5 / 2.4
    R["losa"] = lo

    # =========================================================================
    # 13 · RESUMEN D/C PARA LA PLANILLA Y EL GRÁFICO
    # =========================================================================
    R["dc"] = [
        ("Correa IPN 140 — flexión eje fuerte", v["dc_x"], v["dc_x"] <= 1),
        ("Correa IPN 140 — flecha", v["flecha"] / v["flecha_lim"], v["flecha_ok"]),
        ("Cordón 2×IPE 160 — compresión", t["dc_cordon"], t["dc_cordon"] <= 1),
        ("Cordón 2×IPE 160 — tracción", t["dc_traccion"], t["dc_traccion"] <= 1),
        ("Diagonal IPE 160 (2/panel)", t["dc_diag"], t["dc_diag"] <= 1),
        ("Montante IPE 120", t["dc_montante"], t["dc_montante"] <= 1),
        ("Soldadura filete 6 mm — diagonal", w["dc_diag"], w["dc_diag"] <= 1),
        ("Soldadura filete 6 mm — cordón", w["dc_cordon"], w["dc_cordon"] <= 1),
        ("Soldadura filete 6 mm — placa base", w["dc_placa"], w["dc_placa"] <= 1),
        ("Columna HEB 300 — carga axial", k["casos"]["Sismo R = 6 (planilla original)"]["pc"],
         k["casos"]["Sismo R = 6 (planilla original)"]["pc"] <= 1),
        ("Columna HEB 300 — P-M sismo R = 6", k["casos"]["Sismo R = 6 (planilla original)"]["inter"],
         k["casos"]["Sismo R = 6 (planilla original)"]["ok"]),
        ("Columna HEB 300 — P-M sismo R = 2", k["casos"]["Sismo R = 2 (Tipo IV)"]["inter"],
         k["casos"]["Sismo R = 2 (Tipo IV)"]["ok"]),
        ("Deriva (sismo R = 6)", s["casos"][6]["Delta"] / s["casos"][6]["delta_lim"], s["casos"][6]["deriva_ok"]),
        ("Deriva (sismo R = 2)", s["casos"][2]["Delta"] / s["casos"][2]["delta_lim"], s["casos"][2]["deriva_ok"]),
        ("Zapata — presión de servicio", z["u_serv"], z["u_serv_ok"]),
        ("Zapata — corte simple", z["v_corte"] / z["v_c_corte"], z["corte_ok"]),
        ("Zapata — punzonado", z["v_punz"] / z["v_c_punz"], z["punz_ok"]),
        ("Zapata — acero adoptado / requerido", z["As_req"] / z["As_adop"], z["acero_ok"]),
        ("Zapata — longitud de desarrollo", z["Ld"] / z["Ld_disp"], z["Ld_ok"]),
        ("Zapata — aplastamiento", z["P_u"] / (z["Pn_col"] * 1000), z["apl_ok"]),
        ("Zapata — presión con sismo (σ adm +33 %)", z["u_sismo"], z["sismo_ok"]),
        ("Zapata — asentamiento estimado", z["s_elast"] / z["s_lim"], z["s_ok"]),
        ("Tirante de cabeza Ø1-1/2\u2033 — tracción", ti["dc"], ti["ok"]),
        ("Placa base — placa a flexión (sismo R = 6)", b["casos"]["Sismo R = 6"]["t_nec"] / (b["t"] * 10),
         b["casos"]["Sismo R = 6"]["t_nec"] <= b["t"] * 10),
        ("Placa base — perno Φ3/4\u2033 a tracción (R = 6)",
         b["casos"]["Sismo R = 6"]["T_perno"] / b["casos"]["Sismo R = 6"]["cap_34"],
         b["casos"]["Sismo R = 6"]["T_perno"] <= b["casos"]["Sismo R = 6"]["cap_34"]),
        ("Placa base — perno Φ1\u2033 a tracción (R = 2)",
         b["casos"]["Sismo R = 2"]["T_perno"] / b["casos"]["Sismo R = 2"]["cap_1"],
         b["casos"]["Sismo R = 2"]["T_perno"] <= b["casos"]["Sismo R = 2"]["cap_1"]),
        ("Viga de riostra 40×40 — acero", ri["A_s_req"] / ri["A_s_adop"], ri["acero_ok"]),
        ("Pedestal 40×40 — acero longitudinal", z["ped_As_min"] / z["ped_As"], z["ped_ok"]),
        ("Zapata — deslizamiento sin tirante (FS requerido 1,5)",
         1.5 / z["FS_desliz"], z["FS_desliz"] >= 1.5),
    ]
    return R


if __name__ == "__main__":
    r = calcular()
    def p(*a):
        print(", ".join(str(x) for x in a))
    g, c, a = r["geo"], r["cargas"], r["global"]
    print("== GEOMETRÍA ==")
    p("R_sup", round(g["R_sup"], 3), "R_inf", round(g["R_inf"], 3))
    p("theta", round(g["th_grados"], 3), "rad", round(g["th"], 5))
    p("L_arco", round(g["L_arco"], 3), "L_inf", round(g["L_inf"], 3), "ds", round(g["ds"], 4))
    p("paso correa", round(g["paso_correa"], 4), "alfa", round(g["alfa_apoyo"], 3))
    for nd in g["nudos"]:
        p("  nudo", nd["i"], round(nd["phi"], 3), round(nd["x"], 3), round(nd["ye"], 3), round(nd["yi"], 3))
    print("== CARGAS ==")
    p("D", c["D"], "q_serv", round(c["q_serv"], 2), "q_serv_tot", round(c["q_serv_total"], 2))
    p("q_u", round(c["q_u"], 2), "W_cub", c["W_cub"], "W_pórtico", round(c["W_portico"], 1),
      "W_total", round(c["W_total"] / 1000, 2), "t")
    print("== GLOBAL ==")
    p("R_u", round(a["R_u"]), "H_u", round(a["H_u"]), "M_u", round(a["M_u"]), "N_u", round(a["N_u"]),
      "M_mid", round(a["M_mid"]))
    p("P_u zapata", round(a["P_u_zapata"], 3), "t | P_serv", round(a["P_serv_zapata"], 3), "t")
    print("== SISMO ==")
    for kk, d in r["sismo"]["casos"].items():
        p(" R=", kk, "Ad", round(d["Ad"], 4), "C", round(d["C"], 4), "V0", round(d["V0"], 2), "t",
          "Vcol", round(d["V_col"], 3), "M_base", round(d["M_base"], 2), "t·m",
          "delta_e", round(d["delta_e"], 2), "Delta", round(d["Delta"], 2), "lim", round(d["delta_lim"], 2),
          "ok", d["deriva_ok"], "dP_riostra", round(d["dP_riostra"], 3))
    print("== CORREA ==")
    vv = r["correa"]
    p("q_serv", round(vv["q_serv"], 2), "q_u", round(vv["q_u"], 2), "qn", round(vv["q_n_u"], 2),
      "qt", round(vv["q_t_u"], 2))
    p("Mx", round(vv["Mx_u"], 1), "My", round(vv["My_u"], 1), "dcx", round(vv["dc_x"], 3),
      "dcz", round(vv["dc_z"], 3), "suma", round(vv["dc_biaxial"], 3))
    p("flecha", round(vv["flecha"], 3), "lim", round(vv["flecha_lim"], 3), "ok", vv["flecha_ok"],
      "V_u", round(vv["V_u"], 1))
    print("== CERCHA ==")
    tt = r["cercha"]
    p("cordon lam", round(tt["lam_cordon"], 1), "phiPn", round(tt["phiPn_cordon"]), "dc", round(tt["dc_cordon"], 3),
      "| tracc dc", round(tt["dc_traccion"], 3))
    p("beta diag", round(tt["beta_diag"], 2), "L_diag", round(tt["L_diag"], 2), "N_diag", round(tt["N_diag"]),
      "lam", round(tt["lam_diag"], 1), "phiPn", round(tt["phiPn_diag"]), "dc", round(tt["dc_diag"], 3))
    p("montante lam", round(tt["lam_montante"], 1), "N", round(tt["N_montante"]), "dc", round(tt["dc_montante"], 3),
      "| gusset A", round(tt["A_gusset"], 2), "cm² lado min", round(tt["lado_gusset_min"], 2))
    print("== SOLDADURA ==")
    ww = r["soldadura"]
    p("garganta", round(ww["garganta"], 3), "phiRn/cm", round(ww["phiRn_cm"]), "L_diag", round(ww["L_diag_nec"], 2),
      "L_cordon", round(ww["L_cordon_nec"], 2), "dc_diag", round(ww["dc_diag"], 3),
      "dc_cordon", round(ww["dc_cordon"], 3), "dc_placa", round(ww["dc_placa"], 3))
    print("== COLUMNA ==")
    kk = r["columna"]
    p("lam_x", round(kk["lam_x"], 1), "phiPn", round(kk["phiPn"], 1), "t | phiMn", round(kk["phiMn"], 2), "t·m",
      "| P_u", round(kk["P_u"], 2))
    for n, d in kk["casos"].items():
        p(" ", n, "M", round(d["M"], 2), "pc", round(d["pc"], 3), "pr", round(d["pr"], 3),
          "inter", round(d["inter"], 3), "ok", d["ok"])
    print("== PLACA ==")
    bb = r["placa"]
    p("sigma", round(bb["sigma"], 2), "M_placa", round(bb["M_placa"], 1), "t_nec", round(bb["t_nec"], 1), "mm")
    for nom, d in bb["casos"].items():
        p(" ", nom, "M", round(d["M"], 2), "T_par", round(d["T_par"]), "T_perno", round(d["T_perno"]),
          "Φ", d["perno"], "t_placa", round(d["t_nec"], 1), "mm", d["ok"])
    p("  V_perno R=2", round(bb["V_perno_R2"]), "kg", "| tirante dc", round(bb["tirante"], 3))
    print("== ZAPATA ==")
    zz = r["zapata"]
    p("A_req", round(zz["A_req"], 4), "B_req", round(zz["B_req"], 3), "B", zz["B_adop"], "d", zz["d"])
    p("W_tot", round(zz["W_total"]), "P_tot", round(zz["P_tot_serv"]), "q_serv", round(zz["q_serv"], 1),
      "kg/m² =", round(zz["q_serv_kgcm"], 3), "kg/cm²  uso", round(zz["u_serv"], 3))
    p("corte c", round(zz["c_corte"], 2), "V", round(zz["V_corte"]), "v", round(zz["v_corte"], 3),
      "vc", round(zz["v_c_corte"], 3), zz["corte_ok"])
    p("b_o", zz["b_o"], "V_punz", round(zz["V_punz"]), "v", round(zz["v_punz"], 3), "vc", round(zz["v_c_punz"], 3),
      zz["punz_ok"])
    p("M_u", round(zz["M_u"], 1), "As_flex", round(zz["As_flex"], 3), "As_min", round(zz["As_min"], 2),
      "gobierna", zz["gobierna"], "As_adop", round(zz["As_adop"], 3), zz["acero_ok"])
    p("Ld", round(zz["Ld"], 2), "disp", round(zz["Ld_disp"], 2), zz["Ld_ok"])
    p("Pn_col", round(zz["Pn_col"], 1), "Pn_base", round(zz["Pn_base"], 1), "t  apl_ok", zz["apl_ok"])
    p("sismo P", round(zz["P_sismo_total"]), "q", round(zz["q_sismo"], 1), "u", round(zz["u_sismo"], 3),
      zz["sismo_ok"], "| FS desliz", round(zz["FS_desliz"], 2))
    p("asent", round(zz["s_elast"], 3), "cm lim", zz["s_lim"], zz["s_ok"])
    p("pedestal As min", round(zz["ped_As_min"], 2), "As", round(zz["ped_As"], 2), zz["ped_ok"])
    print("== RIOSTRA ==")
    rri = r["riostra"]
    p("As 8.1", round(rri["A_s_81"], 3), "As min", round(rri["A_s_min"], 3), "As H", round(rri["A_s_H"], 3),
      "adop", rri["A_s_adop"], rri["acero_ok"], "s estribo", rri["s_estribo"], "max", round(rri["s_max"], 2))
    print("== LOSA ==")
    print(r["losa"])
    print("== D/C ==")
    for n, r_, ok in r["dc"]:
        print(f"   {'OK ' if ok else '✗  '} {r_:6.3f}  {n}")
