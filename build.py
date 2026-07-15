# -*- coding: utf-8 -*-
"""Składa samodzielne pliki HTML strony „Implant prącia" z fragmentów + CSS + szablonów."""
import json, pathlib, zipfile, html, base64, re
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent
OUT  = ROOT / 'dist'
OUT.mkdir(parents=True, exist_ok=True)

CSS = (ROOT / 'style.css').read_text(encoding='utf-8')
ZL  = 'https://www.znanylekarz.pl/anna-bonder-nowicka/urolog/warszawa'
MAIL = 'kontakt@turbourolog.pl'
PDF_PRIV = 'https://turbourolog.pl/doc/polityka_prywatnosci_i_plikow_cookies.pdf'

# ------------------------------------------------------------------
# FIGURY „PATENTOWE" (SVG inline, stroke = currentColor)
# ------------------------------------------------------------------
FIG1 = """<svg viewBox="0 0 560 500" class="fig-anim fig-hydro" role="img" aria-label="Animacja poglądowa: pompka napełnia cylindry implantu płynem ze zbiornika, co wywołuje wzwód, a następnie płyn wraca do zbiornika." xmlns="http://www.w3.org/2000/svg">
  <defs>
    <clipPath id="cylL"><rect x="150" y="96" width="44" height="264" rx="22"/></clipPath>
    <clipPath id="cylR"><rect x="206" y="96" width="44" height="264" rx="22"/></clipPath>
    <clipPath id="resC"><circle cx="452" cy="136" r="44"/></clipPath>
  </defs>

  <!-- PŁYN (pod konturami) -->
  <g style="fill: var(--ochre)">
    <g clip-path="url(#cylL)"><rect class="cyl-fluid" x="150" y="96" width="44" height="264"/></g>
    <g clip-path="url(#cylR)"><rect class="cyl-fluid" x="206" y="96" width="44" height="264"/></g>
    <g clip-path="url(#resC)"><rect class="res-fluid" x="408" y="92" width="88" height="88"/></g>
  </g>

  <!-- KONTURY -->
  <g fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
    <rect x="150" y="96" width="44" height="264" rx="22"/>
    <rect x="206" y="96" width="44" height="264" rx="22"/>
    <path d="M158 124 q14 -18 28 0" opacity=".55"/>
    <path d="M214 124 q14 -18 28 0" opacity=".55"/>
    <path d="M158 336 h28 M214 336 h28" opacity=".35"/>
    <!-- łączniki i dreny -->
    <path d="M172 360 V384"/>
    <path d="M228 360 V384"/>
    <path d="M172 384 C172 416 236 436 288 442"/>
    <path d="M228 384 C228 410 262 428 288 436"/>
    <!-- pompka -->
    <rect x="288" y="428" width="22" height="16" rx="3"/>
    <ellipse class="pump" cx="300" cy="468" rx="22" ry="26"/>
    <path d="M268 452 q-9 14 0 28" opacity=".55"/>
    <path d="M332 452 q9 14 0 28" opacity=".55"/>
    <!-- dren do zbiornika -->
    <path d="M310 430 C356 384 420 236 448 178"/>
    <!-- zbiornik -->
    <circle cx="452" cy="136" r="44"/>
    <path d="M424 162 L478 108 M416 148 L466 98 M436 172 L488 122" opacity=".45" stroke-width="1"/>
  </g>

  <!-- PRZEPŁYW PŁYNU (zbiornik -> pompka -> cylindry) -->
  <path class="flow" d="M448 178 C420 236 356 384 310 430" fill="none" stroke="var(--ochre)" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="2 16"/>

  <!-- odnośniki -->
  <g stroke="currentColor" stroke-width="1" opacity=".9">
    <path d="M96 58 L96 110 L146 132" fill="none"/>
    <path d="M118 456 L272 458" fill="none"/>
    <path d="M480 60 L462 94" fill="none"/>
  </g>
  <g fill="currentColor">
    <circle cx="146" cy="132" r="3"/>
    <circle cx="272" cy="458" r="3"/>
    <circle cx="462" cy="94" r="3"/>
  </g>
  <g fill="currentColor" font-family="'Spline Sans Mono', monospace" font-size="12.5" letter-spacing="1.5">
    <text x="24" y="36">1 / CYLINDRY<tspan x="24" dy="16" font-size="10.5" opacity=".7" letter-spacing="1">w ciałach jamistych</tspan></text>
    <text x="24" y="464">2 / POMPKA<tspan x="24" dy="16" font-size="10.5" opacity=".7" letter-spacing="1">w mosznie</tspan></text>
    <text x="536" y="36" text-anchor="end">3 / ZBIORNIK<tspan x="536" dy="16" font-size="10.5" opacity=".7" letter-spacing="1">pod mięśniami brzucha</tspan></text>
  </g>

  <!-- WSKAŹNIK STANU -->
  <g font-family="'Spline Sans Mono', monospace" font-size="13.5" font-weight="500" letter-spacing="2" text-anchor="middle">
    <text class="lbl-flaccid" x="280" y="42" fill="currentColor">&#9679; SPOCZYNEK</text>
    <text class="lbl-erect" x="280" y="42" style="fill: var(--ochre)">&#9679; WZW&Oacute;D</text>
  </g>
</svg>"""

FIG2 = """<svg viewBox="0 0 560 380" class="fig-anim fig-semi" role="img" aria-label="Animacja poglądowa: giętki pręt implantu półsztywnego unosi się do pozycji do współżycia i opada do pozycji na co dzień." xmlns="http://www.w3.org/2000/svg">
  <!-- łuk ruchu (statyczny) -->
  <g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" opacity=".4">
    <path d="M470 300 A250 250 0 0 1 452 70" stroke-width="1.3" stroke-dasharray="5 7"/>
    <path d="M452 70 l-2 14 M452 70 l12 6" stroke-width="1.3"/>
  </g>

  <!-- mocowanie (statyczne) -->
  <rect x="64" y="178" width="20" height="48" rx="5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- RUCHOMY PRĘT -->
  <g class="rod-move" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
    <path d="M84 206 C220 214 340 236 462 296" stroke-width="22" opacity=".13"/>
    <path d="M86 196 C220 204 338 226 456 286" stroke-width="1.7"/>
    <path d="M86 216 C220 224 342 246 464 306" stroke-width="1.7"/>
    <path d="M456 286 q13 9 8 20" stroke-width="1.7"/>
    <path d="M84 206 C220 214 340 236 462 296" stroke-width="1.1" stroke-dasharray="11 6 2 6" opacity=".55"/>
  </g>

  <!-- odnośnik -->
  <g stroke="currentColor" stroke-width="1" opacity=".9" fill="none">
    <path d="M118 330 L232 250"/>
  </g>
  <g fill="currentColor"><circle cx="232" cy="250" r="3"/></g>

  <g fill="currentColor" font-family="'Spline Sans Mono', monospace" font-size="12.5" letter-spacing="1.5">
    <text x="24" y="350">1 / GIĘTKI RDZEŃ<tspan x="24" dy="16" font-size="10.5" opacity=".7" letter-spacing="1">w powłoce hydrofilowej</tspan></text>
  </g>

  <!-- WSKAŹNIK STANU -->
  <g font-family="'Spline Sans Mono', monospace" font-size="13.5" font-weight="500" letter-spacing="2" text-anchor="middle">
    <text class="lbl-flaccid" x="300" y="40" fill="currentColor">&#9679; NA CO DZIEŃ</text>
    <text class="lbl-erect" x="300" y="40" style="fill: var(--ochre)">&#9679; DO WSP&Oacute;ŁŻYCIA</text>
  </g>
</svg>"""

# ------------------------------------------------------------------
# PIĘĆ WARIANTÓW ANATOMICZNYCH FIG.1 (do wyboru)
# każdy używa tych samych klas animacji: cyl-fluid / res-fluid / pump / flow / lbl-*
# ------------------------------------------------------------------
# --- tokeny rozmiarów etykiet figur (jednostki SVG; wspólne dla FIG_AE, FIG2, wariantów) ---
LAB_MAIN_FS = 19    # główna linia etykiety, np. „1 / CYLINDER"
LAB_SUB_FS  = 15    # podpis, np. „w ciele jamistym"
LAB_SUB_DY  = 18    # odstęp podpisu pod główną linią
STATE_FS    = 19    # etykieta stanu SPOCZYNEK / WZWÓD

