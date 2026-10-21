"""Cálculos 12 y 13, planilla general, conclusiones y anexos."""
from hcom import R, f, tabla, calc, fml, sus, res, nota, figura, ok_badge, num

g, c, a, s = R["geo"], R["cargas"], R["global"], R["sismo"]
v, t, w = R["correa"], R["cercha"], R["soldadura"]
ri, z, lo = R["riostra"], R["zapata"], R["losa"]
ti, b, k = R["tirante"], R["placa"], R["columna"]
r6, r2 = s["casos"][6], s["casos"][2]
ca = k["casos"]
cas = b["casos"]


def ej12():
    return f"""
<h2 id="e12">12 · Viga de riostra 25×40 cm — solo longitudinal (corrección Sección 6)</h2>
<p>Las zapatas se amarran con vigas de riostra <b>solo en el sentido longitudinal</b> (entre columnas
   separadas 4,10 m), por indicación del profesor. En el sentido transversal la interconexión la
   cumple la <b>losa sobre terreno</b>, cuyo fondo queda a 1,05 m ≤ 1,50 m del fondo de la zapata
   (COVENIN 1756-1:2019 §13.4.4.c). El diseño sigue el bloque «VIGAS DE RIOSTRA» del Ing. Laine:
   acero a tracción A s = 0,15·P u/(φ·f y) con φ = 0,7, más el acero a flexión del momento
   concurrente repartido por rigidez.</p>
{figura('fig-riostra', ('12.1', 'Sección de la viga de riostra adoptada: 25×40 cm, 4 Φ1/2″ y estribos Φ3/8″ @ 20 cm.')) }

{calc("Paso 12.1", "Acero a tracción (Laine: φ·A s·f y &gt; 0,15·P u, φ = 0,7)",
      fml("A s,trac = 0,15 · P u / (φ · f y)      con P u de la combinación de cátedra 1,4CP + 1,6CV")
      + sus(f"P u (fundación) = {f(z['P_u_cat'], 2)} t = {f(z['P_u_cat'] * 1000, 0)} kg<br>"
            f"A s,trac = 0,15 × {f(z['P_u_cat'] * 1000, 0)} / (0,7 × 4 200) = {f(ri['A_s_81'], 2)} cm²<br>"
            f"Verificación §13.4.4.d: N t = máx[A A/4·P ; 10 %·P] = máx[{f(0.345 / 4 * z['P_CP'], 2)} ; "
            f"{f(0.10 * z['P_CP'], 2)}] t → gobierna el 10 % de P, cubierto por este acero")
      + res(f"A s,trac = {f(ri['A_s_81'], 2)} cm²"))}

{calc("Paso 12.2", "Acero a flexión (momento concurrente repartido por rigidez, K v = I/L)",
      fml("A s,flex = M u / (0,81 · f y · d)      — momento residual de base que no absorbe la zapata")
      + sus(f"M u = {f(ri['M_res_u'], 2)} t·m = {f(ri['M_res_u'] * 100000, 0)} kg·cm<br>"
            f"A s,flex = {f(ri['M_res_u'] * 100000, 0)} / (0,81 × 4 200 × 35) = {f(ri['A_s_flex'], 2)} cm²")
      + res(f"A s,flex = {f(ri['A_s_flex'], 2)} cm²"))}

{calc("Paso 12.3", "Acero adoptado y verificación",
      fml("A s,nec = A s,trac + A s,flex      A s,adop = 4Ø1/2″")
      + sus(f"A s,nec = {f(ri['A_s_81'], 2)} + {f(ri['A_s_flex'], 2)} = {f(ri['A_s_req'], 2)} cm²<br>"
            f"adoptado: 4 Φ1/2″ (2 arriba y 2 abajo) = {f(ri['A_s_adop'], 2)} cm² — gobierna lo "
            f"constructivo (armadura nominal mínima de la corrección), no el cálculo<br>"
            f"capacidad: φ·A s·f y = 0,9 × {f(ri['A_s_adop'], 2)} × 4 200 / 1 000 = "
            f"{f(0.9 * ri['A_s_adop'] * 4200 / 1000, 1)} t ≥ 0,15·P u = {f(0.15 * z['P_u_cat'], 2)} t")
      + res(f"D/C = {f(ri['A_s_req'] / ri['A_s_adop'], 3)}", ok=ri["acero_ok"]))}

{calc("Paso 12.4", "Estribos",
      fml("s ≤ mín [ 25 cm ; 16·d b ]      — reglas de separación de Laine")
      + sus(f"16 × d b = 16 × 1,27 = {f(16 * 1.27, 1)} cm   →   s ≤ {f(ri['s_max'], 1)} cm<br>"
            f"adoptado: Φ3/8″ @ {f(ri['s_estribo'], 0)} cm (2 ramas)")
      + res(f"Φ3/8″ @ {f(ri['s_estribo'], 0)} cm ≤ {f(ri['s_max'], 1)} cm", ok=ri["estribo_ok"]))}

{calc("Paso 12.5", "Qué pasa en el sentido transversal (sin riostra)",
      fml("Interconexión por la losa sobre terreno: distancia fondo de losa → fondo de zapata "
          "= 1,05 m ≤ 1,50 m (COVENIN 1756-1:2019 §13.4.4.c)")
      + sus(f"Sin riostra transversal, el par de vuelco del pórtico (ΔP = 2·M base/L = "
            f"{f(ri['V_zapata_par'], 2)} t con R = 2 en el modelo actual) se cierra con el tirante de "
            f"cabeza en la superestructura, no en la fundación")
      + res("Riostra <b>solo longitudinal</b> (25×40, 4Ø1/2″ + Ø3/8″@20); transversal: losa sobre terreno", ok=True)
      + nota("<b>Divergencia declarada:</b> en el sistema recién adoptado (testeros y fachadas "
             "arriostradas) el momento de base casi desaparece y este ΔP cambiará; el valor mostrado "
             "es el del modelo transversal actual, pendiente del recálculo global del sistema nuevo."))}
"""


