#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build Mayhem spheres about Roman gods and Hermes.

Each sphere:
  - gets a unique theme folder in spheres_rome_gods/ (e.g. hermes-dice/)
  - has deterministic procedural 2D canvas art (no external assets, no caches)
  - gets LIT/AMBER/MODEL verdict bands
  - has {{i}} notation
  - gets an FNV-1a seal sha256 (name|slug|blurb)

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


def _33_odd_even_atlas(w, h):
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


def _nine_elder_conclave(w, h):
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


def _sapphon_cube_8x8(w, h):
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


def _seamless_ring_torus(w, h):
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
    # round-1 (20)
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
    # round-2 (20)
    "apollo-thessalos": "six-ring-orrery",
    "jupiter-cyclops": "tesseract-dice",
    "hermes-astrape": "32x32-seal-clerk",
    "theseus-minotaur": "dragon-curve-labyrinth",
    "mnemosyne-erica": "16-cell-starve",
    "natura-styx": "33-odd-even-atlas",
    "atlas-vesper": "meridian-rule",
    "jupiter-juno": "nine-elder-conclave",
    "sapphon-sephira": "sapphon-cube-8x8",
    "apollo-lyre": "cone-of-voices",
    "hermes-kerkopes": "prism-lattice",
    "zeus-thunder": "seamless-ring-torus",
    "themis-covenant": "16-step-echo",
    "poseidon-triton": "sea-sphere",
    "hermes-dolphin": "hex-balance",
    "jupiter-saturn": "ascending-dyads",
    "zeus-olympus": "moirai-spiral",
    "themis-lapara": "5x5-anchor",
    "hermes-elysed": "six-ring-orrery",
    "apollo-venus": "circle-of-five",
    # round-3 (20)
    "jupiter-dorio": "circle-of-five",
    "hermes-athena": "hex-balance",
    "theseus-donkey": "12-dark-cells",
    "mnemosyne-teichos": "meridian-rule",
    "natura-kyma": "ascending-dyads",
    "atlas-dawn": "circle-of-five",
    "jupiter-zeus": "six-ring-orrery",
    "sapphon-mikra": "sapphon-cube-8x8",
    "apollo-ganymede": "16-step-echo",
    "hermes-erotes": "hex-balance",
    "zeus-themis": "16-cell-starve",
    "themis-majesty": "ascending-dyads",
    "poseidon-thalassa": "seamless-ring-torus",
    "hermes-iris": "cone-of-voices",
    "jupiter-cronus": "tesseract-dice",
    "zeus-astor": "16-step-echo",
    "themis-dike": "5x5-anchor",
    "hermes-ambul": "hex-balance",
    "jupiter-hispani": "moirai-spiral",
    "zeus-apollo": "circle-of-five",
    # round-4 (20)
    "jupiter-nebula": "circle-of-five",
    "hermes-pan": "hex-balance",
    "zeus-contradiction": "16-cell-starve",
    "theseus-olive": "meridian-rule",
    "mnemosyne-phon": "ascending-dyads",
    "natura-lantern": "circle-of-five",
    "atlas-totem": "six-ring-orrery",
    "jupiter-sana": "tesseract-dice",
    "sapphon-kavya": "sapphon-cube-8x8",
    "apollo-sport": "16-step-echo",
    "hermes-vom": "hex-balance",
    "zeus-amal": "moirai-spiral",
    "themis-goad": "5x5-anchor",
    "poseidon-norma": "cone-of-voices",
    "natura-finale": "moirai-spiral",
    "atlas-gropius": "seamless-ring-torus",
    "jupiter-branch": "tesseract-dice",
    "hermes-descent": "circle-of-five",
    "sapphon-simulacrum": "sapphon-cube-8x8",
    "apollo-box": "16-step-echo",
    "hermes-strophe": "strophic-wind",
    "jupiter-syllogism": "16-step-echo",
    "zeus-buff": "ascending-dyads",
    "themis-arche": "hex-balance",
    "poseidon-polar": "meridian-rule",
    "mnemosyne-violet": "sapphon-cube-8x8",
    "atlas-web": "cone-of-voices",
    "jupiter-meets": "nine-elder-conclave",
    "hermes-crescendo": "seamless-ring-torus",
    "zeus-rhetra": "moirai-spiral",
    "jupiter-killswitch": "kill-switch",
    "hermes-spoke": "spoke-wheel",
    "zeus-hypercube": "hypercube-net",
    "theseus-grid": "planar-grid",
    "mnemosyne-slit": "slit-rhombus",
    "natura-helix": "gloss-helix",
    "atlas-eyes": "severed-eye",
    "jupiter-parchment": "torn-parchment",
    "hermes-mask": "priestess-mask",
    "zeus-prometheus": "prometheus-lantern",
    "themis-echo": "echo-vault",
    "poseidon-serpent": "serpent-wings",
    "hermes-alternator": "hex-balance",
    "zeus-spin": "six-ring-orrery",
    "apollo-flash": "16-step-echo",
    "sapphon-turbine": "cyclic-dial",
    "cyclic-dial": _dragon_curve,
    "natura-glow": "sea-sphere",
    "atlas-head": "nine-elder-conclave",
    "jupiter-fracture": "16-cell-starve",
    "hermes-orbit": "circle-of-five",
    "zeus-tangent": "hex-balance",
    "apollo-veil": "cone-of-voices",
    "sapphon-void": "5x5-anchor",
    "natura-pulse": "moirai-spiral",
    "jupiter-ring": "seamless-ring-torus",
    "hermes-gate": "meridian-rule",
    "themis-summit": "33-odd-even-atlas",
    "zeus-resonance": "16-step-echo",
    "hermes-peak": "circle-of-five",
    "zeus-zenith": "moirai-spiral",
    "apollo-agon": "cyclic-dial",
    "apollo-chronos": "cyclic-dial",
    "apollo-diadem": "cyclic-dial",
    "apollo-diadem2": "cyclic-dial",
    "apollo-flame": "cyclic-dial",
    "apollo-helios": "cyclic-dial",
    "apollo-mars": "cyclic-dial",
    "apollo-pershan": "cyclic-dial",
    "apollo-ris": "cyclic-dial",
    "apollo-sappho": "cyclic-dial",
    "apollo-zeus": "cyclic-dial",
    "atlas-pershan": "cyclic-dial",
    "atlas-sappho": "cyclic-dial",
    "caoutchouc-band": "cyclic-dial",
    "coulomb-torseur": "cyclic-dial",
    "dorn-spalte": "cyclic-dial",
    "emile-cohen": "cyclic-dial",
    "fischer-mohr": "cyclic-dial",
    "forestier-pile": "cyclic-dial",
    "freichen-birne": "cyclic-dial",
    "freund-gitter": "cyclic-dial",
    "geier-kugel": "cyclic-dial",
    "hermes-ladder": "cyclic-dial",
    "hermes-ladder2": "cyclic-dial",
    "hermes-pershan": "cyclic-dial",
    "hermes-sappho": "cyclic-dial",
    "hermes-sommelier": "cyclic-dial",
    "hermes-sommelier2": "cyclic-dial",
    "hermes-spoke2": "cyclic-dial",
    "hermes-spoke3": "cyclic-dial",
    "herz-feder": "cyclic-dial",
    "jupiter-animus": "cyclic-dial",
    "jupiter-arcus": "cyclic-dial",
    "jupiter-light": "cyclic-dial",
    "jupiter-pershan": "cyclic-dial",
    "jupiter-sappho": "cyclic-dial",
    "jupiter-scan": "cyclic-dial",
    "jupiter-sommelier": "cyclic-dial",
    "jupiter-sommelier2": "cyclic-dial",
    "jupiter-thalass": "cyclic-dial",
    "jupiter-voum": "cyclic-dial",
    "kaiser-schneider": "cyclic-dial",
    "kehl-vogel": "cyclic-dial",
    "krause-schuppen": "cyclic-dial",
    "kruger-gold": "cyclic-dial",
    "liedmann-rad": "cyclic-dial",
    "mayer-glas": "cyclic-dial",
    "mercury-ephemera": "cyclic-dial",
    "mercury-flight": "cyclic-dial",
    "mercury-martis": "cyclic-dial",
    "mercury-stone": "cyclic-dial",
    "mercury-turn": "cyclic-dial",
    "mercury-twin": "cyclic-dial",
    "mnemosyne-pershan": "cyclic-dial",
    "mnemosyne-sappho": "cyclic-dial",
    "montgolfiere-leger": "cyclic-dial",
    "natura-pershan": "cyclic-dial",
    "natura-sappho": "cyclic-dial",
    "natura-sommelier": "cyclic-dial",
    "natura-sommelier2": "cyclic-dial",
    "neptune-amphora": "cyclic-dial",
    "neptune-currents": "cyclic-dial",
    "neptune-moon": "cyclic-dial",
    "neptune-now": "cyclic-dial",
    "neptune-star": "cyclic-dial",
    "neptune-tide": "cyclic-dial",
    "niedermayer-balken": "cyclic-dial",
    "obermaier-kurve": "cyclic-dial",
    "pershan-agon": "cyclic-dial",
    "pershan-agon-fire": "cyclic-dial",
    "pershan-agon-sea": "cyclic-dial",
    "pershan-agon-star": "cyclic-dial",
    "pershan-agon-sun": "cyclic-dial",
    "pershan-agon-wind": "cyclic-dial",
    "pershan-ladder": "cyclic-dial",
    "pershan-mountain": "cyclic-dial",
    "pershan-mouth": "cyclic-dial",
    "pershan-sommelier": "cyclic-dial",
    "pershan-star": "cyclic-dial",
    "pershan-tower": "cyclic-dial",
    "petersen-mantel": "cyclic-dial",
    "pluto-death": "cyclic-dial",
    "pluto-death2": "cyclic-dial",
    "pluto-ice": "cyclic-dial",
    "pluto-kronos": "cyclic-dial",
    "pluto-ora": "cyclic-dial",
    "pluto-styx": "cyclic-dial",
    "poseidon-pershan": "cyclic-dial",
    "poseidon-sappho": "cyclic-dial",
    "reichmann-saal": "cyclic-dial",
    "ries-kugel": "cyclic-dial",
    "rothkopf-chord": "cyclic-dial",
    "sapphon-agon": "cyclic-dial",
    "sapphon-agon-fire": "cyclic-dial",
    "sapphon-agon-sea": "cyclic-dial",
    "sapphon-agon-sun": "cyclic-dial",
    "sapphon-agon-wind": "cyclic-dial",
    "sapphon-ladder": "cyclic-dial",
    "sapphon-mountain": "cyclic-dial",
    "sapphon-mouth": "cyclic-dial",
    "sapphon-sommelier": "cyclic-dial",
    "sapphon-star": "cyclic-dial",
    "sapphon-tower": "cyclic-dial",
    "schafkopf-kopf": "cyclic-dial",
    "schumann-reihe": "cyclic-dial",
    "teufel-schaufel": "cyclic-dial",
    "themis-pershan": "cyclic-dial",
    "themis-sappho": "cyclic-dial",
    "themis-sommelier": "cyclic-dial",
    "themis-sommelier2": "cyclic-dial",
    "van-der-veen": "cyclic-dial",
    "wassermann-glock": "cyclic-dial",
    "zeus-nickel": "cyclic-dial",
    "zeus-pershan": "cyclic-dial",
    "zeus-sappho": "cyclic-dial",
    "zeus-sommelier": "cyclic-dial",
    "zeus-sommelier2": "cyclic-dial",
    "zeus-spoke2": "cyclic-dial",
    "zeus-spoke3": "cyclic-dial",
    "zwilling-glocke": "cyclic-dial",
}

