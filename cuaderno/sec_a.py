"""Portada, datos de partida y cálculos 1 a 3 del cuaderno."""
import calculos
from hcom import (R, f, tabla, calc, fml, sus, res, nota, figura, ok_badge, num)

g, c, a, s = R["geo"], R["cargas"], R["global"], R["sismo"]
v, t, w = R["correa"], R["cercha"], R["soldadura"]
k, b, ti, z, ri, lo = R["columna"], R["placa"], R["tirante"], R["zapata"], R["riostra"], R["losa"]


def portada():
    filas = [
        ["Luz libre del pórtico", "L", f"{f(g['L'], 2)} m"],
        ["Flecha del arco (clave)", "f", f"{f(g['f'], 2)} m"],
        ["Canto del doble arco", "d", f"{f(g['d'], 2)} m"],
        ["Altura de arranque del arco", "h", f"{f(g['h'], 2)} m"],
        ["Separación entre pórticos", "S", f"{f(g['S'], 2)} m"],
        ["Número de pórticos", "n", f"{g['nport']}"],
        ["Longitud total de la edificación", "L tot", f"{f(g['Ltot'], 2)} m"],
    ]
    return f"""
<div class="portada">
  <h1>Cuaderno de ejercicios — Cálculos estructurales del Auditorio</h1>
  <p class="sub">Universidad Politécnica Territorial de Barlovento «Argelia Laya» · Higuerote,
     estado Miranda · estructuras metálicas y fundaciones</p>
  <p class="sub">Doble arco de celosía con columnas HEB 300, correas IPN 140, cercha de alma
     compuesta y zapatas aisladas de concreto armado.</p>
  <div class="kpis">
    <div class="kpi"><b>{f(g['L'], 2)} m</b><span>luz libre L</span></div>
    <div class="kpi"><b>{f(g['f'], 2)} m</b><span>flecha del arco f</span></div>
    <div class="kpi"><b>{f(c['q_u'], 2)} kg/m</b><span>carga mayorada q u</span></div>
    <div class="kpi"><b>{f(a['H_u'] / 1000, 2)} t</b><span>empuje del arco H u</span></div>
    <div class="kpi"><b>{f(z['B'], 2)}×{f(z['B'], 2)}×{f(z['hz'], 2)} m</b><span>zapata adoptada</span></div>
    <div class="kpi"><b>{f(a['P_serv_zapata'], 2)} t</b><span>carga de servicio por zapata</span></div>
  </div>
  <p class="meta">Documento generado a partir del módulo <code>calculos.py</code>; todas las cifras
     de este cuaderno salen de ese archivo, no hay números escritos a mano en el texto.</p>
</div>

<div class="caja aviso">
  <h4>Cómo debe leerse este cuaderno (hipótesis y alcance)</h4>
  <ul>
    <li><b>Es un trabajo académico.</b> No existe estudio de mecánica de suelos reglamentario;
        las propiedades del suelo son <i>hipótesis declaradas</i> y el documento no es válido para
        permisología hasta que se sustituyan por un EMS real
        (Fratelli, <i>Suelos, Fundaciones y Muros</i>, cap. 1 y cap. 8).</li>
    <li><b>Hipótesis geotécnicas:</b> σ adm = 1,50 kg/cm² para fundaciones aisladas; nivel freático
        NF = 1,50 m (dato municipal); suelo húmedo γ = 1 800 kg/m³; masa equivalente
        γ = 2 100 kg/m³ (Tabla 8.1 del libro, valor ν = 1,15 para el predimensionado).</li>
    <li><b>Acciones excluidas por decisión docente:</b> la acción del viento (COVENIN-MINDUR
        2003-86) y las fundaciones profundas con pilotes. Se resuelve con <b>fundaciones aisladas</b>.</li>
    <li><b>Métodos:</b> se indica de dónde sale cada fórmula y por qué se usa. Los métodos de
        análisis matricial y de sismo se estudiaron de forma autónoma, además de lo visto en clase.</li>
    <li><b>Trazabilidad:</b> el cálculo se rehace por completo en el módulo <code>calculos.py</code>
        (anexo B). La planilla final resume {{filas}} renglones con su relación demanda/capacidad.</li>
  </ul>
</div>

<h2 id="indice">Índice</h2>
<ol class="toc">
  <li><a href="#d0">Datos de partida, materiales y normas</a></li>
  <li><a href="#e1">Geometría del doble arco</a></li>
  <li><a href="#e2">Cargas y combinaciones</a></li>
  <li><a href="#e3">Análisis global del pórtico (empuje y par de fuerzas)</a></li>
  <li><a href="#e4">Acción sísmica (COVENIN 1756-1:2019)</a></li>
  <li><a href="#e5">Correas de cubierta IPN 140</a></li>
  <li><a href="#e6">Cercha de doble arco (cordón, diagonales y montantes)</a></li>
  <li><a href="#e7">Soldadura de filete del nudo de apoyo</a></li>
  <li><a href="#e8">Columna HEB 300</a></li>
  <li><a href="#e9">Tirante de cabeza entre columnas</a></li>
  <li><a href="#e10">Placa base y pernos de anclaje</a></li>
  <li><a href="#e11">Zapata aislada (cálculo más reciente)</a></li>
  <li><a href="#e12">Viga de riostra 40×40</a></li>
  <li><a href="#e13">Losa sobre terreno y macizo del graderío</a></li>
  <li><a href="#planilla">Planilla general y gráfico D/C</a></li>
  <li><a href="#banderas">Conclusiones y banderas rojas</a></li>
  <li><a href="#anexoA">Anexo A — fórmulas, normas y bibliografía</a></li>
  <li><a href="#anexoB">Anexo B — reproducibilidad de los cálculos</a></li>
</ol>
""".replace("{filas}", str(len(R["dc"])))


