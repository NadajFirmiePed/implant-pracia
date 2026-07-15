# -*- coding: utf-8 -*-
"""
Generuje dwie wersje kolorystyczne strony z gotowego dist/:
  dist/v1-ciemny/   — Ciemny premium (granat + błękit)
  dist/v4-grafit/   — Grafit + elektryczny błękit
oraz dist/index.html — stronę wyboru wersji.

Działa przez nadpisanie tokenów + reguł kolorów (wstrzyknięte przed </style>).
Uruchom PO build.py:  python3 build.py && python3 themes.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT / 'dist'

# ---- WERSJA 1: CIEMNY PREMIUM (pełne odwrócenie na ciemny motyw) ----
DARK = """
:root{
  --paper:#0A2540; --paper-2:#0E2D4E; --paper-3:#123457;
  --ink:#EAF1F8; --ink-2:#9FB4C6;
  --petrol:#3EABF0; --petrol-2:#071A2E; --petrol-3:#04101D;
  --ochre:#3EABF0; --ochre-2:#7CC4F5;
  --line:rgba(255,255,255,.13); --line-soft:rgba(255,255,255,.06); --line-inv:rgba(255,255,255,.14);
  --paper-inv:#EAF1F8;
  --sh-card:0 22px 50px -30px rgba(0,0,0,.65);
  --sh-btn:0 10px 24px -12px rgba(0,0,0,.6);
}
body{ background:var(--paper); color:var(--ink); }
.section--dark{ background:#071A2E; }
.site-footer{ background:#071A2E; }
.skip-link{ background:#071A2E; color:#EAF1F8; }
.section--paper2{ background:#0E2D4E; }
.btn--primary{ background:var(--ochre); color:#071A2E; }
.btn--primary:hover{ background:var(--ochre-2); color:#071A2E; }
.btn--inv{ background:#EAF1F8; color:#0A2540; }
.btn--inv:hover{ background:#fff; }
.btn--ghost{ border-color:rgba(255,255,255,.5); color:var(--ink); }
.btn--ghost:hover{ background:var(--ochre); color:#071A2E; border-color:var(--ochre); }
.card{ background:#0E2D4E; border-color:rgba(255,255,255,.10); }
.card .c-tag{ color:var(--ochre); background:rgba(255,255,255,.06); }
.fig{ background-color:rgba(255,255,255,.03); }
.fig svg{ color:#CFE3F4; }
.fig .fig-cap b{ color:var(--ochre); }
.fig-corner{ color:#9FB4C6; }
.photo{ background-color:#123457; }
details.qa summary:hover{ color:var(--ochre); }
.pain-list .p-i{ color:var(--ochre); }
.stat .s-num sup{ color:var(--ochre); }
h1 em, h2 em{ color:var(--ochre); }
.hero-trust .dot{ background:var(--ochre); }
.verdict--myth{ background:rgba(255,255,255,.08); color:var(--ochre); }
::selection{ background:var(--ochre); color:#071A2E; }
"""

# ---- WERSJA 4: GRAFIT + ELEKTRYCZNY BŁĘKIT (motyw jasny) ----
GRAFIT = """
:root{
  --paper:#F4F2EE; --paper-2:#EAE7E0; --paper-3:#E0DBD2;
  --ink:#1C1F26; --ink-2:#565C66;
  --petrol:#0E7FC0; --petrol-2:#1C1F26; --petrol-3:#121419;
  --ochre:#0FA3E8; --ochre-2:#0B84BE;
  --line:rgba(28,31,38,.15); --line-soft:rgba(28,31,38,.08); --line-inv:rgba(244,242,238,.20);
  --paper-inv:#F4F2EE;
}
a{ color:var(--petrol); }
.btn--primary{ background:var(--ochre); color:#04263A; }
.btn--primary:hover{ background:var(--ochre-2); color:#fff; }
.card{ background:#ffffff; }
.hero-trust .dot{ background:var(--ochre); }
.stat .s-num sup{ color:var(--ochre); }
h1 em, h2 em{ color:var(--petrol); }
"""

THEMES = {'v1-ciemny': DARK, 'v4-grafit': GRAFIT}

SKIP = {'implant-pracia-JEDEN-PLIK.html'}

# 1) wczytaj oryginalne strony (płaski build)
pages = {p.name: p.read_text(encoding='utf-8')
         for p in DIST.glob('*.html') if p.name not in SKIP}

# 2) wygeneruj wersje w podfolderach
for slug, override in THEMES.items():
    out = DIST / slug
    out.mkdir(parents=True, exist_ok=True)
    inject = f"\n/* THEME: {slug} */\n{override}\n</style>"
    for name, html in pages.items():
        themed = html.replace('</style>', inject, 1)  # pierwszy = główny arkusz
        (out / name).write_text(themed, encoding='utf-8')
    print(f"OK  dist/{slug}/  ({len(pages)} stron)")

# 3) strona wyboru na wejściu
chooser = """<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Implant prącia — wybór wersji kolorystycznej</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Schibsted Grotesk",system-ui,sans-serif;background:#0A2540;color:#EAF1F8;
  min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;padding:40px 20px}
h1{font-family:"STIX Two Text",Georgia,serif;font-weight:600;font-size:clamp(24px,4vw,38px);text-align:center;letter-spacing:-.01em}
p.sub{color:#9FB4C6;font-size:15px;text-align:center;margin-top:-18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:22px;width:100%;max-width:760px}
a.card{display:block;border-radius:14px;overflow:hidden;text-decoration:none;border:1px solid rgba(255,255,255,.14);transition:transform .15s ease}
a.card:hover{transform:translateY(-3px)}
.sw{height:120px;display:flex;align-items:flex-end;padding:16px}
.lbl{padding:16px 18px;background:#0E2D4E}
.lbl b{font-size:17px;color:#fff;font-weight:600}
.lbl span{display:block;font-size:13px;color:#9FB4C6;margin-top:3px}
.pill{font-family:monospace;font-size:11px;letter-spacing:.1em;padding:6px 10px;border-radius:5px}
</style></head><body>
<h1>Implant prącia — dwie wersje kolorystyczne</h1>
<p class="sub">Kliknij, żeby zobaczyć pełną stronę w danej kolorystyce.</p>
<div class="grid">
  <a class="card" href="v1-ciemny/index.html">
    <div class="sw" style="background:#0A2540"><span class="pill" style="background:#3EABF0;color:#071A2E">granat + błękit</span></div>
    <div class="lbl"><b>Wersja 1 · Ciemny premium</b><span>cała strona ciemna, akcent świeci</span></div>
  </a>
  <a class="card" href="v4-grafit/index.html">
    <div class="sw" style="background:#F4F2EE"><span class="pill" style="background:#0FA3E8;color:#04263A">grafit + elektryczny</span></div>
    <div class="lbl"><b>Wersja 4 · Grafit + elektryczny błękit</b><span>szarości + jeden mocny akcent</span></div>
  </a>
</div>
</body></html>"""
(DIST / 'index.html').write_text(chooser, encoding='utf-8')
print("OK  dist/index.html  (strona wyboru)")