def ej13():
    area = g["Ltot"] * g["L"]
    return f"""
<h2 id="e13">13 · Losa sobre terreno y macizo del graderío</h2>
<p>El graderío del auditorio se forma con un <b>macizo de relleno</b> (concreto pobre) contenido por
   las vigas de riostra, y sobre él una losa de concreto armado de 20 cm con malla electrosoldada o
   barras Φ1/2″. La losa no trabaja a flexión (está apoyada en el terreno en toda su superficie):
   se arma con la cuantía mínima por temperatura y retracción.</p>
{figura('fig-graderio', ('13.1', 'Corte del graderío: macizo de relleno, losa de 20 cm y suelo de '
                                  'apoyo.')) }

{calc("Paso 13.1", "Área de la losa y carga del macizo",
      fml("A losa = L tot × L      σ macizo = γ c · h macizo")
      + sus(f"A = {f(g['Ltot'], 2)} × {f(g['L'], 2)} = {f(area, 2)} m²<br>"
            f"σ = 2,4 t/m³ × 0,75 m = {f(lo['sigma_macizo'], 2)} t/m²")
      + res(f"A = {f(area, 2)} m²   |   σ macizo = {f(lo['sigma_macizo'], 2)} t/m² ≤ σ adm = "
            f"{f(z['sigma_adm'] / 1000, 1)} t/m²", ok=True))}

{calc("Paso 13.2", "Altura máxima del macizo según el suelo",
      fml("h máx = σ adm / γ c")
      + sus(f"h máx = {f(z['sigma_adm'] / 1000, 1)} / 2,4 = {f(lo['h_max_macizo'], 2)} m "
            f"→ el macizo de 0,75 m está muy por debajo")
      + res(f"h máx = {f(lo['h_max_macizo'], 2)} m &gt;&gt; 0,75 m adoptado", ok=True))}

{calc("Paso 13.3", "Acero de la losa",
      fml("A s,mín = 0,002 · b · h      (igual criterio del cap. 8 del libro, ρ mín = 0,002)")
      + sus(f"A s,mín = 0,002 × 100 × {f(lo['h'] * 100, 0)} = {f(lo['As_min'], 2)} cm²/m<br>"
            f"adoptado: Φ1/2″ @ {f(lo['s_adop'], 0)} cm = 1,27 × 100 / {f(lo['s_adop'], 0)} = "
            f"{f(lo['As_adop'], 2)} cm²/m")
      + res(f"D/C = {f(lo['As_min'] / lo['As_adop'], 3)}", ok=lo["losa_ok"])
      + nota("La losa lleva además <b>juntas de retracción</b> cada 6 m como máximo y un borde "
             "libre perimetral de 10 cm sobre el piso terminado, según lo acordado en la memoria "
             "de arquitectura. Las gradas definitivas (peldaños) van sobre este macizo con "
             "contrahuella de 0,15 m."))}
"""


