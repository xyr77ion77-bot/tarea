/* Visor del nivel B (dinámica): comparación R = 6 / R = 2, modo fundamental de vibración,
   espectro de diseño y tablas de contraste. Todos los números salen de dinamica.py
   (modal.json / datos2.js) y de solver2d.py (resultados.json / datos.js): nada está a ojo. */
(function () {
  const M = window.MODELO, RES = window.RESULTADOS, D = window.MODAL;
  if (!M || !RES || !D) { console.warn("faltan datos para el nivel B"); return; }
  const REF = M.referencia.de_cuaderno;
  const NS = "http://www.w3.org/2000/svg";
  const el = (t, a, txt) => {
    const e = document.createElementNS(NS, t);
    for (const k in a) e.setAttribute(k, a[k]);
    if (txt != null) e.textContent = txt;
    return e;
  };
  const fmt = (x, d) => Number(x).toLocaleString("es-VE",
    { minimumFractionDigits: d == null ? 2 : d, maximumFractionDigits: d == null ? 2 : d });
  const pct = (x) => fmt(100 * x, 1) + " %";
  /* "7,6 % menos" suena mejor que "-7,6 %" en el texto */
  const varPct = (r) => r < 1 ? fmt(100 * (1 - r), 1) + " % menos" : fmt(100 * (r - 1), 1) + " % más";
  const nodos = M.nodos.map((n) => ({ x: n.x / 100, y: n.y / 100, n: n.n }));
  const NOM = {}; nodos.forEach((n, i) => { NOM[n.n] = i; });
  const T1 = D.T1, Cd = D.Cd, VEL = 0.25;                  // oscilación a cámara lenta ×1/4
  const idxE = M.elementos.findIndex((e) => e.n === "tirante de cabeza");
  const H_COL = 850;                                       // cm, altura del pilar
  const M_base_modal = (esp) => (esp.V_modal / 2) * H_COL / 1e5;   // t·m (ménsula, corte modal)
  let t = 0, corriendo = true;

  /* proyección isométrica (para las figuras de la estructura) */
  const proy = (W, H, x0, x1, y0, y1, pad) => {
    const k = Math.min((W - pad.l - pad.r) / (x1 - x0), (H - pad.t - pad.b) / (y1 - y0));
    return { k, X: (x) => pad.l + (x - x0) * k, Y: (y) => H - pad.b - (y - y0) * k };
  };
  /* proyección con escalas independientes (para los gráficos de ejes) */
  const proyEjes = (W, H, x0, x1, y0, y1, pad) => {
    const kx = (W - pad.l - pad.r) / (x1 - x0), ky = (H - pad.t - pad.b) / (y1 - y0);
    return { X: (x) => pad.l + (x - x0) * kx, Y: (y) => H - pad.b - (y - y0) * ky };
  };
  const colorN = (n, nmax) => {
    const u = Math.min(1, Math.abs(n) / Math.max(1, nmax)), L = 74 - 26 * u, S = 55 + 40 * u;
    return n < 0 ? `hsl(2,${S}%,${L}%)` : `hsl(199,${S}%,${L}%)`;
  };
  function terreno(svg, P, x0m, x1m) {
    const y0 = P.Y(0), xi = P.X(x0m), xf = P.X(x1m);
    svg.appendChild(el("line", { x1: xi, y1: y0, x2: xf, y2: y0, stroke: "#2c3c5c", "stroke-width": 1.2 }));
    for (let x = xi; x < xf; x += 13)
      svg.appendChild(el("line", { x1: x, y1: y0, x2: x - 9, y2: y0 + 10, stroke: "#24334f",
                                   "stroke-width": 1 }));
    [0, 17.6].forEach((xm) => {
      const p = P.X(xm);
      svg.appendChild(el("rect", { x: p - 11, y: y0, width: 22, height: 11, fill: "#17223a",
                                   stroke: "#67809f", "stroke-width": 1.2 }));
    });
  }

  /* ------------------------------------------- comparación R = 6 / R = 2 (animada) */
  const AMP_CMP = 20;                                      // idéntica en los dos paneles
  function escenaCmp(svgId, R) {
    const svg = document.getElementById(svgId);
    if (!svg) return null;
    const W = 520, H = 430, P = proy(W, H, -3.2, 25.0, -2.6, 13.6, { l: 26, r: 26, t: 34, b: 46 });
    terreno(svg, P, -3.2, 25.0);
    const gGhost = el("g"), gBar = el("g"), gNodo = el("g"), gLbl = el("g");
    [gGhost, gBar, gNodo, gLbl].forEach((g) => svg.appendChild(g));
    M.elementos.forEach((e) => {
      const a = nodos[e.a], b = nodos[e.b];
      gGhost.appendChild(el("line", { x1: P.X(a.x), y1: P.Y(a.y), x2: P.X(b.x), y2: P.Y(b.y),
        stroke: "#334764", "stroke-width": 1.1, "stroke-dasharray": "5 4" }));
    });
    const barras = M.elementos.map(() => gBar.appendChild(el("line", { "stroke-linecap": "round" })));
    const puntos = M.nodos.map(() => gNodo.appendChild(el("circle", { r: 2.1, fill: "#8ea4c8" })));
    const flechas = [0, 1].map(() => {
      const g = gLbl.appendChild(el("g"));
      return { l: g.appendChild(el("line", { stroke: "#f472b6", "stroke-width": 2.4 })),
               h: g.appendChild(el("path", { fill: "#f472b6" })) };
    });
    gLbl.appendChild(el("text", { x: 30, y: 20, fill: "#6b81a3", "font-size": 11,
                                  "font-family": "monospace" },
      `deformada ×${AMP_CMP} — igual en los dos paneles`));
    const txtDelta = gLbl.appendChild(el("text", { fill: "#fca5a5", "font-size": 11.5,
                                                   "font-family": "monospace" }));
    const txtDato = gLbl.appendChild(el("text", { fill: "#9fb3d1", "font-size": 11,
                                                  "font-family": "monospace", x: 30, y: H - 14 }));
    const caso = R === 6 ? "sismo_R6" : "sismo_R2";
    const res = RES.casos[caso], osc = RES.oscilacion[caso], esp = D.espectro[R];
    const axial = res.axial, nmax = Math.max.apply(null, Object.values(axial).map(Math.abs));
    return { render(fase) {
      const dsp = M.nodos.map((n, i) => ({
        u: (osc.grav[i].u + esp.campo_inel[i].u * fase) * AMP_CMP,
        v: (osc.grav[i].v + esp.campo_inel[i].v * fase) * AMP_CMP,
      }));
      const p = (i) => [P.X(nodos[i].x + dsp[i].u / 100), P.Y(nodos[i].y + dsp[i].v / 100)];
      M.elementos.forEach((e, i) => {
        const [x1, y1] = p(e.a), [x2, y2] = p(e.b);
        barras[i].setAttribute("x1", x1); barras[i].setAttribute("y1", y1);
        barras[i].setAttribute("x2", x2); barras[i].setAttribute("y2", y2);
        const N = axial[String(i)];
        if (N === undefined) {                             // sin tirante en este caso
          barras[i].setAttribute("stroke", "#42506b"); barras[i].setAttribute("stroke-width", 1.3);
          barras[i].setAttribute("stroke-dasharray", "6 6");
        } else {
          barras[i].removeAttribute("stroke-dasharray");
          const u = Math.min(1, Math.abs(N) / nmax);
          barras[i].setAttribute("stroke", i === idxE ? "#fbbf24" : colorN(N, nmax));
          barras[i].setAttribute("stroke-width", (i === idxE ? 3 : 1.3 + 3.4 * u).toFixed(2));
        }
      });
      M.nodos.forEach((n, i) => {
        const [x, y] = p(i);
        puntos[i].setAttribute("cx", x); puntos[i].setAttribute("cy", y);
        puntos[i].setAttribute("fill", nodos[i].y === 0 ? "none" : "#8ea4c8");
      });
      flechas.forEach((f, j) => {
        const iN = j === 0 ? NOM["top_i"] : NOM["top_d"], xy = p(iN), yf = xy[1] + 15;
        f.l.setAttribute("x1", xy[0] - 4); f.l.setAttribute("y1", yf);
        f.l.setAttribute("x2", xy[0] + 40); f.l.setAttribute("y2", yf);
        f.h.setAttribute("d", `M${xy[0] + 34},${yf - 5} L${xy[0] + 42},${yf} L${xy[0] + 34},${yf + 5} Z`);
      });
      txtDelta.setAttribute("x", 32);
      txtDelta.setAttribute("y", P.Y(nodos[NOM["top_i"]].y) + 52);
      txtDelta.setAttribute("text-anchor", "start");
      txtDelta.textContent =
        `Δ de diseño = ${fmt(res.deriva_amplificada, 2)} cm = Cd·δ (δ = ${fmt(res.deriva, 2)} cm)`;
      txtDato.textContent =
        `Δ dinámico (T₁) = ${fmt(esp.delta_inel, 2)} cm · límite ${fmt(esp.deriva_lim, 0)} cm`;
    } };
  }
  const c6 = escenaCmp("lienzoR6", 6), c2 = escenaCmp("lienzoR2", 2);

  /* ------------------------------------------------------- panel de R = 6 / 2 */
  function panel(id, R) {
    const res = RES.casos[R === 6 ? "sismo_R6" : "sismo_R2"], esp = D.espectro[R];
    const perno = R === 6 ? REF.perno_R6 : REF.perno_R2;
    const kpi = (lab, val, sub) => `<div class="kpi"><div class="lab">${lab}</div>
      <div class="val">${val}</div><div class="sub">${sub}</div></div>`;
    document.getElementById(id).innerHTML =
      kpi("Deriva Cd·Δ", fmt(res.deriva_amplificada, 2) + " cm",
          `<span class="badge ${res.deriva_ok ? "ok" : "no"}">${res.deriva_ok ? "cumple" : "no cumple"}</span>
           de ${fmt(res.deriva_lim, 0)} cm · cuaderno ${fmt(esp.delta_cuaderno, 2)} cm`) +
      kpi("Δ dinámico (T₁)", fmt(esp.delta_inel, 2) + " cm",
          `δ elástico ${fmt(esp.delta_el, 2)} cm · Sd = ${fmt(esp.Sd_el, 2)} cm`) +
      kpi("Ordenada Ad(T₁)", fmt(esp.Ad_T1, 4),
          `Ad(Ta) = ${fmt(esp.Ad_Ta, 4)} → ${varPct(esp.Ad_T1 / esp.Ad_Ta)}`) +
      kpi("Cortante basal", fmt(esp.V_modal / 1000, 2) + " t",
          `cuaderno ${fmt(esp.V0_cuaderno_portico / 1000, 2)} t/pórtico → ${varPct(esp.V_modal / esp.V0_cuaderno_portico)}`) +
      kpi("M base del pilar", fmt(res.M_base / 1000, 2) + " t·m",
          `izq ${fmt(res.V_col.izquierdo.M / 1000, 2)} · der ${fmt(res.V_col.derecho.M / 1000, 2)} t·m ·
           dinámico ${fmt(M_base_modal(esp), 2)}`) +
      kpi("D/C del pilar", fmt(res.dc.pilar, 3),
          `cuaderno ${fmt(R === 6 ? REF.dc_columna[6] : REF.dc_columna[2], 3)} · perno de la placa ${fmt(perno.dc, 3)}${perno.ok ? "" : " ✗"}`);
  }
  panel("kpiR6", 6); panel("kpiR2", 2);
  document.getElementById("notaComparacion").innerHTML =
    `<section class="card"><h3>Qué cambia entre los dos factores de reducción</h3>
     <div class="nota">Con <b>R = 6</b> el espectro baja y la deriva amplificada queda en
     <b>${fmt(RES.casos.sismo_R6.deriva_amplificada, 2)} cm ≤ 17 cm</b>: cumple. Con <b>R = 2</b> la
     demanda es 3,0 veces mayor y la deriva llega a
     <b>${fmt(RES.casos.sismo_R2.deriva_amplificada, 2)} cm</b>: <b>no cumple</b>, y con ella tampoco
     cumplen el perno Φ1″ de la placa base (D/C ${fmt(REF.perno_R2.dc, 3)}) ni la zapata por
     deslizamiento (FS ${fmt(REF.zapata.FS_desliz, 2)} con la hipótesis de empuje sin tirante). Las dos
     columnas se dibujan con la <b>misma</b> amplificación ×${AMP_CMP} y el <b>mismo</b> instante:
     la diferencia que se ve es la del sismo, no la del dibujo.
     <button id="btnPausa" style="margin-left:8px">⏸ congelar</button></div></section>`;

  /* ------------------------------------------------------------ modo fundamental */
  (function modo() {
    const svg = document.getElementById("lienzoModo");
    if (!svg) return;
    const W = 520, H = 420, P = proy(W, H, -3.6, 21.6, -2.2, 14.4, { l: 28, r: 26, t: 66, b: 30 });
    terreno(svg, P, -3.6, 21.6);
    const m1 = D.modos[0], A = 52;                         // px por unidad de φ (normalizado)
    const gG = el("g"), gM = el("g"), gF = el("g"), gL = el("g");
    [gG, gM, gF, gL].forEach((g) => svg.appendChild(g));
    M.elementos.forEach((e) => {
      const a = nodos[e.a], b = nodos[e.b];
      gG.appendChild(el("line", { x1: P.X(a.x), y1: P.Y(a.y), x2: P.X(b.x), y2: P.Y(b.y),
        stroke: "#2b3853", "stroke-width": 1.1, "stroke-dasharray": "5 4" }));
    });
    const pos = (i) => [P.X(nodos[i].x) + m1.phi[i].u * A, P.Y(nodos[i].y) - m1.phi[i].v * A];
    M.elementos.forEach((e) => {
      const p1 = pos(e.a), p2 = pos(e.b), tir = e.n === "tirante de cabeza";
      gM.appendChild(el("line", { x1: p1[0], y1: p1[1], x2: p2[0], y2: p2[1],
        stroke: tir ? "#fbbf24" : "#7dd3fc", "stroke-width": tir ? 2.4 : 1.6,
        "stroke-linecap": "round" }));
    });
    M.nodos.forEach((n, i) => {
      const p1 = pos(i);
      gM.appendChild(el("circle", { cx: p1[0], cy: p1[1], r: 2.1, fill: "#e6eefc" }));
    });
    const fuerzas = D.espectro[6].fuerza;
    const Fmax = Math.max.apply(null, fuerzas.map((f) => Math.abs(f.F)));
    fuerzas.forEach((f) => {
      if (!f.F) return;
      const i = NOM[f.n], p1 = pos(i), s = Math.sign(f.F);
      const len = 10 + 46 * Math.abs(f.F) / Fmax;
      gF.appendChild(el("line", { x1: p1[0] - s * 4, y1: p1[1], x2: p1[0] + s * len, y2: p1[1],
        stroke: "#f472b6", "stroke-width": 1.8, opacity: .85 }));
      gF.appendChild(el("path", { d: `M${p1[0] + s * (len - 7)},${p1[1] - 4} L${p1[0] + s * (len + 1)},${p1[1]} ` +
        `L${p1[0] + s * (len - 7)},${p1[1] + 4} Z`, fill: "#f472b6", opacity: .85 }));
    });
    gL.appendChild(el("text", { x: 30, y: 20, fill: "#9fb3d1", "font-size": 11,
                                "font-family": "monospace" },
      `modo 1 · T₁ = ${fmt(m1.T, 3)} s · f = ${fmt(m1.f, 2)} Hz`));
    gL.appendChild(el("text", { x: 30, y: 36, fill: "#9fb3d1", "font-size": 11,
                                "font-family": "monospace" },
      `φ normalizado (cabeza de pilar = 1,00) · Γ₁ = ${fmt(m1.gamma, 3)} · ${fmt(m1.porc, 1)} % de la masa`));
    gL.appendChild(el("text", { x: 30, y: 52, fill: "#f9a8d4", "font-size": 11,
                                "font-family": "monospace" },
      "flechas rosadas = fuerza inercial Γ·m·φ (suma = cortante basal)"));
    const p6 = D.espectro[6], p2 = D.espectro[2];
    document.getElementById("txtModo").innerHTML =
      `<div class="nota">El primer modo es una <b>traslación pura</b>: los dos pilares se mueven juntos y
      el arco se traslada con ellos. <b>T₁ = ${fmt(m1.T, 3)} s</b> (f = ${fmt(m1.f, 2)} Hz),
      participación modal Γ₁ = ${fmt(m1.gamma, 3)} y <b>${fmt(m1.porc, 1)} %</b> de la masa
      efectiva; los modos siguientes son locales del arco (T₂ = ${fmt(D.modos[1].T, 3)} s,
      ${fmt(D.modos[1].porc, 1)} % de la masa), así que la respuesta sísmica la gobierna el modo 1.
      Con las masas sísmicas reales (D + 0,5L + pasarela + peso propio) el pórtico pesa
      <b>${fmt(D.W, 0)} kg</b> contra 7 798 kg de la planilla (+39 %).
      T₁ queda en la <b>rama descendente</b> del espectro (T₁ &gt; TC = ${fmt(D.TC, 3)} s):
      Ad(T₁) = ${fmt(p6.Ad_T1, 4)} es ${varPct(p6.Ad_T1 / p6.Ad_Ta)} que la meseta
      Ad(Ta) = ${fmt(p6.Ad_Ta, 4)} del cuaderno. Aun así el cortante basal sube a
      <b>${fmt(p6.V_modal / 1000, 2)} t</b> por pórtico (cuaderno ${fmt(p6.V0_cuaderno_portico / 1000, 2)} t)
      por el peso real, y el desplazamiento de diseño pasa a <b>${fmt(p6.delta_inel, 2)} cm</b>
      (cuaderno ${fmt(p6.delta_cuaderno, 2)} cm); con R = 2 sería
      ${fmt(p2.delta_inel, 2)} cm contra ${fmt(p2.delta_cuaderno, 2)} cm.
      Comprobación cruzada: 2π√(m/k) con k = 2·3EI/h³ = ${fmt(D.k_lateral, 0)} kg/cm da
      ${fmt(D.T1_teorico, 3)} s, contra ${fmt(T1, 3)} s del autovalor (0,5 % de diferencia).</div>`;
  })();

  /* ------------------------------------------------------------------ espectro */
  (function espectro() {
    const svg = document.getElementById("lienzoEspectro");
    if (!svg) return;
    const W = 640, H = 400, pad = { l: 62, r: 26, t: 46, b: 54 };
    const Tmax = 2.0, Amax = 0.5;
    const P = proyEjes(W, H, 0, Tmax, 0, Amax, pad);
    for (let T = 0; T <= Tmax + 0.001; T += 0.25) {
      const mayor = Math.abs(T / 0.5 - Math.round(T / 0.5)) < 1e-6;
      svg.appendChild(el("line", { x1: P.X(T), y1: P.Y(0), x2: P.X(T), y2: P.Y(Amax),
                                   stroke: mayor ? "#1e2b43" : "#172238", "stroke-width": 1 }));
      if (mayor)
        svg.appendChild(el("text", { x: P.X(T), y: P.Y(0) + 18, fill: "#6b81a3", "font-size": 10.5,
                                     "text-anchor": "middle", "font-family": "monospace" }, fmt(T, 1)));
    }
    for (let A = 0; A <= Amax + 1e-9; A += 0.1) {
      svg.appendChild(el("line", { x1: P.X(0), y1: P.Y(A), x2: P.X(Tmax), y2: P.Y(A),
                                   stroke: "#1e2b43", "stroke-width": 1 }));
      svg.appendChild(el("text", { x: P.X(0) - 8, y: P.Y(A) + 4, fill: "#6b81a3", "font-size": 10.5,
                                   "text-anchor": "end", "font-family": "monospace" }, fmt(A, 1)));
    }
    svg.appendChild(el("text", { x: (P.X(0) + P.X(Tmax)) / 2, y: H - 12, fill: "#9fb3d1",
                                 "font-size": 11.5, "text-anchor": "middle" }, "período T (s)"));
    svg.appendChild(el("text", { x: 16, y: P.Y(Amax) - 14, fill: "#9fb3d1", "font-size": 11.5 }, "Ad(T)"));
    const marca = (T, txt, col, w, arriba) => {
      svg.appendChild(el("line", { x1: P.X(T), y1: P.Y(0), x2: P.X(T), y2: P.Y(Amax), stroke: col,
                                   "stroke-width": w || 1.1, "stroke-dasharray": "4 4" }));
      svg.appendChild(el("text", { x: P.X(T) + 4, y: arriba ? P.Y(Amax) + 13 : P.Y(0) - 9,
                                   fill: col, "font-size": 10.5, "font-family": "monospace" }, txt));
    };
    marca(D.Ta, `Ta = ${fmt(D.Ta, 2)} s`, "#6b81a3", 1.1, false);
    marca(D.TC, `TC = ${fmt(D.TC, 3)} s`, "#8fa6c8", 1.1, false);
    marca(T1, `T₁ = ${fmt(T1, 3)} s`, "#fbbf24", 1.8, true);
    [["#38bdf8", 6, "R = 6"], ["#f472b6", 2, "R = 2"]].forEach((cv) => {
      const col = cv[0], R = cv[1], nom = cv[2], esp = D.espectro[R];
      let dd = "";
      D.curva.forEach((pt) => {
        const y = R === 6 ? pt[1] : pt[2];
        dd += `${dd === "" ? "M" : "L"}${P.X(pt[0])},${P.Y(y)} `;
      });
      svg.appendChild(el("path", { d: dd, fill: "none", stroke: col, "stroke-width": 2 }));
      svg.appendChild(el("circle", { cx: P.X(T1), cy: P.Y(esp.Ad_T1), r: 4.2, fill: col,
                                     stroke: "#0a0f1a", "stroke-width": 1.4 }));
      svg.appendChild(el("text", { x: P.X(T1) + 10, y: P.Y(esp.Ad_T1) + (R === 6 ? -8 : 15), fill: col,
                                   "font-size": 11.5, "font-family": "monospace" },
        `${nom}: Ad(T₁) = ${fmt(esp.Ad_T1, 4)}`));
    });
    svg.appendChild(el("text", { x: P.X(0.03), y: P.Y(0.47), fill: "#9fb3d1", "font-size": 11.5,
                                 "font-family": "monospace" }, "meseta 2,4·AA/R"));
    svg.appendChild(el("text", { x: P.X(1.22), y: P.Y(0.38), fill: "#9fb3d1", "font-size": 11.5,
                                 "font-family": "monospace" }, "rama descendente TC/T"));
    const a6 = D.espectro[6], a2 = D.espectro[2];
    document.getElementById("txtEspectro").innerHTML =
      `<div class="nota">La forma espectral es la que documentó el cuaderno (ordenada de la meseta
      <code>Ad = 2,4·AA/R</code> hasta <code>TC</code>, y de ahí en adelante la rama descendente
      <code>TC/T</code>), evaluada ahora en el período real de la estructura en vez de en
      <code>Ta</code>. Como T₁ = ${fmt(T1, 3)} s &gt; TC = ${fmt(D.TC, 3)} s, la ordenada baja
      ${varPct(a6.Ad_T1 / a6.Ad_Ta)}: de ${fmt(a6.Ad_Ta, 4)} a ${fmt(a6.Ad_T1, 4)} (R = 6) y de
      ${fmt(a2.Ad_Ta, 4)} a ${fmt(a2.Ad_T1, 4)} (R = 2). Parámetros de la norma usados por el cuaderno:
      AA = ${fmt(D.AA, 3)}, AV = ${fmt(D.AV, 3)}, Ta = ${fmt(D.Ta, 2)} s, TC = ${fmt(D.TC, 3)} s,
      φ = ${fmt(D.phi_esp, 4)} y Cd = ${fmt(Cd, 2)} (§9.4). Los puntos marcados son la demanda en
      T₁.</div>`;
  })();

  /* ------------------------------------------- estático (cuaderno) contra dinámico */
  (function tablaDin() {
    const r6 = RES.casos.sismo_R6, r2 = RES.casos.sismo_R2;
    const e6 = D.espectro[6], e2 = D.espectro[2];
    const filas = [
      ["Peso sísmico por pórtico", "7 798 kg", fmt(D.W, 0) + " kg", fmt(D.W, 0) + " kg",
       "el peso propio real es 2,24 veces la planilla de 60 kg/m"],
      ["Período fundamental", "—", "—", `T₁ = ${fmt(T1, 3)} s`,
       `mayor que TC = ${fmt(D.TC, 3)} s: la demanda se evalúa en la rama descendente`],
      ["Ordenada de diseño", `Ad(Ta) = ${fmt(e6.Ad_Ta, 4)}`, `Ad(Ta) = ${fmt(e6.Ad_Ta, 4)}`,
       `Ad(T₁) = ${fmt(e6.Ad_T1, 4)}`, `${varPct(e6.Ad_T1 / e6.Ad_Ta)}: efecto favorable del período`],
      ["Cortante basal por pórtico", fmt(e6.V0_cuaderno_portico / 1000, 2) + " t",
       fmt(e6.V0_cuaderno_portico / 1000, 2) + " t", fmt(e6.V_modal / 1000, 2) + " t",
       `+${varPct(e6.V_modal / e6.V0_cuaderno_portico)} por el peso sísmico real`],
      ["M base del pilar (R = 6)", "4,40 t·m", fmt(r6.M_base / 1000, 2) + " t·m",
       fmt(M_base_modal(e6), 2) + " t·m", "gobernado por el pilar derecho (reparto desigual del corte)"],
      ["Desplazamiento elástico δ", fmt(e6.delta_e_cuaderno, 2) + " cm", fmt(r6.deriva, 2) + " cm",
       fmt(e6.delta_el, 2) + " cm", "el estático coincide a 4 cifras con la ménsula del cuaderno"],
      ["Deriva de diseño Cd·δ (R = 6)", fmt(e6.delta_cuaderno, 2) + " cm ✓",
       fmt(r6.deriva_amplificada, 2) + " cm ✓", fmt(e6.delta_inel, 2) + " cm ✓",
       "cumple con los tres criterios (< 17 cm)"],
      ["Deriva de diseño Cd·δ (R = 2)", fmt(e2.delta_cuaderno, 2) + " cm ✗",
       fmt(r2.deriva_amplificada, 2) + " cm ✗", fmt(e2.delta_inel, 2) + " cm ✗",
       "el dinámico agrava el incumplimiento que ya marcaba el cuaderno"],
      ["M base del pilar (R = 2)", "13,21 t·m", fmt(r2.M_base / 1000, 2) + " t·m",
       fmt(M_base_modal(e2), 2) + " t·m",
       "el D/C del pilar sigue por debajo de 1: gobierna la deriva, no la resistencia"],
    ];
    document.querySelector("#tablaDin tbody").innerHTML = filas.map((fila) =>
      `<tr><td>${fila[0]}</td><td class="n">${fila[1]}</td><td class="n">${fila[2]}</td>
       <td class="n" style="color:#7dd3fc">${fila[3]}</td>
       <td style="color:var(--tx3);text-align:left">${fila[4]}</td></tr>`).join("");
    document.getElementById("notasDin").innerHTML =
      `<div class="nota">Los tres bloques son <b>el mismo pórtico</b> con tres niveles de
      aproximación: (1) fórmulas cerradas del cuaderno, (2) modelo 2D de barras con las fuerzas
      laterales del cuaderno y (3) análisis modal con el espectro evaluado en T₁ y las masas reales.
      El modelo de barras reproduce el cuaderno en la deriva (0,00 %), en el momento de la base y en el
      D/C del tirante, del cordón y del pilar: las diferencias del bloque dinámico son
      <b>físicas</b> (peso propio y período), no de programa. El momento modal de la base es
      <code>V_col,modal·h</code> con <code>V_col,modal = V_modal/2</code>, la misma relación de ménsula
      que usó el cuaderno.</div>`;
  })();

  /* ------------------------------------------- sin tirante: las dos hipótesis juntas */
  (function sinTirante() {
    const r = RES.casos.sin_tirante;
    const H_cuad = REF.H_u, M_cuad = H_cuad * H_COL / 1e5;               // t, t·m
    const Ncord = Math.max.apply(null, Object.keys(r.axial)
      .filter((i) => M.elementos[+i] && M.elementos[+i].n.indexOf("cordón") >= 0)
      .map((i) => -r.axial[i]));
    const filas = [
      ["Arranque <b>restringido</b> (hipótesis del cuaderno: el empuje llega a la cabeza del pilar)",
       fmt(H_cuad / 1000, 2) + " t", fmt(M_cuad, 1) + " t·m", "pilar HEB 300 en P‑M",
       fmt(REF.dc_columna_sin_tirante, 2), false],
      ["Arranque <b>libre</b> (modelo 2D: el arco se aplana y separa los apoyos)",
       fmt(r.H_arco / 1000, 2) + " t", fmt(r.M_base / 1000, 2) + " t·m",
       `cordón superior: ${fmt(Ncord / 1000, 1)} t (D/C ${fmt(r.dc.cordon, 2)}) · pilar (D/C ${fmt(r.dc.pilar, 2)})`,
       fmt(r.dc.cordon, 2), true],
    ];
    document.querySelector("#tablaSin tbody").innerHTML = filas.map((f) =>
      `<tr><td>${f[0]}</td><td class="n">${f[1]}</td><td class="n">${f[2]}</td>
       <td style="text-align:left">${f[3]}</td>
       <td class="n" style="color:#f87171">${f[4]} ✗</td></tr>`).join("");
    document.getElementById("notasSin").innerHTML =
      `<div class="nota alerta">El cuaderno comprobó el pilar con <code>H = ${fmt(H_cuad / 1000, 2)} t</code>
      en la cabeza (<code>M = H·h ≈ ${fmt(M_cuad, 0)} t·m</code>, D/C ${fmt(REF.dc_columna_sin_tirante, 2)}:
      <b>no cumple</b>). El modelo 2D deja que los apoyos se separen: el empuje cae a
      ${fmt(r.H_arco / 1000, 2)} t y el pilar queda holgado (D/C ${fmt(r.dc.pilar, 2)} ✓), pero entonces
      la cercha pierde la acción de arco y trabaja como viga curva: el cordón superior llega a
      ${fmt(Ncord / 1000, 1)} t (<b>D/C ${fmt(r.dc.cordon, 2)}: no cumple</b>). Son los dos extremos del
      mismo problema y por eso van juntos en la tabla. <b>Con el tirante ejecutado</b>
      (T = ${fmt(RES.casos.mayorada.tirante_N / 1000, 2)} t de rotura, D/C
      ${fmt(RES.casos.mayorada.dc.tirante, 2)}) el empuje no sale de la cercha y no aparece ninguna de
      las dos fallas: <b>el tirante no es un elemento de confort, cierra el camino de carga más
      desfavorable.</b></div>
      <div class="nota">Ojo con mezclar hipótesis: el <b>deslizamiento de la zapata</b> del cuaderno
      (FS = ${fmt(REF.zapata.FS_desliz, 2)} ✗) se calculó con el empuje del arranque restringido
      (H = ${fmt(REF.zapata.H_sin_tirante / 1000, 2)} t), no con los ${fmt(r.H_arco / 1000, 2)} t del
      arranque libre. Cada D/C del expediente debería declarar con qué hipótesis de empuje se obtuvo
      (AUDITORIA.md §5.3).</div>`;
  })();

  /* -------------------------------------------------------------- animación */
  const btn = document.getElementById("btnPausa");
  let raf = null, t0 = null;
  function paso(now) {
    if (t0 == null) t0 = now;
    const dt = Math.min(0.05, (now - t0) / 1000); t0 = now;
    if (corriendo) t += dt * VEL;
    const fase = Math.sin(2 * Math.PI * t / T1);
    if (c6) c6.render(fase);
    if (c2) c2.render(fase);
    raf = requestAnimationFrame(paso);
  }
  if (btn) btn.onclick = () => {
    corriendo = !corriendo;
    btn.textContent = corriendo ? "⏸ congelar" : "▶ animar";
  };
  if (c6) c6.render(0);
  if (c2) c2.render(0);
  raf = requestAnimationFrame(paso);
  void raf;
})();
