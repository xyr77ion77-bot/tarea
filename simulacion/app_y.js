/* Visor del nivel Y (dirección longitudinal): elevación de UNA fachada arriostrada
   (7 pilares HEB 300 sobre su eje débil, cruces HEB 200 en los 6 vanos), comparación
   R = 4,5 (Tabla 15) contra R = 2, y diafragma rígido contra flexible.
   Todos los números salen de eje_y.py (resultados_y.json / datos_y.js). */
(function () {
  const Y = window.EJEY;
  if (!Y) { console.warn("faltan datos del eje Y"); return; }
  const NS = "http://www.w3.org/2000/svg";
  const el = (t, a, txt) => {
    const e = document.createElementNS(NS, t);
    for (const k in a) e.setAttribute(k, a[k]);
    if (txt != null) e.textContent = txt;
    return e;
  };
  const fmt = (x, d) => Number(x).toLocaleString("es-VE",
    { minimumFractionDigits: d == null ? 2 : d, maximumFractionDigits: d == null ? 2 : d });
  const varPct = (r) => r < 1 ? fmt(100 * (1 - r), 1) + " % menos" : fmt(100 * (r - 1), 1) + " % más";

  const claveR = (R) => (Number(R) === 2 ? "2.0" : String(R));   // claves en datos_y.js
  let diaf = "flexible";                 // hipótesis de diafragma activa
  let corriendo = true, fase = 0, ultimo = null;
  const VEL = () => parseFloat(document.getElementById("velY").value);

  const bloque = () => Y.diafragmas[diaf];
  const nodosM = () => bloque().nodos.map((n) => ({ x: n.x / 100, y: n.y / 100, n: n.n }));

  const proy = (W, H, x0, x1, y0, y1, pad) => {
    const k = Math.min((W - pad.l - pad.r) / (x1 - x0), (H - pad.t - pad.b) / (y1 - y0));
    return { k, X: (x) => pad.l + (x - x0) * k, Y: (y) => H - pad.b - (y - y0) * k };
  };

  /* ------------------------------------------------ escena de fachada (animada) */
  function escena(svgId, R) {
    const svg = document.getElementById(svgId);
    if (!svg) return null;
    const W = 1000, H = 330;
    const P = proy(W, H, -2.2, 27.0, -1.8, 11.4, { l: 30, r: 30, t: 30, b: 40 });
    const b = bloque(), esp = b.espectro[claveR(R)], nods = nodosM();
    /* misma amplificación en los dos paneles: la fija el panel R = 2 (el mayor) */
    const AMP = 2.6 / Math.max(1e-9, b.espectro["2.0"].delta_inel / 100);
    const lab = document.getElementById("ampLabY");
    if (lab) lab.textContent = "×" + Math.round(AMP).toLocaleString("es-VE");

    function dibujar(ph) {
      const s = Math.sin(ph);
      svg.innerHTML = "";
      const pos = nods.map((n, i) => ({
        x: n.x + esp.campo_inel[i].u / 100 * AMP * s,
        y: n.y + esp.campo_inel[i].v / 100 * AMP * s,
      }));
      /* terreno y zapatas */
      const y0 = P.Y(0);
      svg.appendChild(el("line", { x1: P.X(-1.8), y1: y0, x2: P.X(26.4), y2: y0, stroke: "#2c3c5c", "stroke-width": 1.2 }));
      for (let x = P.X(-1.8); x < P.X(26.4); x += 13)
        svg.appendChild(el("line", { x1: x, y1: y0, x2: x - 9, y2: y0 + 10, stroke: "#24334f", "stroke-width": 1 }));
      nods.slice(0, 7).forEach((n) => {
        const p = P.X(pos[nods.indexOf(n)].x);
        svg.appendChild(el("rect", { x: p - 13, y: y0, width: 26, height: 11, fill: "#17223a", stroke: "#67809f", "stroke-width": 1.2 }));
      });
      /* contorno sin deformar (fantasma) */
      b.elementos.forEach((e) => {
        const a = nods[e.a], c = nods[e.b];
        svg.appendChild(el("line", { x1: P.X(a.x), y1: P.Y(a.y), x2: P.X(c.x), y2: P.Y(c.y),
          stroke: "#33456b", "stroke-width": e.sec.includes("HEB 300") ? 5 : 1.4, "stroke-dasharray": "4 4", opacity: .55 }));
      });
      /* deformada: diagonales coloreadas por tracción/compresión instantánea */
      b.elementos.forEach((e) => {
        const a = pos[e.a], c = pos[e.b], o1 = nods[e.a], o2 = nods[e.b];
        let stroke = "#9fb3d1", wdt = 2;
        if (e.sec.includes("HEB 300")) { stroke = "#e6eefc"; wdt = 6; }
        else if (e.sec.includes("IPN")) { stroke = "#38bdf8"; wdt = 3.5; }
        else {
          const L0 = Math.hypot(o2.x - o1.x, o2.y - o1.y), L1 = Math.hypot(c.x - a.x, c.y - a.y);
          stroke = (L1 - L0) * s >= 0 ? "hsl(199,85%,55%)" : "hsl(2,85%,55%)";
          wdt = 2.6;
        }
        svg.appendChild(el("line", { x1: P.X(a.x), y1: P.Y(a.y), x2: P.X(c.x), y2: P.Y(c.y),
          stroke, "stroke-width": wdt, "stroke-linecap": "round" }));
      });
      nods.forEach((n, i) => {
        svg.appendChild(el("circle", { cx: P.X(pos[i].x), cy: P.Y(pos[i].y), r: i < 7 ? 0 : 3,
          fill: "#0a0f1a", stroke: "#9fb3d1", "stroke-width": 1.2 }));
      });
      /* flechas de fuerza inercial en cabezas (Γ·m·φ del modo 1) */
      const fmax = Math.max(...esp.fuerza.map((f) => Math.abs(f.F)), 1);
      esp.fuerza.forEach((f, i) => {
        if (i < 7) return;                                   // solo cabezas t0..t6
        const L = 26 * Math.abs(f.F) / fmax * s, x0 = P.X(pos[i].x), yy = P.Y(pos[i].y) - 14;
        if (Math.abs(L) < 1.5) return;
        const dir = L >= 0 ? 1 : -1;
        svg.appendChild(el("line", { x1: x0, y1: yy, x2: x0 + L, y2: yy, stroke: "#f472b6", "stroke-width": 2 }));
        svg.appendChild(el("path", { d: `M ${x0 + L} ${yy} l ${-6 * dir} -3.4 l 0 6.8 z`, fill: "#f472b6" }));
      });
      /* rótulo de deriva instantánea */
      const dmax = esp.delta_inel * s;
      svg.appendChild(el("text", { x: P.X(24.6), y: 22, "text-anchor": "end", fill: "#9fb3d1",
        "font-size": 13, "font-family": "monospace" },
        `Δ cabeza = ${fmt(Math.abs(dmax))} cm ${s >= 0 ? "→" : "←"}  (máx ${fmt(esp.delta_inel)} cm)`));
    }
    return { dibujar };
  }

  /* ------------------------------------------------ KPIs y tabla */
  function kpis(id, R) {
    const b = bloque(), e = b.espectro[claveR(R)], caja = document.getElementById(id);
    const ok = e.deriva_ok;
    const kpi = (lab, val, sub) => `<div class="kpi"><div class="lab">${lab}</div>` +
      `<div class="val">${val}</div><div class="sub">${sub || ""}</div></div>`;
    caja.innerHTML =
      kpi("Cortante por fachada V", fmt(e.V_estatico / 1000) + " t",
          `modal ${fmt(e.V_modal / 1000)} t · total edificio ${fmt(2 * e.V_estatico / 1000)} t`) +
      kpi("Ad(T₁) — espectro", fmt(e.Ad_T1, 4), e.en_meseta ? "en la meseta (T₁ < TC)" : "rama descendente") +
      kpi("Deriva de diseño Δ = Cd·δ", fmt(e.delta_inel) + " cm",
          `δ elástica ${fmt(e.delta_el, 3)} cm · límite ${fmt(Y.deriva_lim, 0)} cm ` +
          `<span class="badge ${ok ? "ok" : "no"}">${ok ? "✓ cumple" : "✗ no cumple"}</span>`) +
      kpi("Diagonal HEB 200 máx.", fmt(Math.max(e.N_diag_tension, -e.N_diag_compresion) / 1000) + " t",
          `D/C ${fmt(e.dc_diag, 3)} · pilar eje débil D/C ${fmt(e.dc_col, 3)}`);
  }

  function tabla() {
    const tb = document.querySelector("#tablaY tbody");
    const f = (diaf) => Y.diafragmas[diaf];
    const fila = (lab, fn) => `<tr><td>${lab}</td>` +
      ["rigido", "flexible"].map((d) => ["4.5", "2.0"].map((R) =>
        `<td class="n">${fn(f(d), f(d).espectro[R], R)}</td>`).join("")).join("") + "</tr>";
    tb.innerHTML =
      fila("Período fundamental T₁ (s)", (b) => fmt(b.T1, 3)) +
      fila("Masa efectiva modo 1 (%)", (b) => fmt(b.modos[0].porc, 1)) +
      fila("Rigidez de la fachada k (kg/cm)", (b, e) => fmt(e.k_solver, 0)) +
      fila("Cortante por fachada (t)", (b, e) => fmt(e.V_estatico / 1000)) +
      fila("Corte por vano arriostrado (t)", (b, e, R) => fmt(b.reparto[R].por_vano / 1000)) +
      fila("δ elástica en cabeza (cm)", (b, e) => fmt(e.delta_el, 3)) +
      fila("Δ = Cd·δ (cm) — límite 17", (b, e) =>
        `${fmt(e.delta_inel)} <span class="badge ${e.deriva_ok ? "ok" : "no"}">${e.deriva_ok ? "✓" : "✗"}</span>`) +
      fila("Diagonal máx. (t) / D/C", (b, e) =>
        `${fmt(Math.max(e.N_diag_tension, -e.N_diag_compresion) / 1000)} / ${fmt(e.dc_diag, 3)}`) +
      fila("Pilar (eje débil) M (t·m) / D/C", (b, e) => `${fmt(e.M_col)} / ${fmt(e.dc_col, 3)}`);
  }

  function notas() {
    const r = Y.diafragmas.rigido, f = Y.diafragmas.flexible;
    const dR = f.espectro["2.0"].delta_inel / r.espectro["2.0"].delta_inel;
    document.getElementById("notasY").innerHTML =
      `<div class="nota"><b>Las dos hipótesis de diafragma casi coinciden, y es por la decisión de
       arriostrar los 6 vanos:</b> con todos los vanos iguales y la masa uniforme, el reparto por vano es
       V/6 con diafragma rígido (por rigidez) y también V/6 con flexible (por área tributaria). La diferencia
       que queda es la flexibilidad axial del colector: T₁ pasa de ${fmt(r.T1, 3)} s a ${fmt(f.T1, 3)} s y la deriva
       R = 2 de ${fmt(r.espectro["2.0"].delta_inel)} cm a ${fmt(f.espectro["2.0"].delta_inel)} cm (${varPct(dR)}).
       Si los vanos extremos quedaran sin arriostrar, las dos hipótesis darían resultados muy distintos.</div>
       <div class="nota ok"><b>La dirección longitudinal no es el problema sísmico de este edificio:</b>
       con R = 2 la deriva de diseño es ${fmt(f.espectro["2.0"].delta_inel)} cm contra el límite de 17 cm,
       mientras que en el pórtico transversal (nivel B) es 29,76 cm y <b>no cumple</b>. La fachada arriostrada
       es unas ${fmt(f.espectro["2.0"].k_solver / 516, 0)} veces más rígida por fachada que el
       pórtico transversal completo (k = ${fmt(f.espectro["2.0"].k_solver, 0)} kg/cm contra 516 kg/cm).</div>
       <div class="nota"><b>Verificación:</b> la rigidez del solver se contrastó con la fórmula cerrada
       k = 6 vanos × [2·EA/L·cos²θ de la cruz] + 7 pilares eje débil en ménsula = ${fmt(Y.k_teorica, 0)} kg/cm:
       error ${fmt(r.error_k, 2)} % con diafragma rígido y ${fmt(f.error_k, 2)} % con flexible (la flexibilidad
       del colector IPN 140 es justo lo que la hipótesis flexible añade). T₁ = ${fmt(f.T1, 3)} s cae en la
       <b>meseta</b> del espectro (TC = ${fmt(Y.TC, 3)} s), así que Ad no se reduce por período en esta dirección.</div>
       <div class="nota alerta"><b>Límites de este nivel Y:</b> es una <b>elevación plana de una fachada</b> —
       no hay torsión (se suponen las dos fachadas iguales y la mitad del cortante para cada una), no se verificó
       la lámina de cubierta como diafragma ni las conexiones de las cruces (capacidad 30,1 t citada en el chat,
       sin cerrar en el cuaderno), y la capacidad a compresión de la diagonal usa su longitud total
       (λ = ${fmt(Y.capacidades.lam_diag, 0)}), sin contar la conexión en el cruce. La deriva se compara con
       el mismo límite 0,02·h = 17 cm usado en el cuaderno como referencia.</div>`;
  }

  /* ------------------------------------------------ controles y animación */
  let esc45 = null, esc2 = null;
  function reconstruir() {
    esc45 = escena("lienzoYR45", 4.5);
    esc2 = escena("lienzoYR2", 2.0);
    kpis("kpiYR45", 4.5); kpis("kpiYR2", 2.0);
    document.querySelectorAll("#chipsDia .chip").forEach((c) =>
      c.classList.toggle("on", c.dataset.d === diaf));
  }
  document.querySelectorAll("#chipsDia .chip").forEach((c) =>
    c.addEventListener("click", () => { diaf = c.dataset.d; reconstruir(); }));
  const btn = document.getElementById("btnPausaY");
  if (btn) btn.addEventListener("click", () => {
    corriendo = !corriendo;
    btn.textContent = corriendo ? "⏸ Pausar" : "▶ Reanudar";
  });

  function paso(ts) {
    if (ultimo == null) ultimo = ts;
    const dt = Math.min(0.05, (ts - ultimo) / 1000); ultimo = ts;
    if (corriendo) fase += dt * 2 * Math.PI * VEL() / bloque().T1;
    if (esc45) esc45.dibujar(fase);
    if (esc2) esc2.dibujar(fase);
    requestAnimationFrame(paso);
  }
  tabla(); notas(); reconstruir();
  requestAnimationFrame(paso);
})();
