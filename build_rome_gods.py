#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build 20 Mayhem spheres about Roman gods and Hermes.

Each sphere gets:
  - a unique theme folder in spheres_rome_gods/ (e.g. hermes-dice/)
  - deterministic procedural 2D canvas art (no external assets, no caches)
  - LIT/AMBER/MODEL verdict bands
  - {{i}} notation
  - an FNV-1a seal sha256 (name|slug|blurb)

Stdlib only. Run from REPO (C:/Users/Dave/oasis).
"""
import math
from pathlib import Path

REPO = Path(r"C:\Users\Dave\oasis")
OUT = REPO / "spheres_rome_gods"
OUT.mkdir(exist_ok=True, parents=True)


def C(v):
    """Clamp a float to a byte (0..255)."""
    return max(0, min(255, int(v)))


# ---------------------------------------------------------------------------
# Deterministic procedural canvas art. Each returns a bytearray,
# RGBA, w*h*4, identical on every run.
# ---------------------------------------------------------------------------
def _circle_of_five(w, h):
    b = bytearray([0, 0, 0, 255]) * (w * h)
    r = w * 0.33
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - w / 2, y - h / 2)
            if d < r:
                t = (d / r) ** 2
                b[4 * (y * w + x) + 1] = C(0x3e + 30 * (1 - t) + 40 * (1 - t))
                b[4 * (y * w + x) + 2] = C(0x7a + 60 * (1 - t))
    return b


def _six_ring_orrery(w, h):
    b = bytearray([8, 12, 20, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    for i, fr in enumerate([0.30, 0.44, 0.58, 0.72, 0.86, 1.0]):
        rr = fr * min(w, h) * 0.40
        n = 60 if i < 5 else 48
        col = [0xff, 0xd7, 0x7a] if i % 2 == 0 else [0x8f, 0xd7, 0xe8]
        for j in range(n):
            a = 2 * math.pi * j / n - math.pi / 2
            x = cx + rr * math.cos(a)
            y = cy + rr * math.sin(a)
            xi, yi = int(x), int(y)
            if 0 <= xi < w and 0 <= yi < h:
                b[4 * (yi * w + xi) + 0] = col[0]
                b[4 * (yi * w + xi) + 1] = col[1]
                b[4 * (yi * w + xi) + 2] = col[2]
    return b


def _tesseract_dice(w, h):
    b = bytearray([30, 20, 30, 255]) * (w * h)
    for y in range(h):
        for x in range(w):
            v = (x * 7 + y * 13) % 14
            if v < 8:
                b[4 * (y * w + x) + 1] = 0xff
                b[4 * (y * w + x) + 2] = 0xd7
    return b


def _dragon_curve(w, h):
    b = bytearray([8, 8, 12, 255]) * (w * h)
    md = w * w + h * h
    for y in range(h):
        for x in range(w):
            if (x * x + y * y) % md % 3 == 0:
                b[4 * (y * w + x) + 0] = 0xd8
                b[4 * (y * w + x) + 1] = 0xc4
                b[4 * (y * w + x) + 2] = 0x8f
    return b


def _16_cell_starve(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    f = [[0] * 4 for _ in range(4)]
    f[1][1] = f[2][2] = f[0][3] = f[3][0] = 1
    for gy in range(4):
        for gx in range(4):
            x = int(w * gx / 4) + int(w / 16)
            y = int(h * gy / 4) + int(h / 16)
            if x < w and y < h and f[gy][gx]:
                b[4 * (y * w + x) + 0] = 0x3e
                b[4 * (y * w + x) + 1] = 0xe0
                b[4 * (y * w + x) + 2] = 0x7a
    return b


def _32x32_clerk(w, h):
    b = bytearray([0, 0, 0, 255]) * (w * h)
    for y in range(h):
        for x in range(w):
            if (x * y + 7) % 32 == 0:
                b[4 * (y * w + x) + 0] = 0xb4
                b[4 * (y * w + x) + 1] = 0x8c
                b[4 * (y * w + x) + 2] = 0xff
    return b


def _33_odd_even(w, h):
    b = bytearray([15, 10, 20, 255]) * (w * h)
    for y in range(h):
        for x in range(w):
            if ((x + y) % 2) == 0:
                b[4 * (y * w + x) + 0] = 0xb5
                b[4 * (y * w + x) + 1] = 0xc6
                b[4 * (y * w + x) + 2] = 0xa5
            else:
                b[4 * (y * w + x) + 0] = 0x6a
                b[4 * (y * w + x) + 1] = 0x4a
                b[4 * (y * w + x) + 2] = 0x7a
    return b


def _meridian_rule(w, h):
    b = bytearray([20, 30, 60, 255]) * (w * h)
    cx = w / 2
    for y in range(h):
        for x in range(w):
            if abs(x - cx) / cx < 0.04:
                b[4 * (y * w + x) + 0] = 0xff
                b[4 * (y * w + x) + 1] = 0xd7
                b[4 * (y * w + x) + 2] = 0x7a
    return b


def _nine_elder(w, h):
    b = bytearray([10, 10, 20, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    for i in range(9):
        a = 2 * math.pi * i / 9 - math.pi / 2
        x = cx + 0.28 * min(w, h) * math.cos(a)
        y = cy + 0.28 * min(w, h) * math.sin(a)
        xi, yi = int(x), int(y)
        if 0 <= xi < w and 0 <= yi < h:
            b[4 * (yi * w + xi) + 0] = 0xff
            b[4 * (yi * w + xi) + 1] = 0xd7
            b[4 * (yi * w + xi) + 2] = 0x7a
    return b


def _sapphon_cube(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    for gy in range(8):
        for gx in range(8):
            x = int(w * gx / 8) + int(w / 16)
            y = int(h * gy / 8) + int(h / 16)
            if x < w and y < h:
                b[4 * (y * w + x) + 0] = 0xd8
                b[4 * (y * w + x) + 1] = 0xc4
                b[4 * (y * w + x) + 2] = 0x8f
    return b


def _cone_of_voices(w, h):
    b = bytearray([20, 20, 40, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    r = 0.30 * min(w, h)
    for y in range(h):
        for x in range(w):
            if math.hypot(x - cx, y - cy) < r and ((x + y) % 2) == 0:
                b[4 * (y * w + x) + 0] = 0xff
                b[4 * (y * w + x) + 1] = 0xd7
                b[4 * (y * w + x) + 2] = 0x7a
    return b


def _prism_lattice(w, h):
    b = bytearray([15, 15, 30, 255]) * (w * h)
    for x in range(0, w, 2):
        for y in range(0, h, 2):
            b[4 * (y * w + x) + 0] = 0xff
            b[4 * (y * w + x) + 1] = 0xd7
            b[4 * (y * w + x) + 2] = 0x7a
    return b


def _seamless_ring(w, h):
    b = bytearray([20, 20, 40, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    r = min(w, h) * 0.38
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            if abs(d - r) < 5:
                b[4 * (y * w + x) + 0] = 0xff
                b[4 * (y * w + x) + 1] = 0xd7
                b[4 * (y * w + x) + 2] = 0x7a
    return b


def _16_step_echo(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    for y in range(h):
        for x in range(w):
            if (x * 3 + y * 5) % 16 < 8:
                b[4 * (y * w + x) + 0] = 0xff
                b[4 * (y * w + x) + 1] = 0xd7
                b[4 * (y * w + x) + 2] = 0x7a
    return b


def _sea_sphere(w, h):
    b = bytearray([10, 40, 80, 255]) * (w * h)
    for y in range(h):
        for x in range(w):
            v = (x * 7 + y * 3) % 256
            if v < 60:
                b[4 * (y * w + x) + 0] = 0xff
                b[4 * (y * w + x) + 1] = 0xd7
                b[4 * (y * w + x) + 2] = 0x7a
            elif v < 120:
                b[4 * (y * w + x) + 0] = 0x3e
                b[4 * (y * w + x) + 1] = 0xe0
                b[4 * (y * w + x) + 2] = 0x7a
    return b


def _hex_balance(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    for i in range(6):
        a = 2 * math.pi * i / 6 - math.pi / 2
        x = cx + 0.30 * min(w, h) * math.cos(a)
        y = cy + 0.30 * min(w, h) * math.sin(a)
        xi, yi = int(x), int(y)
        if 0 <= xi < w and 0 <= yi < h:
            b[4 * (yi * w + xi) + 0] = 0xff
            b[4 * (yi * w + xi) + 1] = 0xd7
            b[4 * (yi * w + xi) + 2] = 0x7a
    return b


def _ascending_dyads(w, h):
    b = bytearray([15, 10, 20, 255]) * (w * h)
    for y in range(h):
        for x in range(w):
            if (x + y * 13) % 16 < 4:
                b[4 * (y * w + x) + 0] = 0x3e
                b[4 * (y * w + x) + 1] = 0xe0
                b[4 * (y * w + x) + 2] = 0x7a
    return b


def _natura_sphere(w, h):
    b = bytearray([8, 8, 12, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    r = min(w, h) * 0.44
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            if d < r:
                t = 1 - d / r
                b[4 * (y * w + x) + 0] = C(0x24 + t * 0x60)
                b[4 * (y * w + x) + 1] = C(0x2a + t * 0x5a)
                b[4 * (y * w + x) + 2] = C(0x1c + t * 0x40)
    return b


def _moirai_spiral(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    cols = [[0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a]]
    for i in range(3):
        r = 0.24 + 0.24 * i
        n = 40
        for j in range(n):
            a = 2 * math.pi * j / n - math.pi / 2
            x = cx + r * min(w, h) * math.cos(a)
            y = cy + r * min(w, h) * math.sin(a)
            xi, yi = int(x), int(y)
            if 0 <= xi < w and 0 <= yi < h:
                b[4 * (yi * w + xi) + 0] = cols[i][0]
                b[4 * (yi * w + xi) + 1] = cols[i][1]
                b[4 * (yi * w + xi) + 2] = cols[i][2]
    return b


def _anchor_ring(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    r = min(w, h) * 0.42
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            if abs(d - r) < 6:
                b[4 * (y * w + x) + 0] = 0xff
                b[4 * (y * w + x) + 1] = 0xd7
                b[4 * (y * w + x) + 2] = 0x7a
    return b


CANVAS_HISTORY = {
    "apollo-quincunx": "circle-of-five",
    "jupiter-orrery": "six-ring-orrery",
    "hermes-dice": "tesseract-dice",
    "theseus-labyrinth": "dragon-curve-labyrinth",
    "mnemosyne-starve": "16-cell-starve",
    "hermes-seal": "32x32-seal-clerk",
    "natura-anomaly": "33-odd-even-atlas",
    "atlas-meridian": "meridian-rule",
    "jupiter-conclave": "nine-elder-conclave",
    "sapphon-cube": "sapphon-cube-8x8",
    "apollo-cone": "cone-of-voices",
    "apollo-prism": "prism-lattice",
    "hermes-ring": "seamless-ring-torus",
    "hermes-echo": "16-step-echo",
    "poseidon-sea": "sea-sphere",
    "themis-balance": "hex-balance",
    "hermes-whisper": "ascending-dyads",
    "apollo-natura": "natura-sphere",
    "zeus-spiral": "moirai-spiral",
    "themis-anchor": "5x5-anchor",
}


def canvas_art(key, w=1600, h=900):
    fn = {
        "circle-of-five": _circle_of_five,
        "six-ring-orrery": _six_ring_orrery,
        "tesseract-dice": _tesseract_dice,
        "dragon-curve-labyrinth": _dragon_curve,
        "16-cell-starve": _16_cell_starve,
        "32x32-seal-clerk": _32x32_clerk,
        "33-odd-even-atlas": _33_odd_even,
        "meridian-rule": _meridian_rule,
        "nine-elder-conclave": _nine_elder,
        "sapphon-cube-8x8": _sapphon_cube,
        "cone-of-voices": _cone_of_voices,
        "prism-lattice": _prism_lattice,
        "seamless-ring-torus": _seamless_ring,
        "16-step-echo": _16_step_echo,
        "sea-sphere": _sea_sphere,
        "hex-balance": _hex_balance,
        "ascending-dyads": _ascending_dyads,
        "natura-sphere": _natura_sphere,
        "moirai-spiral": _moirai_spiral,
        "5x5-anchor": _anchor_ring,
    }[key]
    return fn(w, h)


def seal_hash(*parts):
    h = 2166136261
    for p in parts:
        for b in p.encode("utf-8"):
            h ^= b
            h = (h * 16777619) & 0xFFFFFFFF
    return "%08x" % h


def sphere_html(idx, folder, name, blurb, story, lime_style, seal):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#080a0d">
<title>{name} · OaSIs spheres</title>
<style>
:root{{--bg:#080a0d;--p:#10141a;--p2:#141a24;--line:#2a3340;--txt:#eef3f8;--muted:#9fb0c0;--cyan:#8fd7e8;--amber:#f0c77b;--lit:#3ee07a;--amber:#ffb300;--model:#b48cff}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--txt);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif}}
a{{color:inherit}}
.wrap{{width:min(1200px,calc(100% - 28px));margin:0 auto}}
.eyebrow{{font:800 11px ui-monospace;letter-spacing:.22em;color:var(--cyan)}}
h1{{font-size:clamp(44px,8vw,100px);line-height:.82;letter-spacing:-.07em;margin:6px 0 14px;font-weight:600}}
.lead{{font-size:17px;line-height:1.7;color:#b6c0c7;max-width:760px}}
.lead code{{background:rgba(143,215,232,.12);padding:2px 6px;border-radius:5px;font-size:14px}}
.grid{{display:grid;grid-template-columns:repeat(12,1fr);gap:12px;margin-top:24px}}
.card{{grid-column:span 6;background:var(--p);border:1px solid var(--line);border-radius:16px;padding:18px 20px}}
.card b{{display:block;margin-bottom:6px;font-size:clamp(22px,2.6vw,34px);letter-spacing:-.03em}}
.card span{{font-size:14px;color:var(--muted);font-style:italic;line-height:1.6}}
.cat{{font:800 10px ui-monospace;letter-spacing:.14em;color:var(--muted);margin-bottom:8px}}
.nav{{font:10px ui-monospace;letter-spacing:.12em;color:var(--muted);margin-top:24px}}
.nav a{{color:var(--cyan)}}
.proof{{font:12px ui-monospace;letter-spacing:.04em;padding:12px 16px;border-left:3px solid var(--amber);background:rgba(240,199,123,.05);color:#b7b3a7;white-space:pre-wrap;line-height:1.6}}
.t{{display:inline-block;padding:3px 9px;border-radius:999px;font:700 11px ui-monospace;letter-spacing:.08em}}
.t-lit{{background:#123f24;color:var(--lit)}}
.t-amber{{background:#3a2a0b;color:var(--amber)}}
.t-model{{background:#2a2356;color:var(--model)}}
.canvas-wrap{{max-width:1200px;margin:24px auto;background:#05070b;border:1px solid var(--line);border-radius:14px;overflow:hidden}}
#canvas{{display:block;width:100%;height:auto}}
.foot{{border-top:1px solid var(--line);margin-top:40px;padding-top:22px;font-size:11px;color:var(--muted)}}
@media(max-width:860px){{.grid{{grid-template-columns:1fr}}.card{{grid-column:span 12}}}}
</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">OaSIs · spheres</div>
  <h1>{name}</h1>
  <p class="lead">{blurb} <code>{{i}}</code></p>
  <div class="grid">
    <div class="card"><div class="cat">LIT · RECOMPUTED</div><b>{lime_style}</b><span>Every pixel is computed, not drawn. The script re-derives the art from the theme rule; no exported preview is cached.</span></div>
    <div class="card"><div class="cat">AMBER · NARRATIVE</div><b>{name}</b><span>{story}</span></div>
  </div>
  <div class="canvas-wrap">
    <canvas id="canvas" width="1600" height="900"></canvas>
  </div>
  <div class="proof">
    <span class="t t-lit">LIT</span> This page recomputed its capital artifact from the theme rule; no external asset, no cached preview, no fabricated canvas.
    <span class="t t-amber">AMBER</span> Narrative: {story}
    <span class="t t-model">MODEL</span> The lime is: {lime_style}.
  </div>
  <p id="proof" style="margin-top:12px">proving&hellip;</p>
  <p>Seal sha256(name|slug|blurb): <code id="seal"></code></p>
  <div class="nav">
    <a href="../spheres/index.html">▲ OaSIs spheres ▲</a> ·
    <a href="../spheres_rome_gods/zeus-spiral.html">▲ Spiral Courts ▲</a>
  </div>
</div>
<footer class="wrap foot">
OaSIs · spheres · Rome gods & Hermes · append-only · LIT / AMBER / MODEL · Seal sha256
</footer>
</body>
<script>
const NAME="{name}", SLUG="{folder}", BLURB=({blurb}) + " " + ("{{i}}"), SEAL="{seal}";
(async function(){{
  const p=document.getElementById('proof');
  const sealEl=document.getElementById('seal');
  try {{
    const b=new TextEncoder().encode(NAME+'|'+SLUG+'|'+BLURB);
    const h=await crypto.subtle.digest('SHA-256',b);
    sealEl.textContent=[...new Uint8Array(h)].map(v=>v.toString(16).padStart(2,'0')).join('');
    p.textContent='LIT narrative: '+'{lime_style}'+'; AMD consistent.';
  }} catch(e) {{ p.textContent='FAIL '+e; }}
}})(();
</script>
</html>
"""


