"""Cálculos 4 a 8 del cuaderno."""
from hcom import R, f, tabla, calc, fml, sus, res, nota, figura, ok_badge

g, c, a, s = R["geo"], R["cargas"], R["global"], R["sismo"]
v, t, w = R["correa"], R["cercha"], R["soldadura"]
k, b, ti = R["columna"], R["placa"], R["tirante"]
r6, r2 = s["casos"][6], s["casos"][2]
ca = k["casos"]


def ej4():
    return f"""
<h2 id="e4">4 · Acción sísmica — COVENIN 1756-1:2019, método de las fuerzas horizontales equivalentes</h2>
<p>El método consiste en estimar el corte basal <b>V₀ = C·W</b> y repartirlo entre los pórticos;
   cada columna queda en voladizo empotrada en su base, de modo que el momento en la base vale
   <b>M = V col·h</b>. Se calculan <u>dos hipótesis de factor de reducción</u>: R = 6 (pórticos de
   acero con nivel de diseño ND3, el que trae la planilla del proyecto) y R = 2 (si la edificación
   se clasifica con un nivel de diseño menor, caso Tipo IV). Comparar las dos es el corazón de
   este cálculo, porque el resultado cambia por completo.</p>
{tabla(["Parámetro", "Símbolo", "Valor", "Observación"],
       [["Aceleración horizontal del suelo", "A a", "0,345", "zonificación de Higuerote (memoria, etapa H)"],
        ["Aceleración vertical", "A v", "0,669", "se usa solo en combinaciones con sismo vertical"],
        ["Período de vibración estimado", "T a", f"{f(s['Ta'], 2)} s", "estimado con las fórmulas del §9"],
        ["Período característico del suelo", "T c", f"{f(s['TC'], 3)} s", "suelo tipo S2"],
        ["Factor de corrección por amortiguamiento", "φ", f"{f(s['phi_esp'], 4)}", "5 % de amortiguamiento"],
        ["Factor de amplificación de la deriva", "C d", f"{f(s['Cd'], 2)}", "Tabla 7.1 (Tipo IV)"],
        ["Peso sísmico", "W", f"{f(c['W_total'] / 1000, 2)} t", "calculado en el paso 2.5"]],
       caption="Tabla 4.1 — Datos sísmicos adoptados (etapa H de la memoria del proyecto).",
       clases="chica")}
{nota("Estos valores se adoptaron en la etapa H del proyecto (análisis sísmico) a partir del mapa "
      "de zonificación y del perfil de suelo supuesto. <b>Deben verificarse contra las tablas "
      "vigentes de COVENIN 1756-1:2019 antes de la entrega definitiva</b>: si cambia la zona o el "
      "perfil de suelo, cambian A a, el corte basal, las derivas y el diseño de la placa base.")}

{calc("Paso 4.1", "Coeficiente sísmico de diseño",
      fml("A d = 2,4 · A a / R      (ordenada del espectro en la meseta, = 2,4·A a, reducida por R)<br>"
          "C = φ · A d      (corrección por amortiguamiento; se compara con C mín = A a / R)")
      + sus(f"R = 6:  A d = 2,4 × 0,345 / 6 = {f(r6['Ad'], 4)}   →   C = {f(s['phi_esp'], 4)} × {f(r6['Ad'], 4)} = {f(r6['C'], 4)}<br>"
            f"R = 2:  A d = 2,4 × 0,345 / 2 = {f(r2['Ad'], 4)}   →   C = {f(s['phi_esp'], 4)} × {f(r2['Ad'], 4)} = {f(r2['C'], 4)}")
      + res(f"C (R = 6) = {f(r6['C'], 4)}   |   C (R = 2) = {f(r2['C'], 4)}"))}

{calc("Paso 4.2", "Corte basal y corte por pórtico",
      fml("V 0 = C · W      V pórtico = V 0 / n      V columna = V pórtico / 2")
      + sus(f"R = 6:  V 0 = {f(r6['C'], 4)} × {f(c['W_total'] / 1000, 2)} t = {f(r6['V0'], 2)} t"
            f"   →   V pórtico = {f(r6['V_portico'], 3)} t   →   V col = {f(r6['V_col'], 3)} t<br>"
            f"R = 2:  V 0 = {f(r2['C'], 4)} × {f(c['W_total'] / 1000, 2)} t = {f(r2['V0'], 2)} t"
            f"   →   V pórtico = {f(r2['V_portico'], 3)} t   →   V col = {f(r2['V_col'], 3)} t")
      + res(f"V 0 (R = 6) = {f(r6['V0'], 2)} t   |   V 0 (R = 2) = {f(r2['V0'], 2)} t")
      + nota("La columna se verifica como <b>ménsula empotrada en la zapata</b>: no hay vigas "
             "de arriostramiento a media altura, el arco toma las cargas verticales y la riostra "
             "transmite el par de vuelco."))}

{calc("Paso 4.3", "Momento en la base de la columna",
      fml("M base = V col · h")
      + sus(f"R = 6:  M base = {f(r6['V_col'], 3)} × {f(g['h'], 2)} = {f(r6['M_base'], 2)} t·m<br>"
            f"R = 2:  M base = {f(r2['V_col'], 3)} × {f(g['h'], 2)} = {f(r2['M_base'], 2)} t·m")
      + res(f"M base (R = 6) = {f(r6['M_base'], 2)} t·m   |   M base (R = 2) = {f(r2['M_base'], 2)} t·m"))}

{calc("Paso 4.4", "Deriva elástica de la columna en voladizo",
      fml("δ e = V col · h³ / (3 · E · I x)      Δ = C d · δ e      Δ adm = 0,020 · h")
      + sus(f"h = {f(g['h'], 2)} m = {f(g['h'] * 100, 1)} cm      I x (HEB 300) = 25 170 cm⁴<br>"
            f"R = 6:  δ e = {f(r6['V_col'] * 1000, 1)} × {f(g['h'] * 100, 1)}³ / (3 × 2,1×10⁶ × 25 170) "
            f"= {f(r6['delta_e'], 3)} cm   →   Δ = {f(s['Cd'], 2)} × {f(r6['delta_e'], 3)} = {f(r6['Delta'], 2)} cm<br>"
            f"R = 2:  δ e = {f(r2['V_col'] * 1000, 1)} × {f(g['h'] * 100, 1)}³ / (3 × 2,1×10⁶ × 25 170) "
            f"= {f(r2['delta_e'], 3)} cm   →   Δ = {f(s['Cd'], 2)} × {f(r2['delta_e'], 3)} = {f(r2['Delta'], 2)} cm")
      + f'<div class="res{" bad" if not r2["deriva_ok"] else ""}">'
        f'Δ adm = 0,020 × 850 = {f(r6["delta_lim"], 1)} cm<br>'
        f'R = 6 → Δ = {f(r6["Delta"], 2)} cm ≤ {f(r6["delta_lim"], 1)} cm '
        f'<span class="badge {"b-ok" if r6["deriva_ok"] else "b-bad"}">cumple</span><br>'
        f'R = 2 → Δ = {f(r2["Delta"], 2)} cm &gt; {f(r2["delta_lim"], 1)} cm '
        f'<span class="badge {"b-ok" if r2["deriva_ok"] else "b-bad"}">no cumple</span></div>')}

{calc("Paso 4.5", "Par de vuelco que recibe la viga de riostra",
      fml("ΔP = 2 · M base / L      — el par de vuelco de dos columnas opuestas se cierra con la riostra")
      + sus(f"R = 6:  ΔP = 2 × {f(r6['M_base'], 2)} / {f(g['L'], 2)} = {f(r6['dP_riostra'], 3)} t<br>"
            f"R = 2:  ΔP = 2 × {f(r2['M_base'], 2)} / {f(g['L'], 2)} = {f(r2['dP_riostra'], 3)} t")
      + res(f"ΔP (R = 6) = {f(r6['dP_riostra'], 2)} t   |   ΔP (R = 2) = {f(r2['dP_riostra'], 2)} t")
      + nota("Este ΔP se suma a la carga de la zapata en la verificación sísmica (paso 11.9) y "
             "define el acero mínimo de la riostra (cálculo 12)."))}

"""