_STATE = (f'<g font-family="\'Spline Sans Mono\',monospace" font-size="{STATE_FS}" font-weight="600" '
          'letter-spacing="1.6" text-anchor="middle">'
          '<text class="lbl-flaccid" x="{x}" y="{y}" fill="currentColor">&#9679; SPOCZYNEK</text>'
          '<text class="lbl-erect" x="{x}" y="{y}" style="fill: var(--ochre)">&#9679; WZW&Oacute;D</text></g>')

def _lab(x, y, n, t, sub, anchor='start'):
    sub_line = (f'<text x="{x}" y="{y+LAB_SUB_DY}" font-size="{LAB_SUB_FS}" opacity=".72" letter-spacing=".6">{sub}</text>') if sub else ''
    return (f'<g font-family="\'Spline Sans Mono\',monospace" fill="currentColor" text-anchor="{anchor}">'
            f'<text x="{x}" y="{y}" font-size="{LAB_MAIN_FS}" font-weight="600" letter-spacing="1.2">{n} / {t}</text>'
            f'{sub_line}</g>')

# ---- WARIANT A: przekrój boczny (prącie poziomo) ----
VAR_A = f"""<svg viewBox="0 0 480 430" class="fig-anim fig-hydro" role="img" aria-label="Wariant A: przekrój boczny. Cylindry w prąciu, pompka w mosznie, zbiornik w miednicy.">
  <defs>
    <clipPath id="a_cyt"><rect x="176" y="190" width="244" height="28" rx="14"/></clipPath>
    <clipPath id="a_cyb"><rect x="176" y="226" width="244" height="28" rx="14"/></clipPath>
    <clipPath id="a_res"><circle cx="104" cy="126" r="38"/></clipPath>
  </defs>
  <g fill="none" stroke="currentColor" stroke-width="1.2" opacity=".26" stroke-linecap="round" stroke-linejoin="round">
    <path d="M64 26 C50 118 56 196 128 236"/>
    <path d="M150 210 C150 250 156 268 160 286"/>
  </g>
  <g style="fill: var(--ochre)">
    <g clip-path="url(#a_cyt)"><rect class="cyl-fluid dir-right" x="176" y="190" width="244" height="28"/></g>
    <g clip-path="url(#a_cyb)"><rect class="cyl-fluid dir-right" x="176" y="226" width="244" height="28"/></g>
    <g clip-path="url(#a_res)"><rect class="res-fluid" x="66" y="88" width="76" height="76"/></g>
  </g>
  <g fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
    <rect x="176" y="190" width="244" height="28" rx="14"/>
    <rect x="176" y="226" width="244" height="28" rx="14"/>
    <circle cx="104" cy="126" r="38"/>
    <path d="M82 146 L128 100 M76 132 L116 94 M92 154 L134 112" opacity=".4" stroke-width="1"/>
    <path d="M160 266 C122 274 116 342 156 372 C186 394 236 390 256 356 C276 322 258 276 220 268 Z" stroke-width="1.6"/>
    <rect x="196" y="284" width="20" height="14" rx="3"/>
    <ellipse class="pump" cx="206" cy="328" rx="20" ry="24"/>
    <path d="M188 254 C184 266 192 278 200 284"/>
    <path d="M212 254 C216 266 212 278 212 284"/>
    <path d="M118 160 C150 224 176 282 196 310"/>
  </g>
  <path class="flow" d="M118 160 C150 224 176 282 196 310" fill="none" stroke="var(--ochre)" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="2 15"/>
  <g stroke="currentColor" stroke-width="1" opacity=".85" fill="none">
    <path d="M300 150 L300 200"/><path d="M104 60 L104 84"/><path d="M300 300 L240 330"/>
  </g>
  <g fill="currentColor"><circle cx="300" cy="200" r="2.6"/><circle cx="104" cy="86" r="2.6"/><circle cx="240" cy="330" r="2.6"/></g>
  {_lab(272,132,'1','CYLINDRY','w prąciu','middle')}
  {_lab(104,52,'3','ZBIORNIK','w miednicy','middle')}
  {_lab(316,306,'2','POMPKA','w mosznie','start')}
  {_STATE.format(x=330,y=40)}
</svg>"""

# ---- WARIANT B: sylwetka frontalna wypełniona, prącie w górę ----
VAR_B = f"""<svg viewBox="0 0 400 470" class="fig-anim fig-hydro" role="img" aria-label="Wariant B: widok od przodu z sylwetką ciała. Cylindry we wzniesionym prąciu, pompka w mosznie, zbiornik w miednicy.">
  <defs>
    <clipPath id="b_cyl"><rect x="168" y="96" width="64" height="212" rx="30"/></clipPath>
    <clipPath id="b_res"><circle cx="300" cy="336" r="32"/></clipPath>
  </defs>
  <path d="M120 300 C120 250 150 244 168 242 L168 128 C168 96 232 96 232 128 L232 242 C250 244 280 250 280 300 C300 306 312 356 286 388 C300 404 296 436 262 440 C246 456 210 456 200 438 C190 456 154 456 138 440 C104 436 100 404 114 388 C88 356 100 306 120 300 Z"
        fill="var(--paper-3)" stroke="none" opacity=".85"/>
  <g style="fill: var(--ochre)">
    <g clip-path="url(#b_cyl)"><rect class="cyl-fluid" x="168" y="96" width="30" height="212"/></g>
    <g clip-path="url(#b_cyl)"><rect class="cyl-fluid" x="202" y="96" width="30" height="212"/></g>
    <g clip-path="url(#b_res)"><rect class="res-fluid" x="268" y="304" width="64" height="64"/></g>
  </g>
  <g fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
    <rect x="168" y="96" width="30" height="212" rx="15"/>
    <rect x="202" y="96" width="30" height="212" rx="15"/>
    <circle cx="300" cy="336" r="32"/>
    <path d="M280 352 L322 310 M276 340 L312 304 M288 358 L326 320" opacity=".4" stroke-width="1"/>
    <path d="M150 360 C120 372 122 418 156 432 C182 444 218 444 244 432 C278 418 280 372 250 360" stroke-width="1.6"/>
    <ellipse class="pump" cx="200" cy="398" rx="22" ry="26"/>
    <path d="M186 308 C182 330 190 350 196 366"/>
    <path d="M214 308 C218 330 210 350 204 366"/>
    <path d="M282 352 C250 372 224 384 214 392"/>
  </g>
  <path class="flow" d="M282 352 C250 372 224 384 214 392" fill="none" stroke="var(--ochre)" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="2 15"/>
  {_lab(120,150,'1','CYLINDRY','w prąciu','start')}
  {_lab(320,300,'3','ZBIORNIK','w miednicy','start')}
  {_lab(60,404,'2','POMPKA','w mosznie','start')}
  {_STATE.format(x=200,y=44)}
</svg>"""

# ---- WARIANT C: schemat + wyraźny worek moszny (minimalna poprawka) ----
VAR_C = f"""<svg viewBox="0 0 460 430" class="fig-anim fig-hydro" role="img" aria-label="Wariant C: schemat z wyraźnym workiem mosznowym. Cylindry, pompka w mosznie, zbiornik.">
  <defs>
    <clipPath id="c_cyL"><rect x="150" y="90" width="40" height="248" rx="20"/></clipPath>
    <clipPath id="c_cyR"><rect x="204" y="90" width="40" height="248" rx="20"/></clipPath>
    <clipPath id="c_res"><circle cx="400" cy="120" r="40"/></clipPath>
  </defs>
  <g style="fill: var(--ochre)">
    <g clip-path="url(#c_cyL)"><rect class="cyl-fluid" x="150" y="90" width="40" height="248"/></g>
    <g clip-path="url(#c_cyR)"><rect class="cyl-fluid" x="204" y="90" width="40" height="248"/></g>
    <g clip-path="url(#c_res)"><rect class="res-fluid" x="360" y="80" width="80" height="80"/></g>
  </g>
  <g fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
    <rect x="150" y="90" width="40" height="248" rx="20"/>
    <rect x="204" y="90" width="40" height="248" rx="20"/>
    <circle cx="400" cy="120" r="40"/>
    <path d="M378 142 L426 94 M372 128 L414 88 M388 150 L430 108" opacity=".4" stroke-width="1"/>
    <path d="M150 350 C104 360 96 410 128 396" opacity="0"/>
    <path d="M166 344 C120 356 110 418 152 402 C150 430 210 442 228 414 C250 442 306 420 296 388 C330 372 322 320 280 336 C300 300 236 300 236 336 C230 320 176 320 174 348 Z" stroke-width="1.6"/>
    <ellipse class="pump" cx="212" cy="384" rx="24" ry="28"/>
    <path d="M170 338 C168 352 176 366 190 372"/>
    <path d="M224 338 C226 354 220 366 214 372"/>
    <path d="M368 150 C320 250 270 330 250 360"/>
  </g>
  <path class="flow" d="M368 150 C320 250 270 330 250 360" fill="none" stroke="var(--ochre)" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="2 15"/>
  {_lab(120,60,'1','CYLINDRY','w prąciu','start')}
  {_lab(400,50,'3','ZBIORNIK','w miednicy','middle')}
  {_lab(300,404,'2','MOSZNA','z pompką','start')}
  {_STATE.format(x=230,y=42)}
</svg>"""