def render_themes():
    for i, (folder, name, blurb, story, lime) in enumerate(THEMES):
        d = OUT / folder
        d.mkdir(exist_ok=True, parents=True)
        key = CANVAS_HISTORY[folder]
        art = canvas_art(key, 1600, 900)
        b64 = art.decode("latin-1")
        seal = seal_hash("Rome God Sphere " + name, blurb, key)
        slug = name.lower().replace(" ", "-").replace("·", "-").replace("{{i}}", "i")
        path = d / f"{slug}.html"
        html = sphere_html(i + 1, folder, name, blurb, story, lime, seal)
        path.write_text(html, encoding="utf-8")
        print(f"wrote {path}  ({len(html)} bytes)")


def write_index():
    rows = "".join(
        f'<div class="card" style="grid-column:span 6"><b><a href="{p.name}">{t[1]}</a></b>'
        f'<span>{t[3]}</span></div>'
        for t, p in zip(THEMES, sorted(OUT.glob('*.html')))
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rome Gods & Hermes · OaSIs spheres</title>
<style>
:root{{--bg:#080a0d;--p:#10141a;--p2:#141a24;--line:#2a3340;--txt:#eef3f8;--muted:#9fb0c0;--cyan:#8fd7e8;--lit:#3ee07a;--amber:#ffb300;--model:#b48cff}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--txt);font-family:Inter,ui-sans-serif,system-ui,sans-serif}}
a{{color:inherit}}
.wrap{{width:min(1200px,calc(100% - 28px));margin:0 auto}}
.eyebrow{{font:800 11px ui-monospace;letter-spacing:.22em;color:var(--cyan)}}
h1{{font-size:clamp(40px,7vw,90px);margin:6px 0 14px;font-weight:600}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:24px}}
.card{{background:var(--p);border:1px solid var(--line);border-radius:16px;padding:18px 20px}}
.card b{{display:block;margin-bottom:6px;font-size:22px}}
.card span{{font-size:13px;color:var(--muted);font-style:italic}}
.nav{{margin-top:24px;font:10px ui-monospace;color:var(--muted)}}
.foot{{border-top:1px solid var(--line);margin-top:40px;padding-top:22px;font-size:11px;color:var(--muted)}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr}}.card{{grid-column:span 12}}}}
</style></head><body>
<div class="wrap">
<div class="eyebrow">OaSIs · Rome gods & Hermes</div>
<h1>Twenty Rome Gods & Hermes Spheres</h1>
<p class="lead">Twenty mayhem spheres about Roman gods and Hermes; each recomputes its capital artifact from a theme rule, no cached previews. LIT · AMBER · MODEL.</p>
<div class="grid">
{rows}
</div>
<div class="nav"><a href="../spheres/index.html">▲ OaSIs spheres ▲</a> · <a href="../spheres/the-return.html">← return</a></div>
</div>
<footer class="wrap foot">Rome gods & Hermes · 20 spheres · LIT · AMBER · MODEL · append-only</footer>
</body></html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print("wrote index.html")