def ej5():
    vv = v
    return f"""
<h2 id="e5">5 · Correas de cubierta — IPN 140</h2>
<p>La correa es una viga simplemente apoyada entre pórticos, de luz S = {f(g['S'], 2)} m, que recibe
   la carga del área tributaria igual al paso de correas. Por estar sobre una superficie inclinada
   α = {f(vv['alfa'], 3)}°, la carga se descompone en una componente perpendicular a la cubierta
   (que flexiona el eje fuerte) y una tangencial (eje débil).</p>

{calc("Paso 5.1", "Carga lineal sobre la correa",
      fml("q = (cargas por m²) · paso de correas + peso propio del perfil")
      + sus(f"q serv = ({f(c['D'], 1)} + {f(c['colgadas'], 1)} + {f(c['L'], 1)}) × {f(vv['tributaria'], 4)} "
            f"+ 14,3 = {f(vv['q_serv'], 2)} kg/m<br>"
            f"q u = [1,2 × 38,0 + 1,6 × 100,0] × {f(vv['tributaria'], 4)} + 1,2 × 14,3 = {f(vv['q_u'], 2)} kg/m")
      + res(f"q serv = {f(vv['q_serv'], 2)} kg/m   |   q u = {f(vv['q_u'], 2)} kg/m"))}

{calc("Paso 5.2", "Descomposición de la carga según la inclinación",
      fml("q n = q u · cos α      (normal a la cubierta, eje fuerte)<br>"
          "q t = q u · sen α      (tangencial, eje débil)")
      + sus(f"q n = {f(vv['q_u'], 2)} × cos {f(vv['alfa'], 3)}° = {f(vv['q_n_u'], 2)} kg/m<br>"
            f"q t = {f(vv['q_u'], 2)} × sen {f(vv['alfa'], 3)}° = {f(vv['q_t_u'], 2)} kg/m")
      + res(f"q n = {f(vv['q_n_u'], 2)} kg/m   |   q t = {f(vv['q_t_u'], 2)} kg/m"))}

{calc("Paso 5.3", "Momentos flectores",
      fml("M x = q n · S² / 8      M y = q t · S² / 8   — viga simplemente apoyada")
      + sus(f"M x = {f(vv['q_n_u'], 2)} × {f(g['S'], 2)}² / 8 = {f(vv['Mx_u'], 1)} kg·m<br>"
            f"M y = {f(vv['q_t_u'], 2)} × {f(g['S'], 2)}² / 8 = {f(vv['My_u'], 1)} kg·m")
      + res(f"M x = {f(vv['Mx_u'], 1)} kg·m   |   M y = {f(vv['My_u'], 1)} kg·m"))}

{calc("Paso 5.4", "Momento resistente de diseño del IPN 140",
      fml("φM n = φ · F y · W x      (φ = 0,90; sección compacta, COVENIN 1618-98 §6.10)")
      + sus(f"φM n,x = 0,90 × 2 530 × 81,9 = {f(vv['Mcx'] * 100, 0)} kg·cm = {f(vv['Mcx'], 0)} kg·m<br>"
            f"φM n,y = 0,90 × 2 530 × 12,3 = {f(vv['Mcz'] * 100, 0)} kg·cm = {f(vv['Mcz'], 0)} kg·m")
      + res(f"φM n,x = {f(vv['Mcx'], 0)} kg·m   |   φM n,y = {f(vv['Mcz'], 0)} kg·m"))}

{calc("Paso 5.5", "Verificación a flexión",
      fml("D/C = M x / φM n,x      (eje fuerte, correa arriostrada contra la lámina)<br>"
          "D/C biaxial = M x / φM n,x + M y / φM n,y      (si la componente tangencial la tomara la correa)")
      + sus(f"D/C eje fuerte = {f(vv['Mx_u'], 1)} / {f(vv['Mcx'], 0)} = {f(vv['dc_x'], 3)}<br>"
            f"D/C eje débil = {f(vv['My_u'], 1)} / {f(vv['Mcz'], 0)} = {f(vv['dc_z'], 3)}<br>"
            f"D/C biaxial = {f(vv['dc_x'], 3)} + {f(vv['dc_z'], 3)} = {f(vv['dc_biaxial'], 3)}")
      + f'<div class="res"><b>Adoptado: la componente tangencial no flexiona la correa</b> — se '
        f'transmite al cordón del arco por la conexión pernada, y el cordón la recibe como fuerza '
        f'axial (cálculo 6). D/C = {f(vv["dc_x"], 3)} '
        f'<span class="badge {"b-ok" if vv["dc_x"] <= 1 else "b-bad"}">cumple</span></div>'
      + nota(f"Sin ese criterio la correa daría D/C = {f(vv['dc_biaxial'], 2)} y no cumpliría: la "
             "conexión con el cordón no es un detalle, es parte del cálculo. Se recomienda además "
             "gramil de dos pernos Φ1/2″ en cada apoyo."))}

{calc("Paso 5.6", "Flecha (estado de servicio)",
      fml("δ = 5 · q n(servicio) · S⁴ / (384 · E · I x)      δ adm = S / 300   — MINDUR 2002, Tabla 9.1")
      + sus(f"q n,serv = {f(vv['q_serv'], 2)} × cos {f(vv['alfa'], 3)}° = {f(vv['q_n_serv'], 2)} kg/m "
            f"= {f(vv['q_n_serv'] / 100, 4)} kg/cm<br>"
            f"δ = 5 × {f(vv['q_n_serv'] / 100, 4)} × 410⁴ / (384 × 2,1×10⁶ × 573) = {f(vv['flecha'], 3)} cm<br>"
            f"δ adm = 410 / 300 = {f(vv['flecha_lim'], 3)} cm")
      + res(f"δ = {f(vv['flecha'], 3)} cm ≤ {f(vv['flecha_lim'], 3)} cm   →  D/C = "
            f"{f(vv['flecha'] / vv['flecha_lim'], 2)}", ok=vv['flecha_ok']))}

{calc("Paso 5.7", "Corte en el apoyo (verificación rápida del alma)",
      fml("V u = q n · S / 2      τ u = V u / (φ · 0,6 · F y · t w · h w)")
      + sus(f"V u = {f(vv['q_n_u'], 2)} × {f(g['S'], 2)} / 2 = {f(vv['V_u'], 1)} kg<br>"
            f"τ u = {f(vv['V_u'], 1)} / (0,90 × 0,60 × 2 530 × 6,88) = {f(vv['tau_u'], 3)} kg/cm² "
            f"&lt;&lt; 0,6·F y = 1 518 kg/cm²")
      + res("El alma del IPN 140 está muy lejos de agotarse por corte; no gobierna.", ok=True))}
"""