def sec_datos():
    perfiles = tabla(
        [("Perfil", "n"), ("A (cm²)", "n"), ("I x (cm⁴)", "n"), ("W x (cm³)", "n"),
         ("i x (cm)", "n"), ("i y (cm)", "n"), ("g (kg/m)", "n"), ("h (cm)", "n")],
        [[p, (f"{d['A']:g}", "n"), (f"{d['Ix']:,}".replace(",", "."), "n"),
          (f"{d['Wx']:g}", "n"), (f"{d['ix']:g}", "n"), (f"{d['iy']:g}", "n"),
          (f"{d['g']:g}", "n"), (f"{d['h']:g}", "n")]
         for p, d in calculos.PERFILES.items()],
        caption="Tabla 0.1 — Perfiles de acero usados (catálogo SIDOR/DIN).")

    geo = tabla(
        ["Parámetro", "Símbolo", "Valor"],
        [[x, (sy, "n"), (vv, "n")] for x, sy, vv in
         [("Luz libre entre apoyos", "L", f"{f(g['L'], 2)} m"),
          ("Flecha del arco (extradós)", "f", f"{f(g['f'], 2)} m"),
          ("Espesor (canto) del arco", "d", f"{f(g['d'], 2)} m"),
          ("Altura de arranque", "h", f"{f(g['h'], 2)} m"),
          ("Radio del extradós", "R sup", f"{f(g['R_sup'], 3)} m"),
          ("Radio del intradós", "R inf", f"{f(g['R_inf'], 3)} m"),
          ("Ángulo total del arco", "θ", f"{f(g['th_grados'], 3)}°"),
          ("Longitud del arco (extradós)", "L arco", f"{f(g['L_arco'], 3)} m"),
          ("Separación entre pórticos", "S", f"{f(g['S'], 2)} m"),
          ("Altura total en la clave", "h + f", f"{f(g['h_clave'], 2)} m")]],
        caption="Tabla 0.2 — Geometría de partida (levantamiento del proyecto).")

    return f"""
<h2 id="d0">0 · Datos de partida, materiales y normas</h2>
<p>Antes de calcular nada se fijan los datos con los que se va a trabajar en todo el cuaderno.
   Cada valor lleva su origen: levantamiento del proyecto, decisión del profesor, hipótesis
   declarada o tabla de norma. Los números en <i>cursiva</i> son hipótesis que deben validarse.</p>

<h3>0.1 Materiales</h3>
{tabla(["Material / parámetro", "Símbolo", "Valor", "Origen"],
       [["Concreto de la fundación", "f′ c", "210 kg/cm²", "grado usual para fundaciones (COVENIN-MINDUR 1753)"],
        ["Peso específico del concreto armado", "γ c", "2 400 kg/m³", "valor práctico del libro, cap. 8"],
        ["Acero de refuerzo", "f y", "4 200 kg/cm²", "ADN 420 (grado 60), barras corrugadas"],
        ["Acero estructural de perfiles", "F y", "2 530 kg/cm²", "A52 SIDOR, equivalente al A36"],
        ["Resistencia última del acero", "F u", "4 100 kg/cm²", "mismo acero"],
        ["Módulo de elasticidad del acero", "E", "2,1×10⁶ kg/cm²", "COVENIN 1618"],
        ["Electrodo de soldadura", "F EXX", "4 920 kg/cm²", "E70XX"],
        ["Peso específico del suelo (hipótesis)", "γ s", "1 800 kg/m³", "suelo húmedo, hipótesis declarada"],
        ["Masa equivalente base−relleno", "γ", "2 100 kg/m³", "Tabla 8.1 del libro (Fratelli)"],
        ["Capacidad admisible del suelo (hipótesis)", "σ adm", "1,50 kg/cm²", "dato del proyecto municipal; <i>sin EMS</i>"],
        ["Nivel freático", "NF", "1,50 m", "dato municipal"],
        ["Factor de asentamiento", "ν", "1,15", "Tabla 8.1 del libro (1,15–1,30)"]],
       caption="Tabla 0.3 — Materiales, suelos (hipótesis) y coeficientes.",
       clases="chica")}

<h3>0.2 Perfiles</h3>
{perfiles}
{geo}

<h3>0.3 Acciones sobre la cubierta</h3>
{tabla(["Acción", "Símbolo", "Valor", "Comentario"],
       [["Lámina de techo (acanalada + fijaciones)", "D₁", "5,5 kg/m²", "carga muerta"],
        ["Correas IPN 140", "D₂", "7,5 kg/m²", "repartida por m² de cubierta"],
        ["Cielo raso / aislante", "D₃", "10,0 kg/m²", "carga muerta"],
        ["Carga variable de techo (mantenimiento)", "L", "100 kg/m²", "COVENIN 2002-88, cubierta no accesible"],
        ["Cargas colgadas (acústica, iluminación, ductos)", "—", "15,0 kg/m²", "carga muerta adicional"],
        ["Peso propio de la cercha (lineal por pórtico)", "PP est", "35,0 kg/m", "estimado por el área tributaria; se contrasta con el peso real de los perfiles (≈ 73 kg/m)"],
        ["Peso propio de la pasarela de servicio", "PP pas", "25,0 kg/m", "carga lineal por pórtico"]],
       caption="Tabla 0.4 — Acciones consideradas sobre un pórtico tipo.")}

<h3>0.4 Normas de referencia</h3>
<ul class="small">
  <li><b>COVENIN 1756-1:2019</b> — <i>Edificaciones sismorresistentes</i>. Se usa para el
      espectro, el factor de reducción R y el control de derivas (método de las fuerzas
      horizontales equivalentes: V = C·W).</li>
  <li><b>COVENIN 1618-98</b> — <i>Estructuras de acero. Método de los estados límites</i>.
      De aquí salen φP n (pandeo por compresión, §6.8), φM n (flexión, §6.10) y la resistencia
      de las soldaduras de filete φR n = 0,75·0,6·F EXX·garganta (parte 4, §7).</li>
  <li><b>COVENIN–MINDUR 2002-88</b> — <i>Criterios y acciones mínimas para el proyecto de
      edificaciones</i>: cargas muertas y variables, y las combinaciones de acciones.</li>
  <li><b>COVENIN–MINDUR 1753-2006</b> — proyecto y construcción de estructuras de concreto armado:
      corte simple, punzonado, flexión, longitud de desarrollo y aplastamiento.</li>
  <li><b>Fratelli, M. G. — <i>Suelos, Fundaciones y Muros</i>, cap. 8</b>
      (Fundaciones directas aisladas y continuas, págs. 246–274): predimensionado de zapatas,
      verificación al punzonado, tabla de ρ mín = 0,002, riostras y concreto pobre de limpieza.</li>
  <li><b>COVENIN 810-1998</b> — <i>Salidas de emergencia en edificaciones</i>: se usó en la
      memoria de arquitectura para el aforo y los medios de escape.</li>
</ul>
"""


