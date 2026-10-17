# Contexto del proyecto + qué desbloquea el libro

**Proyecto:** Auditorio para la Universidad Politécnica Territorial de Barlovento «Argelia Laya» — Higuerote, Miranda.
**Origen:** export de la conversación `chat-export-1792016016949.json` (Qwen3.8-Max, 72 mensajes).
**Fecha de este documento:** 14 de octubre de 2026.

---

## 1. Contenido de `_contexto/`

| Ruta | Qué es |
|---|---|
| `fuentes/chat-export-1792016016949.json` | Export original completo (mensajes, adjuntos y URLs) |
| `fuentes/Fundaciones y Muros_cap 1.pdf` | Escaneo del libro (caps. 1–2 + arranque del 3) |
| `fuentes/Fundaciones y Muros_cap 8.pdf` | Escaneo del libro (cap. 8: fundaciones directas) |
| `chat_auditorio_higuerote.md` | El mismo chat, transcrito a texto legible y buscable (652 KB) |
| `cad/CT01.scr` | El script de AutoCAD del corte transversal, tal como lo dejó el chat |
| `cad/CT01.dxf` + `cad/CT01_preview.png` | Ese script convertido a **DXF** y su vista previa (ver §4) |
| `cad/scr_a_dxf.py` | Conversor `.scr` → `.dxf` con verificación geométrica de arcos |

El análisis de los dos PDF (OCR completo, páginas y secciones, resumen por capítulo) está en `../_analisis/ANALISIS.md`.

---

## 2. Estado del proyecto según la conversación

### 2.1 Cerrado y consistente

| Tema | Valor acordado | Dónde |
|---|---|---|
| Ubicación / uso | Higuerote (costa abierta, NE de Miranda) | — |
| Aforo de proyecto | **312 butacas** + 4 PMR + 6 staff = **322 personas** (Grupo B1, COVENIN 1756‑1:2019) | msjs. 53 y 65 |
| Geometría de cubierta | L = 17,60 m · f = 2,50 m · d = 0,80 m · R_sup = **16,738 m** · R_inf = **15,938 m** · θ = 63,437° · L_arco = **18,532 m** · α_apoyo = 31,72° | msj. 35 |
| Estructuración | 7 pórticos, S = 4,10 m, pilares h = 8,50 m, cercha de doble arco con 8 paneles (Δs = 2,317 m) | msj. 35 |
| Cargas | D = 23 kg/m² · colgadas = 15 kg/m² · L = 100 kg/m² · PP cercha+pasarela = 60 kg/m | msj. 37 |
| Combinación de gravedad | Q_u = [1,2(23+15)+1,6(100)]·4,10 + 1,2(60) = **914,96 kg/m** | msj. 37 |
| Perfiles | Cordones 2×IPE 160 · diagonales IPE 160 · montantes IPE 120 · **correas IPN 140** · pilares **HEB 300** | msjs. 35, 45, 53 |
| Reacción en apoyo | R_arco = Q_u·L/2 = 8,05 t (última) · P_s ≈ 5,51 t (servicio) | msj. 45 |
| Sismo | AA = 0,345 · AV = 0,669 · TC = 0,809 s · Ad = 0,138 · C = 0,133 · R = 2 (Tipo IV) | msjs. 1 y 53 |
| Nivel freático | **NF = 1,50 m** bajo rasante (dato municipal, Alcaldía Brión) | msjs. 26 y 45 |
| Decisión docente (final) | **Sin viento** y **fundaciones aisladas** (sin pilotes); platea sobre terreno | msj. 44 |
| Macizo de graderío | Muro de 1,5 m al fondo (última fila), descenso escalonado hasta ±0,00 en H1; sin excavación | msjs. 62–65 |
| Medios de escape | 3 salidas (1,80 + 0,90 + 0,90 = 3,60 m), recorrido máx ≈ 15 m ≤ 30 m | msj. 65 |

### 2.2 Pendiente (explícito en el chat)

