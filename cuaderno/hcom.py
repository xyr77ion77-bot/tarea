"""Piezas comunes del cuaderno HTML: CSS, plantillas y armado de la página."""
import calculos
import svg as _svg

R = calculos.calcular()
FIG = {k: h for k, h, _ in _svg.todas(R)}
CAP = {k: c for k, _, c in _svg.todas(R)}
num = _svg.fmt


def f(x, d=2):
    return _svg.fmt(x, d)


def ley(v):
    """Devuelve el número sin ceros sobrantes (para textos)."""
    return f"{v:g}".replace(".", ",")


# ---------------------------------------------------------------------------
# CSS (todo incrustado: el cuaderno no llama a ningún recurso externo)
# ---------------------------------------------------------------------------
CSS = """
:root{
  --ink:#111827; --sub:#4b5563; --rule:#d1d5db; --accent:#0e7490; --accent2:#0f766e;
  --ok:#15803d; --bad:#b91c1c; --warn-bg:#fffbeb; --warn-br:#f59e0b;
  --fml-bg:#f8fafc; --res-bg:#ecfdf5; --bad-bg:#fef2f2;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#eef2f6;color:var(--ink);
     font:16px/1.62 Georgia,'Times New Roman',serif}
.hoja{max-width:1060px;margin:0 auto;background:#fff;padding:44px 54px 64px;
      box-shadow:0 1px 3px rgba(15,23,42,.12)}
h1{font-size:29px;line-height:1.22;margin:0 0 6px}
h1+.sub{font-size:17px;color:var(--sub);margin:0 0 4px}
h2{font-size:21px;margin:44px 0 14px;padding:6px 0 6px 12px;border-left:5px solid var(--accent);
   background:linear-gradient(90deg,#f1f5f9,transparent 70%)}
h3{font-size:17.5px;margin:26px 0 8px}
h4{font-size:15.5px;margin:18px 0 6px;color:#1f2937}
p{margin:9px 0}
small,.small{font-size:13.5px}
.sub{color:var(--sub)}
code,.mono{font:14px/1.5 ui-monospace,SFMono-Regular,Consolas,'Liberation Mono',monospace}
a{color:#0e7490}
hr{border:0;border-top:1px solid var(--rule);margin:26px 0}
/* ---------- portada ---------- */
.portada{border-bottom:3px double var(--accent);padding-bottom:16px;margin-bottom:8px}
.portada .meta{font-size:13.5px;color:var(--sub);margin-top:10px}
.kpis{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0 4px}
.kpi{flex:1 1 160px;border:1px solid var(--rule);border-top:3px solid var(--accent);border-radius:6px;
     padding:8px 10px;background:#fbfdff}
.kpi b{display:block;font:600 17px/1.3 system-ui,-apple-system,sans-serif}
.kpi span{font-size:12.5px;color:var(--sub);font-family:system-ui,-apple-system,sans-serif}
.caja{border:1px solid var(--rule);border-radius:8px;padding:12px 16px;background:#fbfdff;margin:14px 0}
.caja.aviso{background:var(--warn-bg);border-color:#fcd34d}
.caja.aviso h4{margin-top:0}
.caja ul{margin:8px 0 4px 18px;padding:0}
.caja li{margin:5px 0}
/* ---------- pasos de cálculo ---------- */
.calc{border:1px solid var(--rule);border-radius:8px;background:#fff;margin:14px 0;overflow:hidden}
.calc>.hd{background:#f1f5f9;border-bottom:1px solid var(--rule);padding:7px 14px;
          font:600 14px/1.5 system-ui,-apple-system,sans-serif}
.calc>.hd .n{display:inline-block;min-width:64px;color:var(--accent)}
.calc>.bd{padding:10px 16px 14px}
.fml{font:14px/1.6 ui-monospace,SFMono-Regular,Consolas,monospace;background:var(--fml-bg);
     border-left:3px solid var(--accent);padding:7px 12px;margin:8px 0;overflow-x:auto;white-space:pre-wrap}
.sus{font:14px/1.6 ui-monospace,SFMono-Regular,Consolas,monospace;color:#334155;
     padding:3px 0 3px 15px;margin:2px 0 8px;overflow-x:auto;white-space:pre-wrap}
.res{font:600 15px/1.5 system-ui,-apple-system,sans-serif;background:var(--res-bg);
     border-left:3px solid var(--ok);padding:6px 12px;margin:6px 0}
.res.bad{background:var(--bad-bg);border-color:var(--bad)}
.res ul{margin:0 0 0 16px;padding:0}
.nota{font-size:13.5px;background:var(--warn-bg);border-left:3px solid var(--warn-br);
      padding:7px 12px;margin:8px 0;color:#4b5563}
.nota b{color:#92400e}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font:600 11.5px/1.7 system-ui,sans-serif;
       letter-spacing:.03em;text-transform:uppercase;vertical-align:1px}
.b-ok{background:#dcfce7;color:#166534}
.b-bad{background:#fee2e2;color:#991b1b}
.b-nt{background:#e2e8f0;color:#334155}
/* ---------- tablas ---------- */
table{width:100%;border-collapse:collapse;margin:12px 0;font:14px/1.45 system-ui,-apple-system,sans-serif}
caption{caption-side:top;text-align:left;font:600 13.5px/1.5 system-ui,sans-serif;color:#374151;padding-bottom:5px}
th,td{border:1px solid #cbd5e1;padding:5px 8px;vertical-align:top}
th{background:#f1f5f9;text-align:left;font-weight:600}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
tbody tr:nth-child(even) td{background:#fafbfc}
table.chica{font-size:13px}
tr.tot td{font-weight:600;background:#f1f5f9!important}
/* ---------- figuras ---------- */
figure{margin:16px 0;border:1px solid var(--rule);border-radius:8px;padding:10px 12px 8px;background:#fff}
figure svg{display:block;width:100%;height:auto}
figcaption{font:13px/1.5 system-ui,-apple-system,sans-serif;color:var(--sub);margin-top:6px}
figcaption b{color:var(--ink)}
/* ---------- índice ---------- */
ol.toc{columns:2;column-gap:34px;font:14.5px/1.75 system-ui,-apple-system,sans-serif;margin:8px 0 0 20px}
ol.toc a{text-decoration:none}
ol.toc a:hover{text-decoration:underline}
/* ---------- estilos internos de las figuras SVG ---------- */
.fig{background:#fff}
.fig .ln{fill:none;stroke:#1f2937;stroke-width:1.6}
.fig .ln2{fill:none;stroke:#6b7280;stroke-width:.95}
.fig .thin{fill:none;stroke:#94a3b8;stroke-width:.55}
.fig .dash{fill:none;stroke:#b45309;stroke-width:1.3;stroke-dasharray:6 4}
.fig .dim{fill:none;stroke:#0e7490;stroke-width:.8}
.fig .steel{fill:none;stroke:#1e3a8a;stroke-width:2.4}
.fig .bar{fill:none;stroke:#0f766e;stroke-width:1.5}
.fig .bar2{fill:#0f766e;stroke:#0f766e}
.fig .bolt{fill:none;stroke:#334155;stroke-width:1.1}
.fig .stirrup{fill:none;stroke:#7c3aed;stroke-width:1.1}
.fig .weld,.fig .weld2{fill:#f59e0b;stroke:#b45309;stroke-width:.9}
.fig .weld2{fill:none;stroke:#b45309;stroke-width:2.6;stroke-linecap:round}
.fig .qload{fill:none;stroke:#b91c1c;stroke-width:1}
.fig .Npar{fill:none;stroke:#b91c1c;stroke-width:1.4;stroke-dasharray:7 4}
.fig .Harrow{fill:none;stroke:#0f766e;stroke-width:1.6}
.fig .pl{fill:none;stroke:#b45309;stroke-width:1.2}
.fig .nf{fill:none;stroke:#0284c7;stroke-width:1;stroke-dasharray:9 3 2 3}
.fig .scut{fill:none;stroke:#be123c;stroke-width:1.1;stroke-dasharray:5 3}
.fig .dfc{fill:none;stroke:#1d4ed8;stroke-width:1.5}
.fig .dfcfill{fill:#dbeafe;stroke:none}
.fig .dmf{fill:none;stroke:#c2410c;stroke-width:1.5}
.fig .dmffill{fill:#ffedd5;stroke:none}
.fig .conc{fill:#e2e8f0;stroke:#334155;stroke-width:1}
.fig .poor{fill:#d6d3d1;stroke:#57534e;stroke-width:.8}
.fig .soilfill{fill:#f1f5f9;stroke:none}
.fig .placa{fill:#fde68a;stroke:#92400e;stroke-width:1}
.fig .steelbox,.fig .steelbox2{fill:#c7d2fe;stroke:#1e3a8a;stroke-width:1}
.fig .steelfill{fill:#dbeafe;stroke:#1e3a8a;stroke-width:1}
.fig .colbox{fill:#a5b4fc;stroke:#1e3a8a;stroke-width:1}
.fig .macizo{fill:#e2e8f0;stroke:#94a3b8;stroke-width:.6}
.fig .ground{fill:#f8fafc;stroke:none}
.fig .dot{fill:#111827}.fig .dot2{fill:#b91c1c}.fig .dot3{fill:#0f766e}
.fig .track{fill:#eef2f7;stroke:none}
.fig .barok{fill:#16a34a}.fig .barbad{fill:#dc2626}
.fig .lim{fill:none;stroke:#dc2626;stroke-width:1.4}
.fig .grid{fill:none;stroke:#cbd5e1;stroke-width:.8}
.fig .tx{font:11px -apple-system,system-ui,sans-serif;fill:#111827}
.fig .txs{font:9.6px -apple-system,system-ui,sans-serif;fill:#374151}
.fig .txb{font:bold 11.5px -apple-system,system-ui,sans-serif;fill:#111827}
.fig .txdim{font:9.6px -apple-system,system-ui,sans-serif;fill:#0e7490}
.fig .txnf{font:9.6px -apple-system,system-ui,sans-serif;fill:#0284c7}
.fig .txr{font:10px -apple-system,system-ui,sans-serif;fill:#b91c1c}
.fig .txdc{font:9.6px -apple-system,system-ui,sans-serif;fill:#166534}
.fig .txbad{font:bold 9.6px -apple-system,system-ui,sans-serif;fill:#b91c1c}
.fig .txlim{font:9.6px -apple-system,system-ui,sans-serif;fill:#b91c1c}
/* ---------- impresión ---------- */
@media print{
  body{background:#fff;font-size:11pt}
  .hoja{box-shadow:none;max-width:none;padding:0 12mm}
  h2{break-before:page}
  h1,h2,h3{break-after:avoid}
  .calc,figure,table,.caja{break-inside:avoid}
  a{color:inherit}
}
"""