# ---- WARIANT D: kontur ciała (ghost, przerywany) ----
VAR_D = f"""<svg viewBox="0 0 440 450" class="fig-anim fig-hydro" role="img" aria-label="Wariant D: przerywany kontur anatomii z implantem w środku.">
  <defs>
    <clipPath id="d_cyL"><rect x="176" y="100" width="30" height="190" rx="15"/></clipPath>
    <clipPath id="d_cyR"><rect x="210" y="100" width="30" height="190" rx="15"/></clipPath>
    <clipPath id="d_res"><circle cx="320" cy="250" r="32"/></clipPath>
  </defs>
  <path d="M168 292 L168 138 A40 40 0 0 1 248 138 L248 292 C284 306 292 372 256 402 C232 424 184 424 160 402 C124 372 132 306 168 292 Z"
        fill="none" stroke="currentColor" stroke-width="1.4" stroke-dasharray="5 6" opacity=".33"/>
  <g style="fill: var(--ochre)">
    <g clip-path="url(#d_cyL)"><rect class="cyl-fluid" x="176" y="100" width="30" height="190"/></g>
    <g clip-path="url(#d_cyR)"><rect class="cyl-fluid" x="210" y="100" width="30" height="190"/></g>
    <g clip-path="url(#d_res)"><rect class="res-fluid" x="288" y="218" width="64" height="64"/></g>
  </g>
  <g fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
    <rect x="176" y="100" width="30" height="190" rx="15"/>
    <rect x="210" y="100" width="30" height="190" rx="15"/>
    <circle cx="320" cy="250" r="32"/>
    <path d="M300 266 L342 224 M296 254 L332 218" opacity=".4" stroke-width="1"/>
    <ellipse class="pump" cx="208" cy="360" rx="22" ry="26"/>
    <path d="M192 290 C188 314 196 334 200 344"/>
    <path d="M224 290 C228 314 220 334 216 344"/>
    <path d="M302 266 C270 300 236 332 222 348"/>
  </g>
  <path class="flow" d="M302 266 C270 300 236 332 222 348" fill="none" stroke="var(--ochre)" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="2 15"/>
  {_lab(120,150,'1','CYLINDRY','w prąciu','start')}
  {_lab(340,214,'3','ZBIORNIK','w miednicy','start')}
  {_lab(60,366,'2','POMPKA','w mosznie','start')}
  {_STATE.format(x=208,y=44)}
</svg>"""

# ---- WARIANT E: jeden ciągły kontur (ikoniczny) ----
VAR_E = f"""<svg viewBox="0 0 420 450" class="fig-anim fig-hydro" role="img" aria-label="Wariant E: jeden ciągły kontur ciała, styl ikoniczny, z implantem.">
  <defs>
    <clipPath id="e_cyL"><rect x="166" y="104" width="28" height="182" rx="14"/></clipPath>
    <clipPath id="e_cyR"><rect x="198" y="104" width="28" height="182" rx="14"/></clipPath>
    <clipPath id="e_res"><circle cx="312" cy="256" r="30"/></clipPath>
  </defs>
  <path d="M156 288 L156 140 A40 40 0 0 1 236 140 L236 288 C270 300 278 366 244 396 C220 418 172 418 148 396 C114 366 122 300 156 288 Z"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
  <path d="M188 300 C188 340 204 340 204 300" fill="none" stroke="currentColor" stroke-width="1.2" opacity=".35"/>
  <g style="fill: var(--ochre)">
    <g clip-path="url(#e_cyL)"><rect class="cyl-fluid" x="166" y="104" width="28" height="182"/></g>
    <g clip-path="url(#e_cyR)"><rect class="cyl-fluid" x="198" y="104" width="28" height="182"/></g>
    <g clip-path="url(#e_res)"><rect class="res-fluid" x="282" y="226" width="60" height="60"/></g>
  </g>
  <g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
    <rect x="166" y="104" width="28" height="182" rx="14"/>
    <rect x="198" y="104" width="28" height="182" rx="14"/>
    <circle cx="312" cy="256" r="30"/>
    <path d="M294 270 L332 232 M290 258 L326 224" opacity=".4" stroke-width="1"/>
    <ellipse class="pump" cx="196" cy="360" rx="20" ry="24"/>
    <path d="M184 286 C180 312 188 334 190 344"/>
    <path d="M212 286 C216 312 206 334 202 344"/>
    <path d="M294 270 C262 302 228 334 214 348"/>
  </g>
  <path class="flow" d="M294 270 C262 302 228 334 214 348" fill="none" stroke="var(--ochre)" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="2 15"/>
  {_lab(110,154,'1','CYLINDRY','w prąciu','start')}
  {_lab(332,220,'3','ZBIORNIK','w miednicy','start')}
  {_lab(52,366,'2','POMPKA','w mosznie','start')}
  {_STATE.format(x=196,y=46)}
</svg>"""