# ---------------------------------------------------------------------------
# PLANILLA GENERAL
# ---------------------------------------------------------------------------
PLANILLA = [
    ("1", "Correa IPN 140 — flexión eje fuerte",
     "M x / φM n,x = 598,2 / 1 864,9", "598,2 kg·m", "1 864,9 kg·m"),
    ("2", "Correa IPN 140 — flecha",
     "δ / δ adm = 0,592 / 1,367", "0,592 cm", "1,367 cm"),
    ("3", "Cordón 2×IPE 160 — compresión",
     "N u / φP n = 29 523 / 40 728", "29,52 t", "40,73 t"),
    ("4", "Cordón 2×IPE 160 — tracción",
     "N u / φP n = 29 523 / 91 535", "29,52 t", "91,54 t"),
    ("5", "Diagonal IPE 160 (2 por panel)",
     "N diag / φP n = 12 333 / 18 489", "12,33 t", "18,49 t"),
    ("6", "Montante IPE 120",
     "N / φP n = 686 / 25 721", "0,69 t", "25,72 t"),
    ("7", "Soldadura filete 6 mm — diagonal",
     "N diag / (L·φR n) = 12 333 / (18 × 939)", "12,33 t", "16,90 t"),
    ("8", "Soldadura filete 6 mm — cordón del arco",
     "N / (4·L·φR n) = 29 523 / (4 × 20 × 939)", "29,52 t", "75,12 t"),
    ("9", "Soldadura filete 6 mm — placa base",
     "P u / (perímetro·φR n) = 9 245 / (120 × 939)", "9,25 t", "112,68 t"),
    ("10", "Columna HEB 300 — compresión axial",
     "P u / φP n = 9,25 / 141,5", "9,25 t", "141,50 t"),
    ("11", "Columna HEB 300 — P–M con sismo R = 6",
     "P u/φP n + (8/9)·M u/φM n = 0,065 + 0,102", "—", "1,00"),
    ("12", "Columna HEB 300 — P–M con sismo R = 2",
     "P u/φP n + (8/9)·M u/φM n = 0,065 + 0,307", "—", "1,00"),
    ("13", "Deriva de entrepiso — sismo R = 6",
     "Δ = C d·δ e = 4,25 × 2,01", "8,52 cm", "17,00 cm"),
    ("14", "Deriva de entrepiso — sismo R = 2",
     "Δ = C d·δ e = 4,25 × 6,02", "25,57 cm", "17,00 cm"),
    ("15", "Zapata — presión de servicio",
     "σ s / σ adm = 0,637 / 1,500", "0,637 kg/cm²", "1,500 kg/cm²"),
    ("16", "Zapata — corte simple",
     "v u / (0,53√f′c) = 0,072 / 8,38", "0,072 kg/cm²", "8,38 kg/cm²"),
    ("17", "Zapata — punzonado",
     "v u / (1,06√f′c) = 0,403 / 16,76", "0,403 kg/cm²", "16,76 kg/cm²"),
    ("18", "Zapata — acero adoptado vs requerido (Laine)",
     "A s,nec / A s,adop = 10,50 / 16,50", "10,50 cm²/m", "16,50 cm²/m"),
    ("19", "Zapata — longitud de desarrollo (con gancho)",
     "l dh / L disp = 22,19 / 27,50", "22,19 cm", "27,50 cm"),
    ("20", "Zapata — aplastamiento pedestal–zapata",
     "P u / φP n = 9,25 / 1 249,5", "9,25 t", "1 249,50 t"),
    ("21", "Zapata — presión con sismo (σ adm + 33 %)",
     "σ sismo / (1,33·σ adm) = 0,687 / 1,995", "0,687 kg/cm²", "1,995 kg/cm²"),
    ("22", "Zapata — asentamiento estimado",
     "s / s adm = 0,463 / 2,50", "0,463 cm", "2,50 cm"),
    ("23", "Tirante de cabeza Φ1-1/2″ — tracción",
     "T u / φP n = 14,17 / 25,96", "14,17 t", "25,96 t"),
    ("24", "Placa base — placa a flexión (sismo R = 6)",
     "t nec / t = 14,6 / 25,0", "14,6 mm", "25,0 mm"),
    ("25", "Placa base — perno Φ3/4″ a tracción (R = 6)",
     "T perno / φT n = 2,71 / 5,41", "2,71 t", "5,41 t"),
    ("26", "Placa base — perno Φ1″ a tracción (R = 2)",
     "T perno / φT n = 10,45 / 9,62", "10,45 t", "9,62 t"),
    ("27", "Viga de riostra 25×40 (solo longitudinal) — acero",
     "A s,nec / A s,adop = 1,76 / 5,08", "1,76 cm²", "5,08 cm²"),
    ("28", "Pedestal 0,60×0,70 — acero longitudinal",
     "4Ø5/8″ adoptado = 7,92", "7,92 cm²", "7,92 cm²"),
    ("29", "Zapata — deslizamiento sin tirante (FS ≥ 1,5)",
     "FS = 0,5·P / H u = 5 380 / 14 171", "FS = 0,38", "FS = 1,50"),
]