1. **Sección de viento** de la memoria — quedó pendiente y luego el profesor la declaró innecesaria (msjs. 53, 44).
2. **Trayectoria del empuje del arco H = 14,2 t** — es el hueco estructural más grande. El chat lo resolvió por la vía del **tirante de cabeza Ø1‑1/2"** a cota +8,50 (que anula H en la cabeza del pilar y deja la zapata a compresión, «camino A» del msj. 45), pero **la sección de fundaciones se quedó escrita bajo ese supuesto** y el profesor todavía no aclaró las fundaciones.
3. **Momento en la base del pilar** — el chat detectó la incongruencia (msj. 1, hallazgo H1): con Kx = 2,0 y H entrando por la cabeza, M_base ≈ H·h = 14,2 × 8,5 ≈ **120 t·m**, no 23,6 t·m. **Ese momento nunca se recalculó**, y es justamente el que decide el tamaño y la excentricidad de la zapata.
4. **Acero de la zapata y planilla de fundaciones** — no existe todavía.
5. **Planos CAD** — solo CT‑01 quedó scripteado (y con el error de la línea en blanco ya diagnosticado). Faltan **P‑01** (abanico con 2 vomitorios), **CL‑01** y **P‑02**.
6. **Tarima del escenario** — el chat propuso bajarla a **+0,60 m** para que H1 vea el escenario (hallazgo H‑C, msj. 65) y espera confirmación.

---

## 3. Qué desbloquea el Capítulo 8 del libro (con páginas verificadas)

Todo lo de esta tabla está **confirmado contra el escaneo a 350–500 dpi** (no es OCR dudoso), así que ya se
puede citar con número de página en la memoria:

| Tema | Dato del libro | Pág. del libro |
|---|---|---|
| Fundación directa | apoyo en estrato a **≤ 5 m** de profundidad | 246 |
| Análisis vs. diseño | dimensiones en planta con **cargas de servicio y σ admisible**; diseño con cargas mayoradas y resistencias minoradas | 248 |
| Sismo en la base | σ_adm se puede **incrementar 33 %**; el **área traccionada ≤ 25 %** de la superficie de contacto | 248 |
| Predimensionado | **A_req = ν·P/σ_adm**; **ν = 1,15 / 1,20 / 1,30** según H ≤ 1,5 / ≤ 3 / ≤ 5 m; B redondeado por exceso, múltiplo de 5 cm | 253 |
| Peso propio + relleno | masa uniforme equivalente de **2.100 kg/m³** (concreto 2.400–2.500 y suelo 1.700–2.000) | 253 |
| Concreto pobre | capa de **10 a 15 cm**; dosificación 150–200 kg cemento/m³; excavar los últimos 20 cm antes de vaciar | 247 |
| Vigas de riostra | encadenado en dos direcciones ortogonales (obligatorio en zona sísmica); sección **25×25** (encofrada) o **40×40** (en zanja); **4 Φ 1/2″ mínimo**; estribos **Φ 3/8″** con s ≤ 30 cm y s ≤ 12 d_b | 250–251 |
| Acero de riostra | **A_s = 0,15 P_u** (para φ = 0,7) y cuantías mínimas 0,01 A_c y 0,15 A_c f_c′/f_y | 250 |
| Corte simple | **v_u = V_u/(φ B d) ≤ v_c = 0,53 √f_c′**, φ = 0,85 | 254 |
| Punzonado | **b_o = 4(b + d)** (columna cuadrada); **V_u = P_u − σ_u(b+d)²**; **v_c = 1,06 √f_c′**, φ = 0,85 | 254 |
| Altura útil inicial | **d ≥ √(M_u/(μ f_c′ B))** y luego se aumenta para corte y punzonado; en bases aisladas **manda el punzonado** | 255 |
| Aplastamiento | P_u ≤ φ(0,85 f_c′ A₁) con φ = 0,7; en la base con √(A₂/A₁) ≤ 2 | 255 |
| Prediseño exprés | **Tablas 8.2–8.6**: dimensiones, d, P_u, σ_u, M_u y acero por metro para **σ_adm = 1 / 1,5 / 2 / 2,5 / 3 kg/cm²** y f_y = 2.800 / 3.000 / 3.500 / 4.200 | 258–262 |

**Comprobación rápida con los números del proyecto** (zapata 1,20 × 1,20 × 0,40 m, como la dejó el msj. 45;
f_c′ = 210, b_col = 0,40 m, d = 0,33 m, σ_u = P_u/A = 9,05/1,44 = 6,28 t/m²):

| Verificación | Cálculo | Resultado |
|---|---|---|
| Corte simple | V_u = 6,28 × 1,20 × (0,40 − 0,33) | 0,53 t → 0,16 kg/cm² ≤ **7,68** ✔ |
| Punzonado | b_o = 4(0,40+0,33) = 2,92 m; V_u = 9,05 − 6,28(0,73)² | 5,70 t → 0,70 kg/cm² ≤ **15,36** ✔ |
| Flexión | M_u = σ_u·B·c²/2 = 6,28 × 1,20 × 0,40²/2 | 0,60 t·m → A_s = 0,53 cm² |
| Acero mínimo (§7.7) | 0,002 · b · h = 0,002 × 100 × 40 | **8 cm²/m** ⇒ gobierna el mínimo |