def ej1():
    nd = g["nudos"]
    filas = [[f"J{i}", (f"{f(d['phi'], 3)}°", "n"), (f"{f(d['x'], 3)} m", "n"),
              (f"{f(d['ye'], 3)} m", "n"), (f"{f(d['yi'], 3)} m", "n")] for i, d in enumerate(nd)]
    return f"""
<h2 id="e1">1 · Geometría del doble arco</h2>
<p>El pórtico tiene dos cordones (doble arco de celosía) unidos por diagonales en cruz, con 8 paneles
   iguales. El extradós pasa por los dos arranques y por la clave; con esos tres puntos la geometría
   queda determinada por el teorema de la circunferencia que pasa por tres puntos.</p>
{figura('fig-portico', ('1.1', 'Geometría del pórtico tipo: arco de celosía, columnas HEB 300 y carga mayorada.'))}

{calc("Paso 1.1", "Radio del extradós",
      fml("R sup = (L/2)² / (2·f) + f/2   — circunferencia por los tres puntos del arco")
      + sus(f"R sup = (17,60/2)² / (2 × 2,50) + 2,50/2 = 77,44/5,00 + 1,25 = 15,488 + 1,25")
      + res(f"R sup = {f(g['R_sup'], 3)} m"))}

{calc("Paso 1.2", "Radio del intradós",
      fml("R inf = R sup − d")
      + sus(f"R inf = {f(g['R_sup'], 3)} − {f(g['d'], 2)} = {f(g['R_inf'], 3)}")
      + res(f"R inf = {f(g['R_inf'], 3)} m"))}

{calc("Paso 1.3", "Ángulo total del arco",
      fml("θ = 2 · arcsen [ (L/2) / R sup ]")
      + sus(f"θ = 2 · arcsen (8,80 / {f(g['R_sup'], 3)}) = 2 · arcsen (0,5258) = 2 × 31,719°")
      + res(f"θ = {f(g['th_grados'], 3)}°   (semiapertura α = θ/2 = {f(g['alfa_apoyo'], 3)}°)"))}

{calc("Paso 1.4", "Longitud de los cordones",
      fml("L arco = R sup · θ (rad)      L intradós = R inf · θ (rad)")
      + sus(f"θ = {f(g['th_grados'], 3)}° × π/180 = {f(g['th'], 5)} rad<br>"
            f"L arco = {f(g['R_sup'], 3)} × {f(g['th'], 5)} = {f(g['L_arco'], 3)} m<br>"
            f"L intradós = {f(g['R_inf'], 3)} × {f(g['th'], 5)} = {f(g['L_inf'], 3)} m")
      + res(f"L arco = {f(g['L_arco'], 3)} m   |   L intradós = {f(g['L_inf'], 3)} m"))}

{calc("Paso 1.5", "División en paneles y paso de correas",
      fml("Δs = L arco / 8 paneles      paso correa = L arco / 12")
      + sus(f"Δs = {f(g['L_arco'], 3)} / 8 = {f(g['ds'], 4)} m<br>"
            f"paso de correas = {f(g['L_arco'], 3)} / 12 = {f(g['paso_correa'], 4)} m")
      + res(f"Δs = {f(g['ds'], 4)} m   |   paso de correas = {f(g['paso_correa'], 4)} m")
      + nota("Se adoptan 13 correas (12 espacios) para que la lámina de techo tenga apoyos "
             "cada ≈ 1,54 m, compatible con los perfiles IPN 140."))}

<h3>1.6 Coordenadas de los nudos</h3>
<p>Con origen en el apoyo izquierdo del extradós, la coordenada vertical de cada nudo que
   corresponde a φ = i·θ/8 sobre el extradós es <span class="mono">y e = (f − R sup) +
   √(R sup² − x²)</span>, con <span class="mono">x = R sup·sen φ</span>; la del intradós es
   <span class="mono">y i = y e − d/cos φ</span> (el canto se mide perpendicular al arco).</p>
{tabla([("Nudo", ""), ("φ (°)", "n"), ("x (m)", "n"), ("y e (m)", "n"), ("y i (m)", "n")],
       filas, caption="Tabla 1.1 — Nudos del arco (cada dos paneles).")}
"""