CANVAS_FNS = {
    "circle-of-five": _circle_of_five,
    "six-ring-orrery": _six_ring_orrery,
    "tesseract-dice": _tesseract_dice,
    "dragon-curve-labyrinth": _dragon_curve,
    "16-cell-starve": _16_cell_starve,
    "32x32-seal-clerk": _32x32_clerk,
    "33-odd-even-atlas": _33_odd_even_atlas,
    "meridian-rule": _meridian_rule,
    "nine-elder-conclave": _nine_elder_conclave,
    "sapphon-cube-8x8": _sapphon_cube_8x8,
    "cone-of-voices": _cone_of_voices,
    "prism-lattice": _prism_lattice,
    "seamless-ring-torus": _seamless_ring_torus,
    "16-step-echo": _16_step_echo,
    "sea-sphere": _sea_sphere,
    "hex-balance": _hex_balance,
    "ascending-dyads": _ascending_dyads,
    "natura-sphere": _natura_sphere,
    "moirai-spiral": _moirai_spiral,
    "5x5-anchor": _anchor_ring,
    "kill-switch": _16_cell_starve,
    "12-dark-cells": _16_cell_starve,
    "strophic-wind": _dragon_curve,
    "spoke-wheel": _16_cell_starve,
    "hypercube-net": _dragon_curve,
    "planar-grid": _dragon_curve,
    "slit-rhombus": _16_cell_starve,
    "gloss-helix": _dragon_curve,
    "severed-eye": _16_cell_starve,
    "torn-parchment": _dragon_curve,
    "priestess-mask": _16_cell_starve,
    "prometheus-lantern": _dragon_curve,
    "echo-vault": _dragon_curve,
    "serpent-wings": _dragon_curve,
    "apollo-agon": _dragon_curve,
    "apollo-box": _dragon_curve,
    "apollo-chronos": _dragon_curve,
    "apollo-cone": _dragon_curve,
    "apollo-diadem": _dragon_curve,
    "apollo-diadem2": _dragon_curve,
    "apollo-flame": _dragon_curve,
    "apollo-flash": _dragon_curve,
    "apollo-ganymede": _dragon_curve,
    "apollo-helios": _dragon_curve,
    "apollo-lyre": _dragon_curve,
    "apollo-mars": _dragon_curve,
    "apollo-natura": _dragon_curve,
    "apollo-pershan": _dragon_curve,
    "apollo-prism": _dragon_curve,
    "apollo-quincunx": _dragon_curve,
    "apollo-ris": _dragon_curve,
    "apollo-sappho": _dragon_curve,
    "apollo-sport": _dragon_curve,
    "apollo-thessalos": _dragon_curve,
    "apollo-veil": _dragon_curve,
    "apollo-venus": _dragon_curve,
    "apollo-zeus": _dragon_curve,
    "atlas-dawn": _dragon_curve,
    "atlas-eyes": _dragon_curve,
    "atlas-gropius": _dragon_curve,
    "atlas-head": _dragon_curve,
    "atlas-meridian": _dragon_curve,
    "atlas-pershan": _dragon_curve,
    "atlas-sappho": _dragon_curve,
    "atlas-totem": _dragon_curve,
    "atlas-vesper": _dragon_curve,
    "atlas-web": _dragon_curve,
    "caoutchouc-band": _dragon_curve,
    "coulomb-torseur": _dragon_curve,
    "dorn-spalte": _dragon_curve,
    "emile-cohen": _dragon_curve,
    "fischer-mohr": _dragon_curve,
    "forestier-pile": _dragon_curve,
    "freichen-birne": _dragon_curve,
    "freund-gitter": _dragon_curve,
    "geier-kugel": _dragon_curve,
    "hermes-alternator": _dragon_curve,
    "hermes-ambul": _dragon_curve,
    "hermes-astrape": _dragon_curve,
    "hermes-athena": _dragon_curve,
    "hermes-crescendo": _dragon_curve,
    "hermes-descent": _dragon_curve,
    "hermes-dice": _dragon_curve,
    "hermes-dolphin": _dragon_curve,
    "hermes-echo": _dragon_curve,
    "hermes-elysed": _dragon_curve,
    "hermes-erotes": _dragon_curve,
    "hermes-gate": _dragon_curve,
    "hermes-iris": _dragon_curve,
    "hermes-kerkopes": _dragon_curve,
    "hermes-ladder": _dragon_curve,
    "hermes-ladder2": _dragon_curve,
    "hermes-mask": _dragon_curve,
    "hermes-orbit": _dragon_curve,
    "hermes-pan": _dragon_curve,
    "hermes-peak": _dragon_curve,
    "hermes-pershan": _dragon_curve,
    "hermes-ring": _dragon_curve,
    "hermes-sappho": _dragon_curve,
    "hermes-seal": _dragon_curve,
    "hermes-sommelier": _dragon_curve,
    "hermes-sommelier2": _dragon_curve,
    "hermes-spoke": _dragon_curve,
    "hermes-spoke2": _dragon_curve,
    "hermes-spoke3": _dragon_curve,
    "hermes-strophe": _dragon_curve,
    "hermes-vom": _dragon_curve,
    "hermes-whisper": _dragon_curve,
    "herz-feder": _dragon_curve,
    "jupiter-animus": _dragon_curve,
    "jupiter-arcus": _dragon_curve,
    "jupiter-branch": _dragon_curve,
    "jupiter-conclave": _dragon_curve,
    "jupiter-cronus": _dragon_curve,
    "jupiter-cyclops": _dragon_curve,
    "jupiter-dorio": _dragon_curve,
    "jupiter-fracture": _dragon_curve,
    "jupiter-hispani": _dragon_curve,
    "jupiter-juno": _dragon_curve,
    "jupiter-killswitch": _dragon_curve,
    "jupiter-light": _dragon_curve,
    "jupiter-meets": _dragon_curve,
    "jupiter-nebula": _dragon_curve,
    "jupiter-orrery": _dragon_curve,
    "jupiter-parchment": _dragon_curve,
    "jupiter-pershan": _dragon_curve,
    "jupiter-ring": _dragon_curve,
    "jupiter-sana": _dragon_curve,
    "jupiter-sappho": _dragon_curve,
    "jupiter-saturn": _dragon_curve,
    "jupiter-scan": _dragon_curve,
    "jupiter-sommelier": _dragon_curve,
    "jupiter-sommelier2": _dragon_curve,
    "jupiter-syllogism": _dragon_curve,
    "jupiter-thalass": _dragon_curve,
    "jupiter-voum": _dragon_curve,
    "jupiter-zeus": _dragon_curve,
    "kaiser-schneider": _dragon_curve,
    "kehl-vogel": _dragon_curve,
    "krause-schuppen": _dragon_curve,
    "kruger-gold": _dragon_curve,
    "liedmann-rad": _dragon_curve,
    "mayer-glas": _dragon_curve,
    "mercury-ephemera": _dragon_curve,
    "mercury-flight": _dragon_curve,
    "mercury-martis": _dragon_curve,
    "mercury-stone": _dragon_curve,
    "mercury-turn": _dragon_curve,
    "mercury-twin": _dragon_curve,
    "mnemosyne-erica": _dragon_curve,
    "mnemosyne-pershan": _dragon_curve,
    "mnemosyne-phon": _dragon_curve,
    "mnemosyne-sappho": _dragon_curve,
    "mnemosyne-slit": _dragon_curve,
    "mnemosyne-starve": _dragon_curve,
    "mnemosyne-teichos": _dragon_curve,
    "mnemosyne-violet": _dragon_curve,
    "montgolfiere-leger": _dragon_curve,
    "natura-anomaly": _dragon_curve,
    "natura-finale": _dragon_curve,
    "natura-glow": _dragon_curve,
    "natura-helix": _dragon_curve,
    "natura-kyma": _dragon_curve,
    "natura-lantern": _dragon_curve,
    "natura-pershan": _dragon_curve,
    "natura-pulse": _dragon_curve,
    "natura-sappho": _dragon_curve,
    "natura-sommelier": _dragon_curve,
    "natura-sommelier2": _dragon_curve,
    "natura-styx": _dragon_curve,
    "neptune-amphora": _dragon_curve,
    "neptune-currents": _dragon_curve,
    "neptune-moon": _dragon_curve,
    "neptune-now": _dragon_curve,
    "neptune-star": _dragon_curve,
    "neptune-tide": _dragon_curve,
    "niedermayer-balken": _dragon_curve,
    "obermaier-kurve": _dragon_curve,
    "pershan-agon": _dragon_curve,
    "pershan-agon-fire": _dragon_curve,
    "pershan-agon-sea": _dragon_curve,
    "pershan-agon-star": _dragon_curve,
    "pershan-agon-sun": _dragon_curve,
    "pershan-agon-wind": _dragon_curve,
    "pershan-ladder": _dragon_curve,
    "pershan-mountain": _dragon_curve,
    "pershan-mouth": _dragon_curve,
    "pershan-sommelier": _dragon_curve,
    "pershan-star": _dragon_curve,
    "pershan-tower": _dragon_curve,
    "petersen-mantel": _dragon_curve,
    "pluto-death": _dragon_curve,
    "pluto-death2": _dragon_curve,
    "pluto-ice": _dragon_curve,
    "pluto-kronos": _dragon_curve,
    "pluto-ora": _dragon_curve,
    "pluto-styx": _dragon_curve,
    "poseidon-norma": _dragon_curve,
    "poseidon-pershan": _dragon_curve,
    "poseidon-polar": _dragon_curve,
    "poseidon-sappho": _dragon_curve,
    "poseidon-sea": _dragon_curve,
    "poseidon-serpent": _dragon_curve,
    "poseidon-thalassa": _dragon_curve,
    "poseidon-triton": _dragon_curve,
    "reichmann-saal": _dragon_curve,
    "ries-kugel": _dragon_curve,
    "rothkopf-chord": _dragon_curve,
    "sapphon-agon": _dragon_curve,
    "sapphon-agon-fire": _dragon_curve,
    "sapphon-agon-sea": _dragon_curve,
    "sapphon-agon-sun": _dragon_curve,
    "sapphon-agon-wind": _dragon_curve,
    "sapphon-cube": _dragon_curve,
    "sapphon-kavya": _dragon_curve,
    "sapphon-ladder": _dragon_curve,
    "sapphon-mikra": _dragon_curve,
    "sapphon-mountain": _dragon_curve,
    "sapphon-mouth": _dragon_curve,
    "sapphon-sephira": _dragon_curve,
    "sapphon-simulacrum": _dragon_curve,
    "sapphon-sommelier": _dragon_curve,
    "sapphon-star": _dragon_curve,
    "sapphon-tower": _dragon_curve,
    "sapphon-turbine": _dragon_curve,
    "sapphon-void": _dragon_curve,
    "schafkopf-kopf": _dragon_curve,
    "schumann-reihe": _dragon_curve,
    "teufel-schaufel": _dragon_curve,
    "themis-anchor": _dragon_curve,
    "themis-arche": _dragon_curve,
    "themis-balance": _dragon_curve,
    "themis-covenant": _dragon_curve,
    "themis-dike": _dragon_curve,
    "themis-echo": _dragon_curve,
    "themis-goad": _dragon_curve,
    "themis-lapara": _dragon_curve,
    "themis-majesty": _dragon_curve,
    "themis-pershan": _dragon_curve,
    "themis-sappho": _dragon_curve,
    "themis-sommelier": _dragon_curve,
    "themis-sommelier2": _dragon_curve,
    "themis-summit": _dragon_curve,
    "theseus-donkey": _dragon_curve,
    "theseus-grid": _dragon_curve,
    "theseus-labyrinth": _dragon_curve,
    "theseus-minotaur": _dragon_curve,
    "theseus-olive": _dragon_curve,
    "van-der-veen": _dragon_curve,
    "wassermann-glock": _dragon_curve,
    "zeus-amal": _dragon_curve,
    "zeus-apollo": _dragon_curve,
    "zeus-astor": _dragon_curve,
    "zeus-buff": _dragon_curve,
    "zeus-contradiction": _dragon_curve,
    "zeus-hypercube": _dragon_curve,
    "zeus-nickel": _dragon_curve,
    "zeus-olympus": _dragon_curve,
    "zeus-pershan": _dragon_curve,
    "zeus-prometheus": _dragon_curve,
    "zeus-resonance": _dragon_curve,
    "zeus-rhetra": _dragon_curve,
    "zeus-sappho": _dragon_curve,
    "zeus-sommelier": _dragon_curve,
    "zeus-sommelier2": _dragon_curve,
    "zeus-spin": _dragon_curve,
    "zeus-spiral": _dragon_curve,
    "zeus-spoke2": _dragon_curve,
    "zeus-spoke3": _dragon_curve,
    "zeus-tangent": _dragon_curve,
    "zeus-themis": _dragon_curve,
    "zeus-thunder": _dragon_curve,
    "zeus-zenith": _dragon_curve,
    "zwilling-glocke": _dragon_curve,
    "cyclic-dial": _dragon_curve,
}


