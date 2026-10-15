/* Visor animado del pórtico 2D — consume modelo.json + resultados.json (datos.js).
   Dibuja las cargas, la deformada amplificada, los axiales con color y los momentos de
   los pilares. Todos los desplazamientos salen del análisis matricial (solver2d.py):
   no hay nada dibujado «a ojo». */
(function () {
  const M = window.MODELO, RES = window.RESULTADOS;
  const CASOS = ["servicio", "mayorada", "sismo_R6", "sismo_R2", "sin_tirante"];
  const ETIQ = { servicio: "Servicio D+L", mayorada: "Rotura 1,2D+1,6L",
                 sismo_R6: "Sismo R = 6", sismo_R2: "Sismo R = 2", sin_tirante: "Sin tirante" };
  const REF_R = { servicio: null, mayorada: null, sismo_R6: 6, sismo_R2: 2, sin_tirante: "sin" };
  const ref = M.referencia.de_cuaderno;
  const est = { caso: "mayorada", escala: 20, prog: 0, osc: false, t: 0,
                cargas: true, axial: true, mom: false };

  // ---------------------------------------------------------------- pantalla
  const W = 1000, H = 620, mar = { l: 78, r: 190, t: 54, b: 62 };
  const mx0 = -1.3, mx1 = 18.9, my0 = -1.6, my1 = 13.3;
  const k = Math.min((W - mar.l - mar.r) / (mx1 - mx0), (H - mar.t - mar.b) / (my1 - my0));
  const PX = (xm) => mar.l + (xm - mx0) * k;
  const PY = (ym) => H - mar.b - (ym - my0) * k;
  const NS = "http://www.w3.org/2000/svg";
  const el = (t, a, txt) => {
    const e = document.createElementNS(NS, t);
    for (const kk in a) e.setAttribute(kk, a[kk]);
    if (txt != null) e.textContent = txt;
    return e;
  };
  const svg = document.getElementById("lienzo");
  const g = {};
  ["gTerreno", "gGhost", "gDef", "gMom", "gCarga", "gNodo", "gCota", "gLbl", "gCaja"]
    .forEach((id) => { g[id] = el("g"); svg.appendChild(g[id]); });

  const idx = M.nodos.map((n) => ({ x: n.x / 100, y: n.y / 100, n: n.n }));
  const NOM = {}; idx.forEach((n, i) => { NOM[n.n] = i; });
  const pos = (i, disp) => {
    const n = idx[i], amp = est.escala / 100;
    return [PX(n.x + (disp ? disp.u * amp : 0)), PY(n.y + (disp ? disp.v * amp : 0))];
  };

  /* ---------------------------------------------------------------- estático */
  (function estatico() {
    const y0 = PY(0), xi = PX(0) - 74, xf = PX(17.6) + 74;
    g.gTerreno.appendChild(el("line", { x1: xi, y1: y0, x2: xf, y2: y0, stroke: "#2c3c5c", "stroke-width": 1.2 }));
    for (let x = xi; x < xf; x += 13)
      g.gTerreno.appendChild(el("line", { x1: x, y1: y0, x2: x - 9, y2: y0 + 10, stroke: "#24334f", "stroke-width": 1 }));
    [0, 17.6].forEach((xm) => {                       // empotramiento en la base
      const p = PX(xm);
      g.gTerreno.appendChild(el("rect", { x: p - 13, y: y0, width: 26, height: 13,
                                          fill: "#17223a", stroke: "#67809f", "stroke-width": 1.4 }));
      for (let i = -10; i <= 10; i += 6)
        g.gTerreno.appendChild(el("line", { x1: p + i, y1: y0 + 13, x2: p + i - 7, y2: y0 + 20,
                                            stroke: "#67809f", "stroke-width": 1 }));
      g.gTerreno.appendChild(el("line", { x1: p - 15, y1: y0 + 13, x2: p + 15, y2: y0 + 13,
                                          stroke: "#67809f", "stroke-width": 1.4 }));
    });
    // cotas
    const cotaH = (x1, x2, y, txt, off) => {
      g.gCota.appendChild(el("line", { x1, y1: y, x2, y2: y, stroke: "#3d5680", "stroke-width": 1 }));
      g.gCota.appendChild(el("line", { x1, y1: y - 5, x2: x1, y2: y + 5, stroke: "#3d5680", "stroke-width": 1 }));
      g.gCota.appendChild(el("line", { x1: x2, y1: y - 5, x2, y2: y + 5, stroke: "#3d5680", "stroke-width": 1 }));
      g.gCota.appendChild(el("text", { x: (x1 + x2) / 2, y: y + (off || 16), fill: "#8fa6c8",
                                       "font-size": 12, "text-anchor": "middle" }, txt));
    };
    const cotaV = (x, y1, y2, txt) => {
      g.gCota.appendChild(el("line", { x1: x, y1, x2: x, y2, stroke: "#3d5680", "stroke-width": 1 }));
      g.gCota.appendChild(el("line", { x1: x - 5, y1, x2: x + 5, y2: y1, stroke: "#3d5680", "stroke-width": 1 }));
      g.gCota.appendChild(el("line", { x1: x - 5, y1: y2, x2: x + 5, y2, stroke: "#3d5680", "stroke-width": 1 }));
      g.gCota.appendChild(el("text", { x, y: (y1 + y2) / 2, fill: "#8fa6c8", "font-size": 12,
                                       "text-anchor": "middle", transform: `rotate(-90 ${x} ${(y1 + y2) / 2})` }, txt));
    };
    cotaH(PX(0), PX(17.6), y0 + 54, "L = 17,60 m");
    cotaV(PX(0) - 66, PY(0), PY(8.5), "h = 8,50 m");
    // f (flecha del arco)
    g.gCota.appendChild(el("line", { x1: PX(8.0), y1: PY(11), x2: PX(8.0), y2: PY(12.5),
                                     stroke: "#3d5680", "stroke-dasharray": "4 4" }));
    g.gCota.appendChild(el("text", { x: PX(8.05), y: PY(12.85), fill: "#8fa6c8", "font-size": 12 },
                           "f = 2,50 m"));
    // rótulos de barras
    g.gLbl.appendChild(el("text", { x: PX(-1.25), y: 74, fill: "#8fa6c8", "font-size": 11.5 },
                          "cercha de doble cordón: 2×IPE 160 (extradós e intradós)"));
    g.gLbl.appendChild(el("text", { x: PX(-1.25), y: 90, fill: "#8fa6c8", "font-size": 11.5 },
                          "montantes IPE 120 · diagonales IPE 160 en X (San Andrés)"));
    ["HEB 300"].forEach((t) => {
      [[PX(0.62), PY(4.6), -90], [PX(17.0), PY(4.6), 90]].forEach(([x, y, r]) => {
        g.gLbl.appendChild(el("text", { x, y, fill: "#8fa6c8", "font-size": 12,
                                        transform: `rotate(${r} ${x} ${y})`, "text-anchor": "middle" }, t));
      });
    });
  })();

  /* ---------------------------------------------------------------- barras y nudos */
  const lineas = M.elementos.map(() => {
    const gh = el("line", { stroke: "#3a4c6d", "stroke-width": 1.2, "stroke-dasharray": "5 4" });
    g.gGhost.appendChild(gh);
    const l = el("line", { "stroke-linecap": "round" });
    g.gDef.appendChild(l);
    return { e: l, ghost: gh };
  });
  const puntos = M.nodos.map(() => {
    const c = el("circle", { r: 2.3, fill: "#8ea4c8" });
    g.gNodo.appendChild(c);
    return c;
  });
  const NODOS_E = [], NODOS_I = [];
  M.nodos.forEach((n, i) => {
    if (/^e\d$/.test(n.n)) NODOS_E.push(i);
    if (/^i\d$/.test(n.n)) NODOS_I.push(i);
  });
  const flechasV = NODOS_E.concat(NODOS_I).map(() => {
    const gg = el("g"); g.gCarga.appendChild(gg);
    const l = el("line", { stroke: "#eab308", "stroke-width": 1.5 }); gg.appendChild(l);
    const t = el("path", { fill: "#eab308" }); gg.appendChild(t);
    return { g: gg, l, t };
  });
  const flechasH = [0, 1].map(() => {
    const gg = el("g"); g.gCarga.appendChild(gg);
    const l = el("line", { stroke: "#f472b6", "stroke-width": 2.6 }); gg.appendChild(l);
    const t = el("path", { fill: "#f472b6" }); gg.appendChild(t);
    const tx = el("text", { fill: "#f9a8d4", "font-size": 11, "font-family": "monospace" });
    gg.appendChild(tx);
    return { g: gg, l, t, tx };
  });
  const deriva = (() => {
    const gg = el("g"); g.gCarga.appendChild(gg);
    gg.appendChild(el("line", { stroke: "#f87171", "stroke-width": 1.2, "stroke-dasharray": "4 3" }));
    gg.appendChild(el("line", { stroke: "#f87171", "stroke-width": 1.6 }));
    gg.appendChild(el("path", { fill: "#f87171" }));
    gg.appendChild(el("path", { fill: "#f87171" }));
    const tx = el("text", { fill: "#fca5a5", "font-size": 11.5, "font-family": "monospace" });
    gg.appendChild(tx);
    return { g: gg, tx };
  })();
  const etiqTirante = el("text", { fill: "#fbbf24", "font-size": 12, "font-family": "monospace",
                                   "text-anchor": "middle" });
  g.gLbl.appendChild(etiqTirante);
  // caja de datos (margen derecho)
  const caja = el("g"); g.gCaja.appendChild(caja);
  const cajaTxt = [];
  (function () {
    const x = 236, y = 300, w = 208, h = 200;
    caja.appendChild(el("rect", { x, y, width: w, height: h, rx: 8, fill: "#0e1729",
                                  stroke: "#25344f", "stroke-width": 1 }));
    for (let i = 0; i < 7; i++) {
      cajaTxt.push(el("text", { x: x + 12, y: y + 24 + i * 20, fill: "#9fb3d1", "font-size": 11,
                                "font-family": "monospace" }));
      caja.appendChild(cajaTxt[i]);
    }
    const grad = el("linearGradient", { id: "gradN", x1: "0", x2: "1" });
    grad.appendChild(el("stop", { offset: "0", "stop-color": "hsl(199,90%,60%)" }));
    grad.appendChild(el("stop", { offset: "1", "stop-color": "hsl(2,85%,52%)" }));
    const defs = el("defs"); defs.appendChild(grad); svg.appendChild(defs);
    caja.appendChild(el("rect", { x: x + 12, y: y + h - 22, width: w - 24, height: 7, rx: 3,
                                  fill: "url(#gradN)" }));
    caja.appendChild(el("text", { x: x + 12, y: y + h - 27, fill: "#6b81a3", "font-size": 9.5 },
                         "tracción"));
    caja.appendChild(el("text", { x: x + w - 12, y: y + h - 27, fill: "#6b81a3", "font-size": 9.5,
                                  "text-anchor": "end" }, "compresión"));
  })();

  /* ---------------------------------------------------------------- render */
  function campo(caso, i) {
    const osc = RES.oscilacion && RES.oscilacion[caso], p = est.prog;
    if (!osc) { const d = RES.casos[caso].nodos[i]; return { u: d.u * p, v: d.v * p }; }
    const gr = osc.grav[i], l = osc.lat[i];
    const fl = 1 + (est.osc ? 0.85 * Math.sin(2 * Math.PI * est.t / 1.7) : 0);
    return { u: (gr.u + l.u * fl) * p, v: (gr.v + l.v * fl) * p };
  }
  const colorN = (n, nmax) => {
    const t = Math.min(1, Math.abs(n) / nmax), L = 74 - 26 * t, S = 55 + 40 * t;
    return n < 0 ? `hsl(2,${S}%,${L}%)` : `hsl(199,${S}%,${L}%)`;
  };

  function render() {
    const caso = est.caso, res = RES.casos[caso], mod = M.casos[caso];
    const axial = res.axial, nmax = Math.max(1, ...Object.values(axial).map(Math.abs));
    const disp = M.nodos.map((n, i) => campo(caso, i));
    const p = (i) => pos(i, disp[i]);
    const hayTirante = axial[String(M.elementos.findIndex((e) => e.n === "tirante de cabeza"))] !== undefined;

    M.elementos.forEach((e, i) => {
      const [x1, y1] = p(e.a), [x2, y2] = p(e.b), L = lineas[i], N = axial[String(i)];
      L.e.setAttribute("x1", x1); L.e.setAttribute("y1", y1);
      L.e.setAttribute("x2", x2); L.e.setAttribute("y2", y2);
      const esTirante = e.n === "tirante de cabeza";
      if (N === undefined && esTirante) {
        L.e.setAttribute("stroke", "#42506b"); L.e.setAttribute("stroke-width", 1.4);
        L.e.setAttribute("stroke-dasharray", "6 6");
      } else {
        L.e.removeAttribute("stroke-dasharray");
        const t = Math.min(1, Math.abs(N) / nmax);
        L.e.setAttribute("stroke", est.axial ? (esTirante ? "#fbbf24" : colorN(N, nmax)) : "#cbd5e1");
        L.e.setAttribute("stroke-width", (esTirante ? 3.2 : 1.4 + 3.6 * t).toFixed(2));
      }
      if (est.prog <= 0.02) { L.e.setAttribute("stroke", "#2b3853"); L.e.setAttribute("stroke-width", 1.4); }
    });
    M.nodos.forEach((n, i) => {
      const [x, y] = p(i);
      puntos[i].setAttribute("cx", x); puntos[i].setAttribute("cy", y);
      puntos[i].setAttribute("fill", idx[i].y === 0 ? "none" : "#8ea4c8");
    });
    // rótulo del tirante
    const iTir = M.elementos.findIndex((e) => e.n === "tirante de cabeza");
    const NT = axial[String(iTir)];
    if (NT !== undefined) {
      const a = p(M.elementos[iTir].a), b = p(M.elementos[iTir].b);
      etiqTirante.setAttribute("x", (a[0] + b[0]) / 2);
      etiqTirante.setAttribute("y", a[1] + 22);
      etiqTirante.textContent = `tirante Ø1-1/2″   T = ${(NT / 1000).toFixed(2)} t`;
    } else {
      etiqTirante.setAttribute("x", PX(8.8)); etiqTirante.setAttribute("y", PY(8.5) + 22);
      etiqTirante.textContent = "SIN tirante de cabeza";
    }
    // cargas verticales
    const Fv = mod.Fv, maxF = Math.max(1, ...Object.values(Fv).map(Math.abs));
    flechasV.forEach((fch, j) => {
      const lista = j < 9 ? NODOS_E : NODOS_I, i = lista[j % 9];
      const val = Fv[M.nodos[i].n];
      if (!est.cargas || val === undefined || !val) { fch.g.setAttribute("opacity", 0); return; }
      const [x, y] = p(i), len = 13 + 30 * Math.abs(val) / maxF, pas = j >= 9;
      const col = pas ? "#60a5fa" : "#eab308";
      fch.g.setAttribute("opacity", Math.min(1, est.prog * 1.8));
      fch.l.setAttribute("x1", x); fch.l.setAttribute("y1", y - len);
      fch.l.setAttribute("x2", x); fch.l.setAttribute("y2", y - 3);
      fch.l.setAttribute("stroke", col);
      fch.t.setAttribute("d", `M${x - 4},${y - 9} L${x},${y - 1} L${x + 4},${y - 9} Z`);
      fch.t.setAttribute("fill", col);
    });
    // sismo
    const hay = !!(mod.Fh && Object.keys(mod.Fh).length);
    flechasH.forEach((fch, j) => {
      if (!hay || !est.cargas) { fch.g.setAttribute("opacity", 0); return; }
      const iN = j === 0 ? NOM["top_i"] : NOM["top_d"];
      const [x, y] = p(iN), yf = y + 12;
      fch.g.setAttribute("opacity", Math.min(1, est.prog * 1.8));
      fch.l.setAttribute("x1", x - 6); fch.l.setAttribute("y1", yf);
      fch.l.setAttribute("x2", x + 56); fch.l.setAttribute("y2", yf);
      fch.t.setAttribute("d", `M${x + 50},${yf - 5} L${x + 58},${yf} L${x + 50},${yf + 5} Z`);
      fch.tx.setAttribute("x", x + 6); fch.tx.setAttribute("y", yf + 16);
      fch.tx.textContent = `V = ${(mod.Fh.top_i / 1000).toFixed(2)} t`;
    });
    // deriva
    const nT = NOM["top_i"], uT = disp[nT].u;
    if (est.prog > 0.03 && Math.abs(uT) > 0.02) {
      const [x0, y0] = pos(nT, null), [xd] = p(nT);
      const yD = y0 + 44, s = xd - x0;
      deriva.g.setAttribute("opacity", 1);
      const ln = deriva.g.children[0], la = deriva.g.children[1], t1 = deriva.g.children[2],
            t2 = deriva.g.children[3];
      ln.setAttribute("x1", x0); ln.setAttribute("y1", y0 + 6); ln.setAttribute("x2", x0); ln.setAttribute("y2", yD + 6);
      la.setAttribute("x1", Math.min(x0, xd) - 6); la.setAttribute("y1", yD);
      la.setAttribute("x2", Math.max(x0, xd) + 6); la.setAttribute("y2", yD);
      t1.setAttribute("d", `M${Math.min(x0, xd) - 6 + 8},${yD - 5} L${Math.min(x0, xd) - 6},${yD} L${Math.min(x0, xd) - 6 + 8},${yD + 5} Z`);
      t2.setAttribute("d", `M${Math.max(x0, xd) + 6 - 8},${yD - 5} L${Math.max(x0, xd) + 6},${yD} L${Math.max(x0, xd) + 6 - 8},${yD + 5} Z`);
      const real = Math.abs(RES.casos[caso].nodos[nT].u);
      deriva.tx.textContent = `Δ = ${real.toFixed(2)} cm`;
      deriva.tx.setAttribute("x", Math.max(x0, xd) + 12);
      deriva.tx.setAttribute("y", yD + 18);
      deriva.tx.setAttribute("text-anchor", "start");
    } else deriva.g.setAttribute("opacity", 0);
    // momentos en pilares
    g.gMom.innerHTML = "";
    if (est.mom && est.prog > 0.4) {
      const Mm = Math.max(1, ...Object.values(res.momento).map(Math.abs));
      M.elementos.forEach((e, i) => {
        if (e.n.indexOf("pilar") < 0) return;
        const [x1, y1] = p(e.a), [x2, y2] = p(e.b);
        const m1 = res.momento[String(i)], m2 = res.momento2[String(i)] || 0;
        const s = e.n.indexOf("izq") > 0 ? 1 : -1, a = 36 / Mm;
        g.gMom.appendChild(el("path", {
          d: `M${x1},${y1} L${x1 + s * m1 * a},${y1} L${x2 + s * m2 * a},${y2} L${x2},${y2} Z`,
          fill: "rgba(251,191,36,.20)", stroke: "#fbbf24", "stroke-width": 1.1 }));
        g.gMom.appendChild(el("text", { x: x1 + s * 14, y: y1 + (y2 > y1 ? -8 : 8), fill: "#fbbf24",
                                        "font-size": 11, "font-family": "monospace",
                                        "text-anchor": s > 0 ? "start" : "end" },
          `M = ${(m1 / 1000).toFixed(2)} t·m`));
      });
    }
    // caja de datos
    cajaTxt[0].textContent = "CASO: " + ETIQ[caso];
    cajaTxt[1].textContent = `q techo  = ${mod.q_techo.toFixed(0)} kg/m`;
    cajaTxt[2].textContent = `q pasarela = ${mod.q_pas.toFixed(0)} kg/m`;
    cajaTxt[3].textContent = `PP real   = 135 kg/m`;
    cajaTxt[4].textContent = `(planilla = 60 kg/m)`;
    cajaTxt[5].textContent = `|N| máx   = ${(nmax / 1000).toFixed(2)} t`;
    cajaTxt[6].textContent = hayTirante
      ? `T tirante = ${(axial[String(iTir)] / 1000).toFixed(2)} t` : "tirante   = NO EXISTE";
    pintarPanel();
  }

  /* ---------------------------------------------------------------- panel HTML */
  const barraDC = (v) => {
    const c = v < 0.85 ? "#34d399" : v < 1 ? "#fbbf24" : "#ef4444";
    return `<div class="dc"><i style="width:${Math.min(100, v * 100)}%;background:${c}"></i></div>`;
  };
  function pintarPanel() {
    const caso = est.caso, r = RES.casos[caso], d = r.dc, lim = r.deriva_lim;
    document.getElementById("tituloCaso").innerHTML =
      `<b style="color:var(--tx)">${ETIQ[caso]}</b> — ${r.label}`;
    const badge = r.deriva_ok ? `<span class="badge ok">cumple</span>`
                              : `<span class="badge no">NO cumple</span>`;
    const kpi = (lab, val, sub, cls) =>
      `<div class="kpi ${cls || ""}"><div class="lab">${lab}</div><div class="val">${val}</div>
       <div class="sub">${sub || ""}</div></div>`;
    const cuM = REF_R[caso] ? (ref.M_base_cantil[REF_R[caso]] / 1000).toFixed(2) + " t·m" : "—";
    document.getElementById("kpis").innerHTML =
      kpi("Tirante de cabeza",
          r.tirante_N ? (r.tirante_N / 1000).toFixed(2) + " t" : "sin tirante",
          `D/C ${d.tirante.toFixed(3)} · cuaderno ${(ref.tirante_T_u / 1000).toFixed(2)} t (D/C ${ref.tirante_dc.toFixed(3)})`) +
      kpi("Empuje H en el pilar", (r.V_base / 1000).toFixed(2) + " t",
          `D/C pilar ${d.pilar.toFixed(3)}`) +
      kpi("M en la base del pilar", (r.M_base / 1000).toFixed(2) + " t·m",
          `cuaderno: ${cuM}`) +
      kpi("Deriva Δ en la cabeza", r.deriva.toFixed(2) + " cm",
          `Cd·Δ = ${r.deriva_amplificada.toFixed(2)} cm ≤ ${lim} cm`) +
      kpi("Axial en el pilar", (r.N_pilar / 1000).toFixed(2) + " t",
          `2 pilares = ${(2 * r.N_pilar / 1000).toFixed(1)} t`) +
      kpi("q total del pórtico", (r.q_total + r.peso_propio / 17.6).toFixed(0) + " kg/m",
          `PP real ${(r.peso_propio / 17.6).toFixed(0)} kg/m`) +
      `<div class="kpi ancho"><div class="lab">Semáforo de deriva (COVENIN 1756‑1:2019 §9.4)</div>
        <div class="val">${badge} <span class="sub">Cd·Δ = ${r.deriva_amplificada.toFixed(2)} cm
        contra ${lim} cm</span></div></div>`;
    const cu = (v) => v == null ? "—" : v.toFixed(3);
    const filas = [
      ["Cordón 2×IPE 160", d.cordon, ref.dc_cordon],
      ["Diagonal IPE 160", d.diagonal, ref.dc_diagonal],
      ["Montante IPE 120", d.montante, ref.dc_montante],
      ["Tirante Ø1-1/2″", d.tirante, ref.tirante_dc],
      ["Pilar HEB 300", d.pilar, REF_R[caso] === 6 ? ref.dc_columna[6]
        : REF_R[caso] === 2 ? ref.dc_columna[2]
        : REF_R[caso] === "sin" ? ref.dc_columna_sin_tirante : null],
    ];
    document.querySelector("#tablaDC tbody").innerHTML = filas.map(([nom, a, b]) =>
      `<tr><td>${nom}${barraDC(a)}</td><td class="n" style="color:${a < 1 ? "#34d399" : "#f87171"}">
        ${a.toFixed(3)}</td><td class="n" style="color:var(--tx3)">${cu(b)}</td></tr>`).join("");
    const notas = {
      servicio: "Combinación de servicio (sin mayorar): sirve para flechas, asentamientos y peso sísmico. El tirante toma 8,48 t.",
      mayorada: "Combinación de rotura 1,2D + 1,6L. El tirante toma 12,18 t (D/C 0,47 frente a 0,546 del cuaderno): cordones y diagonales van holgados.",
      sismo_R6: "R = 6 (planilla original, pórticos ND3). La deriva amplificada 7,48 cm queda por debajo del límite de 17 cm.",
      sismo_R2: "R = 2 — hipótesis adoptada por el proyecto (Tipo IV, §3.5.4). La deriva amplificada 24,53 cm supera los 17 cm: <b>NO CUMPLE</b>. Es la misma bandera roja del cuaderno.",
      sin_tirante: "Sin tirante la cercha pierde la acción de arco y trabaja como viga curva: el cordón superior llega a −45,1 t (D/C 1,11 ✗). El pilar sólo recibe 0,36 t porque el arco se abre. Ver AUDITORIA.md §5.3.",
    };
    document.getElementById("notas").innerHTML =
      `<div class="nota ${caso === "sismo_R2" || caso === "sin_tirante" ? "alerta" : ""}">${notas[caso]}</div>`;
  }

  /* ---------------------------------------------------------------- UI */
  const chips = document.getElementById("chips");
  CASOS.forEach((c) => {
    const b = document.createElement("button");
    b.className = "chip" + (c === est.caso ? " on" : "");
    b.textContent = ETIQ[c];
    b.onclick = () => {
      est.caso = c; est.prog = 0; est.osc = false; est.t = 0;
      [...chips.children].forEach((x) => x.classList.remove("on"));
      b.classList.add("on");
      document.getElementById("btnOsc").style.display = (RES.oscilacion || {})[c] ? "" : "none";
      animar();
    };
    chips.appendChild(b);
  });
  let raf = null, t0 = 0;
  function animar() {
    cancelAnimationFrame(raf);
    const arranca = est.prog;
    t0 = performance.now();
    const paso = (now) => {
      const q = Math.min(1, (now - t0) / 1700);
      est.prog = arranca + (1 - arranca) * (1 - Math.pow(1 - q, 3));
      if (now - t0 > 1700 && (RES.oscilacion || {})[est.caso]) est.osc = true;
      if (est.osc) est.t += 1 / 60;
      render();
      if (est.prog < 0.999 || est.osc) raf = requestAnimationFrame(paso);
    };
    raf = requestAnimationFrame(paso);
  }
  document.getElementById("btnPlay").onclick = () => { est.prog = 0; est.osc = false; est.t = 0; animar(); };
  document.getElementById("btnReset").onclick = () => {
    cancelAnimationFrame(raf); est.prog = 0; est.osc = false; est.t = 0; render();
  };
  document.getElementById("btnOsc").onclick = () => {
    est.osc = !est.osc; est.t = 0;
    if (est.osc) { est.prog = 1; animar(); } else render();
  };
  document.getElementById("escala").oninput = (e) => {
    est.escala = +e.target.value;
    document.getElementById("escLab").textContent = est.escala;
    document.getElementById("escLab2").textContent = est.escala;
    render();
  };
  document.getElementById("ckCargas").onchange = (e) => { est.cargas = e.target.checked; render(); };
  document.getElementById("ckAxial").onchange = (e) => { est.axial = e.target.checked; render(); };
  document.getElementById("ckMom").onchange = (e) => { est.mom = e.target.checked; render(); };
  render();
  animar();
})();