⇒ La zapata **pasa holgada con Ø1/2″ @ 15 cm en ambas direcciones** (8,5 cm²/m > 8,0 cm²/m) siempre que
M_base ≈ 0 (camino A, con tirante). **Si H baja al apoyo sin tirante, esta zapata no sirve**: entra
excentricidad y hay que dimensionar con las ecs. de distribución no uniforme (§6.4 del libro) y el 33 % del σ_adm.

---

## 4. CAD dentro de este entorno

El problema que rompió el script en el chat («comando M inválido») fue **una línea en blanco que partió el
bloque `-LAYER`**: en un `.scr`, línea en blanco = Enter = fin del comando.

Aquí se resolvió por la vía inmune al idioma y al cierre inesperado de comandos: **convertir el `.scr` a DXF
con `cad/scr_a_dxf.py`**. El resultado ya está generado y verificado:

- `cad/CT01.dxf` — 54 entidades en 4 capas (GRID/8, NIV/3, STRUCT/1, ARCH/4). Se abre en AutoCAD 2018 con
  **ARCHIVO ▸ ABRIR** (no hace falta `_SCRIPT`).
- `cad/CT01_preview.png` — vista previa del mismo archivo.
- Verificación geométrica automática de los arcos: extradós **R = 16,7380 m** y centro **(0, −5,738)**;
  intradós **R = 15,9381 m**, centro **(0, −5,7381)** → coincide con la corrección de la ficha (el centro
  no era (0, −8,238)).

Con este mismo script se pueden generar **P‑01** (abanico de 16 arcos, R_i = 2,00 + 0,80(i−1), recorte
|X| ≤ 7,05, 2 vomitorios) y **CL‑01** (poligonal del graderío + cotas), y quedar como `.dxf` listos para que
el arquitecto o el calcista los abran.

---

## 5. Los tres conflictos que conviene cerrar antes de tocar fundaciones

1. **H = 14,2 t: ¿lo cancela el tirante o llega a la base?** El libro (§8.1, pág. 248) es explícito: «sería
   deseable que la resultante de las cargas exteriores se halle aplicada en el baricentro de la base»; si
   hay excentricidad, la distribución NO es uniforme, y en zona sísmica el área traccionada no puede pasar
   del 25 %. Sin definir esto, el cálculo de la zapata no es cerrable.
2. **M_base del pilar.** H = 14,2 t × 8,5 m = 120 t·m frente a los 23,6 t·m con que se verificó la placa
   base. Las dos cosas no pueden ser ciertas a la vez (hallazgo H1 del chat, nunca resuelto).
3. **R sísmico = 6 → 2.** El chat ya lo corrigió a Tipo IV (R = 2) al adoptar columna en voladizo; conviene
   que eso quede escrito en la memoria con la Tabla 15 de la COVENIN 1756‑1:2019 y no como comentario suelto.

Y dos que el propio libro obliga a no olvidar: **ν = 1,15** (H = 1,20 m) y el **aumento del 33 %** del σ_adm
para la combinación con sismo, que en Higuerote es la que gobierna.

---

## 6. Siguientes pasos sugeridos

1. **Hoja de cálculo de la zapata aislada** (una por eje E1–E7, ya que la carga del pórtico es la misma):
   predimensionado con ν y σ_adm, corte simple, punzonado, aplastamiento y acero mínimo, con la numeración
   del libro (8.7, 8.11–8.22) como encabezado de cada bloque. Con los números de §3 pasa holgada, pero hay
   que dejarlo escrito para el jurado.
2. **Cerrar la trayectoria de H** (tirante sí/no) y, si va tirante, redactar su verificación como mérito
   propio (§14.4 de la COVENIN 1618‑98) más el atado entre zapatas opuestas de cada pórtico.
3. **Planos P‑01 y CL‑01 en DXF** con el conversor de `cad/` (una vez el usuario confirme aforo 312 y la
   tarima +0,60).
4. **Reemitir la ficha P‑01 con los 2 vomitorios** (COVENIN 810 §5.2.1.1.c: máximo 14 asientos por fila
   entre dos pasillos) — el chat ya dejó el diagnóstico, falta el plano.
