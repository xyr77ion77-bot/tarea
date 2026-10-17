"""Cálculos 9 a 11: tirante, placa base y zapata aislada (el cálculo más reciente)."""
from hcom import R, f, tabla, calc, fml, sus, res, nota, figura, ok_badge, num

g, c, a, s = R["geo"], R["cargas"], R["global"], R["sismo"]
w, ti, b = R["soldadura"], R["tirante"], R["placa"]
z = R["zapata"]
r6, r2 = s["casos"][6], s["casos"][2]
H_serv = c["q_serv_total"] * g["L"] ** 2 / (8 * g["f"])


def ej9():
    return f"""
<h2 id="e9">9 · Tirante de cabeza entre columnas</h2>
<p>El resultado del cálculo 8 es concluyente: <b>la columna no puede recibir el empuje del arco</b>
   (interacción 3,18 con H u = {f(a['H_u'] / 1000, 2)} t). La solución clásica —y la que usan los
   arcos de celosía de este tipo— es un <b>tirante de cabeza</b> que amarra las dos columnas a la
   altura de arranque del arco, de modo que el empuje se cierre entre ellas y no llegue a la
   fundación.</p>

{calc("Paso 9.1", "Tracción de diseño del tirante",
      fml("T u = H u      (el tirante toma todo el empuje del arco)")
      + sus(f"T u = {f(a['H_u'], 0)} kg = {f(a['H_u'] / 1000, 2)} t<br>"
            f"En servicio:  H serv = q serv,tot · L²/(8f) = {f(c['q_serv_total'], 2)} × {f(g['L'], 2)}² / "
            f"(8 × {f(g['f'], 2)}) = {f(H_serv, 0)} kg")
      + res(f"T u = {f(ti['T_u'] / 1000, 2)} t   |   T serv = {f(H_serv / 1000, 2)} t"))}

{calc("Paso 9.2", "Selección del diámetro (barra roscada / cabilla de anclaje)",
      fml("φP n = φ · F y · A      (φ = 0,90 — cedencia a tracción, COVENIN 1618-98 §6.9)")
      + sus(f"Φ1-1/2″ → A = {f(ti['A'], 2)} cm²<br>"
            f"φP n = 0,90 × 2 530 × {f(ti['A'], 2)} = {f(ti['phiPn'], 0)} kg = {f(ti['phiPn'] / 1000, 2)} t")
      + res(f"D/C = {f(ti['T_u'], 0)} / {f(ti['phiPn'], 0)} = {f(ti['dc'], 3)} "
            f"→ se adopta Φ1-1/2″ (A = {f(ti['A'], 2)} cm²)", ok=ti["ok"]))}

{calc("Paso 9.3", "Esfuerzo real y flecha por peso propio",
      fml("σ = T / A      f peso propio ≈ w·L² / (8·T)")
      + sus(f"σ serv = {f(H_serv, 0)} / {f(ti['A'], 2)} = {f(ti['sigma_serv'], 0)} kg/cm² "
            f"(≤ 0,60·F y = 1 518 kg/cm²)<br>"
            f"σ u = {f(ti['T_u'], 0)} / {f(ti['A'], 2)} = {f(ti['sigma'], 0)} kg/cm²<br>"
            f"w = {f(ti['A'], 2)} cm² × 0,785 = {f(ti['w'], 2)} kg/m   →   "
            f"f = {f(ti['w'], 2)} × {f(g['L'], 2)}² / (8 × {f(ti['T_u'], 0)}) = "
            f"{f(ti['sag'], 4)} m")
      + res(f"σ serv = {f(ti['sigma_serv'], 0)} kg/cm² &lt; 1 518 kg/cm²   |   flecha por peso "
            f"propio ≈ {f(ti['sag'] * 100, 1)} cm (despreciable)", ok=True)
      + nota("El tirante se arma con <b>tensores (turnbuckles)</b> en los extremos para poder "
             "tensarlo en obra, y las orejetas de anclaje se sueldan a la placa base con el mismo "
             "filete de 6 mm del cálculo 7. <b>Esta solución debe quedar escrita en la memoria</b>: "
             "si el tirante no se coloca, la columna HEB 300 no resiste (cálculo 8, tabla 8.1)."))}
"""