def ej6():
    return f"""
<h2 id="e6">6 · Cercha de doble arco</h2>
<p>El arco son dos cordones (extradós e intradós) de 2×IPE 160 cada uno, unidos por diagonales en
   cruz de San Andrés en cada panel y montantes en los nudos. La fuerza axial de los cordones
   proviene del par de fuerzas del paso 3.4 y las diagonales del panel extremo reciben la
   reacción de la columna.</p>
{figura('fig-cl', ('6.1', 'Esquema del par de fuerzas N u = M u/d que comprime el cordón superior '
                           'y tracciona el inferior.'))}

{calc("Paso 6.1", "Pandeo del cordón (2×IPE 160)",
      fml("λ = K · L pandeo / i y<br>"
          "F e = π² · E / λ²<br>"
          "F cr = 0,658^(F y / F e) · F y   (pandeo inelástico, λ ≤ 4,71√(E/F y))<br>"
          "φP n = φ · F cr · A      (φ = 0,90 — COVENIN 1618-98 §6.8, AISC 360 §E3)")
      + sus(f"L pandeo = Δs = {f(t['L_pandeo_cordon'], 2)} cm (un panel);  i y = 1,84 cm<br>"
            f"λ = {f(t['L_pandeo_cordon'], 2)} / 1,84 = {f(t['lam_cordon'], 1)}   ≤ 4,71·√(2,1×10⁶/2 530) = 135,7 ✓<br>"
            f"F e = π² × 2,1×10⁶ / {f(t['lam_cordon'], 1)}² = {f(t['Fcr_cordon'] * 0 + (3.1416**2 * 2.1e6 / t['lam_cordon']**2), 0)} kg/cm²<br>"
            f"F cr = 0,658^({f(2530 / (3.1416**2 * 2.1e6 / t['lam_cordon']**2), 3)}) × 2 530 = {f(t['Fcr_cordon'], 0)} kg/cm²"
            f"   →   φF cr = {f(t['phiFcr_cordon'], 0)} kg/cm²<br>"
            f"φP n = {f(t['phiFcr_cordon'], 0)} × {f(t['A_cordon'], 1)} = {f(t['phiPn_cordon'], 0)} kg")
      + res(f"φP n = {f(t['phiPn_cordon'] / 1000, 2)} t   →   D/C = N u / φP n = "
            f"{f(t['N_cordon'], 0)} / {f(t['phiPn_cordon'], 0)} = {f(t['dc_cordon'], 3)}",
            ok=t["dc_cordon"] <= 1))}

{calc("Paso 6.2", "Tracción del cordón inferior",
      fml("φP n = φ · F y · A      (φ = 0,90 — cedencia en la sección bruta)")
      + sus(f"φP n = 0,90 × 2 530 × {f(t['A_cordon'], 1)} = {f(t['phiPn_traccion'], 0)} kg")
      + res(f"D/C = {f(t['N_cordon'], 0)} / {f(t['phiPn_traccion'], 0)} = {f(t['dc_traccion'], 3)}",
            ok=t["dc_traccion"] <= 1))}

{calc("Paso 6.3", "Diagonal del panel extremo (cruz de San Andrés)",
      fml("β = arctan (d / Δs)      L diag = √(Δs² + d²)<br>"
          "N diag,total = R u / sen β      N diag = N diag,total / 2   (dos diagonales por panel)")
      + sus(f"β = arctan ({f(g['d'], 2)} / {f(g['ds'], 4)}) = {f(t['beta_diag'], 2)}°<br>"
            f"L diag = √({f(g['ds'], 4)}² + {f(g['d'], 2)}²) × 100 = {f(t['L_diag'], 2)} cm<br>"
            f"N diag,total = {f(a['R_u'], 0)} / sen {f(t['beta_diag'], 2)}° = {f(t['N_diag_total'], 0)} kg<br>"
            f"N diag = {f(t['N_diag_total'], 0)} / 2 = {f(t['N_diag'], 0)} kg")
      + res(f"Cada diagonal toma N = {f(t['N_diag'] / 1000, 2)} t"))}

{calc("Paso 6.4", "Verificación de la diagonal IPE 160",
      fml("λ = L diag / i y      φP n = φ · F cr · A   (mismo procedimiento del paso 6.1)")
      + sus(f"λ = {f(t['L_diag'], 2)} / 1,84 = {f(t['lam_diag'], 1)}<br>"
            f"F e = π² × 2,1×10⁶ / {f(t['lam_diag'], 1)}² = "
            f"{f(3.1416**2 * 2.1e6 / t['lam_diag'] ** 2, 0)} kg/cm²   →   F cr = {f(t['Fcr_diag'], 0)} kg/cm²<br>"
            f"φP n = {f(t['phiFcr_diag'], 0)} × {f(20.1, 1)} = {f(t['phiPn_diag'], 0)} kg")
      + res(f"D/C = {f(t['N_diag'], 0)} / {f(t['phiPn_diag'], 0)} = {f(t['dc_diag'], 3)}",
            ok=t["dc_diag"] <= 1))}

{calc("Paso 6.5", "Montante en el nudo de la correa (IPE 120)",
      fml("N montante = reacción de la correa = q u · S / 2      λ = d / i y      φP n según 6.1")
      + sus(f"N = {f(v['q_u'], 2)} × {f(g['S'], 2)} / 2 = {f(t['N_montante'], 0)} kg<br>"
            f"λ = {f(t['L_montante'], 0)} / 1,45 = {f(t['lam_montante'], 1)}   →   F cr = {f(t['Fcr_montante'], 0)} kg/cm²"
            f"   →   φP n = {f(t['phiPn_montante'], 0)} kg")
      + res(f"D/C = {f(t['dc_montante'], 3)}", ok=t["dc_montante"] <= 1))}

{calc("Paso 6.6", "Cartela (gusset) del nudo de apoyo",
      fml("A cartela = N apoyo,horizontal / (0,66 · F y)   — aplastamiento/fluencia de la plancha<br>"
          "lado mínimo = √A      se adopta cartela 20 × 35 cm, t = 1,2 cm")
      + sus(f"A = {f(a['H_u'], 0)} / (0,66 × 2 530) = {f(t['A_gusset'], 2)} cm²<br>"
            f"lado mínimo = √{f(t['A_gusset'], 2)} = {f(t['lado_gusset_min'], 2)} cm")
      + res(f"Cartela adoptada: {t['cartela'][0]} × {t['cartela'][1]} cm, t = {f(t['espesor_gusset'], 1)} cm "
            f"&gt;&gt; lado mínimo {f(t['lado_gusset_min'], 1)} cm", ok=True))}
"""