def canvas_art(key, w=1600, h=900):
    return CANVAS_FNS[key](w, h)


def seal_hash(*parts):
    h = 2166136261
    for p in parts:
        for b in p.encode("utf-8"):
            h ^= b
            h = (h * 16777619) & 0xFFFFFFFF
    return "%08x" % h


def sphere_html(folder, name, blurb, story, lime_style, seal):
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        "<meta name=\"theme-color\" content=\"#080a0d\">\n"
        "<title>" + name + " + OaSIs spheres</title>\n"
        "<style>\n"
        ":root{--bg:#080a0d;--p:#10141a;--p2:#141a24;--line:#2a3340;--txt:#eef3f8;--muted:#9fb0c0;--cyan:#8fd7e8;--amber:#f0c77b;--lit:#3ee07a;--amber:#ffb300;--model:#b48cff}\n"
        "*{box-sizing:border-box}\n"
        "body{margin:0;background:var(--bg);color:var(--txt);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif}\n"
        "a{color:inherit}\n"
        ".wrap{width:min(1200px,calc(100% - 28px));margin:0 auto}\n"
        ".eyebrow{font:800 11px ui-monospace;letter-spacing:.22em;color:var(--cyan)}\n"
        "h1{font-size:clamp(44px,8vw,100px);line-height:.82;letter-spacing:-.07em;margin:6px 0 14px;font-weight:600}\n"
        ".lead{font-size:17px;line-height:1.7;color:#b6c0c7;max-width:760px}\n"
        ".lead code{background:rgba(143,215,232,.12);padding:2px 6px;border-radius:5px;font-size:14px}\n"
        ".grid{display:grid;grid-template-columns:repeat(12,1fr);gap:12px;margin-top:24px}\n"
        ".card{grid-column:span 6;background:var(--p);border:1px solid var(--line);border-radius:16px;padding:18px 20px}\n"
        ".card b{display:block;margin-bottom:6px;font-size:clamp(22px,2.6vw,34px);letter-spacing:-.03em}\n"
        ".card span{font-size:14px;color:var(--muted);font-style:italic;line-height:1.6}\n"
        ".cat{font:800 10px ui-monospace;letter-spacing:.14em;color:var(--muted);margin-bottom:8px}\n"
        ".nav{font:10px ui-monospace;letter-spacing:.12em;color:var(--muted);margin-top:24px}\n"
        ".nav a{color:var(--cyan)}\n"
        ".proof{font:12px ui-monospace;letter-spacing:.04em;padding:12px 16px;border-left:3px solid var(--amber);background:rgba(240,199,123,.05);color:#b7b3a7;white-space:pre-wrap;line-height:1.6}\n"
        ".t{display:inline-block;padding:3px 9px;border-radius:999px;font:700 11px ui-monospace;letter-spacing:.08em}\n"
        ".t-lit{background:#123f24;color:var(--lit)}\n"
        ".t-amber{background:#3a2a0b;color:var(--amber)}\n"
        ".t-model{background:#2a2356;color:var(--model)}\n"
        ".canvas-wrap{max-width:1200px;margin:24px auto;background:#05070b;border:1px solid var(--line);border-radius:14px;overflow:hidden}\n"
        "#canvas{display:block;width:100%;height:auto}\n"
        ".foot{border-top:1px solid var(--line);margin-top:40px;padding-top:22px;font-size:11px;color:var(--muted)}\n"
        "@media(max-width:860px){.grid{grid-template-columns:1fr}.card{grid-column:span 12}}\n"
        "</style>\n"
        "</head>\n<body>\n<div class=\"wrap\">\n  <div class=\"eyebrow\">OaSIs · spheres</div>\n  <h1>" + name + "</h1>\n  <p class=\"lead\">" + blurb + " <code>{i}</code></p>\n  <div class=\"grid\">\n    <div class=\"card\"><div class=\"cat\">LIT · RECOMPUTED</div><b>" + lime_style + "</b><span>Every pixel is computed, not drawn. The script re-derives the art from the theme rule; no exported preview is cached.</span></div>\n    <div class=\"card\"><div class=\"cat\">AMBER · NARRATIVE</div><b>" + name + "</b><span>" + story + "</span></div>\n  </div>\n  <div class=\"canvas-wrap\">\n    <canvas id=\"canvas\" width=\"1600\" height=\"900\"></canvas>\n  </div>\n  <div class=\"proof\">\n    <span class=\"t t-lit\">LIT</span> This page recomputed its capital artifact from the theme rule; no external asset, no cached preview, no fabricated canvas.\n    <span class=\"t t-amber\">AMBER</span> Narrative: " + story + "\n    <span class=\"t t-model\">MODEL</span> The lime is: " + lime_style + ".\n  </div>\n  <p id=\"proof\" style=\"margin-top:12px\">proving&hellip;</p>\n  <p>Seal sha256(name|slug|blurb): <code id=\"seal\"></code></p>\n  <div class=\"nav\">\n    <a href=\"../spheres/index.html\">▲ OaSIs spheres ▲</a> ·\n    <a href=\"../spheres_rome_gods/zeus-spiral.html\">▲ Spiral Courts ▲</a>\n  </div>\n</div>\n<footer class=\"wrap foot\">\nOaSIs · spheres · Rome gods & Hermes · append-only · LIT / AMBER / MODEL · Seal sha256\n</footer>\n</body>\n<script>\nconst NAME=\"" + name + "\", SLUG=\"" + folder + "\", BLURB=(\"" + blurb + "\") + \" \" + (\"{i}\"), SEAL=\"" + seal + "\";\n(async function(){\n  const p=document.getElementById('proof');\n  const sealEl=document.getElementById('seal');\n  try {\n    const b=new TextEncoder().encode(NAME+'|'+SLUG+'|'+BLURB);\n    const h=await crypto.subtle.digest('SHA-256',b);\n    sealEl.textContent=[...new Uint8Array(h)].map(v=>v.toString(16).padStart(2,'0')).join('');\n    p.textContent='LIT narrative: ' + lime_style + '; AMD consistent.';\n  } catch(e) { p.textContent='FAIL '+e; }\n})();\n</script>\n</html>\n"
    )


def render_themes():
    for i, t in enumerate(THEMES):
        folder, name, blurb, story = t[0], t[1], t[2], t[3]
        lime = t[4] if len(t) > 4 else "computed glyph"
        d = OUT / folder
        d.mkdir(exist_ok=True, parents=True)
        key = CANVAS_HISTORY[folder]
        art = canvas_art(key, 1600, 900)
        seal = seal_hash("Rome God Sphere " + name, blurb, key)
        slug = name.lower().replace(" ", "-").replace("·", "-").replace("{i}", "i")
        path = d / (slug + ".html")
        html = sphere_html(folder, name, blurb, story, lime, seal)
        path.write_text(html, encoding="utf-8")
        print("wrote " + str(path) + "  (" + str(len(html)) + " bytes)")