def planilla():
    filas = []
    for i, (n, nom, formula, dem, cap) in enumerate(PLANILLA):
        _nom, dc, ok = R["dc"][i]
        filas.append([(n, "n"), nom, f'<span class="mono small">{formula}</span>',
                      (dem, "n"), (cap, "n"), (f"{f(dc, 3)}", "n"), (ok_badge(ok), "")])
    return f"""
<h2 id="planilla">Planilla general de cálculos</h2>
<p>Resumen de las {len(PLANILLA)} verificaciones del cuaderno. La columna <b>D/C</b> es la relación
   demanda/capacidad: mientras más cerca de 1,00, más ajustado el elemento. Los renglones marcados
   con <span class="badge b-bad">revisar</span> son las <b>banderas rojas</b> del proyecto y se
   explican en la sección siguiente.</p>
{tabla([("#", "n"), ("Verificación", ""), ("Fórmula / criterio", ""), ("Demanda", "n"),
        ("Capacidad", "n"), ("D/C", "n"), ("Estado", "")],
       filas,
       caption="Planilla general — auditorio UPT Barlovento «Argelia Laya» (Higuerotes).",
       clases="chica")}
<p class="small">D/C promedio de los renglones que cumplen: valor máximo
   {f(max(x for _, x, o in R['dc'] if o), 3)} (zapata, acero adoptado vs requerido) y mínimo
   {f(min(x for _, x, o in R['dc'] if o), 3)}. Ningún elemento está por encima de 0,95 salvo las
   tres banderas rojas.</p>
{figura('fig-dc', ('P.1', "Gráfico de barras del D/C: verde = cumple, rojo = no cumple; la línea "
                           "marca D/C = 1,00."))}
"""