# ---- WARIANT A+E: sagittalny przekrój, ciągły kontur, prawdziwa struktura ----
FIG_AE = f"""<svg viewBox="56 18 452 480" class="fig-anim fig-hydro" role="img" aria-label="Przekrój boczny męskiej miednicy z trzyczęściowym implantem hydraulicznym. Podczas wzwodu trzon prącia unosi się, a cylinder wypełnia się płynem ze zbiornika.">
  <defs>
    <clipPath id="ae_cyl"><rect x="216" y="240" width="222" height="22" rx="11"/></clipPath>
    <clipPath id="ae_res"><circle cx="166" cy="200" r="30"/></clipPath>
  </defs>

  <!-- płaszczyzna cięcia -->
  <g stroke="currentColor" opacity=".38" stroke-width="1.1">
    <line x1="112" y1="64" x2="112" y2="392"/>
    <g stroke-width=".9" opacity=".7">
      <line x1="112" y1="84" x2="100" y2="74"/><line x1="112" y1="116" x2="100" y2="106"/>
      <line x1="112" y1="148" x2="100" y2="138"/><line x1="112" y1="180" x2="100" y2="170"/>
      <line x1="112" y1="212" x2="100" y2="202"/><line x1="112" y1="244" x2="100" y2="234"/>
      <line x1="112" y1="276" x2="100" y2="266"/><line x1="112" y1="308" x2="100" y2="298"/>
      <line x1="112" y1="340" x2="100" y2="330"/><line x1="112" y1="372" x2="100" y2="362"/>
    </g>
  </g>

  <!-- KONTUR CIAŁA (statyczny): brzuch, spojenie, moszna -->
  <path d="M112 64
           C150 82 190 158 204 226
           C208 244 210 250 214 256
           C240 274 256 306 260 346
           C264 388 240 418 198 418
           C156 418 138 380 146 346
           C152 316 148 304 128 304
           L112 304 Z"
        fill="none" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round"/>

  <!-- pęcherz moczowy (delikatnie) -->
  <path d="M132 168 C132 140 200 140 200 168 C200 192 180 202 166 202 C146 202 132 188 132 168 Z"
        fill="none" stroke="currentColor" stroke-width="1.3" opacity=".26"/>

  <!-- ZBIORNIK (płyn + kontur) -->
  <g style="fill: var(--ochre)">
    <g clip-path="url(#ae_res)"><rect class="res-fluid" x="136" y="170" width="60" height="60"/></g>
  </g>
  <circle cx="166" cy="200" r="30" fill="none" stroke="currentColor" stroke-width="2.3"/>
  <path d="M146 218 L188 176 M142 206 L178 172 M154 222 L192 186" opacity=".32" stroke="currentColor" stroke-width="1.1"/>

  <!-- dreny (statyczne, wychodzą z nasady = z osi obrotu) -->
  <g fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
    <path d="M212 262 C196 292 194 322 200 342"/>
    <path d="M200 344 C176 296 168 244 166 230"/>
  </g>
  <path class="flow" d="M166 230 C168 286 186 330 200 346 C201 330 204 288 210 262" fill="none" stroke="var(--ochre)" stroke-width="3" stroke-linecap="round" stroke-dasharray="2 15"/>

  <!-- POMPKA w mosznie -->
  <ellipse class="pump" cx="204" cy="360" rx="19" ry="23" fill="none" stroke="currentColor" stroke-width="2.3"/>

  <!-- RUCHOMY TRZON PRĄCIA (obraca się wokół nasady 212,252) -->
  <g class="penis-move">
    <!-- kontur trzonu + żołądź -->
    <path d="M212 238 L444 238 C472 238 472 266 444 266 L212 266 A14 14 0 0 1 212 238 Z"
          fill="var(--paper)" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round"/>
    <!-- drugie ciało jamiste (za płaszczyzną) -->
    <rect x="216" y="234" width="214" height="16" rx="8" fill="none" stroke="currentColor" stroke-width="1.3" opacity=".3"/>
    <!-- cewka moczowa pod cylindrem -->
    <g stroke="currentColor" fill="none" opacity=".5">
      <path d="M220 271 C320 269 400 267 458 266" stroke-width="1.2"/>
      <path d="M220 276 C320 274 400 272 456 271" stroke-width="1.2"/>
    </g>
    <!-- płyn w cylindrze -->
    <g style="fill: var(--ochre)">
      <g clip-path="url(#ae_cyl)"><rect class="cyl-fluid dir-right" x="216" y="240" width="222" height="22"/></g>
    </g>
    <!-- kontur cylindra -->
    <rect x="216" y="240" width="222" height="22" rx="11" fill="none" stroke="currentColor" stroke-width="2.3"/>
  </g>

  <!-- nasada / kość łonowa (na wierzchu, maskuje przegub) -->
  <circle cx="212" cy="252" r="16" fill="var(--paper)" stroke="none"/>
  <ellipse cx="210" cy="274" rx="14" ry="18" fill="var(--paper-3)" stroke="currentColor" stroke-width="1.6"/>
  <g stroke="currentColor" stroke-width="1" opacity=".5">
    <line x1="200" y1="264" x2="220" y2="284"/><line x1="198" y1="272" x2="218" y2="288"/><line x1="204" y1="260" x2="222" y2="276"/>
  </g>

  <!-- odnośniki + etykiety implantu (poza strefą ruchu trzonu: x186-463, y165-433) -->
  <g stroke="currentColor" stroke-width="1.1" opacity=".8" fill="none">
    <path d="M152 60 L166 172"/>
    <path d="M356 116 L356 180"/>
    <path d="M198 448 L204 384"/>
  </g>
  <g fill="currentColor"><circle cx="166" cy="172" r="2.8"/><circle cx="356" cy="180" r="2.8"/><circle cx="204" cy="384" r="2.8"/></g>
  {_lab(60,38,'3','ZBIORNIK','za spojeniem łonowym','start')}
  {_lab(356,88,'1','CYLINDER','w ciele jamistym','middle')}
  {_lab(150,456,'2','POMPKA','w mosznie','start')}

  {_STATE.format(x=436,y=60)}
</svg>"""

# ------------------------------------------------------------------
# FIGURY URZĄDZENIA (zamiast zdjęć produktowych) — animowane, styl patentowy
# ------------------------------------------------------------------
FIG_DEV1 = f"""<svg viewBox="0 0 480 372" class="fig-anim fig-hydro" role="img" aria-label="Schemat trzyczęściowego implantu hydraulicznego: dwa cylindry, pompka i zbiornik połączone drenami. Płyn przepływa ze zbiornika przez pompkę do cylindrów.">
  <defs>
    <clipPath id="dev1_cyT"><rect x="150" y="70" width="262" height="26" rx="13"/></clipPath>
    <clipPath id="dev1_cyB"><rect x="150" y="104" width="262" height="26" rx="13"/></clipPath>
    <clipPath id="dev1_res"><circle cx="392" cy="264" r="38"/></clipPath>
  </defs>
  <g style="fill: var(--ochre)">
    <g clip-path="url(#dev1_cyT)"><rect class="cyl-fluid dir-right" x="150" y="70" width="262" height="26"/></g>
    <g clip-path="url(#dev1_cyB)"><rect class="cyl-fluid dir-right" x="150" y="104" width="262" height="26"/></g>
    <g clip-path="url(#dev1_res)"><rect class="res-fluid" x="354" y="226" width="76" height="76"/></g>
  </g>
  <g fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
    <rect x="150" y="70" width="262" height="26" rx="13"/>
    <rect x="150" y="104" width="262" height="26" rx="13"/>
    <circle cx="392" cy="264" r="38"/>
    <ellipse class="pump" cx="150" cy="266" rx="26" ry="32"/>
    <path d="M150 96 C150 150 150 210 150 234"/>
    <path d="M164 130 C168 165 156 210 154 234"/>
    <path d="M176 270 C258 290 316 278 356 268"/>
  </g>
  <path class="flow" d="M356 268 C316 278 210 292 176 270" fill="none" stroke="var(--ochre)" stroke-width="2.8" stroke-linecap="round" stroke-dasharray="2 15"/>
  <path class="flow" d="M150 236 C150 190 150 140 150 98" fill="none" stroke="var(--ochre)" stroke-width="2.8" stroke-linecap="round" stroke-dasharray="2 15"/>
  <g stroke="currentColor" stroke-width="1.1" opacity=".8" fill="none">
    <path d="M250 60 L250 70"/>
    <path d="M120 316 L148 300"/>
    <path d="M392 320 L392 304"/>
  </g>
  <g fill="currentColor"><circle cx="250" cy="70" r="2.8"/><circle cx="148" cy="300" r="2.8"/><circle cx="392" cy="304" r="2.8"/></g>
  {_lab(250,42,'1','CYLINDRY','dwa, w prąciu','middle')}
  {_lab(40,326,'2','POMPKA','w mosznie','start')}
  {_lab(392,326,'3','ZBIORNIK','w brzuchu','middle')}
  {_STATE.format(x=400,y=42)}
</svg>"""

FIG_DEV2 = f"""<svg viewBox="0 0 470 372" class="fig-anim fig-hydro" role="img" aria-label="Przekrój cylindra implantu hydraulicznego. Wypełnienie płynem rozpręża cylinder, prącie zyskuje sztywność, długość i obwód.">
  <defs>
    <clipPath id="dev2_lum"><rect x="70" y="150" width="322" height="72" rx="36"/></clipPath>
  </defs>
  <g style="fill: var(--ochre)">
    <g clip-path="url(#dev2_lum)"><rect class="cyl-fluid dir-right" x="70" y="150" width="322" height="72"/></g>
  </g>
  <g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
    <rect x="58" y="138" width="346" height="96" rx="48" stroke-width="2.4"/>
    <rect x="70" y="150" width="322" height="72" rx="36" stroke-width="1.3" opacity=".45"/>
  </g>
  <g clip-path="url(#dev2_lum)" stroke="currentColor" stroke-width=".9" opacity=".28">
    <line x1="60" y1="150" x2="96" y2="186"/><line x1="60" y1="176" x2="86" y2="202"/>
    <line x1="66" y1="214" x2="102" y2="178"/><line x1="60" y1="200" x2="90" y2="170"/>
  </g>
  <g stroke="currentColor" stroke-width="1.6" fill="none" opacity=".55" stroke-linecap="round">
    <path d="M231 128 L231 112 M225 118 L231 112 L237 118"/>
    <path d="M231 244 L231 260 M225 254 L231 260 L237 254"/>
    <path d="M410 186 L426 186 M420 180 L426 186 L420 192"/>
  </g>
  <g stroke="currentColor" stroke-width="1.1" opacity=".8" fill="none"><path d="M231 96 L231 60"/></g>
  <g fill="currentColor"><circle cx="231" cy="96" r="2.8"/></g>
  {_lab(231,52,'1','CYLINDER','w przekroju','middle')}
  <g font-family="'Spline Sans Mono',monospace" fill="currentColor" text-anchor="middle" font-size="{LAB_SUB_FS}" opacity=".72">
    <text x="231" y="322">rozprężanie: długość + obwód</text>
  </g>
  {_STATE.format(x=372,y=316)}
</svg>"""