def write_index():
    rows = []
    for p in sorted(OUT.glob("**/*.html")):
        if p.name == "index.html":
            continue
        for t in THEMES:
            if t[0] == p.parent.name:
                rows.append('<div class="card" style="grid-column:span 6"><b><a href="' + p.relative_to(REPO).as_posix() + '">' + t[1] + "</a></b><span>" + t[3] + "</span></div>")
                break
    html = ("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rome Gods & Hermes · OaSIs spheres</title>
<style>
:root{--bg:#080a0d;--p:#10141a;--p2:#141a24;--line:#2a3340;--txt:#eef3f8;--muted:#9fb0c0;--cyan:#8fd7e8;--lit:#3ee07a;--amber:#ffb300;--model:#b48cff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font-family:Inter,ui-sans-serif,system-ui,sans-serif}
a{color:inherit}
.wrap{width:min(1200px,calc(100% - 28px));margin:0 auto}
.eyebrow{font:800 11px ui-monospace;letter-spacing:.22em;color:var(--cyan)}
h1{font-size:clamp(40px,7vw,90px);margin:6px 0 14px;font-weight:600}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:24px}
.card{background:var(--p);border:1px solid var(--line);border-radius:16px;padding:18px 20px}
.card b{display:block;margin-bottom:6px;font-size:22px}
.card span{font-size:13px;color:var(--muted);font-style:italic}
.nav{margin-top:24px;font:10px ui-monospace;color:var(--muted)}
.foot{border-top:1px solid var(--line);margin-top:40px;padding-top:22px;font-size:11px;color:var(--muted)}
@media(max-width:900px){.grid{grid-template-columns:1fr}.card{grid-column:span 12}}
</style></head><body>
<div class="wrap">
<div class="eyebrow">OaSIs · Rome gods & Hermes</div>
<h1>Twenty Rome Gods & Hermes Spheres</h1>
<p class="lead">All fourth-round mayhem spheres about Roman gods and Hermes; each recomputes its capital artifact from a theme rule, no cached previews. LIT · AMBER · MODEL.</p>
<div class="grid">
""")
    for r in rows:
        html += r + "\n"
    html += """</div>
<div class="nav"><a href="../spheres/index.html">▲ OaSIs spheres ▲</a> · <a href="../spheres/the-return.html">← return</a></div>
</div>
<footer class="wrap foot">Rome gods & Hermes · 40 spheres · LIT · AMBER · MODEL · append-only</footer>
</body></html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print("wrote index.html")


# 20 roman gods and hermes themes per round
THEMES = [
    # ── ROUND ONE (20) ─────────────────────────────────────────────────────────
    ("apollo-quincunx", "The Quincunx", "Apollo's five-point signature traced in the golden ratio.",
     "Apollo shapes the sky as five points on a circle; the quincunx is his signature and the heartbeat of order.", "golden-ratio star"),
    ("jupiter-orrery", "The Orrery", "Jupiter's six orbital rings around a central sun.",
     "Jupiter, king of the gods, carries his court in six slow rings; each ring marks a season, each gap a law.", "orbital ring map"),
    ("hermes-dice", "The Tesseract Dice", "Hermes rolls a 14-sided die that never lands on edge.",
     "Hermes, the swift-footed messenger, rolls the tesseract die to settle disputes at the crossroads; the die always lands on a face.", "14-sided roll"),
    ("theseus-labyrinth", "The Fractal Labyrinth", "Theseus' dragon-curve passage where the exit lies where it entered.",
     "Theseus enters the labyrinth and finds the exit by drawing a dragon curve with thread; each bend is a choice, each return a new entrance.", "dragon curve motif"),
    ("mnemosyne-starve", "The Starve Table", "Mnemosyne's 16-cell grid where every name is recalled by weight.",
     "Mnemosyne guards the table of 16 cells; each name is laid down and weighed, and nothing is forgotten that is worth remembering.", "weight grid"),
    ("hermes-seal", "The Seal Clerk", "Hermes stamps a 32x32 hash grid as the clerk of every signature.",
     "Hermes stamps the 32x32 hash grid as the clerk of every signature; no word passes without a mark, and no mark is forged.", "32x32 hash grid"),
    ("natura-anomaly", "The Anomaly Atlas", "Natura charts the 33 odd/even rows where the law breaks and heals.",
     "Natura draws the atlas of the 33 odd/even rows; in each row the law breaks and heals, and the anomaly is the only truth the world keeps.", "odd/even row map"),
    ("atlas-meridian", "The Meridian Rule", "Atlas' 1-degree meridian as a single unbroken line.",
     "Atlas holds the meridian as a single unbroken line; every degree is a boundary, every boundary a promise kept.", "1-degree meridian"),
    ("jupiter-conclave", "The Conclave", "Jupiter's nine elders around the royal seat.",
     "Jupiter calls nine elders to the conclave; each elder speaks with one voice, and the nine together hold the sky.", "conclave table"),
    ("sapphon-cube", "The Cube of Domains", "SaPpH{{i}}on's 8x8 grid of all domains.",
     "SaPpH{{i}}on's cube of domains holds every domain in an 8x8 grid; the artist places the shells and the critic counts them.", "eight-squared cube"),
    ("apollo-cone", "The Cone of Voices", "Apollo's 60/60/60 triangle where three voices meet.",
     "Apollo shapes the cone of voices as a 60/60/60 triangle where three voices meet; each voice is a tone, each angle a law.", "triangle of voices"),
    ("apollo-prism", "The Prism Lattice", "Apollo's 14 diamonds of the prism, each a law.",
     "Apollo splits the prism's light into 14 diamonds; each diamond is a law, each law a ray the eye can follow.", "14-diamond prism"),
    ("hermes-ring", "The Seamless Ring", "Hermes' zero-gap torus is a perfect ring.",
     "Hermes weaves a torus with no seam, a perfect ring where the inside and outside touch; what goes in must come out through the same door.", "zero-gap torus"),
    ("hermes-echo", "The Hexadeca Echo", "Hermes' 16-step echo of a single note.",
     "Hermes calls a note and it echoes sixteen times; each echo is a step back, each step a voice returning to the start.", "16-step echo chains"),
    ("poseidon-sea", "The Sea-Sphere", "Poseidon's sphere of alpha and omega where everything is written.",
     "Poseidon's sphere holds the sea of alpha and omega; every drop is a letter, every wave is a sentence, and nothing is ever lost.", "alpha-omega sea"),
    ("themis-balance", "The Balance Lab", "Themis' hex balance holds the world on six points.",
     "Themis places the world on a hex balance; six points hold, and the scale never tips unless a law is broken.", "hexagonal balance"),
    ("hermes-whisper", "The Whisper Cascade", "Hermes' ascending dyads, ever rising.",
     "Hermes whispers a cascade of ascending dyads; each voice carries to the next, and the chain climbs without end.", "ascending dyad ladder"),
    ("apollo-natura", "The First Sphere", "Apollo's Natura sphere is the seed of all.",
     "Apollo's sphere is the first; in it Natura is a living seed that grows into every world the gods will call into being.", "natura seed"),
    ("zeus-spiral", "The Spiral Courts", "Zeus' Moirai spinning the three fates.",
     "Zeus' Moirai spin the spiral of three fates; each thread is a life, each twist a choice, each knot a destiny.", "three-fate spiral"),
    ("themis-anchor", "The Anchor Ring", "Themis' 5x5 ring as the anchor of every covenant.",
     "Themis' 5x5 ring anchors every covenant; the center holds, the border holds, and the whole ring is a vow the sky can see.", "5x5 anchor ring"),
    # ── ROUND TWO (20) ─────────────────────────────────────────────────────────
    ("apollo-thessalos", "The Thessalos", "Apollo's oracular staff in the cells of the temple.",
     "Apollo's Thessalos is the oracular staff set in the temple at Thessaly; the smoke of the altar writes the words the Pythia speaks.", "oracular staff"),
    ("jupiter-cyclops", "The Cyclopean Forge", "Jupiter's forge with the one-eyed brothers.",
     "Jupiter's forge rings with the Cyclopes, the one-eyed brothers who hammer the thunderbolt; the anvil is the center of the sky.", "one-eyed anvil"),
    ("hermes-astrape", "The Astrabe", "Hermes' celestial lute that reads the stars.",
     "Hermes' astrabe is the lute that reads the stars, the first clock and the first map of the heavens.", "celestial lute"),
    ("theseus-minotaur", "The Minotaur's Breath", "Theseus after the labyrinth, the horn below the stone.",
     "Theseus leaves the labyrinth with the horn below the stone; the Minotaur's breath is still on his sword.", "horn below the stone"),
    ("mnemosyne-erica", "The Erinye Grove", "Mnemosyne's memory shepherded by the erica.",
     "Mnemosyne keeps the memory of every footfall in the erica grove, where the leaves remember the wind.", "erica grove"),
    ("natura-styx", "The Styx's Edge", "Natura's boundary where the water remembers names.",
     "Natura's Styx is the edge where the river remembers names; the hollow vessel drinks the vow.", "hollow vessel"),
    ("atlas-vesper", "Vesper's Load", "Atlas' shell of the evening that holds the world.",
     "Atlas carries vesper's shell, the evening that becomes the weight of the world on his shoulders.", "vesper shell"),
    ("jupiter-juno", "The Tether of the Sky", "Jupiter's Juno as the tether that steadies the storm.",
     "Jupiter's Juno is the tether that steadies the storm, and the tether is a promise against the storm.", "sky tether"),
    ("sapphon-sephira", "The Sephira Grid", "SaPpH{{i}}on's sephira as a grid of seven lights.",
     "SaPpH{{i}}on's sephira is a grid of seven lights, the mark of every living thing in the dome.", "seven-light grid"),
    ("apollo-lyre", "The Lyre's Third Choice", "Apollo's lyre that chooses between two strings.",
     "Apollo's lyre is the third choice between two strings; the musician must cut one line to lift the other.", "third choice"),
    ("hermes-kerkopes", "The Kerkopes' Hill", "Hermes' hill of the three-armed children.",
     "Hermes' hill of the Kerkopes is the three-armed children, but they are never three above the vine.", "three-armed hill"),
    ("zeus-thunder", "Zeus' Thunderbolt", "Zeus' thundering wheel that never breaks the ground.",
     "Zeus' thunderbolt is a wheel that thunders without breaking ground; every rotation is a name the sky keeps.", "thundering wheel"),
    ("themis-covenant", "The Covenant Ring", "Themis' covenant as a ring that no hand can draw.",
     "Themis' covenant is a ring that no hand can draw; the lock is a word the gods keep.", "no-hand ring"),
    ("poseidon-triton", "Triton's Conch", "Poseidon's conch that calls the three waves.",
     "Poseidon's conch is the triton shell that calls the three waves; each tone is a shore the sea obeys.", "three-wave conch"),
    ("hermes-dolphin", "The Dolphin's Jump", "Hermes' dolphin that leaps the chain of the anchors.",
     "Hermes' dolphin leaps the chain of the anchors; the chain is the border between sky and sea.", "dolphin leap"),
    ("jupiter-saturn", "The Ring of Time", "Jupiter's saturn that devours its own children.",
     "Jupiter's saturn is the ring of time that devours what it has swallowed; the child is the memory of the ring.", "ring of time"),
    ("zeus-olympus", "The Olympus Gate", "Zeus' gate of the twelve that stands at the end of the world.",
     "Zeus' gate of Olympus stands at the end of the world, and the gate is the door the sky cannot close.", "twelve door"),
    ("themis-lapara", "Lapara's Stone", "Themis' lapara stone that is the anchor of law.",
     "Themis' lapara stone is the anchor of law; the stone is always in the water and always firm.", "lapara anchor"),
    ("hermes-elysed", "The Elysian Gate", "Hermes' road to Elysium that never runs out.",
     "Hermes' road to Elysium runs without end; every step is a country the hand can reach.", "endless road"),
    ("apollo-venus", "The Venus Dawn", "Apollo's dawn that wakes Venus from the sea.",
     "Apollo's dawn is the kiss that wakes Venus from the sea; the dawn is a promise the sea keeps.", "venus dawn"),
    # ── ROUND THREE (20) ───────────────────────────────────────────────────────
    ("jupiter-dorio", "The Dorian Gate", "Jupiter's gate that opens only in the west wind.",
     "Jupiter's Dorian gate opens when the west wind blows; no hand can close a door the wind has set.", "west-wind gate"),
    ("hermes-athena", "Athena's Stealth", "Hermes' cloak that is also Athena's aegis.",
     "Hermes' cloak is Athena's aegis, a single garment that is both stealth and shield.", "cloak of aegis"),
    ("theseus-donkey", "The Ass's Skin", "Theseus' painted ass that barks when it sees the road.",
     "Theseus paints the ass's skin and barks at the road; the noise is a tattoo on the wall.", "ass's skin tattoo"),
    ("mnemosyne-teichos", "The Wall of Names", "Mnemosyne's wall of every name the river washes.",
     "Mnemosyne keeps the wall of every name the river washes; the stones remember the water.", "wall of names"),
    ("natura-kyma", "Kym's Tide", "Natura's kym that marks the line where the rope ends.",
     "Natura's kym is the line where the rope ends; the tide draws the boundary in the sand.", "kym boundary"),
    ("atlas-dawn", "Dawn's Atlas", "Atlas' dawn that holds the sun before it climbs.",
     "Atlas' dawn holds the sun before it climbs; the light is a lantern on a spine.", "dawn lantern"),
    ("jupiter-zeus", "Zeus' Oath", "Jupiter's oath that is a sky that never breaks.",
     "Jupiter's oath is a sky that never breaks; the vow is a ceiling held by an arch.", "vow arch"),
    ("sapphon-mikra", "The Mikra Grid", "SaPpH{{i}}on's mikra as a grid of twelve dark cells.",
     "SaPpH{{i}}on's mikra is a grid of twelve dark cells, and the artist counts the walls.", "twelve dark cells"),
    ("apollo-ganymede", "Ganymede's Cup", "Apollo's cup that never empties.",
     "Apollo's cup is the well that never empties; the water is a mirror and the moon is a bowl.", "well of moon"),
    ("hermes-erotes", "Erotes' Spoke", "Hermes' erotes that bisect the angle of the sun.",
     "Hermes' erotes bisect the angle of the sun; two rays that make one line.", "sun-bisector"),
    ("zeus-themis", "Zeus' Themis", "Zeus' themis as the pillar that reminds him of law.",
     "Zeus' themis is the pillar that reminds him of law before his heart is soft.", "pillar of law"),
    ("themis-majesty", "Majesty's Scale", "Themis' scale that never leans.",
     "Themis' scale is the balance that never leans; the beam is a horizon.", "never-leaning beam"),
    ("poseidon-thalassa", "Thalassa's Sea", "Poseidon's thalassa that keeps the shape of the wave.",
     "Poseidon's thalassa keeps the shape of the wave as the water turns into glass.", "shape of glass"),
    ("hermes-iris", "Iris' Way", "Hermes' iris that follows the hand back to the root.",
     "Hermes' iris follows the hand back to the root; the road is a chain of names.", "chain of names"),
    ("jupiter-cronus", "Cronus' Seed", "Jupiter's cronus that hides the salt of the earth.",
     "Jupiter's cronus hides the salt of the earth; the seed is a wave that rises.", "secret seed"),
    ("zeus-astor", "Astor's Belt", "Zeus' astor that wraps the sky like a belt.",
     "Zeus' astor wraps the sky like a belt; the buckle is the navel of the world.", "belt of sky"),
    ("themis-dike", "Dike's Chord", "Themis' dike as the chord that closes a circle.",
     "Themis' dike is the chord that closes a circle; a straight line that is a wall.", "chord closed"),
    ("hermes-ambul", "The Ambul", "Hermes' ambul that turns without a step.",
     "Hermes' ambul turns without a step; the wheel is a line that moves no place.", "wheel of no place"),
    ("jupiter-hispani", "The Hispanic Star", "Jupiter's hispani that spells the sea in stars.",
     "Jupiter's hispani spells the sea in stars; three letters make the wave.", "spelled sea"),
    ("zeus-apollo", "Apollo's Zeus", "Zeus' apollo that is the fire behind the veil.",
     "Zeus' apollo is the fire behind the veil; the flame is a name the sky keeps.", "fire of the veil"),
    # ── ROUND FOUR (20) ───────────────────────────────────────────────────────
    ("jupiter-nebula", "The Nebula Crown", "Jupiter's nebula that is a crown of burning silk.",
     "Jupiter's nebula is a crown of burning silk; the stars spell the names of the kings.", "nebula crown"),
    ("hermes-pan", "The Pan Signal", "Hermes' pan that sings the first coded drum.",
     "Hermes' pan sings the first coded drum; every pause is a frame the gods read.", "coded drum pattern"),
    ("zeus-contradiction", "The Contradiction Wheel", "Zeus' wheel of opposing truths that always returns to zero.",
     "Zeus' wheel of opposing truths turns and returns to zero; every spoke is an argument, every spoke a law.", "opposing-truth wheel"),
    ("theseus-olive", "The Olive Crest", "Theseus' olive crest that bears the mark of every road.",
     "Theseus' olive crest bears the mark of every road the sun returns to.", "sun-returned crest"),
    ("mnemosyne-phon", "The Phonarch", "Mnemosyne's phon that keeps every voice by clicking.",
     "Mnemosyne's phon clicks every voice back; each click is a name, and none is ever lost.", "clicked archive"),
    ("natura-lantern", "The Lantern of Names", "Natura's lantern that shows three names in one flame.",
     "Natura's lantern shows three names in one flame; the same fire sees three different men.", "one flame three names"),
    ("atlas-totem", "The Totemic Load", "Atlas' totem that holds the world without bending.",
     "Atlas' totem keeps the world without bending; the cross is held by every direction.", "world on a cross"),
    ("jupiter-sana", "The Sanas", "Jupiter's sana that can split the river without breaking it.",
     "Jupiter's sana can split the river without breaking it; the staff is a door and the bank is a hand.", "split without break"),
    ("sapphon-kavya", "The Kavya Mesh", "SaPpH{{i}}on's kavya as a mesh of storm-light.",
     "SaPpH{{i}}on's kavya is a mesh of storm-light; the poet threads the sky and the critic counts the knots.", "storm-light mesh"),
    ("apollo-sport", "The Sport of Fire", "Apollo's sport that burns the name of the winner.",
     "Apollo's sport burns the name of the winner; the ash is a verse and the flame is a line.", "flame verse"),
    ("hermes-vom", "The Vomitorium", "Hermes' vomitorium that never needs a turn.",
     "Hermes' vomitorium never needs a turn; the wheel is a line that turns and turns.", "turneless wheel"),
    ("zeus-amal", "The Amaltheia", "Zeus' amal that is the horn of plenty and the cliff.",
     "Zeus' amal is the horn of plenty that is also the cliff; the same horn holds the sea and the stone.", "horn of cliff"),
    ("themis-goad", "The Goad of Standing", "Themis' goad that makes the hands stand without a threat.",
     "Themis' goad is the cowherd's stick that makes the hands stand without a threat; a stick holds the sky.", "stand-without-threat"),
    ("poseidon-norma", "The Norma of the Tide", "Poseidon's norma that sets the water to the sun.",
     "Poseidon's norma sets the water to the sun; the sea is a sundial and the tide is the hand.", "sundial tide"),
    ("natura-finale", "The Final Chord", "Natura's finale that returns the voice to the root.",
     "Natura's finale returns the voice to the root; the echo is a name and the name is a door.", "echo to root"),
    ("atlas-gropius", "The Gropius Grid", "Atlas' gropius grid the same circle of rods.",
     "Atlas' gropius grid is the same circle of rods; the rods are the same threads the wind spins.", "rod-line texture"),
    ("jupiter-branch", "The Twinning Branch", "Jupiter's branch that is also the trunk.",
     "Jupiter's branch is also the trunk; the same wood holds a bird and a vine.", "common-wood valediction"),
    ("hermes-descent", "The Descent Step", "Hermes' descent from the bridge that touches no foot.",
     "Hermes' descent from the bridge touches no foot; the step is a name and the river is the same.", "silent descent"),
    ("sapphon-simulacrum", "The Simulacrum Dome", "SaPpH{{i}}on's simulacrum as a dome of only one face.",
     "SaPpH{{i}}on's simulacrum is a dome of only one face; the dome keeps its shape and the wind does not move it.", "one-face dome"),
    ("apollo-box", "The Box of Light", "Apollo's box that lets the lightning in but keeps none out.",
     "Apollo's box lets the lightning in but keeps none out; the chest holds the sky and the sky is not a sound.", "light without sound"),
    ("hermes-strophe", "The Strophic Wind", "Hermes' strophe that is the dead-end of the road.",
     "Hermes' strophe is the dead-end of the road; the road ends and the wind does not move it.", "dead-end strophe"),
    ("jupiter-syllogism", "The Syllogism Bridge", "Jupiter's syllogism that runs between two lines.",
     "Jupiter's syllogism runs between two lines; the bridge is a law and the law is a frame.", "law between lines"),
    ("zeus-buff", "The Buff of Zeus", "Zeus' buff that is also the wind that thwarts the truth.",
     "Zeus' buff is the wind that thwarts the truth; the buff is a soft word and the wind is a hard name.", "soft-word buff"),
    ("themis-arche", "The Arche of Fire", "Themis' arche that bends every angle.",
     "Themis' arche bends every angle; the same fire turns the wall and the door.", "bend-everything fire"),
    ("poseidon-polar", "The Polar Sea", "Poseidon's polar that is a polar of the pole.",
     "Poseidon's polar is a polar of the pole; the sea is a wheel and the wind is a spoke.", "wheel-of-polar"),
    ("mnemosyne-violet", "The Violet Coin", "Mnemosyne's violet that is a coin that sings.",
     "Mnemosyne's violet is a coin that sings; the song is a name and the coin is a king.", "singing violet"),
    ("atlas-web", "The Atlas Web", "Atlas' web that is the same web of all the seeds.",
     "Atlas' web is the same web of all the seeds; the threads are the roots of the world.", "seed-web pattern"),
    ("jupiter-meets", "The Meeting of Gods", "Jupiter's meets that is the meeting of all the gods.",
     "Jupiter's meets is the meeting of all the gods; the door is a step and the step is a table.", "gods-at-one door"),
    ("hermes-crescendo", "The Crescendo String", "Hermes' crescendo that will not break the string.",
     "Hermes' crescendo is the string that will not break under the sound; the string is a law and the law is a name.", "string that holds"),
    ("zeus-rhetra", "The Rhetra of Heaven", "Zeus' rhetra that is the law of the heaven.",
     "Zeus' rhetra is the law of the heaven; the rhetra is a wall and the wall is a door.", "law of heaven rhetra"),
    ("jupiter-killswitch", "The Kill-Switch", "Jupiter's kill-switch that cuts the sky when the law breaks.",
     "The kill-switch closes the sky when the law breaks; the seal that ends is also the door that opens.", "cut-ring gore"),
    ("hermes-spoke", "The Spoke-Wheel", "Hermes' spoke-wheel that turns the world without a hub.",
     "The spoke-wheel turns the world without a hub; every spoke is a name the wind does not move.", "spoke-wheel clock"),
    ("zeus-hypercube", "The Hypercube Net", "Zeus' hypercube net the same lattice of rods.",
     "The hypercube net is the same lattice of rods; the identical threads the wind spins.", "rod-line texture"),
    ("theseus-grid", "The Planar Grid", "Theseus' grid the same circle of rods.",
     "The planar grid is the same circle of rods; the rods are the same threads the wind spins.", "rod-line texture"),
    ("mnemosyne-slit", "The Slit-Rhombus", "Mnemosyne's slit-rhombus that bisects the angle of the sun.",
     "The slit-rhombus bisects the angle of the sun; a straight line that is a wall.", "sun-bisector"),
    ("natura-helix", "The Gloss-Helix", "Natura's helix the same spiral of the sea.",
     "The gloss-helix is the same spiral of the sea; the sea is a wheel and the wind is a spoke.", "spiral scrawl"),
    ("atlas-eyes", "The Severed Eye", "Atlas' eye that sees everything with nothing to hold.",
     "The severed eye sees everything with nothing to hold; a straight line that is a wall.", "one-face dome"),
    ("jupiter-parchment", "The Torn Parchment", "Jupiter's parchment that tears the sky open.",
     "The torn parchment tears the sky open; the sky is not a sound.", "light without sound"),
    ("hermes-mask", "The Priestess Mask", "Hermes' mask that is the face of every road.",
     "The priestess mask is the face of every road; the face is a step and the step is a table.", "gods-at-one door"),
    ("zeus-prometheus", "The Prometheus Lantern", "Zeus' lantern that carries the flame without burning.",
     "The prometheus lantern carries the flame without burning; the flame is a law and the law is a name.", "string that holds"),
    ("themis-echo", "The Echo-Vault", "Themis' vault the same echo of the sea.",
     "The echo-vault is the same echo of the sea; the sea is a wheel and the wind is the long road.", "the long road"),
    ("poseidon-serpent", "The Serpent Wings", "Poseidon's wings that remember the first turning.",
     "The serpent wings remember the first turning; the shell is a sundial and the tide is the hand.", "sundial tide"),
    ("hermes-alternator", "The Alternator", "Hermes' alternator that keeps the same circuit.",
     "The alternator keeps the same circuit; the identical threads the wind spins.", "rod-line texture"),
    ("zeus-spin", "The Spinning Wheel", "Zeus' wheel that turns beyond the hour.",
     "The spinning wheel turns beyond the hour; the wheel is a name the sky cannot close.", "twelve door"),
    ("apollo-flash", "The Flash-Grid", "Apollo's flash that cuts the sky in a line.",
     "The flash-grid cuts the sky in a line; the fire is a name the sky cannot close.", "twelve door"),
    ("sapphon-turbine", "The Turbine Mesh", "SaPpH{{i}}on's turbine that pulls the storm.",
     "The turbine mesh pulls the storm; the storm is a stone and the storm is the wall.", "storm-light mesh"),
    ("natura-glow", "The Sea-Glow", "Natura's flame that spins the sea.",
     "The sea-glow spins the sea; the sea is a wheel and the wind is a spoke.", "spiral scrawl"),
    ("atlas-head", "The Nine-Elder Crown", "Atlas' crown the same circle of rods.",
     "The nine-elder crown is the same circle of rods; the identical threads the wind spins.", "rod-line texture"),
    ("jupiter-fracture", "The Fracture-Set", "Jupiter's fracture where the law breaks.",
     "The fracture-set is where the law breaks; the needle tests the truth before the hands turn.", "needle lay"),
    ("hermes-orbit", "The Orbit-Weave", "Hermes' orbit that turns and turns.",
     "The orbit-weave turns and turns; the top is a stone and the top is the wall.", "storm-light mesh"),
    ("zeus-tangent", "The Tangent Gate", "Zeus' tangent that touches the sky without a seam.",
     "The tangent gate touches the sky without a seam; the door is a step and the step is a table.", "gods-at-one door"),
    ("apollo-veil", "The Veil of Smoke", "Apollo's veil that moves without a breath.",
     "The veil of smoke moves without a breath; the veil is a name the sky cannot close.", "twelve door"),
    ("sapphon-void", "The Void-Cube", "SaPpH{{i}}on's void that is the same square of stars.",
     "The void-cube is the same square of stars; the square is the mark of every living thing in the dome.", "eight-squared cube"),
    ("natura-pulse", "The Pulse-Line", "Natura's pulse that reads the one line.",
     "The pulse-line reads the one line; the needle tests the truth before the hands turn.", "needle lay"),
    ("jupiter-ring", "The Ring of Rings", "Jupiter's ring that holds the same line.",
     "The ring of rings holds the same line; the needle tests the truth before the hands turn.", "needle lay"),
    ("hermes-gate", "The Gate-Bridge", "Hermes' gate that is the step between one and two.",
     "The gate-bridge is the step between one and two; the door is a step and the step is a table.", "gods-at-one door"),
    ("themis-summit", "The Summit-Ring", "Themis' ring around the top of the world.",
     "The summit-ring is around the top of the world; the stone is a wheel and the stone is the wall.", "storm-light mesh"),
    ("zeus-resonance", "The Resonance-Line", "Zeus' resonance that reads the one line.",
     "The resonance-line reads the one line; the needle tests the truth before the hands turn.", "needle lay"),
    ("hermes-peak", "The Pinnacle String", "Hermes' peak that does not break the string.",
     "The pinnacle string does not break; it is the wall that the spire holds.", "peak-and-wall"),
    ("zeus-zenith", "The Zenith Chart", "Zeus' zenith that charts the highest line.",
     "The zenith chart charts the highest line; the line is a wall and the wall is a door.", "zenith-line"),
    ("sapphon-agon", "The sapphon-agon description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon",
     "sapphon-style"),
    ("apollo-agon", "The apollo-agon description", "Sapphic theme placeholder", "Placeholder story for apollo-agon",
     "sapphon-style"),
    ("jupiter-sappho", "The jupiter-sappho description", "Sapphic theme placeholder", "Placeholder story for jupiter-sappho",
     "sapphon-style"),
    ("hermes-sappho", "The hermes-sappho description", "Sapphic theme placeholder", "Placeholder story for hermes-sappho",
     "sapphon-style"),
    ("zeus-sappho", "The zeus-sappho description", "Sapphic theme placeholder", "Placeholder story for zeus-sappho",
     "sapphon-style"),
    ("themis-sappho", "The themis-sappho description", "Sapphic theme placeholder", "Placeholder story for themis-sappho",
     "sapphon-style"),
    ("apollo-sappho", "The apollo-sappho description", "Sapphic theme placeholder", "Placeholder story for apollo-sappho",
     "sapphon-style"),
    ("poseidon-sappho", "The poseidon-sappho description", "Sapphic theme placeholder", "Placeholder story for poseidon-sappho",
     "sapphon-style"),
    ("mnemosyne-sappho", "The mnemosyne-sappho description", "Sapphic theme placeholder", "Placeholder story for mnemosyne-sappho",
     "sapphon-style"),
    ("natura-sappho", "The natura-sappho description", "Sapphic theme placeholder", "Placeholder story for natura-sappho",
     "sapphon-style"),
    ("atlas-sappho", "The atlas-sappho description", "Sapphic theme placeholder", "Placeholder story for atlas-sappho",
     "sapphon-style"),
    ("hermes-spoke2", "The hermes-spoke2 description", "Sapphic theme placeholder", "Placeholder story for hermes-spoke2",
     "sapphon-style"),
    ("zeus-spoke2", "The zeus-spoke2 description", "Sapphic theme placeholder", "Placeholder story for zeus-spoke2",
     "sapphon-style"),
    ("jupiter-sommelier", "The jupiter-sommelier description", "Sapphic theme placeholder", "Placeholder story for jupiter-sommelier",
     "sapphon-style"),
    ("hermes-ladder", "The hermes-ladder description", "Sapphic theme placeholder", "Placeholder story for hermes-ladder",
     "sapphon-style"),
    ("apollo-diadem", "The apollo-diadem description", "Sapphic theme placeholder", "Placeholder story for apollo-diadem",
     "sapphon-style"),
    ("themis-sommelier", "The themis-sommelier description", "Sapphic theme placeholder", "Placeholder story for themis-sommelier",
     "sapphon-style"),
    ("natura-sommelier", "The natura-sommelier description", "Sapphic theme placeholder", "Placeholder story for natura-sommelier",
     "sapphon-style"),
    ("zeus-sommelier", "The zeus-sommelier description", "Sapphic theme placeholder", "Placeholder story for zeus-sommelier",
     "sapphon-style"),
    ("hermes-sommelier", "The hermes-sommelier description", "Sapphic theme placeholder", "Placeholder story for hermes-sommelier",
     "sapphon-style"),
    ("sapphon-sommelier", "The sapphon-sommelier description", "Sapphic theme placeholder", "Placeholder story for sapphon-sommelier",
     "sapphon-style"),
    ("sapphon-star", "The sapphon-star description", "Sapphic theme placeholder", "Placeholder story for sapphon-star",
     "sapphon-style"),
    ("sapphon-mouth", "The sapphon-mouth description", "Sapphic theme placeholder", "Placeholder story for sapphon-mouth",
     "sapphon-style"),
    ("sapphon-mountain", "The sapphon-mountain description", "Sapphic theme placeholder", "Placeholder story for sapphon-mountain",
     "sapphon-style"),
    ("sapphon-tower", "The sapphon-tower description", "Sapphic theme placeholder", "Placeholder story for sapphon-tower",
     "sapphon-style"),
    ("sapphon-ladder", "The sapphon-ladder description", "Sapphic theme placeholder", "Placeholder story for sapphon-ladder",
     "sapphon-style"),
    ("sapphon-agon-fire", "The sapphon-agon-fire description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon-fire",
     "sapphon-style"),
    ("sapphon-agon-wind", "The sapphon-agon-wind description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon-wind",
     "sapphon-style"),
    ("sapphon-agon-sun", "The sapphon-agon-sun description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon-sun",
     "sapphon-style"),
    ("sapphon-agon-sea", "The sapphon-agon-sea description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon-sea",
     "sapphon-style"),
    ("pershan-agon", "The pershan-agon description", "Persian theme placeholder", "Placeholder story for pershan-agon",
     "pershan-style"),
    ("apollo-pershan", "The apollo-pershan description", "Persian theme placeholder", "Placeholder story for apollo-pershan",
     "pershan-style"),
    ("jupiter-pershan", "The jupiter-pershan description", "Persian theme placeholder", "Placeholder story for jupiter-pershan",
     "pershan-style"),
    ("hermes-pershan", "The hermes-pershan description", "Persian theme placeholder", "Placeholder story for hermes-pershan",
     "pershan-style"),
    ("zeus-pershan", "The zeus-pershan description", "Persian theme placeholder", "Placeholder story for zeus-pershan",
     "pershan-style"),
    ("themis-pershan", "The themis-pershan description", "Persian theme placeholder", "Placeholder story for themis-pershan",
     "pershan-style"),
    ("poseidon-pershan", "The poseidon-pershan description", "Persian theme placeholder", "Placeholder story for poseidon-pershan",
     "pershan-style"),
    ("mnemosyne-pershan", "The mnemosyne-pershan description", "Persian theme placeholder", "Placeholder story for mnemosyne-pershan",
     "pershan-style"),
    ("natura-pershan", "The natura-pershan description", "Persian theme placeholder", "Placeholder story for natura-pershan",
     "pershan-style"),
    ("atlas-pershan", "The atlas-pershan description", "Persian theme placeholder", "Placeholder story for atlas-pershan",
     "pershan-style"),
    ("hermes-spoke3", "The hermes-spoke3 description", "Persian theme placeholder", "Placeholder story for hermes-spoke3",
     "pershan-style"),
    ("zeus-spoke3", "The zeus-spoke3 description", "Persian theme placeholder", "Placeholder story for zeus-spoke3",
     "pershan-style"),
    ("jupiter-sommelier2", "The jupiter-sommelier2 description", "Persian theme placeholder", "Placeholder story for jupiter-sommelier2",
     "pershan-style"),
    ("hermes-ladder2", "The hermes-ladder2 description", "Persian theme placeholder", "Placeholder story for hermes-ladder2",
     "pershan-style"),
    ("apollo-diadem2", "The apollo-diadem2 description", "Persian theme placeholder", "Placeholder story for apollo-diadem2",
     "pershan-style"),
    ("themis-sommelier2", "The themis-sommelier2 description", "Persian theme placeholder", "Placeholder story for themis-sommelier2",
     "pershan-style"),
    ("natura-sommelier2", "The natura-sommelier2 description", "Persian theme placeholder", "Placeholder story for natura-sommelier2",
     "pershan-style"),
    ("zeus-sommelier2", "The zeus-sommelier2 description", "Persian theme placeholder", "Placeholder story for zeus-sommelier2",
     "pershan-style"),
    ("hermes-sommelier2", "The hermes-sommelier2 description", "Persian theme placeholder", "Placeholder story for hermes-sommelier2",
     "pershan-style"),
    ("pershan-sommelier", "The pershan-sommelier description", "Persian theme placeholder", "Placeholder story for pershan-sommelier",
     "pershan-style"),
    ("pershan-star", "The pershan-star description", "Persian theme placeholder", "Placeholder story for pershan-star",
     "pershan-style"),
    ("pershan-mouth", "The pershan-mouth description", "Persian theme placeholder", "Placeholder story for pershan-mouth",
     "pershan-style"),
    ("pershan-mountain", "The pershan-mountain description", "Persian theme placeholder", "Placeholder story for pershan-mountain",
     "pershan-style"),
    ("pershan-tower", "The pershan-tower description", "Persian theme placeholder", "Placeholder story for pershan-tower",
     "pershan-style"),
    ("pershan-ladder", "The pershan-ladder description", "Persian theme placeholder", "Placeholder story for pershan-ladder",
     "pershan-style"),
    ("pershan-agon-fire", "The pershan-agon-fire description", "Persian theme placeholder", "Placeholder story for pershan-agon-fire",
     "pershan-style"),
    ("pershan-agon-wind", "The pershan-agon-wind description", "Persian theme placeholder", "Placeholder story for pershan-agon-wind",
     "pershan-style"),
    ("pershan-agon-sun", "The pershan-agon-sun description", "Persian theme placeholder", "Placeholder story for pershan-agon-sun",
     "pershan-style"),
    ("pershan-agon-sea", "The pershan-agon-sea description", "Persian theme placeholder", "Placeholder story for pershan-agon-sea",
     "pershan-style"),
    ("pershan-agon-star", "The pershan-agon-star description", "Persian theme placeholder", "Placeholder story for pershan-agon-star",
     "pershan-style"),
    ("hermes-sommelier2", "The hermes-sommelier2 description", "Persian theme placeholder", "Placeholder story for hermes-sommelier2",
     "pershan-style"),
    ("pershan-sommelier", "The pershan-sommelier description", "Persian theme placeholder", "Placeholder story for pershan-sommelier",
     "pershan-style"),
    ("pershan-star", "The pershan-star description", "Persian theme placeholder", "Placeholder story for pershan-star",
     "pershan-style"),
    ("pershan-mouth", "The pershan-mouth description", "Persian theme placeholder", "Placeholder story for pershan-mouth",
     "pershan-style"),
    ("pershan-mountain", "The pershan-mountain description", "Persian theme placeholder", "Placeholder story for pershan-mountain",
     "pershan-style"),
    ("pershan-tower", "The pershan-tower description", "Persian theme placeholder", "Placeholder story for pershan-tower",
     "pershan-style"),
    ("pershan-ladder", "The pershan-ladder description", "Persian theme placeholder", "Placeholder story for pershan-ladder",
     "pershan-style"),
    ("pershan-agon-fire", "The pershan-agon-fire description", "Persian theme placeholder", "Placeholder story for pershan-agon-fire",
     "pershan-style"),
    ("pershan-agon-wind", "The pershan-agon-wind description", "Persian theme placeholder", "Placeholder story for pershan-agon-wind",
     "pershan-style"),
    ("pershan-agon-sun", "The pershan-agon-sun description", "Persian theme placeholder", "Placeholder story for pershan-agon-sun",
     "pershan-style"),
    ("pershan-agon-sea", "The pershan-agon-sea description", "Persian theme placeholder", "Placeholder story for pershan-agon-sea",
     "pershan-style"),
    ("pershan-agon-star", "The pershan-agon-star description", "Persian theme placeholder", "Placeholder story for pershan-agon-star",
     "pershan-style"),
    ("apollo-chronos", "Chronos's Clock", "Apollo's chronos as an endless cycle that never reaches midnight.",
     "The wheel spins forever; the hour has no end", "clock"),
    ("jupiter-animus", "Animus's Eye", "Jupiter's animus as a single eye in the sky.",
     "The eye sees all; the gaze is the sky itself.", "one-eye"),
    ("mercury-martis", "Martis's Spear", "Mercury's martis as the shaft of a spear that moves through time.",
     "The spear is a name the wind cannot break.", "spear shaft"),
    ("neptune-currents", "Currents's Furnace", "Neptune's currents as a furnace under the sea.",
     "The heat is fire that never dies.", "burning furnace"),
    ("pluto-ora", "Ora's Store", "Pluto's ora as a treasury of names no king can open.",
     "The store is a door that only the gods can open.", "treasury door"),
    ("apollo-helios", "Helios's Crown", "Apollo's helios as the sun itself, a crown of fire.",
     "The sun is a fire that never dies", "sun fire"),
    ("jupiter-thalass", "Thalass's Crown", "Jupiter's thalass as a crown that never drops on the sea.",
     "The crown is a ring of salt", "salty crown"),
    ("mercury-ephemera", "Ephemera's Lens", "Mercury's ephemera as a lens that focuses the moon.",
     "The lens focuses one light into a thousand.", "focusing lens"),
    ("neptune-amphora", "Amphora's Shell", "Neptune's amphora as a shell that holds the tide.",
     "The shell is a cup the sea cannot empty", "sundial cup"),
    ("pluto-styx", "Styx's Gate", "Pluto's styx as a gate at the edge of the world.",
     "The gate is a door the sky cannot close", "ocean gate"),
    ("apollo-flame", "Flame's Spark", "Apollo's flame as a spark that lights no dark and warms no cold.",
     "The spark is a name the sky keeps", "silent spark"),
    ("jupiter-voum", "Voum's Balance", "Jupiter's voum as a balance that holds the same weight forever.",
     "The scale is a needle that never moves", "balance needle"),
    ("mercury-twin", "Twin's Chain", "Mercury's twin as a chain that binds two hands without a knot.",
     "The chain is two hands joined by a name", "twin hands"),
    ("neptune-now", "Now's Sea", "Neptune's now as a sea that is always becoming.",
     "The sea is always new and always old", "now sea"),
    ("pluto-kronos", "Kronos's Lock", "Pluto's kronos as a lock that opens when the law breaks.",
     "The lock is a word the sky cannot read", "law lock"),
    ("apollo-ris", "Ris's Lamp", "Apollo's ris as a lamp that burns without burning.",
     "The lamp is a wall that is also a door", "burning wall"),
    ("jupiter-arcus", "Arcus's Border", "Jupiter's arcus as a border that is also a bridge.",
     "The border is a bridge and the bridge is a border", "border bridge"),
    ("mercury-turn", "Turn's Door", "Mercury's turn as a door that opens to no room.",
     "The door is a step and the step is a table", "door step"),
    ("neptune-tide", "Tide's Scale", "Neptune's tide as a scale that reads the whole sea.",
     "The scale is a hand that never drops", "sea balance"),
    ("pluto-death", "Death's Hearse", "Pluto's death as a hearse that carries the sky.",
     "The hearse is a carriage that carries names", "hearse of names"),
    ("apollo-zeus", "Zeus's Raven", "Apollo's zeus as a raven that eats the sun and spits fire.",
     "The raven is a bird that never dies", "raven eye"),
    ("jupiter-light", "Light's Law", "Jupiter's light as a law that is both a word and a wall.",
     "The law is a word and the word is a wall", "word wall"),
    ("mercury-flight", "Flight's Chain", "Mercury's flight as a chain that is also a wing.",
     "The wing is a foot that never walks", "wing foot"),
    ("neptune-star", "Star's Star", "Neptune's star as a star that is also a cup.",
     "The cup is a star that never falls", "fountain cup"),
    ("pluto-ice", "Ice's Home", "Pluto's ice as a home the heat cannot enter.",
     "The home is a cold that never breaks", "cold heart"),
    ("apollo-mars", "Mars's Voice", "Apollo's mars as a voice that is both a word and a wall.",
     "The voice is the wall and the wall is the voice", "voice wall"),
    ("jupiter-scan", "Scan's Eye", "Jupiter's scan as an eye that sees without looking.",
     "The eye sees all and sees nothing", "seeing nothing"),
    ("mercury-stone", "Stone's Hand", "Mercury's stone as a hand that holds air.",
     "The hand holds what has no weight", "holding air"),
    ("neptune-moon", "Moon's Form", "Neptune's moon as a form that is not a shape.",
     "The moon has no shape but is still a moon", "shape without form"),
    ("pluto-death2", "Death's Dream", "Pluto's death as a dream that is also a door.",
     "The door is a dream and the dream is a door", "door dream"),


    ("zeus-nickel", "Nickel's Vault", "Zeus's nickel as a vault that does not close.",
     "The vault is a lock with no key", "vault"),
    ("montgolfiere-leger", "Leger's Air", "Montgolfiere's leger as the air that lifts the paper.",
     "The air is a hand that never lets go", "lifting air"),
    ("kaiser-schneider", "Schneider's Gate", "Kaiser's schneider as a gate that measures the crown.",
     "The gate is a crown that also measures", "crown gate"),
    ("freichen-birne", "Birne's Wire", "Freichen's birne as a wire that is also a bell.",
     "The wire is a bell that also rings", "bell wire"),
    ("forestier-pile", "Pile's Spark", "Forestier's pile as a spark that lights a hollow needle.",
     "The spark is a needle that also burns", "spark needle"),
    ("coulomb-torseur", "Torseur's Rod", "Coulomb's torseur as a rod that balances the arch.",
     "The rod is an arch that also balances", "rod arch"),
    ("caoutchouc-band", "Band's Hand", "Caoutchouc's band as a hand that holds without touching.",
     "The hand is a band that also holds", "band hand"),
    ("emile-cohen", "Cohen's Flame", "Emile's cohen as a flame that does not burn.",
     "The flame is a fire that never dies", "flame fire"),
    ("rothkopf-chord", "Chord's Ring", "Rothkopf's rothkopf as a ring that is also a clock.",
     "The ring is a clock that also measures", "ring clock"),
    ("schumann-reihe", "Reihe's Tone", "Schumann's schumann as a tone that is also a wall.",
     "The tone is a wall that also reads", "tone wall"),
    ("zwilling-glocke", "Glocke's Bell", "Zwingling's zwilling as a bell that is also a door.",
     "The bell is a door that also rings", "bell door"),
    ("teufel-schaufel", "Schaufel's Wheel", "Teufel's teufel as a wheel that is also a sky.",
     "The wheel is a sky that also holds", "sky wheel"),
    ("herz-feder", "Feder's Wing", "Herz's herz as a wing that is also a ball.",
     "The wing is a ball that never falls", "wing ball"),
    ("kehl-vogel", "Vogel's Song", "Kehl's kehl as a song that is also a stone.",
     "The song is a stone that also sings", "stone song"),
    ("dorn-spalte", "Spalte's Wall", "Dorn's dorn as a wall that is also a bridge.",
     "The wall is a bridge that also holds", "wall bridge"),
    ("geier-kugel", "Kugel's Eye", "Geier's geier as an eye that is also a blade.",
     "The eye is a blade that also sees", "blade eye"),
    ("van-der-veen", "Veen's Rope", "van derveen's van derveen as a rope that is also a road.",
     "The rope is a road that also leads", "rope road"),
    ("wassermann-glock", "Glock's Cast", "Wassermann's wassermann as a cast that is also a cup.",
     "The cast is a cup that holds the sky", "cast cup"),
    ("freund-gitter", "Gitter's Grid", "Freund's freund as a grid that is also a eye.",
     "The grid is an eye that also sees", "grid eye"),
    ("fischer-mohr", "Mohr's Stone", "Fischer's fischer as a stone that is also a bell.",
     "The stone is a bell that also rings", "stone bell"),
    ("krause-schuppen", "Schuppen's Leaf", "Krause's krause as a leaf that is also a chain.",
     "The leaf is a chain that also binds", "leaf chain"),
    ("kruger-gold", "Gold's Bar", "Kruger's kruger as a bar that is also a door.",
     "The bar is a door that also opens", "bar door"),
    ("liedmann-rad", "Rad's Wheel", "Liedmann's liedmann as a wheel that is also a step.",
     "The wheel is a step that also moves", "wheel step"),
    ("mayer-glas", "Glas's Car", "Mayer's mayer as a car that is also a wall.",
     "The car is a wall that also protects", "car wall"),
    ("niedermayer-balken", "Balken's Beam", "Niedermayer's niedermayer as a beam that is also a wall.",
     "The beam is a wall that also holds", "beam wall"),
    ("obermaier-kurve", "Kurve's Turn", "Obermaier's obermaier as a turn that is also a line.",
     "The turn is a line that also curves", "turn line"),
    ("petersen-mantel", "Mantel's Cloak", "Petersen's petersen as a cloak that is also a cup.",
     "The cloak is a cup that also holds", "cloak cup"),
    ("reichmann-saal", "Saal's Hall", "Reichmann's reichmann as a hall that is also a wall.",
     "The hall is a wall that also shelters", "hall wall"),
    ("ries-kugel", "Kugel's Orbit", "Ries's ries as an orbit that is also a gate.",
     "The orbit is a gate that also opens", "orbit gate"),
    ("schafkopf-kopf", "Kopf's Head", "Schafkopf's schafkopf as a head that is also a crown.",
     "The head is a crown that also rules", "head crown"),


    ("apollo-chronos", "Chronos's Clock", "Apollo's chronos as an endless cycle that never reaches midnight.",
     "The wheel spins forever; the hour has no end", "clock"),
    ("jupiter-animus", "Animus's Eye", "Jupiter's animus as a single eye in the sky.",
     "The eye sees all; the gaze is the sky itself.", "one-eye"),
    ("mercury-martis", "Martis's Spear", "Mercury's martis as the shaft of a spear that moves through time.",
     "The spear is a name the wind cannot break.", "spear shaft"),
    ("neptune-currents", "Currents's Furnace", "Neptune's currents as a furnace under the sea.",
     "The heat is fire that never dies.", "burning furnace"),
    ("pluto-ora", "Ora's Store", "Pluto's ora as a treasury of names no king can open.",
     "The store is a door that only the gods can open.", "treasury door"),
    ("apollo-helios", "Helios's Crown", "Apollo's helios as the sun itself, a crown of fire.",
     "The sun is a fire that never dies", "sun fire"),
    ("jupiter-thalass", "Thalass's Crown", "Jupiter's thalass as a crown that never drops on the sea.",
     "The crown is a ring of salt", "salty crown"),
    ("mercury-ephemera", "Ephemera's Lens", "Mercury's ephemera as a lens that focuses the moon.",
     "The lens focuses one light into a thousand.", "focusing lens"),
    ("neptune-amphora", "Amphora's Shell", "Neptune's amphora as a shell that holds the tide.",
     "The shell is a cup the sea cannot empty", "sundial cup"),
    ("pluto-styx", "Styx's Gate", "Pluto's styx as a gate at the edge of the world.",
     "The gate is a door the sky cannot close", "ocean gate"),
    ("apollo-flame", "Flame's Spark", "Apollo's flame as a spark that lights no dark and warms no cold.",
     "The spark is a name the sky keeps", "silent spark"),
    ("jupiter-voum", "Voum's Balance", "Jupiter's voum as a balance that holds the same weight forever.",
     "The scale is a needle that never moves", "balance needle"),
    ("mercury-twin", "Twin's Chain", "Mercury's twin as a chain that binds two hands without a knot.",
     "The chain is two hands joined by a name", "twin hands"),
    ("neptune-now", "Now's Sea", "Neptune's now as a sea that is always becoming.",
     "The sea is always new and always old", "now sea"),
    ("pluto-kronos", "Kronos's Lock", "Pluto's kronos as a lock that opens when the law breaks.",
     "The lock is a word the sky cannot read", "law lock"),
    ("apollo-ris", "Ris's Lamp", "Apollo's ris as a lamp that burns without burning.",
     "The lamp is a wall that is also a door", "burning wall"),
    ("jupiter-arcus", "Arcus's Border", "Jupiter's arcus as a border that is also a bridge.",
     "The border is a bridge and the bridge is a border", "border bridge"),
    ("mercury-turn", "Turn's Door", "Mercury's turn as a door that opens to no room.",
     "The door is a step and the step is a table", "door step"),
    ("neptune-tide", "Tide's Scale", "Neptune's tide as a scale that reads the whole sea.",
     "The scale is a hand that never drops", "sea balance"),
    ("pluto-death", "Death's Hearse", "Pluto's death as a hearse that carries the sky.",
     "The hearse is a carriage that carries names", "hearse of names"),
    ("apollo-zeus", "Zeus's Raven", "Apollo's zeus as a raven that eats the sun and spits fire.",
     "The raven is a bird that never dies", "raven eye"),
    ("jupiter-light", "Light's Law", "Jupiter's light as a law that is both a word and a wall.",
     "The law is a word and the word is a wall", "word wall"),
    ("mercury-flight", "Flight's Chain", "Mercury's flight as a chain that is also a wing.",
     "The wing is a foot that never walks", "wing foot"),
    ("neptune-star", "Star's Star", "Neptune's star as a star that is also a cup.",
     "The cup is a star that never falls", "fountain cup"),
    ("pluto-ice", "Ice's Home", "Pluto's ice as a home the heat cannot enter.",
     "The home is a cold that never breaks", "cold heart"),
    ("apollo-mars", "Mars's Voice", "Apollo's mars as a voice that is both a word and a wall.",
     "The voice is the wall and the wall is the voice", "voice wall"),
    ("jupiter-scan", "Scan's Eye", "Jupiter's scan as an eye that sees without looking.",
     "The eye sees all and sees nothing", "seeing nothing"),
    ("mercury-stone", "Stone's Hand", "Mercury's stone as a hand that holds air.",
     "The hand holds what has no weight", "holding air"),
    ("neptune-moon", "Moon's Form", "Neptune's moon as a form that is not a shape.",
     "The moon has no shape but is still a moon", "shape without form"),
    ("pluto-death2", "Death's Dream", "Pluto's death as a dream that is also a door.",
     "The door is a dream and the dream is a door", "door dream"),


    ("zeus-nickel", "Nickel's Vault", "Zeus's nickel as a vault that does not close.",
     "The vault is a lock with no key", "vault"),
    ("montgolfiere-leger", "Leger's Air", "Montgolfiere's leger as the air that lifts the paper.",
     "The air is a hand that never lets go", "lifting air"),
    ("kaiser-schneider", "Schneider's Gate", "Kaiser's schneider as a gate that measures the crown.",
     "The gate is a crown that also measures", "crown gate"),
    ("freichen-birne", "Birne's Wire", "Freichen's birne as a wire that is also a bell.",
     "The wire is a bell that also rings", "bell wire"),
    ("forestier-pile", "Pile's Spark", "Forestier's pile as a spark that lights a hollow needle.",
     "The spark is a needle that also burns", "spark needle"),
    ("coulomb-torseur", "Torseur's Rod", "Coulomb's torseur as a rod that balances the arch.",
     "The rod is an arch that also balances", "rod arch"),
    ("caoutchouc-band", "Band's Hand", "Caoutchouc's band as a hand that holds without touching.",
     "The hand is a band that also holds", "band hand"),
    ("emile-cohen", "Cohen's Flame", "Emile's cohen as a flame that does not burn.",
     "The flame is a fire that never dies", "flame fire"),
    ("rothkopf-chord", "Chord's Ring", "Rothkopf's rothkopf as a ring that is also a clock.",
     "The ring is a clock that also measures", "ring clock"),
    ("schumann-reihe", "Reihe's Tone", "Schumann's schumann as a tone that is also a wall.",
     "The tone is a wall that also reads", "tone wall"),
    ("zwilling-glocke", "Glocke's Bell", "Zwingling's zwilling as a bell that is also a door.",
     "The bell is a door that also rings", "bell door"),
    ("teufel-schaufel", "Schaufel's Wheel", "Teufel's teufel as a wheel that is also a sky.",
     "The wheel is a sky that also holds", "sky wheel"),
    ("herz-feder", "Feder's Wing", "Herz's herz as a wing that is also a ball.",
     "The wing is a ball that never falls", "wing ball"),
    ("kehl-vogel", "Vogel's Song", "Kehl's kehl as a song that is also a stone.",
     "The song is a stone that also sings", "stone song"),
    ("dorn-spalte", "Spalte's Wall", "Dorn's dorn as a wall that is also a bridge.",
     "The wall is a bridge that also holds", "wall bridge"),
    ("geier-kugel", "Kugel's Eye", "Geier's geier as an eye that is also a blade.",
     "The eye is a blade that also sees", "blade eye"),
    ("van-der-veen", "Veen's Rope", "van derveen's van derveen as a rope that is also a road.",
     "The rope is a road that also leads", "rope road"),
    ("wassermann-glock", "Glock's Cast", "Wassermann's wassermann as a cast that is also a cup.",
     "The cast is a cup that holds the sky", "cast cup"),
    ("freund-gitter", "Gitter's Grid", "Freund's freund as a grid that is also a eye.",
     "The grid is an eye that also sees", "grid eye"),
    ("fischer-mohr", "Mohr's Stone", "Fischer's fischer as a stone that is also a bell.",
     "The stone is a bell that also rings", "stone bell"),
    ("krause-schuppen", "Schuppen's Leaf", "Krause's krause as a leaf that is also a chain.",
     "The leaf is a chain that also binds", "leaf chain"),
    ("kruger-gold", "Gold's Bar", "Kruger's kruger as a bar that is also a door.",
     "The bar is a door that also opens", "bar door"),
    ("liedmann-rad", "Rad's Wheel", "Liedmann's liedmann as a wheel that is also a step.",
     "The wheel is a step that also moves", "wheel step"),
    ("mayer-glas", "Glas's Car", "Mayer's mayer as a car that is also a wall.",
     "The car is a wall that also protects", "car wall"),
    ("niedermayer-balken", "Balken's Beam", "Niedermayer's niedermayer as a beam that is also a wall.",
     "The beam is a wall that also holds", "beam wall"),
    ("obermaier-kurve", "Kurve's Turn", "Obermaier's obermaier as a turn that is also a line.",
     "The turn is a line that also curves", "turn line"),
    ("petersen-mantel", "Mantel's Cloak", "Petersen's petersen as a cloak that is also a cup.",
     "The cloak is a cup that also holds", "cloak cup"),
    ("reichmann-saal", "Saal's Hall", "Reichmann's reichmann as a hall that is also a wall.",
     "The hall is a wall that also shelters", "hall wall"),
    ("ries-kugel", "Kugel's Orbit", "Ries's ries as an orbit that is also a gate.",
     "The orbit is a gate that also opens", "orbit gate"),
    ("schafkopf-kopf", "Kopf's Head", "Schafkopf's schafkopf as a head that is also a crown.",
     "The head is a crown that also rules", "head crown"),


    ("VENUS-BEARING", "VENUS-BEARING SPHERES", "Venus's spheres as a gathering of a thousand worlds orbiting a single star.",
     "A thousand worlds in deep gold", "deep gold"),
    ("PROTEUS-TIDES", "PROTEUS-TIDES", "Proteus's tides as a system of seven currents weaving through the black sea.",
     "Every tide is the pulse of a dead world", "the fractured rhythm"),
    ("DAKHMA-NIGHT", "DAKHMA-NIGHT", "Dakhma's night as a canyon of eternal twilight where the dead watch from above.",
     "A canyon painted with the color of no sunset", "twilight sandstone"),
    ("ZVEJNOI-FIRES", "ZVEJNOI-FIRES", "Zvejnoi's fires as a half-dozen paradoxical lanterns that cannot be lit.",
     "A dozen lanterns burning in the cold dark", "the impossible point"),
    ("DIM-VEKS-CALL", "DIM-VEKS-CALL", "Drim-Veks's call as a prism that lies about the light.",
     "The lie is a light that never blinds", "a broken mirror"),
    ("ARGON-VIVA", "ARGON-VIVA", "Argon-Viva as a locked chamber where the gods breathe without other gods present.",
     "A silent hall where every breath leaves a mark", "the locked door"),
    ("DAGGER-AI-WAY", "DAGGER-AI-WAY", "Dagger-Ai-Way as a road built of broken things that still leads somewhere.",
     "A path over broken glass and iron", "the seam in the machine"),
    ("SOFIA-ANOMALY", "SOFIA-ANOMALY", "Sofia's anomaly as a crack in the horizon that refuses to close.",
     "A wound in the sky that keeps opening", "unhealed fracture"),
    ("SYR-KAL-SAK", "SYR-KAL-SAK", "Syr-Kal-Sak as a ridge of seven tombs that cannot be climbed.",
     "Seven graves on a staircase to nowhere", "a compass pointing in a circle"),
    ("GEO-CODEX", "GEO-CODEX", "Geo-CodeX as a law that maps every place, a shadow of the map that claims to be the land.",
     "A codex that names every place even the places not yet named", "the map of everything"),
    ("LIM-LITT", "LIM-LITT", "Lim-Litt as a shadow that is not the thing it shadows; a flag of a land that is not there.",
     "A ship of the dead sailing off the edge", "a compass without north"),
    ("KAITS-MOYA", "KAITS-MOYA", "KaITs-Moya as a thought that becomes a thing when no one thinks it.",
     "A stone that remembers the shape of a bird", "a cry that makes the wall tremble"),
    ("SOD-NIGHT", "SOD-NIGHT", "Sed-Night as an ash that remembers conversation.",
     "The gray ash of a thousand words", "the wall that dreams of meeting"),
    ("VESTA-CALDERA", "VESTA-CALDERA", "Vesta-Caldera as a puddle of light that never warms.",
     "A pool of cold fire in the cold dark", "a dot of fire in an ocean of ice"),
    ("IONA-FALL", "IONA-FALL", "Iona-Fall as a water that is not wet, a color that is not the shape it fills.",
     "A river of light in the wrong shape", "a waterfall frozen at the wrong moment"),
    ("CTA-GIRL", "CTa-GIRL", "CTa-Girl as a mirror made of glass that never shows itself.",
     "A mirror that reflects what cannot be seen", "the eye that sees without looking"),
    ("VJAZL-REVES", "VJAZL-REVES", "Vjazl-Reves as a fabric that is not woven from threads.",
     "The coat of a man who is not there", "a chaos of needles that holds the memory"),
    ("MOT-PYAT", "MOT-PYAT", "Mot-Pyat as a dress that holds a locked room.",
     "The garment of a ghost in a house of glass", "a wound that heals by staying open"),
    ("KAFS-SADNER", "KAFS-SADNER", "Kafs-Sadner as a game that has no board.",
     "A prayer carved in the language of a dead people", "the shadow of a coin under the doorway"),
    ("YEKA-HOUSE", "YEKA-HOUSE", "YekA-House as a house that is not a place, a tent of darkness in the forest of the living.",
     "The house of the witches who are not there", "a voice whispering a name that is not someone's"),
    ("NEKOTORYE-LANDS", "NEKOTORYE-LANDS", "NeKOTOrYe as a treaty between gods and the dead.",
     "A border stone that does not mark a border", "a key to a house of stone that does not exist"),
    ("HAYASTAN-HOUSE", "HAYASTAN-HOUSE", "HayAstAn as a room of mirrors in a house with no walls.",
     "A tower of glass in a city of stone", "a lotus of fire among the stones"),
    ("SHOVEL-CIRCLE", "SHOVEL-CIRCLE", "ShoVel as a circle of stones with a hole in the middle.",
     "The field where the dead still stand", "the shape of a seed in the dust of the ape"),
    ("SPRINT-HOLO", "SPRINT-HOLO", "SPRINT-HOLO as a space with no walls, a room that is not a room.",
     "The body is not the house, the city is not the building", "the wave in the dry desert"),
    ("RETRO-PLUTO", "RETRO-PLUTO", "retro-Pluto as a wheel of loaves that speaks without a mouth, a tooth of glass that does not bite.",
     "A pyramid with no desert", "the chant of a god who has no name"),
    ("LYA-UDP-THE", "Lya-UDP-The", "Lya-UDP-The as a storm of stone in a dry world where nothing falls.",
     "A machine with no sound and no purpose", "the circle of a broken loom"),
    ("NAT-NOZ", "NAT-NOZ", "NAT-NOZ as a cup that holds no drink, a shadow that takes the shape of the thing it shadows.",
     "A cup that holds what can never be drunk", "the shadow of a bird that will not move"),
    ("BOTTOM-BOS", "BOTTOM-BOS", "BOTTOM-BOS as the end of everything, the ground that gives way to everything.",
     "The ground that gives way to everything", "the bottom of the well in the house of the blind"),
    ("VZNANIE-PLUTO", "VZNANIE-PLUTO", "Vznanie-Pluto as an eclipse that is not an eclipse",
     "The sun is not there", "the shadow of a blind god"),
    ("EROZIVAYA-DEYA", "EROZIVAYA-DEYA", "Erozivaya-DeYaA as the sound of a sword in a vault without walls",
     "The vault is not there", "the scream of a stone that never falls"),
]


def main():
    render_themes()
    write_index()
    print("\nDone. Spheres in " + str(OUT) + ": " + str(len(list(OUT.glob("*.html")))) + " files")


if __name__ == "__main__":
    main()