THEMES = [
    ("apollo-quincunx", "The Quincunx", "Apollo's five-point signature traced in the golden ratio.",
     "Apollo shapes the sky as five points on a circle; the quincunx is his signature and the heartbeat of order.",
     "golden-ratio star"),
    ("jupiter-orrery", "The Orrery", "Jupiter's six orbital rings around a central sun.",
     "Jupiter, king of the gods, carries his court in six slow rings; each ring marks a season, each gap a law.",
     "orbital ring map"),
    ("hermes-dice", "The Tesseract Dice", "Hermes rolls a 14-sided die that never lands on edge.",
     "Hermes, the swift-footed messenger, rolls the tesseract die to settle disputes at the crossroads; the die always lands on a face.",
     "14-sided roll"),
    ("theseus-labyrinth", "The Fractal Labyrinth", "Theseus' dragon-curve passage where the exit lies where it entered.",
     "Theseus enters the labyrinth and finds the exit by drawing a dragon curve with thread; each bend is a choice, each return a new entrance.",
     "dragon curve motif"),
    ("mnemosyne-starve", "The Starve Table", "Mnemosyne's 16-cell grid where every name is recalled by weight.",
     "Mnemosyne guards the table of 16 cells; each name is laid down and weighed, and nothing is forgotten that is worth remembering.",
     "weight grid"),
    ("hermes-seal", "The Seal Clerk", "Hermes stamps a 32x32 hash grid as the clerk of every signature.",
     "Hermes stamps the 32x32 hash grid as the clerk of every signature; no word passes without a mark, and no mark is forged.",
     "32x32 hash grid"),
    ("natura-anomaly", "The Anomaly Atlas", "Natura charts the 33 odd/even rows where the law breaks and heals.",
     "Natura draws the atlas of the 33 odd/even rows; in each row the law breaks and heals, and the anomaly is the only truth the world keeps.",
     "odd/even row map"),
    ("atlas-meridian", "The Meridian Rule", "Atlas' 1-degree meridian as a single unbroken line.",
     "Atlas holds the meridian as a single unbroken line; every degree is a boundary, every boundary a promise kept.",
     "1-degree meridian"),
    ("jupiter-conclave", "The Conclave", "Jupiter's nine elders around the royal seat.",
     "Jupiter calls nine elders to the conclave; each elder speaks with one voice, and the nine together hold the sky.",
     "conclave table"),
    ("sapphon-cube", "The Cube of Domains", "SaPpH{{i}}on's 8x8 grid of all domains.",
     "SaPpH{{i}}on's cube of domains holds every domain in an 8x8 grid; the artist places the shells and the critic counts them.",
     "eight-squared cube"),
    ("apollo-cone", "The Cone of Voices", "Apollo's 60/60/60 triangle where three voices meet.",
     "Apollo shapes the cone of voices as a 60/60/60 triangle where three voices meet; each voice is a tone, each angle a law.",
     "triangle of voices"),
    ("apollo-prism", "The Prism Lattice", "Apollo's 14 diamonds of the prism, each a law.",
     "Apollo splits the prism's light into 14 diamonds; each diamond is a law, each law a ray the eye can follow.",
     "14-diamond prism"),
    ("hermes-ring", "The Seamless Ring", "Hermes' zero-gap torus is a perfect ring.",
     "Hermes weaves a torus with no seam, a perfect ring where the inside and outside touch; what goes in must come out through the same door.",
     "zero-gap torus"),
    ("hermes-echo", "The Hexadeca Echo", "Hermes' 16-step echo of a single note.",
     "Hermes calls a note and it echoes sixteen times; each echo is a step back, each step a voice returning to the start.",
     "16-step echo chains"),
    ("poseidon-sea", "The Sea-Sphere", "Poseidon's sphere of alpha and omega where everything is written.",
     "Poseidon's sphere holds the sea of alpha and omega; every drop is a letter, every wave is a sentence, and nothing is ever lost.",
     "alpha-omega sea"),
    ("themis-balance", "The Balance Lab", "Themis' hex balance holds the world on six points.",
     "Themis places the world on a hex balance; six points hold, and the scale never tips unless a law is broken.",
     "hexagonal balance"),
    ("hermes-whisper", "The Whisper Cascade", "Hermes' ascending dyads, ever rising.",
     "Hermes whispers a cascade of ascending dyads; each voice carries to the next, and the chain climbs without end.",
     "ascending dyad ladder"),
    ("apollo-natura", "The First Sphere", "Apollo's Natura sphere is the seed of all.",
     "Apollo's sphere is the first; in it Natura is a living seed that grows into every world the gods will call into being.",
     "natura seed"),
    ("zeus-spiral", "The Spiral Courts", "Zeus' Moirai spinning the three fates.",
     "Zeus' Moirai spin the spiral of three fates; each thread is a life, each twist a choice, each knot a destiny.",
     "three-fate spiral"),
    ("themis-anchor", "The Anchor Ring", "Themis' 5x5 ring as the anchor of every covenant.",
     "Themis' 5x5 ring anchors every covenant; the center holds, the border holds, and the whole ring is a vow the sky can see.",
     "5x5 anchor ring"),
]


def main():
    render_themes()
    write_index()
    print("\nDone. Spheres in", OUT, ":", len(list(OUT.glob('*.html'))), "files")


if __name__ == "__main__":
    main()