def ej10():
    cas = b["casos"]
    return f"""
<h2 id="e10">10 · Placa base y pernos de anclaje</h2>
<p>La placa base reparte la carga de la columna sobre el pedestal de concreto y, cuando hay sismo,
   tiene que transmitir además el <b>par de vuelco</b>: una parte de los pernos trabaja a tracción
   y el concreto en compresión. La placa adoptada es de <b>{f(b['lado'], 0)} × {f(b['lado'], 0)} cm,
   t = {f(b['t'] * 10, 0)} mm</b>, con {b['n_pernos']} pernos Φ3/4″ repartidos en dos líneas.</p>
{figura('fig-placa', ('10.1', 'Placa base 45×45 cm, líneas de pernos y detalle del anclaje.') )}

{calc("Paso 10.1", "Presión de contacto sobre el pedestal",
      fml("σ = P u / A placa      y comparación con la resistencia al aplastamiento del concreto"
          "<br>φP p = φ·0,85·f′c·A₁·√(A₂/A₁) ≤ 2·φ·0,85·f′c·A₁      (φ = 0,70)")
      + sus(f"σ = {f(z['P_u'], 0)} / {f(b['lado'] ** 2, 0)} = {f(b['sigma'], 2)} kg/cm²<br>"
            f"φP p (pedestal 40×40) = 0,70 × 0,85 × 210 × 1 600 / 1 000 = {f(z['Pn_col'], 1)} t "
            f"(sin el factor √(A₂/A₁) ≤ 2)")
      + res(f"σ = {f(b['sigma'], 2)} kg/cm² &lt;&lt; 0,85·f′c = 178,5 kg/cm²  →  "
            f"P u / φP p = {f(z['P_u'] / (z['Pn_col'] * 1000), 4)}", ok=True))}

{calc("Paso 10.2", "Espesor de la placa por flexión (hipótesis de compresión)",
      fml("m = (lado − ancho del ala)/2      M placa = σ·m²/2      t = √(4·M/(0,9·F y))")
      + sus(f"m = ({f(b['lado'], 0)} − 30,0)/2 = {f(b['m'], 1)} cm<br>"
            f"M = {f(b['sigma'], 2)} × {f(b['m'], 1)}² / 2 = {f(b['M_placa'], 1)} kg·cm/cm<br>"
            f"t = √(4 × {f(b['M_placa'], 1)} / (0,9 × 2 530)) = {f(b['t_nec'] / 10, 3)} cm = {f(b['t_nec'], 1)} mm")
      + res(f"t nec (compresión) = {f(b['t_nec'], 1)} mm → no gobierna; se adopta t = {f(b['t'] * 10, 0)} mm "
            f"por la tracción de los pernos (paso 10.4)", ok=True))}

{calc("Paso 10.3", "Par de vuelco y tracción en los pernos",
      fml("z = 0,90 · s      (brazo del par entre la línea de pernos traccionada y la compresión del concreto)<br>"
          "T par = M base / z      T total = T par − P u/2      T perno = T total / (n/2)")
      + sus(f"z = 0,90 × {f(b['s_pernos'], 1)} = {f(b['z_pernos'] * 100, 2)} cm<br>"
            f"Sismo R = 6:  M base = {f(cas['Sismo R = 6']['M'], 2)} t·m → T par = {f(cas['Sismo R = 6']['T_par'], 0)} kg; "
            f"T total = {f(cas['Sismo R = 6']['T_par'], 0)} − {f(z['P_u'], 0)}/2 = {f(cas['Sismo R = 6']['T_total'], 0)} kg; "
            f"T perno = {f(cas['Sismo R = 6']['T_perno'], 0)} kg<br>"
            f"Sismo R = 2:  M base = {f(cas['Sismo R = 2']['M'], 2)} t·m → T par = {f(cas['Sismo R = 2']['T_par'], 0)} kg; "
            f"T total = {f(cas['Sismo R = 2']['T_total'], 0)} kg; T perno = {f(cas['Sismo R = 2']['T_perno'], 0)} kg")
      + f'<div class="res">'
        f'Φ3/4″ (A = 2,85 cm²): φT n = 0,75 × 2,85 × 2 530 = {f(cas["Sismo R = 6"]["cap_34"], 0)} kg → '
        f'D/C = {f(cas["Sismo R = 6"]["T_perno"] / cas["Sismo R = 6"]["cap_34"], 3)} '
        f'<span class="badge b-ok">cumple (R = 6)</span><br>'
        f'Φ1″ (A = 5,07 cm²): φT n = 0,75 × 5,07 × 2 530 = {f(cas["Sismo R = 2"]["cap_1"], 0)} kg → '
        f'D/C = {f(cas["Sismo R = 2"]["T_perno"] / cas["Sismo R = 2"]["cap_1"], 3)} '
        f'<span class="badge b-bad">no cumple (R = 2)</span></div>'
      + nota("<b>Bandera roja del proyecto:</b> la placa base está dimensionada con el sismo "
             "R = 6, que es el que trae la planilla. Si la edificación se clasifica finalmente con "
             "R = 2, hay que rediseñar la placa (más pernos o pernos de mayor diámetro y placa más "
             "gruesa). Queda planteado como tarea pendiente."))}

{calc("Paso 10.4", "Espesor de la placa por tracción de los pernos (sismo R = 6)",
      fml("M placa = T perno · a      t = √(6·M/(0,9·F y·b franja))   con b franja = ancho del ala = 30 cm")
      + sus(f"a = {f(b['a_perno'], 0)} cm (del perno a la cara del ala)<br>"
            f"M = {f(cas['Sismo R = 6']['T_perno'], 0)} × {f(b['a_perno'], 0)} = "
            f"{f(cas['Sismo R = 6']['T_perno'] * b['a_perno'], 0)} kg·cm<br>"
            f"t = √(6 × {f(cas['Sismo R = 6']['T_perno'] * b['a_perno'], 0)} / "
            f"(0,9 × 2 530 × 30)) = {f(cas['Sismo R = 6']['t_nec'] / 10, 3)} cm = "
            f"{f(cas['Sismo R = 6']['t_nec'], 1)} mm")
      + res(f"t nec = {f(cas['Sismo R = 6']['t_nec'], 1)} mm ≤ t = {f(b['t'] * 10, 0)} mm → D/C = "
            f"{f(cas['Sismo R = 6']['t_nec'] / (b['t'] * 10), 3)}",
            ok=cas["Sismo R = 6"]["t_nec"] <= b["t"] * 10))}

{calc("Paso 10.5", "Corte en los pernos",
      fml("V perno = V col / n pernos      φV n ≈ 0,40·A b·F u   (corte en el vástago roscado)")
      + sus(f"R = 6:  V perno = {f(r6['V_col'] * 1000, 0)} / {b['n_pernos']} = {f(b['V_perno'], 0)} kg<br>"
            f"R = 2:  V perno = {f(r2['V_col'] * 1000, 0)} / {b['n_pernos']} = {f(b['V_perno_R2'], 0)} kg<br>"
            f"φV n ≈ 0,40 × 2,85 × 4 100 = {f(0.4 * 2.85 * 4100, 0)} kg (Φ3/4″)")
      + res(f"D/C = {f(b['V_perno_R2'] / (0.4 * 2.85 * 4100), 3)} (R = 2) → el corte no gobierna", ok=True))}
"""