def ej7():
    return f"""
<h2 id="e7">7 · Soldadura de filete del nudo de apoyo</h2>
<p>Todas las uniones se resuelven con soldadura de filete de <b>6 mm de pata</b> y electrodo E70XX.
   La resistencia de diseño de un cordón de filete es
   <span class="mono">φR n = φ·0,6·F EXX·garganta</span> por centímetro de longitud, con
   garganta = 0,707·pata (COVENIN 1618-98, parte 4 §7.2; AISC 360 §J2.4).</p>
{figura('fig-soldadura', ('7.1', 'Nudo de apoyo: cordones de filete en la diagonal, el cordón del '
                                 'arco y la placa base.'))}

{calc("Paso 7.1", "Resistencia de un cordón de filete de 6 mm",
      fml("garganta = 0,707 · pata      φR n = φ · 0,6 · F EXX · garganta      (φ = 0,75)")
      + sus(f"garganta = 0,707 × 0,6 cm = {f(w['garganta'], 4)} cm<br>"
            f"φR n = 0,75 × 0,6 × 4 920 × {f(w['garganta'], 4)} = {f(w['phiRn_cm'], 0)} kg por cm de cordón")
      + res(f"φR n = {f(w['phiRn_cm'], 0)} kg/cm") )}

{calc("Paso 7.2", "Longitud de cordón en la diagonal",
      fml("L nec = N diag / φR n      L mín = 4 · pata")
      + sus(f"L nec = {f(t['N_diag'], 0)} / {f(w['phiRn_cm'], 0)} = {f(w['L_diag_nec'], 2)} cm (suma de los dos filetes)<br>"
            f"L mín = 4 × 6 mm = {f(w['Lmin'], 1)} cm por cordón<br>"
            f"adoptado: 2 cordones de {f(w['L_diag_adop'] / 2, 0)} cm = {f(w['L_diag_adop'], 0)} cm")
      + res(f"D/C = {f(w['dc_diag'], 3)}", ok=w["dc_diag"] <= 1))}

{calc("Paso 7.3", "Longitud de cordón en el cordón del arco (2×IPE 160)",
      fml("L nec = N cordón / (4 · φR n)      — cuatro cordones, dos por cada IPE")
      + sus(f"L nec = {f(t['N_cordon'], 0)} / (4 × {f(w['phiRn_cm'], 0)}) = {f(w['L_cordon_nec'], 2)} cm por cordón<br>"
            f"adoptado: 4 cordones de {f(w['L_cordon_adop'], 0)} cm (longitud de la cartela)")
      + res(f"D/C = {f(w['dc_cordon'], 3)}", ok=w["dc_cordon"] <= 1))}

{calc("Paso 7.4", "Cordón de la placa base",
      fml("φR n,total = perímetro soldado · φR n      D/C = P u / φR n,total")
      + sus(f"perímetro = 4 × 30 cm = {f(w['perim_columna'], 0)} cm (alas de la HEB 300)<br>"
            f"φR n,total = {f(w['perim_columna'], 0)} × {f(w['phiRn_cm'], 0)} = "
            f"{f(w['perim_columna'] * w['phiRn_cm'], 0)} kg<br>"
            f"D/C = {f(a['P_u_zapata'] * 1000, 0)} / {f(w['perim_columna'] * w['phiRn_cm'], 0)}")
      + res(f"D/C = {f(w['dc_placa'], 3)}", ok=w["dc_placa"] <= 1)
      + nota("La placa base se suelda con <b>cartelas de refuerzo</b> en las cuatro esquinas "
             "para que el momento sísmico se transmita sin flexar la placa; sin cartelas el "
             "cordón del ala trabajaría a tracción y habría que recalcular la junta."))}
"""