FAQ = [
 dict(q='„Implant prącia to rozwiązanie tylko dla starszych mężczyzn"', v='myth', teaser=True, a=[
  'Do implantacji kwalifikuje stan ciał jamistych, a nie data urodzenia. Wypadki komunikacyjne, urazy rdzenia kręgowego, przebyty priapizm czy operacje w miednicy potrafią odebrać wzwód mężczyźnie przed trzydziestką.',
  'Jest też argument, o którym mało kto mówi: nieleczone ciężkie zaburzenia erekcji skracają prącie o 0,5–1 cm rocznie. Im młodszy pacjent, tym więcej traci na czekaniu.']),
 dict(q='„Po wszczepieniu implantu penis będzie mniejszy"', v='myth', teaser=True, a=[
  'Implant zachowuje długość prącia z dnia operacji. Za skracanie odpowiada choroba: prącie pozbawione wzwodów włóknieje i traci 0,5–1 cm rocznie.',
  'Wszczepienie ten proces zatrzymuje, a implant hydrauliczny przy każdej aktywacji dodatkowo rozpręża tkanki na długość i obwód.']),
 dict(q='„Implant powiększy penisa"', v='myth', a=[
  'Nie powiększy. Prącie będzie miało po operacji tyle, ile ma w dniu zabiegu. Mówię o tym każdemu pacjentowi wprost, bo jeśli ktoś obiecuje Ci przy okazji implantu dodatkowe centymetry, to po prostu nie mówi prawdy.']),
 dict(q='„Seks z implantem będzie dokładnie taki jak przed chorobą"', v='half', a=[
  'Będzie inny. Lata choroby, operacje czy uraz zostawiły ślad i tego żadna metoda nie cofnie. Wraca natomiast to, co najważniejsze: pewny wzwód, kontrola nad jego czasem trwania i spokojna głowa zamiast lęku przed porażką.',
  'Czucie, orgazm i satysfakcja z bliskości pozostają. Dla 98% pacjentów z implantem hydraulicznym ten bilans okazuje się bardzo korzystny.']),
 dict(q='Czy partnerka wyczuje, że mam implant?', v=None, a=[
  'Podczas zbliżenia praktycznie nie ma takiej możliwości: sztywność jest pełna, a prącie w dotyku pozostaje naturalne. Pompka implantu hydraulicznego to niewielki element w mosznie, wyczuwalny wyłącznie przy celowym dotyku.',
  'Zdecydowana większość par szybko przestaje o niej myśleć. A wielu z nich wspólna wizyta przed operacją oszczędza miesięcy domysłów, dlatego chętnie widzę na konsultacji obie strony.']),
 dict(q='„Wszczepienie implantu to decyzja nieodwracalna"', v='fact', a=[
  'Po implantacji naturalne ani wspomagane lekami erekcje nie będą już możliwe, ponieważ mechanizm wzwodu w całości przejmuje implant. Dlatego to trzecia linia leczenia, po tabletkach i iniekcjach, i dlatego kwalifikuję do niej tak starannie.',
  'Sam implant można w przyszłości wymienić na nowy. Wrócić do stanu sprzed operacji się nie da.']),
 dict(q='Jak długo działa implant prącia?', v=None, a=[
  'Większość nowoczesnych implantów pracuje bezawaryjnie ponad 20 lat. Jeśli po latach mechanika się zużyje, implant wymienia się na nowy podczas kolejnego, planowego zabiegu.']),
 dict(q='„Czucie, orgazm i wytrysk zostają po operacji"', v='fact', a=[
  'Implant trafia do ciał jamistych i nie narusza unerwienia czuciowego prącia. Doznania pozostają Twoje. Orgazm i wytrysk również, o ile prostata i odpowiednie nerwy nie zostały uszkodzone wcześniej, na przykład podczas operacji onkologicznej. Ojcostwo także pozostaje możliwe.']),
 dict(q='„Rezonans magnetyczny i bramki na lotnisku są bezpieczne"', v='fact', a=[
  'Z nowoczesnym implantem prącia możesz bez obaw iść i na rezonans, i w podróż. Badania obrazowe są bezpieczne, a bramki bezpieczeństwa nie podnoszą alarmu.']),
 dict(q='Kiedy wrócę do współżycia po operacji?', v=None, a=[
  'Plan wygląda tak: 3–4 tygodnie gojenia, potem aktywacja implantu w gabinecie i około 3 tygodnie codziennego rozprężania tkanek. Do współżycia wracasz stopniowo, zwykle około 6. tygodnia od zabiegu.']),
 dict(q='Czy operacja i rekonwalescencja bolą?', v=None, a=[
  'Sam zabieg przesypiasz w znieczuleniu ogólnym. Po nim normą są obrzęk, zasinienie i uczucie ucisku, które kontrolujemy lekami przeciwbólowymi. Dolegliwości wyraźnie słabną w kolejnych tygodniach gojenia.']),
 dict(q='Kto nie może mieć implantu?', v=None, a=[
  'Bezwzględnie: mężczyźni z aktywną infekcją układu moczowego lub zmianami zapalnymi skóry w polu operacyjnym (najpierw leczymy, potem operujemy) oraz z potwierdzoną alergią na antybiotyki.',
  'Cukrzyca, urazy rdzenia kręgowego i obniżona odporność nie wykluczają zabiegu, ale podnoszą ryzyko infekcji. Tych pacjentów przygotowuję według rozszerzonego protokołu.']),
 dict(q='Ile kosztuje implant prącia?', v=None, a=[
  'To zależy przede wszystkim od typu implantu: półsztywny jest wyraźnie tańszy od hydraulicznego trzyczęściowego. Konkretną, pełną wycenę, razem z kosztami operacji i opieki pooperacyjnej, otrzymujesz na konsultacji kwalifikacyjnej. Bez ukrytych pozycji i dopisków drobnym drukiem.']),
 dict(q='„Zanim pomyślę o implancie, muszę wypróbować wszystkie tabletki świata"', v='myth', teaser=True, a=[
  'Obowiązuje zasada 6–8 prób danego leku, zanim uznamy go za nieskuteczny. Ale kolekcjonowanie kolejnych preparatów traci sens, gdy przyczyna jest nieodwracalna: po radykalnej prostatektomii czy przy trwałym uszkodzeniu nerwów żadna tabletka nie zadziała.',
  'Konsultacja porządkuje tę ścieżkę. Czasem kończy się receptą, czasem kwalifikacją do zabiegu, a zawsze konkretnym planem.']),
 dict(q='„Skoro implant rozwiązuje problem, diagnostyka jest zbędna"', v='myth', a=[
  'Implant usuwa skutek, ale nie leczy przyczyny. A zaburzenia erekcji bywają pierwszym objawem chorób naczyń: potrafią wyprzedzać incydenty sercowe o około 5 lat. Dlatego każdego pacjenta diagnozuję w całości, żeby operacja nie przykryła problemu wymagającego leczenia u kardiologa czy diabetologa.']),
]

VERDICT_HTML = {
 'myth': '<span class="verdict verdict--myth">Mit</span>',
 'fact': '<span class="verdict verdict--fact">Fakt</span>',
 'half': '<span class="verdict verdict--half">Połowiczna prawda</span>',
}
VERDICT_TXT = {'myth': 'Mit. ', 'fact': 'Fakt. ', 'half': 'Połowiczna prawda. ', None: ''}

def faq_item_html(i, item):
    badge = VERDICT_HTML.get(item['v'], '')
    body = ''.join(f'<p>{p}</p>' for p in item['a'])
    return (f'<details class="qa">\n'
            f'  <summary><span class="q-i">Q/{i:02d}</span><span>{item["q"]}</span><span class="q-m">+</span></summary>\n'
            f'  <div class="qa-body">{badge}{body}</div>\n'
            f'</details>')

FAQ_ITEMS_HTML = '\n'.join(faq_item_html(i + 1, it) for i, it in enumerate(FAQ))
FAQ_TEASER_HTML = '\n'.join(faq_item_html(i + 1, it) for i, it in enumerate(FAQ) if it.get('teaser'))

FAQ_JSONLD = json.dumps({
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [{
        "@type": "Question",
        "name": it['q'].replace('„', '').replace('"', ''),
        "acceptedAnswer": {"@type": "Answer", "text": VERDICT_TXT[it['v']] + ' '.join(it['a'])}
    } for it in FAQ]
}, ensure_ascii=False, indent=1)