def ej2():
    return f"""
<h2 id="e2">2 · Cargas y combinaciones</h2>
<p>Las cargas se llevan a carga lineal por pórtico multiplicando por la separación
   S = {f(g['S'], 2)} m (área tributaria de un pórtico). Las combinaciones son las de
   COVENIN–MINDUR 2002-88 (formato de diseño por estados límites, igual al del texto de acero).</p>

{calc("Paso 2.1", "Carga muerta total de cubierta",
      fml("D = D₁ + D₂ + D₃")
      + sus(f"D = 5,5 + 7,5 + 10,0 = {f(c['D'], 1)} kg/m²")
      + res(f"D = {f(c['D'], 1)} kg/m²"))}

{calc("Paso 2.2", "Carga de servicio lineal por pórtico",
      fml("q serv = (D + L + colgadas) · S")
      + sus(f"q serv = ({f(c['D'], 1)} + {f(c['L'], 1)} + {f(c['colgadas'], 1)}) × {f(g['S'], 2)} "
            f"= 138,0 × {f(g['S'], 2)}")
      + res(f"q serv = {f(c['q_serv'], 2)} kg/m"))}

{calc("Paso 2.3", "Peso propio de la estructura y carga de servicio total",
      fml("PP = PP cercha + PP pasarela      q serv,tot = q serv + PP")
      + sus(f"PP = {f(c['pp_cercha'], 1)} + {f(c['pp_pasarela'], 1)} = {f(c['PP'], 1)} kg/m<br>"
            f"q serv,tot = {f(c['q_serv'], 2)} + {f(c['PP'], 1)} = {f(c['q_serv_total'], 2)} kg/m")
      + res(f"q serv,tot = {f(c['q_serv_total'], 2)} kg/m"))}

{calc("Paso 2.4", "Carga mayorada de diseño",
      fml("q u = [1,2·(D + colgadas) + 1,6·L] · S + 1,2·PP   — combinación 1,2D + 1,6L")
      + sus(f"q u = [1,2 × ({f(c['D'], 1)} + {f(c['colgadas'], 1)}) + 1,6 × {f(c['L'], 1)}] × {f(g['S'], 2)} "
            f"+ 1,2 × {f(c['PP'], 1)}<br>"
            f"q u = (45,6 + 160,0) × {f(g['S'], 2)} + 72,0 = {f(c['q_u_cubierta'], 2)} × {f(g['S'], 2)} + 72,0")
      + res(f"q u = {f(c['q_u'], 2)} kg/m")
      + nota("Esta es la carga que gobierna todos los elementos de la cubierta y el empuje del arco. "
             "No incluye viento (acción excluida por el profesor) ni granizo."))}

{calc("Paso 2.5", "Peso sísmico de la edificación (para el cálculo de sismo)",
      fml("W = (D + colgadas + 0,5·L)·S + PP   — COVENIN 1756-1:2019, W incluye 50 % de L<br>"
          "W total = W por pórtico × n pórticos")
      + sus(f"W cubierta = {f(c['D'], 1)} + {f(c['colgadas'], 1)} + 0,5 × {f(c['L'], 1)} = {f(c['W_cub'], 1)} kg/m²<br>"
            f"W lineal = {f(c['W_cub'], 1)} × {f(g['S'], 2)} + {f(c['PP'], 1)} = {f(c['W_lineal'], 1)} kg/m<br>"
            f"W por pórtico = {f(c['W_lineal'], 1)} × {f(g['L_arco'], 3)} = {f(c['W_portico'], 0)} kg<br>"
            f"W total = {f(c['W_portico'], 0)} × {g['nport']} = {f(c['W_total'], 0)} kg")
      + res(f"W total = {f(c['W_total'] / 1000, 2)} t"))}
"""