def ej8():
    filas = []
    for nombre, d in ca.items():
        filas.append([nombre, (f"{f(d['M'], 2)} t·m", "n"), (f"{f(d['pc'], 3)}", "n"),
                      (f"{f(d['pr'], 3)}", "n"), (f"{f(d['inter'], 3)}", "n"),
                      (ok_badge(d["ok"]), "")])
    return f"""
<h2 id="e8">8 · Columna HEB 300</h2>
<p>La columna está <b>empotrada en la zapata y libre arriba</b> (recibe el arco). Su longitud de
   pandeo es por eso K·h con K = 2,0 — el caso más desfavorable de ménsula. Se calcula con la
   misma formulación de acero y luego se verifica la interacción <b>carga axial + momento</b>
   con las dos ramas de la ecuación de interacción de COVENIN 1618-98 (AISC 360 §H1).</p>

{calc("Paso 8.1", "Pandeo por compresión pura",
      fml("λ x = K · h / i x      F e = π²·E/λ²      F cr = 0,658^(F y/F e)·F y      φP n = φ·F cr·A")
      + sus(f"λ x = 2,0 × 850 / 12,99 = {f(k['lam_x'], 1)}   (≤ 135,7 → pandeo inelástico)<br>"
            f"F e = π² × 2,1×10⁶ / {f(k['lam_x'], 1)}² = {f(3.1416**2 * 2.1e6 / k['lam_x'] ** 2, 0)} kg/cm²"
            f"   →   F cr = {f(k['Fcr_x'], 0)} kg/cm²   →   φF cr = {f(k['phiFcr_x'], 0)} kg/cm²<br>"
            f"φP n = {f(k['phiFcr_x'], 0)} × 149,1 / 1 000 = {f(k['phiPn'], 2)} t")
      + res(f"φP n = {f(k['phiPn'], 2)} t   →   D/C axial = {f(k['P_u'], 2)} / {f(k['phiPn'], 2)} = "
            f"{f(k['dc_carga'], 3)}", ok=k["dc_carga"] <= 1))}

{calc("Paso 8.2", "Momento resistente",
      fml("φM n = φ · F y · W x      (φ = 0,90)")
      + sus(f"φM n = 0,90 × 2 530 × 1 679 / 100 000 = {f(k['phiMn'], 2)} t·m")
      + res(f"φM n = {f(k['phiMn'], 2)} t·m"))}

{calc("Paso 8.3", "Interacción carga axial + momento (tres hipótesis)",
      fml("Si P u/φP n ≥ 0,20:  P u/φP n + (8/9)·(M u/φM n) ≤ 1,00<br>"
          "Si P u/φP n &lt; 0,20:  P u/(2·φP n) + M u/φM n ≤ 1,00")
      + res("Resultados (M u según la hipótesis de empuje o de sismo)", ok=None)
      + tabla([("Hipótesis", ""), ("M u (t·m)", "n"), ("P u/φP n", "n"), ("M u/φM n", "n"),
               ("Interacción", "n"), ("Estado", "")],
              filas, caption="Tabla 8.1 — Interacción P–M de la columna HEB 300.")
      + nota("<b>Lectura del resultado:</b> con sismo (R = 6 o R = 2) la columna cumple de sobra, "
             "porque el momento sísmico es pequeño. En cambio, si el empuje del arco H u llegara a "
             "la cabeza de la columna (sin tirante), el momento vale ≈ 120 t·m y la interacción da "
             "3,18: <b>no cumple</b>. Esa es la razón técnica del tirante del cálculo 9."))}
"""