def ej11():
    return f"""
<h2 id="e11">11 · Zapata aislada — cálculo más reciente</h2>
<p>Esta es la fundación del pórtico: <b>zapata aislada de concreto armado</b> bajo cada columna,
   con pedestal de 40×40 cm, calculada con las hipótesis del capítulo 8 del libro de Fratelli
   (fundaciones directas aisladas) y las verificaciones de COVENIN–MINDUR 1753. Se resuelve
   <b>paso a paso, como un examen</b>: predimensionado, pesos propios, presión de servicio,
   corte, punzonado, flexión, acero, longitud de desarrollo, aplastamiento y las verificaciones
   sísmicas.</p>
{figura('fig-zapata', ('11.1', 'Zapata adoptada: planta del armado, corte, secciones críticas de '
                                'corte y punzonado, y presión sobre el suelo.')) }

<h3>Datos de partida</h3>
{tabla(["Dato", "Símbolo", "Valor", "Origen / por qué"],
       [["Carga axial de servicio en la base", "P serv", f"{f(z['P_serv'] / 1000, 2)} t", "paso 3.5 (sin mayorar)"],
        ["Carga axial mayorada", "P u", f"{f(z['P_u'] / 1000, 2)} t", "paso 3.5"],
        ["Capacidad admisible del suelo (hipótesis)", "σ adm", "1,50 kg/cm²", "proyecto; <i>sin EMS</i>"],
        ["Factor de asentamiento (Tabla 8.1)", "ν", f"{f(z['v'], 2)}", "1,15–1,30 según rigidez"],
        ["Profundidad de desplante", "D f", f"{f(z['D_f'], 2)} m", "≤ NF = 1,50 m (dato municipal)"],
        ["Canto de la zapata", "h", f"{f(z['hz'], 2)} m", "predimensionado, se verifica al corte"],
        ["Recubrimiento libre", "rec", f"{f(z['rec'] * 100, 1)} cm", "fundación en contacto con el suelo"],
        ["Lado del pedestal", "a", f"{f(z['a_col'] * 100, 0)} cm", "columna HEB 300 + 5 cm por lado"],
        ["f′ c del concreto", "f′ c", "210 kg/cm²", "Tabla 0.3"],
        ["f y del acero de refuerzo", "f y", "4 200 kg/cm²", "ADN 420"]],
       caption="Tabla 11.1 — Datos de la zapata.", clases="chica")}

<h3>Predimensionado</h3>
{calc("Paso 11.1", "Área por capacidad de carga",
      fml("A req = ν · P serv / σ adm      — el factor ν de la Tabla 8.1 del libro cubre el aumento "
          "de presión por el peso propio de la fundación y por los momentos")
      + sus(f"A req = {f(z['v'], 2)} × {f(z['P_serv'], 0)} / 15 000 = {f(z['A_req'], 4)} m²<br>"
            f"B req = √A req = {f(z['B_req'], 3)} m")
      + res(f"A req = {f(z['A_req'], 3)} m²   →   B req = {f(z['B_req'], 2)} m"))}

{calc("Paso 11.2", "Ancho mínimo por longitud de desarrollo del acero",
      fml("L d = máx [ 0,06·A b·f y/√f′c ; 0,006·d b·f y ] · ψ      (ψ = 1,4 conservador)",
          )
      + sus(f"Barras Φ1/2″: A b = {f(1.27, 2)} cm², d b = {f(1.27, 2)} cm, √f′c = {f(210 ** .5, 2)}<br>"
            f"0,06 × 1,27 × 4 200 / 14,49 = {f(z['Ld1'] / 1.4, 2)} cm   →   × 1,4 = {f(z['Ld1'], 2)} cm<br>"
            f"0,006 × 1,27 × 4 200 = {f(z['Ld2'] / 1.4, 2)} cm   →   × 1,4 = {f(z['Ld2'], 2)} cm<br>"
            f"L d = {f(z['Ld'], 2)} cm   →   B mín = a + 2·(L d + rec) = 40 + 2 × "
            f"({f(z['Ld'], 2)} + 7,5) = {f(z['B_req_Ld'] * 100, 1)} cm")
      + res(f"B mín = {f(z['B_req_Ld'], 2)} m por longitud de desarrollo", ok=True)
      + nota("Sin el factor ψ = 1,4 la longitud de desarrollo sería 32,0 cm y bastaría B ≥ 1,19 m. "
             "Se usa el valor conservador porque la malla inferior de una zapata de 40 cm de canto "
             "puede quedar en la condición de <i>barra superior</i> si el vaciado se hace de una "
             f"sola colada. Con este criterio gobierna <b>B ≥ {f(z['B_req_Ld'], 2)} m</b>: la zapata "
             "no la gobierna la presión del suelo (0,71 m) sino el anclaje del acero."))}

{calc("Paso 11.3", "Geometría adoptada",
      fml("B = 1,50 m   h = 0,40 m   D f = 1,20 m   rec = 7,5 cm<br>"
          "d = h − rec = 32,5 cm      (canto útil)")
      + res(f"Zapata <b>{f(z['B'], 2)} × {f(z['B'], 2)} × {f(z['hz'], 2)} m</b>, pedestal 40×40 "
            f"de 0,50 a 1,20 m, d = {f(z['d'], 1)} cm", ok=True)
      + nota("El ancho de 1,50 m cubre las tres exigencias: presión del suelo (0,71 m), longitud "
             "de desarrollo (1,45 m) y un módulo constructivo cómodo para el pedestal. La primera "
             "propuesta del proyecto era 1,20 × 1,20 m (46 % de σ adm); se amplió al incluir la "
             "verificación sísmica del par de riostras y el anclaje del acero."))}

<h3>Presión sobre el suelo (estado de servicio)</h3>
{calc("Paso 11.4", "Pesos propios de la fundación y del relleno",
      fml("W zapata = B²·h·γ c      W pedestal = a²·(D f − h)·γ c      "
          "W tierra = (B² − a²)·(D f − h)·γ s")
      + sus(f"W zapata = {f(z['B'], 2)}² × {f(z['hz'], 2)} × 2 400 = {f(z['W_zapata'], 0)} kg<br>"
            f"W pedestal = 0,40² × {f(z['D_f'] - z['hz'], 2)} × 2 400 = {f(z['W_pedestal'], 0)} kg<br>"
            f"W tierra = ({f(z['B'], 2)}² − 0,40²) × {f(z['D_f'] - z['hz'], 2)} × 1 800 = {f(z['W_tierra'], 0)} kg")
      + res(f"W total = {f(z['W_total'], 0)} kg"))}

{calc("Paso 11.5", "Presión de servicio y comparación con la admisible",
      fml("σ s = (P serv + W) / A      A = B²")
      + sus(f"P total = {f(z['P_serv'], 0)} + {f(z['W_total'], 0)} = {f(z['P_tot_serv'], 0)} kg<br>"
            f"σ s = {f(z['P_tot_serv'], 0)} / {f(z['A'], 2)} = {f(z['q_serv'], 0)} kg/m² = "
            f"{f(z['q_serv_kgcm'], 3)} kg/cm²")
      + res(f"σ s = {f(z['q_serv_kgcm'], 3)} kg/cm² ≤ σ adm = 1,50 kg/cm²   →   D/C = "
            f"{f(z['u_serv'], 3)} ({f(z['u_serv'] * 100, 1)} % de la capacidad)", ok=z["u_serv_ok"]))}

<h3>Verificación estructural a rotura (carga mayorada)</h3>
{calc("Paso 11.6", "Presión última de diseño",
      fml("σ u = P u / A      (presión neta que produce los esfuerzos internos)")
      + sus(f"σ u = {f(z['P_u'], 0)} / {f(z['A'], 2)} = {f(z['q_u'], 0)} kg/m²")
      + res(f"σ u = {f(z['q_u'] / 10000, 3)} kg/cm²"))}

{calc("Paso 11.7", "Corte simple (sección crítica a d del borde del pedestal)",
      fml("c = (B − a)/2 − d      V u = σ u · B · c<br>"
          "v u = V u / (φ·B·d)      v c = 0,53·√f′c      (φ = 0,85 — MINDUR 1753, ec. 11-5)")
      + sus(f"c = ({f(z['B'], 2)} − 0,40)/2 × 100 − {f(z['d'], 1)} = {f(z['c_corte'], 1)} cm<br>"
            f"V u = {f(z['q_u'], 0)} × {f(z['B'], 2)} × {f(z['c_corte'] / 100, 3)} = {f(z['V_corte'], 0)} kg<br>"
            f"v u = {f(z['V_corte'], 0)} / (0,85 × 150 × {f(z['d'], 1)}) = {f(z['v_corte'], 3)} kg/cm²<br>"
            f"v c = 0,53 × √210 = {f(z['v_c_corte'], 2)} kg/cm²")
      + res(f"D/C = {f(z['v_corte'] / z['v_c_corte'], 3)}", ok=z["corte_ok"]))}

{calc("Paso 11.8", "Punzonado (corte por penetración, ec. 8.14 y 8.17 del libro)",
      fml("b o = 4·(a + d)      V punz = P u − σ u·(a + d)²<br>"
          "v u = V punz / (φ·b o·d)      v c = 1,06·√f′c      (φ = 0,85)")
      + sus(f"b o = 4 × (40 + {f(z['d'], 1)}) = {f(z['b_o'], 0)} cm<br>"
            f"V punz = {f(z['P_u'], 0)} − {f(z['q_u'], 0)} × ({f((z['a_col'] * 100 + z['d']) / 100, 3)})² = "
            f"{f(z['V_punz'], 0)} kg<br>"
            f"v u = {f(z['V_punz'], 0)} / (0,85 × {f(z['b_o'], 0)} × {f(z['d'], 1)}) = {f(z['v_punz'], 3)} kg/cm²<br>"
            f"v c = 1,06 × √210 = {f(z['v_c_punz'], 2)} kg/cm²")
      + res(f"D/C = {f(z['v_punz'] / z['v_c_punz'], 3)}", ok=z["punz_ok"])
      + nota("El punzonado <b>no gobierna</b> con este canto: la zapata de 40 cm es holgada. "
             "En zapatas delgadas es la verificación que manda, y es la razón por la que el libro "
             "recomienda arrancar de d ≥ √(M u/(μ·f′c·B)) y luego revisar punzonado."))}

{calc("Paso 11.9", "Flexión y acero de refuerzo",
      fml("c = (B − a)/2      M u = σ u·B·c²/2      A s = M u / (φ·f y·0,90·d)      (φ = 0,90)<br>"
          "A s,mín = 0,002 · b · h      (ρ mín = 0,002 — tabla del cap. 8 del libro)")
      + sus(f"c = ({f(z['B'], 2)} − 0,40)/2 = {f(z['c_flex'], 2)} m<br>"
            f"M u = {f(z['q_u'], 0)} × {f(z['B'], 2)} × {f(z['c_flex'], 2)}² / 2 = {f(z['M_u'], 1)} kg·m "
            f"= {f(z['M_u'] * 100, 0)} kg·cm<br>"
            f"A s = {f(z['M_u'] * 100, 0)} / (0,90 × 4 200 × 0,90 × {f(z['d'], 1)}) = {f(z['As_flex'], 2)} cm²<br>"
            f"A s,mín = 0,002 × 100 × {f(z['hz'] * 100, 0)} = {f(z['As_min'], 2)} cm²/m")
      + res(f"Gobierna el <b>acero mínimo</b>: A s = {f(z['As_req'], 2)} cm²/m "
            f"(flexión apenas pide {f(z['As_flex'], 2)} cm²/m)", ok=True))}

{calc("Paso 11.10", "Separación del acero adoptado",
      fml("s = 100 · A barra / A s,nec      y se compara con A s,mín")
      + sus(f"Φ1/2″ → A barra = {f(1.27, 2)} cm²<br>"
            f"s = 100 × 1,27 / {f(z['As_req'], 2)} = {f(100 * 1.27 / z['As_req'], 2)} cm   →   "
            f"se adopta s = {f(z['s_adop'], 0)} cm<br>"
            f"A s,adoptado = 1,27 × 100 / {f(z['s_adop'], 0)} = {f(z['As_adop'], 2)} cm²/m")
      + res(f"<b>Malla inferior Φ1/2″ @ {f(z['s_adop'], 0)} cm en ambos sentidos</b> "
            f"(A s = {f(z['As_adop'], 2)} cm²/m ≥ {f(z['As_req'], 2)} cm²/m)  →  D/C = "
            f"{f(z['As_req'] / z['As_adop'], 3)}", ok=z["acero_ok"]))}

{calc("Paso 11.11", "Longitud de desarrollo disponible",
      fml("L d,disp = (B − a)/2 − rec      y comparación con L d")
      + sus(f"L d,disp = ({f(z['B'], 2)} − 0,40)/2 × 100 − {f(z['rec'] * 100, 1)} = {f(z['Ld_disp'], 1)} cm<br>"
            f"L d = {f(z['Ld'], 2)} cm  (paso 11.2)")
      + res(f"D/C = {f(z['Ld'] / z['Ld_disp'], 3)} → el anclaje entra recto, sin gancho "
            f"(margen de {f(z['Ld_disp'] - z['Ld'], 1)} cm)", ok=z["Ld_ok"]))}

{calc("Paso 11.12", "Aplastamiento pedestal–zapata y columna–placa",
      fml("φP n = 0,7·0,85·f′c·A₁·√(A₂/A₁) ≤ 2·0,7·0,85·f′c·A₁   (φ = 0,70)")
      + sus(f"A₁ = 40 × 40 = 1 600 cm²      A₂ = 150 × 150 = 22 500 cm²<br>"
            f"√(A₂/A₁) = √(22 500/1 600) = {f((22500 / 1600) ** .5, 2)} → se limita a 2,00<br>"
            f"φP n (pedestal) = 0,7 × 0,85 × 210 × 1 600 / 1 000 = {f(z['Pn_col'], 1)} t<br>"
            f"φP n (con el factor 2) = {f(z['Pn_base'], 1)} t")
      + res(f"D/C = {f(z['P_u'] / 1000, 2)} / {f(z['Pn_base'] / 1, 1)} = "
            f"{f(z['P_u'] / (z['Pn_base'] * 1000), 4)}", ok=z["apl_ok"]))}

{calc("Paso 11.13", "Pedestal 40×40 — acero longitudinal y estribos",
      fml("ρ mín = 0,005 para elementos a compresión      A s,nec = 0,005·A g<br>"
          "estribos Φ3/8″ @ 20 cm ≤ 30 cm")
      + sus(f"A s,nec = 0,005 × 40 × 40 = {f(z['ped_As_min'], 2)} cm²<br>"
            f"adoptado: 4 Φ3/4″ = {f(z['ped_As'], 2)} cm²")
      + res(f"D/C = {f(z['ped_As_min'] / z['ped_As'], 3)}", ok=z["ped_ok"]))}

<h3>Verificaciones con sismo y con el par de riostras</h3>
{calc("Paso 11.14", "Presión con sismo (σ adm + 33 %)",
      fml("P sismo = 0,9·(P serv − P pilar) + W fundación + ΔP riostra<br>"
          "σ adm,sismo = 1,33 · σ adm      (el libro admite +33 % con sismo si el área traccionada "
          "no supera 25 % de la base)")
      + sus(f"P sismo = 0,9 × ({f(a['R_serv'], 0)} + {f(a['p_pilar_serv'] * 1000, 0)}) + "
            f"{f(z['W_total'], 0)} + {f(r2['dP_riostra'] * 1000, 0)} = {f(z['P_sismo_total'], 0)} kg<br>"
            f"σ sismo = {f(z['P_sismo_total'], 0)} / {f(z['A'], 2)} = {f(z['q_sismo'], 0)} kg/m²<br>"
            f"σ adm,sismo = 1,33 × 1,50 = {f(z['sigma_adm_sismo'] / 10000, 3)} kg/cm²")
      + res(f"σ sismo = {f(z['q_sismo'] / 10000, 3)} kg/cm² → D/C = {f(z['u_sismo'], 3)} "
            f"({f(z['u_sismo'] * 100, 1)} %)", ok=z["sismo_ok"])
      + nota("Se tomó el ΔP de la hipótesis R = 2 (1,50 t), que es la más desfavorable. Con el "
             "coeficiente 0,9 en la carga vertical se cubre el efecto de vuelco: la excentricidad "
             "resultante es pequeña porque el par lo cierra la riostra entre zapatas opuestas."))}

{calc("Paso 11.15", "Deslizamiento en la base (sin tirante)",
      fml("F roce = μ · P total      μ ≈ 0,5 (concreto–suelo)      FS = F roce / H u ≥ 1,5")
      + sus(f"F roce = 0,5 × {f(z['P_tot_serv'], 0)} = {f(z['F_roce'], 0)} kg<br>"
            f"H u = {f(z['H_sin_tirante'], 0)} kg<br>"
            f"FS = {f(z['F_roce'], 0)} / {f(z['H_sin_tirante'], 0)} = {f(z['FS_desliz'], 2)}")
      + f'<div class="res bad">FS = {f(z["FS_desliz"], 2)} &lt; 1,50 → <b>la zapata deslizaría</b> '
        f'si el empuje del arco llegara a la base <span class="badge b-bad">no cumple</span></div>'
      + nota("<b>Esta verificación es la prueba numérica de que el tirante es obligatorio.</b> "
             "El empuje del arco (14,17 t) es más de dos veces la fuerza de roce disponible "
             "(5,99 t). Alternativa si no se quisiera el tirante: zapata con pedestal muy masivo, "
             "o una viga de riostra calculada para tomar H (A s = 3,75 cm², ver cálculo 12)."))}

{calc("Paso 11.16", "Asentamiento elástico estimado (hipótesis de arcilla blanda)",
      fml("s = q · B · (1 − μ²) · I s / E s      — fórmula elástica de asentamiento inmediato")
      + sus(f"Hipótesis declaradas: E s = {f(z['Es'], 0)} kg/cm², μ = {f(z['nu_suelo'], 2)}, "
            f"I s = 1,12 (zapata rígida)<br>"
            f"s = {f(z['q_serv_kgcm'], 3)} × 150 × (1 − 0,25) × 1,12 / {f(z['Es'], 0)} = "
            f"{f(z['s_elast'], 3)} cm   ≤   s adm = {f(z['s_lim'], 1)} cm")
      + res(f"s = {f(z['s_elast'], 3)} cm (D/C = {f(z['s_elast'] / z['s_lim'], 3)})", ok=z["s_ok"])
      + nota("Es una estimación de orden de magnitud y no sustituye un estudio de suelos con "
             "ensayo de consolidación (cap. 2 del libro). Si el suelo real fuese una arcilla "
             "compresible, el asentamiento por consolidación sería mayor y podría gobernar el "
             "diseño del tamaño de la zapata."))}

{calc("Paso 11.17", "Concreto pobre de limpieza y excavación",
      fml("Se coloca una plantilla de concreto pobre de 10 cm (Fratelli, pág. 247) bajo la zapata "
          "para trabajar limpio y proteger el acero.")
      + sus(f"Excavación total = D f + 0,10 m = {f(z['D_f'], 2)} + 0,10 = {f(z['D_f'] + 0.10, 2)} m<br>"
            f"Volumen de excavación por zapata ≈ {f(z['B'], 2)}² × {f(z['D_f'] + 0.10, 2)} = "
            f"{f(z['B'] ** 2 * (z['D_f'] + 0.10), 2)} m³ ≈ {f(z['B'] ** 2 * (z['D_f'] + 0.10), 1)} m³")
      + res("Concreto pobre 150 kg/cm² de 10 cm de espesor, 10 cm más ancho que la zapata "
            "en todo su perímetro.", ok=True))}
"""