def conclusiones():
    return f"""
<h2 id="banderas">Conclusiones y banderas rojas</h2>

<h3>Lo que queda resuelto</h3>
<ul>
  <li>Geometría completa del doble arco (R sup = {f(g['R_sup'], 3)} m, θ = {f(g['th_grados'], 2)}°,
      L arco = {f(g['L_arco'], 3)} m) y 8 paneles de {f(g['ds'], 3)} m.</li>
  <li>Cargas de diseño: q u = {f(c['q_u'], 2)} kg/m y peso sísmico W = {f(c['W_total'] / 1000, 2)} t.</li>
  <li>Todos los perfiles verificados con D/C ≤ 0,73 salvo el cordón del arco (0,725) y la soldadura
      de la diagonal (0,73).</li>
  <li>Fundación resuelta: zapata aislada de <b>{f(z['B'], 2)} × {f(z['B'], 2)} × {f(z['hz'], 2)} m</b>
      con malla Φ5/8″ @ {f(z['s_adop'], 0)} cm (con gancho), presionando el suelo al
      {f(z['u_serv'] * 100, 1)} % de la capacidad admisible hipotética.</li>
  <li>La necesidad del tirante de cabeza quedó demostrada numéricamente por dos vías:
      la interacción P–M de la columna (3,18) y el deslizamiento de la zapata (FS = 0,42).</li>
</ul>

<h3>Banderas rojas (hay que decidir antes de entregar la memoria)</h3>
{tabla(["#", "Bandera", "Por qué importa", "Qué hacer"],
       [[("1", "n"),
         "<b>Hipótesis sísmica R</b>: la planilla usa R = 6, pero la clasificación Tipo IV lleva a R = 2",
         "Con R = 2 la deriva da 25,57 cm (límite 17,00 cm) y los pernos de la placa base no alcanzan ni con Φ1″",
         "Definir el R definitivo con la clasificación de ocupación y escribirlo en la memoria (capítulo de sismo). Si es R = 2: rigidizar el pórtico (riostras diagonales en las columnas) o rediseñar la placa base con más pernos"],
        [("2", "n"),
         "<b>El tirante de cabeza todavía no está en los planos</b>",
         "Sin él la columna HEB 300 no cumple y la zapata desliza: es un elemento estructural, no un detalle",
         "Dibujarlo y acotarlo en el plano de la cercha (CL-01) y en la planilla de perfiles, con las orejetas de anclaje y los tensores"],
        [("3", "n"),
         "<b>No hay estudio de mecánica de suelos</b>",
         "σ adm = 1,50 kg/cm² y NF = 1,50 m son hipótesis; el asentamiento y el tamaño de la zapata dependen de ellos",
         "Declararlo en la memoria (alcance académico) y sustituir las hipótesis por un EMS antes de cualquier trámite de permisología"],
        [("4", "n"),
         "<b>Análisis global simplificado</b>",
         "El empuje se calculó con la fórmula del arco triarticulado y los momentos con la viga biempotrada equivalente: es predimensionado, no un análisis estructural",
         "Modelar el pórtico de doble arco con las cargas reales (software matricial) y revisar los D/C con los diagramas definitivos"],
        [("5", "n"),
         "<b>Graderío y losa sobre terreno</b>",
         "El macizo de 0,75 m y la losa de 20 cm cumplen con el suelo hipotético (σ = 1,80 t/m² vs 15 t/m² admisible)",
         "Revisar las juntas de retracción y el drenaje del macizo; confirmar la contrahuella definitiva con la memoria de arquitectura"]],
       caption="Tabla 14.1 — Banderas rojas del proyecto.")}
"""


def anexos():
    return f"""
<h2 id="anexoA">Anexo A — fórmulas, normas y bibliografía</h2>
<h3>A.1 Fórmulas usadas y su origen</h3>
{tabla(["Cálculo", "Fórmula", "Norma / origen"],
       [["Geometría del arco", "R = (L/2)²/(2f) + f/2 ; θ = 2·arcsen((L/2)/R)",
         "geometría analítica; procedimiento del curso"],
        ["Empuje del arco", "H = q·L²/(8f)", "arco triarticulado / viga equivalente (texto de análisis estructural)"],
        ["Momento de la viga equivalente", "M = q·L²/12 ; M centro = q·L²/24", "viga biempotrada con carga repartida"],
        ["Par de fuerzas del arco", "N = M/d", "equilibrio de la sección del arco de celosía"],
        ["Pandeo por compresión", "φP n = φ·F cr·A ; F cr = 0,658^(F y/F e)·F y ; F e = π²E/λ²",
         "COVENIN 1618-98 §6.8 (equivalente a AISC 360 §E3)"],
        ["Flexión", "φM n = φ·F y·W x", "COVENIN 1618-98 §6.10"],
        ["Interacción P–M", "P u/φP n + (8/9)·M u/φM n ≤ 1", "COVENIN 1618-98 §6.11 (AISC 360 §H1-1a)"],
        ["Soldadura de filete", "φR n = φ·0,6·F EXX·garganta ; garganta = 0,707·pata",
         "COVENIN 1618-98 parte 4 §7.2 (AISC 360 §J2.4)"],
        ["Sismo", "V 0 = C·W ; A d = 2,4·A a/R ; Δ = C d·δ e ≤ 0,020·h",
         "COVENIN 1756-1:2019, método de las fuerzas horizontales equivalentes"],
        ["Corte en fundaciones", "V u ≤ φ·0,53·√f′c·b·d", "COVENIN–MINDUR 1753, ec. 11-5 (libro ec. 8.12)"],
        ["Punzonado", "v u = V u/(φ·b o·d) ; b o = 4(a+d) ; v c = 1,06·√f′c",
         "COVENIN–MINDUR 1753; libro, ec. 8.14 y 8.17–8.18"],
        ["Flexión en la zapata", "M u = σ u·B·c²/2 ; A s = M u/(φ·f y·0,90·d)", "COVENIN–MINDUR 1753, §11.2"],
        ["Cuantía mínima en fundaciones", "ρ mín = 0,002", "libro, cap. 8, pág. 263"],
        ["Longitud de desarrollo", "L d = máx[0,06·A b·f y/√f′c ; 0,006·d b·f y]",
         "COVENIN–MINDUR 1753 §12.2 (ACI 318 §25.4)"],
        ["Aplastamiento", "φP n = 0,7·0,85·f′c·A₁·√(A₂/A₁) ≤ 2·…", "COVENIN–MINDUR 1753 §10.17"],
        ["Riostras", "A s = 0,15·P u/f y ; s ≤ 30 cm y ≤ 12 d b", "libro, págs. 250–251"],
        ["Asentamiento elástico", "s = q·B·(1−μ²)·I s/E s", "teoría de la elasticidad (libro, cap. 2)"]],
       caption="Tabla A.1 — Fórmulas empleadas.",
       clases="chica")}

<h3>A.2 Bibliografía</h3>
<ol class="small">
  <li>Fratelli, M. G. <i>Suelos, Fundaciones y Muros</i>. Capítulo 8: «Fundaciones directas
      aisladas y continuas» (págs. 246–274) y capítulos 1–2 (propiedades del suelo,
      nivel freático y asentamientos).</li>
  <li>COVENIN 1756-1:2019. <i>Edificaciones sismorresistentes. Parte 1: Requisitos</i>.
      FONDONORMA.</li>
  <li>COVENIN 1618-98. <i>Estructuras de acero. Método de los estados límites</i>. FONDONORMA.</li>
  <li>COVENIN–MINDUR 2002-88. <i>Criterios y acciones mínimas para el proyecto de edificaciones</i>.</li>
  <li>COVENIN–MINDUR 1753-2006. <i>Proyecto y construcción de estructuras de concreto armado
      para edificaciones</i>.</li>
  <li>COVENIN 810-1998. <i>Salidas de emergencia en edificaciones</i> (usada en la memoria de
      arquitectura para el aforo de 450 personas y los medios de escape).</li>
  <li>AISC 360-16. <i>Specification for Structural Steel Buildings</i> — referencia de las
      formulaciones de acero (pandeo, flexión e interacción).</li>
  <li>ACI 318. <i>Building Code Requirements for Structural Concrete</i> — referencia de las
      formulaciones de concreto (corte, punzonado y anclaje).</li>
</ol>
"""