PHYSICIAN_JSONLD = json.dumps({
    "@context": "https://schema.org",
    "@type": "Physician",
    "name": "dr Anna Bonder-Nowicka",
    "description": "Urolog i seksuolog. Leczenie ciężkich zaburzeń erekcji, wszczepianie implantów prącia. Warszawa.",
    "medicalSpecialty": "Urologic",
    "url": "https://turbourolog.pl/",
    "email": f"mailto:{MAIL}",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "ul. Żelazna 67/29",
        "postalCode": "00-871",
        "addressLocality": "Warszawa",
        "addressCountry": "PL"
    },
    "sameAs": [
        ZL,
        "https://www.instagram.com/turbourolog/",
        "https://www.facebook.com/profile.php?id=61569814723670&locale=pl_PL",
        "https://www.linkedin.com/in/anna-bonder-nowicka-a73193344/"
    ]
}, ensure_ascii=False, indent=1)

# ------------------------------------------------------------------
# STRONY
# ------------------------------------------------------------------
PAGES = [
 dict(file='index.html', nav=None, cta=True, schema=[PHYSICIAN_JSONLD],
      title='Implant prącia Warszawa | dr Anna Bonder-Nowicka',
      desc='Ciężkie zaburzenia erekcji? Implant prącia to metoda o najwyższej satysfakcji pacjentów (do 98%). Operuje urolog i seksuolog dr Anna Bonder-Nowicka.'),
 dict(file='rodzaje-implantow.html', nav='rodzaje', cta=True, schema=[],
      title='Rodzaje implantów prącia: hydrauliczny i półsztywny',
      desc='Implant hydrauliczny trzyczęściowy czy półsztywny? Porównanie budowy, obsługi, dyskrecji i kosztów oraz to, jak dobieram implant do pacjenta.'),
 dict(file='implant-hydrauliczny.html', nav='rodzaje', cta=True, schema=[],
      title='Implant hydrauliczny prącia (trzyczęściowy) | Warszawa',
      desc='Implant hydrauliczny trzyczęściowy: naturalny wygląd w spoczynku, pełna sztywność na żądanie, satysfakcja do 98%. Jak działa i dla kogo jest przeznaczony.'),
 dict(file='implant-polsztywny.html', nav='rodzaje', cta=True, schema=[],
      title='Implant półsztywny prącia: prostota i niższy koszt | Warszawa',
      desc='Implant półsztywny: bez mechaniki, najniższe ryzyko awarii i najniższy koszt. Dobre rozwiązanie przy ograniczonej sprawności dłoni. Jak działa i dla kogo.'),
 dict(file='przebieg-leczenia.html', nav='przebieg', cta=True, schema=[],
      title='Wszczepienie implantu prącia krok po kroku | Warszawa',
      desc='Wszczepienie implantu prącia etap po etapie: diagnostyka, kwalifikacja, operacja 60–90 min, aktywacja po 3–4 tyg. i powrót do współżycia ok. 6. tygodnia.'),
 dict(file='zycie-z-implantem.html', nav='zycie', cta=True, schema=[],
      title='Życie i seks z implantem prącia | dr Bonder-Nowicka',
      desc='Dyskrecja na co dzień, czucie i orgazm bez zmian, rezonans i lotnisko bez obaw, trwałość 20+ lat. Tak naprawdę wygląda życie z implantem prącia.'),
 dict(file='o-lekarce.html', nav='lekarka', cta=True, schema=[],
      title='dr Anna Bonder-Nowicka: urolog i seksuolog, implanty',
      desc='Urolog i seksuolog w jednej osobie. Szpital Bielański, seksuologia kliniczna SWPS, staże implantacyjne w Stambule i Ammanie: 44 implanty w 3 tygodnie.'),
 dict(file='fakty-i-mity.html', nav='faq', cta=True, schema=[FAQ_JSONLD],
      title='Implant prącia: fakty, mity i FAQ | dr Bonder-Nowicka',
      desc='Czy implant powiększa prącie? Czy partnerka go wyczuje? Czy decyzja jest odwracalna? 15 najczęstszych pytań i mitów o implantach prącia, bez owijania.'),
 dict(file='kontakt.html', nav='kontakt', cta=False, schema=[PHYSICIAN_JSONLD],
      title='Kontakt i umawianie konsultacji | Implant prącia',
      desc='Umów konsultację w sprawie implantu prącia w Warszawie: rejestracja online przez ZnanyLekarz, ul. Żelazna 67/29. Pełna dyskrecja, odpowiedź osobista.'),
 dict(file='warianty-animacji.html', nav=None, cta=False, schema=[], noindex=True,
      title='Warianty animacji implantu (do wyboru)',
      desc='Robocza strona z pięcioma wersjami animacji implantu do wyboru.'),
]

NAV = [
 ('rodzaje-implantow.html', 'Rodzaje implantów', 'rodzaje'),
 ('przebieg-leczenia.html', 'Przebieg leczenia', 'przebieg'),
 ('zycie-z-implantem.html', 'Życie z implantem', 'zycie'),
 ('o-lekarce.html', 'O lekarce', 'lekarka'),
 ('fakty-i-mity.html', 'Fakty i mity', 'faq'),
 ('kontakt.html', 'Kontakt', 'kontakt'),
]

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           "%3Crect width='64' height='64' rx='9' fill='%23003D47'/%3E"
           "%3Ctext x='32' y='44' font-family='Georgia,serif' font-size='32' fill='%23FEFBF9' "
           "text-anchor='middle'%3EiP%3C/text%3E%3C/svg%3E")

FONTS = ('https://fonts.googleapis.com/css2?'
         'family=STIX+Two+Text:ital,wght@0,400;0,600;1,400;1,600'
         '&family=Schibsted+Grotesk:wght@400;500;600;700'
         '&family=Spline+Sans+Mono:wght@400;500&display=swap')


def head(page):
    schema = '\n'.join(f'<script type="application/ld+json">\n{s}\n</script>' for s in page['schema'])
    robots = 'noindex, nofollow' if page.get('noindex') else 'index, follow'
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page['title']}</title>
<meta name="description" content="{page['desc']}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#003D47">
<!-- TODO przy wdrożeniu: uzupełnij docelową domenę i odkomentuj -->
<!-- <link rel="canonical" href="https://TWOJA-DOMENA.pl/{page['file']}"> -->
<!-- <meta property="og:locale" content="pl_PL"><meta property="og:type" content="website">
     <meta property="og:title" content="{page['title']}">
     <meta property="og:description" content="{page['desc']}">
     <meta property="og:url" content="https://TWOJA-DOMENA.pl/{page['file']}"> -->
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
{schema}
<style>
{CSS}
</style>
</head>
<body>
<a class="skip-link" href="#main">Przejdź do treści</a>"""


def header(page):
    links = '\n      '.join(
        f'<a href="{href}"{aria}>{label}</a>'
        for href, label, nid in NAV
        for aria in (' aria-current="page"' if page["nav"] == nid else '',))
    return f"""
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="Implant prącia — strona główna">
      <span class="b-name">Implant prącia</span>
      <span class="b-sub">dr Anna Bonder&#8209;Nowicka</span>
    </a>
    <button class="burger" aria-expanded="false" aria-controls="site-nav" aria-label="Otwórz menu">
      <span></span><span></span><span></span>
    </button>
    <nav class="main-nav" id="site-nav" aria-label="Nawigacja główna">
      {links}
      <a class="btn btn--primary nav-cta" href="{ZL}" target="_blank" rel="noopener">Umów konsultację</a>
    </nav>
  </div>
</header>
<main id="main">"""


CTA_BAND = f"""
<section class="cta-band">
  <div class="wrap">
    <div data-reveal>
      <p class="eyebrow eyebrow--inv" style="margin-bottom:14px">Następny krok</p>
      <h2>Pierwsza rozmowa niczego nie przesądza.</h2>
      <p>Na konsultacji po prostu porozmawiamy. Zrobię wywiad, zbadam Cię i powiem, jakie masz realne opcje i skąd bierze się problem. Niczego nie musisz od razu postanawiać. Decyzję o operacji zostawiamy na później.</p>
    </div>
    <div class="cta-actions" data-reveal="2">
      <a class="btn btn--inv" href="{ZL}" target="_blank" rel="noopener">Umów konsultację przez ZnanyLekarz</a>
      <p class="btn-note">Terminy online 24/7 · Warszawa · pełna dyskrecja</p>
    </div>
  </div>