def ej3():
    return f"""
<h2 id="e3">3 · Análisis global del pórtico</h2>
<p>El pórtico se resuelve con dos esquemas clásicos de predimensionado, que se declaran de forma
   explícita: el <b>empuje H</b> con la fórmula del arco triarticulado (viga equivalente) y los
   <b>momentos</b> con el esquema de viga biempotrada de igual luz; con los dos se obtiene el
   par de fuerzas <b>N = M/d</b> que circula por los cordones del arco. Es el mismo procedimiento
   del texto de la asignatura y del capítulo 8 del libro.</p>
{figura('fig-cl', ('3.1', 'Cuerpo libre del pórtico: empuje H u, reacción vertical R u y par de fuerzas N u.'))}

{calc("Paso 3.1", "Reacción vertical en el apoyo",
      fml("R u = q u · L / 2   — simetría de la estructura y de la carga")
      + sus(f"R u = {f(c['q_u'], 2)} × {f(g['L'], 2)} / 2 = {f(c['q_u'] * g['L'] / 2, 0)} kg")
      + res(f"R u = {f(a['R_u'], 0)} kg = {f(a['R_u'] / 1000, 2)} t"))}

{calc("Paso 3.2", "Empuje horizontal del arco",
      fml("H u = q u · L² / (8·f)   — arco triarticulado (viga equivalente), carga repartida")
      + sus(f"H u = {f(c['q_u'], 2)} × {f(g['L'], 2)}² / (8 × {f(g['f'], 2)}) "
            f"= {f(c['q_u'] * g['L'] ** 2, 1)} / {f(8 * g['f'], 1)}")
      + res(f"H u = {f(a['H_u'], 0)} kg = {f(a['H_u'] / 1000, 2)} t")
      + nota("El empuje <b>es la carga más importante del proyecto</b>: vale casi el doble que la "
             "reacción vertical. De él dependen el tirante de cabeza, la placa base y la zapata."))}

{calc("Paso 3.3", "Momento flector en la viga equivalente",
      fml("M u (extremos) = q u · L² / 12      M u (centro) = q u · L² / 24<br>"
          "— viga biempotrada con carga repartida uniforme")
      + sus(f"M u = {f(c['q_u'], 2)} × {f(g['L'], 2)}² / 12 = {f(a['M_u'], 0)} kg·m<br>"
            f"M centro = {f(c['q_u'], 2)} × {f(g['L'], 2)}² / 24 = {f(a['M_mid'], 0)} kg·m")
      + res(f"M u = {f(a['M_u'] / 1000, 2)} t·m (extremos)   |   M centro = {f(a['M_mid'] / 1000, 2)} t·m"))}

{calc("Paso 3.4", "Par de fuerzas en el doble arco",
      fml("N u = M u / d   — el momento se transforma en un par de fuerzas separadas el canto d")
      + sus(f"N u = {f(a['M_u'], 0)} / {f(g['d'], 2)} = {f(a['N_u'], 0)} kg")
      + res(f"N u = {f(a['N_u'] / 1000, 2)} t (compresión en el cordón superior, tracción en el inferior)")
      + nota("Este par es el que se verifica como <b>cordón 2×IPE 160</b> en el cálculo 6."))}

{calc("Paso 3.5", "Reacción inclinada en el apoyo y carga de la columna",
      fml("N apoyo = √(H u² + R u²)      P u,zapata = R u + 1,2 · g perfil · h")
      + sus(f"N apoyo = √({f(a['H_u'], 0)}² + {f(a['R_u'], 0)}²) = {f(a['N_apoyo'], 0)} kg<br>"
            f"P u,zapata = {f(a['R_u'] / 1000, 3)} + 1,2 × 117,0 × {f(g['h'], 2)}/1000 "
            f"= {f(a['R_u'] / 1000, 3)} + {f(a['p_pilar_u'], 3)}")
      + res(f"N apoyo = {f(a['N_apoyo'] / 1000, 2)} t   |   P u (columna) = {f(a['P_u_zapata'], 3)} t")
      + nota("En servicio (sin mayorar) la carga de la columna vale "
             f"P serv = {f(a['P_serv_zapata'], 3)} t. Es la carga que baja a la zapata del cálculo 11."))}

{figura('fig-dfc', ('3.2', 'DFC y DMF de la viga biempotrada equivalente: V máx en los apoyos y '
                            'M negativo en extremos, positivo al centro.'))}
"""