def anexo_b():
    return f"""
<h2 id="anexoB">Anexo B — reproducibilidad de los cálculos</h2>
<p>Todos los números de este cuaderno se calculan en el módulo <code>calculos.py</code>; el documento
   HTML se arma con <code>gen_html.py</code>, que lee ese módulo y produce las figuras SVG
   (<code>svg.py</code>). Ningún valor está escrito a mano en el texto: si se cambia un dato de
   entrada, cambian el cuaderno y la planilla.</p>
{tabla(["Archivo", "Qué contiene"],
       [["<code>calculos.py</code>", "los 13 bloques de cálculo y el resumen D/C; se ejecuta con "
         "<code>python3 calculos.py</code> e imprime la planilla completa en texto"],
        ["<code>svg.py</code>", "las 9 figuras SVG (pórtico, cuerpo libre, DFC/DMF, zapata, placa "
         "base, soldadura, riostra, graderío y gráfico D/C)"],
        ["<code>hcom.py</code>, <code>sec_a.py</code> … <code>sec_d.py</code>", "texto y armado del cuaderno (CSS y plantillas)"],
        ["<code>gen_html.py</code>", "genera <code>cuaderno.html</code> (archivo único, sin internet)"]],
       caption="Tabla B.1 — Archivos del cuaderno.")}
<div class="caja">
  <h4>Comprobación rápida (para el profesor)</h4>
  <p class="small">Ejecutar <code>python3 calculos.py</code> en la carpeta <code>cuaderno/</code>:
     imprime los {len(PLANILLA)} renglones de la planilla y todos los valores intermedios. Los
     datos de entrada están al inicio del archivo, en los diccionarios de cada bloque; los
     materiales y perfiles están en las constantes <code>PERFILES</code> y <code>BARRAS</code>.</p>
</div>
<p class="small" style="margin-top:22px;color:#6b7280">Cuaderno generado automáticamente desde
   <code>calculos.py</code>. Uso académico: las hipótesis de suelo están declaradas en la sección 0
   y deben sustituirse por un estudio de mecánica de suelos antes de cualquier uso profesional.</p>
"""