</section>"""


def footer():
    nav_links = '\n        '.join(f'<li><a href="{href}">{label}</a></li>' for href, label, _ in NAV)
    return f"""</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="f-grid">
      <div class="f-brand">
        <div class="b-name">Implant prącia</div>
        <div class="b-sub">dr Anna Bonder&#8209;Nowicka</div>
        <p>Serwis informacyjny o leczeniu ciężkich zaburzeń erekcji metodą wszczepienia implantu. Część praktyki <a href="https://turbourolog.pl/" target="_blank" rel="noopener">turbourolog.pl</a>.</p>
      </div>
      <div>
        <h4>Na tej stronie</h4>
        <ul>
        <li><a href="index.html">Strona główna</a></li>
        {nav_links}
        </ul>
      </div>
      <div>
        <h4>Praktyka</h4>
        <ul>
          <li>ul. Żelazna 67/29<br>00&#8209;871 Warszawa</li>
          <li><a href="mailto:{MAIL}">{MAIL}</a></li>
          <li><a href="{ZL}" target="_blank" rel="noopener">Rejestracja online (ZnanyLekarz)</a></li>
        </ul>
      </div>
      <div>
        <h4>Obserwuj</h4>
        <ul>
          <li><a href="https://www.instagram.com/turbourolog/" target="_blank" rel="noopener">Instagram</a></li>
          <li><a href="https://www.facebook.com/profile.php?id=61569814723670&amp;locale=pl_PL" target="_blank" rel="noopener">Facebook</a></li>
          <li><a href="https://www.linkedin.com/in/anna-bonder-nowicka-a73193344/" target="_blank" rel="noopener">LinkedIn</a></li>
        </ul>
      </div>
    </div>
    <div class="f-legal">
      <span>© 2026 Praktyka Lekarska Anna Bonder&#8209;Nowicka · NIP 5252152491</span>
      <span><a href="{PDF_PRIV}" target="_blank" rel="noopener">Polityka prywatności i plików cookies</a></span>
    </div>
    <p class="f-disclaimer">Treści na tej stronie mają charakter informacyjny i edukacyjny. Nie zastępują konsultacji lekarskiej ani indywidualnej kwalifikacji do zabiegu; decyzja o leczeniu operacyjnym zawsze zapada podczas wizyty, po badaniu i omówieniu ryzyka. Dane o satysfakcji pacjentów pochodzą z badań dotyczących nowoczesnych implantów prącia. Indywidualne wyniki leczenia mogą się różnić.</p>
  </div>