# ---------------------------------------------------------------------------
# plantillas
# ---------------------------------------------------------------------------
def calc(n, titulo, cuerpo):
    return (f'<div class="calc"><div class="hd"><span class="n">{n}</span>{titulo}</div>'
            f'<div class="bd">{cuerpo}</div></div>')


def fml(s):
    return f'<div class="fml">{s}</div>'


def sus(s):
    return f'<div class="sus">{s}</div>'


def res(s, bad=False, ok=None):
    cls = "res bad" if bad else "res"
    extra = f' <span class="badge {"b-bad" if bad else "b-ok"}">{"no cumple" if bad else "cumple"}</span>' if ok else ""
    return f'<div class="{cls}">{s}{extra}</div>'


def nota(s):
    return f'<div class="nota">{s}</div>'


def figura(k, pie=None):
    return (f'<figure>{FIG[k]}<figcaption><b>Fig. {pie[0]}</b> — {pie[1] if pie else CAP[k]}'
            f'</figcaption></figure>')


def tabla(head, filas, caption=None, clases="", tot=False):
    th = "".join(f'<th class="{c}">{h}</th>' for h, c in head) if isinstance(head[0], tuple) \
        else "".join(f"<th>{h}</th>" for h in head)
    trs = []
    for i, fil in enumerate(filas):
        tds = []
        for j, celda in enumerate(fil):
            if isinstance(celda, tuple):
                val, cl = celda
            else:
                val, cl = celda, ""
            tds.append(f'<td class="{cl}">{val}</td>')
        trs.append(f'<tr>{"".join(tds)}</tr>')
    cap = f"<caption>{caption}</caption>" if caption else ""
    return f'<table class="{clases}">{cap}<thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'


def ok_badge(v):
    return ('<span class="badge b-ok">cumple</span>' if v
            else '<span class="badge b-bad">revisar</span>')


def page(titulo, cuerpo):
    return (f'<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{titulo}</title>\n<style>{CSS}</style>\n</head>\n<body>\n'
            f'<div class="hoja">\n{cuerpo}\n</div>\n</body>\n</html>\n')