</footer>
<script>
(function(){{
  var h=document.querySelector('.site-header');
  var onScroll=function(){{ h.classList.toggle('scrolled', window.scrollY>8); }};
  addEventListener('scroll', onScroll, {{passive:true}}); onScroll();

  var b=document.querySelector('.burger'), n=document.getElementById('site-nav');
  if(b&&n){{ b.addEventListener('click', function(){{
    var open=n.classList.toggle('open');
    b.setAttribute('aria-expanded', open);
    b.setAttribute('aria-label', open ? 'Zamknij menu' : 'Otwórz menu');
  }}); }}

  var items=document.querySelectorAll('[data-reveal]');
  if(matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)){{
    items.forEach(function(el){{ el.classList.add('in'); }});
  }} else {{
    var io=new IntersectionObserver(function(es){{
      es.forEach(function(e){{ if(e.isIntersecting){{ e.target.classList.add('in'); io.unobserve(e.target); }} }});
    }}, {{threshold:.12}});
    items.forEach(function(el){{ io.observe(el); }});
  }}

  /* Formularz kontaktowy: tryb mailto. DEV: przy wdrożeniu podłącz własny endpoint. */
  var f=document.getElementById('contact-form');
  if(f){{ f.addEventListener('submit', function(ev){{
    ev.preventDefault();
    if(!f.reportValidity()) return;
    var v=function(id){{ var el=document.getElementById(id); return el?el.value:''; }};
    var subject='Wiadomość ze strony: '+v('f-topic');
    var body='Imię: '+v('f-name')+'\\nE-mail: '+v('f-mail')+'\\n\\n'+v('f-msg');
    location.href='mailto:{MAIL}?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
  }}); }}
}})();
</script>
</body>
</html>"""


# ------------------------------------------------------------------
# TRYB EDYCJI — oznaczanie edytowalnych bloków tekstu (data-ef / data-eo)
# Każdy blok dostaje: data-ef = plik źródłowy we frag/, data-eo = base64
# jego oryginalnej treści (klucz do zamiany w źródle przez edit-server.py).
# SVG jest chronione (tokenizowane), żeby parser go nie ruszył.
# ------------------------------------------------------------------
EDITABLE_TAGS = {'p', 'h1', 'h2', 'h3', 'h4', 'blockquote', 'figcaption',
                 'summary', 'td', 'th', 'li'}
VOID_TAGS = {'br', 'img', 'hr', 'wbr', 'input', 'source', 'meta', 'link', 'col'}


class _EditableMarker(HTMLParser):
    def __init__(self, src_file):
        super().__init__(convert_charrefs=False)
        self.file = src_file
        self.out = []
        self.in_block = False
        self.buf = []
        self.block_tag = None
        self.block_start = None
        self.inner = 0

    def _emit(self, s):
        (self.buf if self.in_block else self.out).append(s)

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text()
        if not self.in_block and tag in EDITABLE_TAGS:
            self.in_block = True
            self.block_tag = tag
            self.block_start = raw
            self.buf = []
            self.inner = 0
            return
        if self.in_block and tag not in VOID_TAGS:
            self.inner += 1
        self._emit(raw)

    def handle_startendtag(self, tag, attrs):
        self._emit(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self.in_block:
            if self.inner == 0 and tag == self.block_tag:
                inner = ''.join(self.buf)
                if '\x00SVG' in inner:
                    # blok zawiera ikonę/figurę SVG — nie oznaczamy jako edytowalny
                    self.out.append(self.block_start + inner + f'</{tag}>')
                else:
                    b64 = base64.b64encode(inner.encode('utf-8')).decode('ascii')
                    st = self.block_start[:-1] + f' data-ef="{self.file}" data-eo="{b64}"' + '>'
                    self.out.append(st + inner + f'</{tag}>')
                self.in_block = False
                self.buf = []
                self.block_tag = None
                return
            if self.inner > 0:
                self.inner -= 1
            self.buf.append(f'</{tag}>')
            return
        self.out.append(f'</{tag}>')

    def handle_data(self, d):
        self._emit(d)

    def handle_entityref(self, n):
        self._emit(f'&{n};')

    def handle_charref(self, n):
        self._emit(f'&#{n};')

    def handle_comment(self, c):
        self._emit(f'<!--{c}-->')

    def handle_decl(self, d):
        self._emit(f'<!{d}>')


def make_editable(fragment, src_file):
    # 1) wyjmij SVG (XML case-sensitive) pod tokeny, żeby parser go nie zepsuł
    svgs = []

    def _stash(m):
        svgs.append(m.group(0))
        return f'\x00SVG{len(svgs) - 1}\x00'

    protected = re.sub(r'<svg\b.*?</svg>', _stash, fragment, flags=re.S | re.I)
    # 2) oznacz edytowalne bloki
    p = _EditableMarker(src_file)
    p.feed(protected)
    p.close()
    result = ''.join(p.out)
    # 3) przywróć SVG
    for i, svg in enumerate(svgs):
        result = result.replace(f'\x00SVG{i}\x00', svg)
    return result


# ------------------------------------------------------------------
# ZASOBY EDYTORA (aktywne tylko, gdy strona serwowana jest przez edit-server.py)
# ------------------------------------------------------------------
EDITOR_ASSETS = r'''<style>
#ed-bar{position:fixed;right:16px;bottom:16px;z-index:9999;display:none;gap:8px;
  align-items:center;background:#003D47;color:#FBF7F4;padding:8px 10px;border-radius:6px;
  font-family:system-ui,sans-serif;font-size:14px;box-shadow:0 10px 30px -10px rgba(0,0,0,.5)}
body.ed-ready #ed-bar{display:flex}
#ed-bar button{background:#3EABF0;color:#012A31;border:0;border-radius:4px;padding:7px 12px;
  font-weight:600;cursor:pointer;font-size:14px}
#ed-bar button#ed-cancel{background:transparent;color:#EDEFE8;text-decoration:underline;padding:7px 6px}
#ed-msg{opacity:.9;font-size:13px;max-width:240px}
body.ed-on [data-ef]{outline:2px dashed rgba(169,123,34,.7);outline-offset:3px;cursor:text}
body.ed-on [data-ef]:focus{outline:2px solid #A97B22;background:rgba(169,123,34,.08)}
</style>
<div id="ed-bar" aria-hidden="true">
  <button id="ed-toggle" type="button">&#9998; Edytuj tre&#347;&#263;</button>
  <span id="ed-actions" hidden>
    <button id="ed-save" type="button">&#128190; Zapisz</button>
    <button id="ed-cancel" type="button">Anuluj</button>
  </span>
  <span id="ed-msg"></span>
</div>
<script>
(function(){
  fetch('/__ping').then(function(r){if(r.ok)init();}).catch(function(){});
  function init(){
    document.body.classList.add('ed-ready');
    var nodes=[].slice.call(document.querySelectorAll('[data-ef]'));
    var editing=false;
    var toggle=document.getElementById('ed-toggle');
    var actions=document.getElementById('ed-actions');
    var msgEl=document.getElementById('ed-msg');
    function msg(t){msgEl.textContent=t||'';}
    function mark(e){e.currentTarget.setAttribute('data-dirty','1');}
    function setEdit(on){
      editing=on;
      document.body.classList.toggle('ed-on',on);
      actions.hidden=!on; toggle.hidden=on;
      nodes.forEach(function(n){
        n.contentEditable=on?'true':'false';
        if(on)n.addEventListener('input',mark);
      });
      msg(on?'Klikaj w teksty i pisz. Potem Zapisz.':'');
    }
    toggle.onclick=function(){setEdit(true);};
    document.getElementById('ed-cancel').onclick=function(){location.reload();};
    document.getElementById('ed-save').onclick=function(){
      var dirty=nodes.filter(function(n){return n.getAttribute('data-dirty');});
      if(!dirty.length){msg('Nic nie zmieniono.');return;}
      msg('Zapisywanie…');
      fetch('/__save',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({edits:dirty.map(function(n){
          return {file:n.getAttribute('data-ef'),eo:n.getAttribute('data-eo'),html:n.innerHTML};
        })})})
        .then(function(r){return r.json();})
        .then(function(res){
          if(res.failed&&res.failed.length)
            msg('Zapisano '+res.saved+', nie udało się '+res.failed.length+'. Przeładuj i spróbuj ponownie.');
          else{msg('Zapisano ✓ przeładowuję…');setTimeout(function(){location.reload();},700);}
        })
        .catch(function(){msg('Błąd zapisu.');});
    };
  }
})();
</script>'''

# ------------------------------------------------------------------
# SKŁADANIE
# ------------------------------------------------------------------
ROUTE_HTML = {}
for page in PAGES:
    frag = (ROOT / 'frag' / page['file']).read_text(encoding='utf-8')
    frag = (frag.replace('{{FIG1}}', FIG_AE)
                .replace('{{FIG2}}', FIG2)
                .replace('{{FIG_AE}}', FIG_AE)
                .replace('{{FIG_DEV1}}', FIG_DEV1)
                .replace('{{FIG_DEV2}}', FIG_DEV2)
                .replace('{{VAR_A}}', VAR_A)
                .replace('{{VAR_B}}', VAR_B)
                .replace('{{VAR_C}}', VAR_C)
                .replace('{{VAR_D}}', VAR_D)
                .replace('{{VAR_E}}', VAR_E)
                .replace('{{FAQ_ITEMS}}', FAQ_ITEMS_HTML)
                .replace('{{FAQ_TEASER}}', FAQ_TEASER_HTML))
    frag = make_editable(frag, page['file'])
    doc = head(page) + header(page) + '\n' + frag + '\n' + (CTA_BAND if page['cta'] else '') + footer()
    doc = doc.replace('</body>', EDITOR_ASSETS + '\n</body>')
    (OUT / page['file']).write_text(doc, encoding='utf-8')
    ROUTE_HTML[page['file']] = frag + '\n' + (CTA_BAND if page['cta'] else '')
    print(f"OK  {page['file']:26s} {len(doc)/1024:6.1f} kB")

zip_path = ROOT / 'implant-pracia-strona.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.glob('*.html')):
        if p.name == 'warianty-animacji.html':
            continue  # robocza strona wyboru — poza publiczną paczką
        z.write(p, p.name)
print(f"\nZIP {zip_path} ({zip_path.stat().st_size/1024:.1f} kB)")


# ------------------------------------------------------------------
# JEDEN PLIK (SPA) — cały serwis w jednym HTML, nawigacja przez #hash
# ------------------------------------------------------------------
import re as _re

BUNDLE_PAGES = [p['file'] for p in PAGES if not p.get('noindex')]  # bez roboczej strony wariantów

def _slug(fname):
    return fname[:-5] if fname.endswith('.html') else fname

def _namespace_svg_ids(chunk, slug):
    # Prefiksuj TYLKO id-ki używane przez url(#..) (maski/gradienty SVG), by nie kolidowały między sekcjami
    refs = set(_re.findall(r'url\(#([A-Za-z0-9_\-]+)\)', chunk))
    for name in refs:
        new = f'{slug}__{name}'
        chunk = chunk.replace(f'id="{name}"', f'id="{new}"')
        chunk = chunk.replace(f'url(#{name})', f'url(#{new})')
    return chunk

# złóż sekcje-trasy
routes_html = []
for fname in BUNDLE_PAGES:
    slug = _slug(fname)
    chunk = _namespace_svg_ids(ROUTE_HTML[fname], slug)
    routes_html.append(f'<div class="route" data-route="{slug}" hidden>\n{chunk}\n</div>')

bundle_page = dict(file='index.html', nav=None, cta=False,
                   title='Implant prącia — dr Anna Bonder-Nowicka | Warszawa',
                   desc='Implant prącia: trzecia linia leczenia zaburzeń erekcji. Rodzaje implantów, przebieg leczenia, życie z implantem. dr Anna Bonder-Nowicka, Warszawa.',
                   schema=[PHYSICIAN_JSONLD], noindex=False)

bundle = head(bundle_page) + header(bundle_page) + '\n' + '\n'.join(routes_html) + '\n' + footer()

# przepisz linki wewnętrzne PLIK.html[#kotwica] -> #plik[~kotwica]
def _relink(m):
    slug = _slug(m.group(1) + '.html')
    sub = m.group(3)
    return f'href="#{slug}~{sub}"' if sub else f'href="#{slug}"'
bundle = _re.sub(r'href="([A-Za-z0-9_\-]+)\.html(#([A-Za-z0-9_\-]+))?"', _relink, bundle)

# router SPA + zamykanie menu po kliknięciu
_router = """
<script>
(function(){
  var routes=[].slice.call(document.querySelectorAll('.route'));
  var names=routes.map(function(r){return r.getAttribute('data-route');});
  function activeRoute(){return routes.filter(function(r){return !r.hidden;})[0];}
  function show(name,sub){
    if(names.indexOf(name)<0){var a=activeRoute();var t=a&&a.querySelector('[id="'+name+'"]');if(t)t.scrollIntoView();return;}
    routes.forEach(function(r){var on=r.getAttribute('data-route')===name;r.hidden=!on;
      if(on){r.querySelectorAll('[data-reveal]').forEach(function(el){el.classList.add('in');});}});
    document.querySelectorAll('.main-nav a').forEach(function(a){a.removeAttribute('aria-current');});
    document.querySelectorAll('.main-nav a[href="#'+name+'"]').forEach(function(a){a.setAttribute('aria-current','page');});
    var r=document.querySelector('.route[data-route="'+name+'"]');
    var nav=document.querySelector('.main-nav'); if(nav)nav.classList.remove('open');
    var bg=document.querySelector('.burger'); if(bg)bg.setAttribute('aria-expanded','false');
    if(sub){var t=r.querySelector('[id="'+sub+'"]');if(t){t.scrollIntoView();return;}}
    window.scrollTo(0,0);
  }
  function router(){var h=location.hash.replace(/^#/,'');if(!h){show('index');return;}var p=h.split('~');show(p[0],p[1]);}
  window.addEventListener('hashchange',router);
  router();
})();
</script>
"""
bundle = bundle.replace('</body>', _router + '</body>')

bundle_path = OUT / 'implant-pracia-JEDEN-PLIK.html'
bundle_path.write_text(bundle, encoding='utf-8')
print(f"JEDEN PLIK  {bundle_path.name}  ({len(bundle)/1024:.1f} kB, {len(BUNDLE_PAGES)} sekcji)")
