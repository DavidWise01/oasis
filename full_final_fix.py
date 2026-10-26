#!/usr/bin/env python3
"""
Final comprehensive fix for build_rome_gods.py (committed HEAD state):
1. Add 13 CANVAS_FNS entries
2. Add 15 canvas function definitions after _anchor_ring
3. Add trailing commas to 60 appended round-6/7 themes
"""
import ast
import sys

def fix_build_rome_gods(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # FIX 1: Add 13 CANVAS_FNS entries after CANVAS_FNS close
    old_fns_close = '''    "5x5-anchor": _anchor_ring,
    "12-dark-cells": _16_cell_starve,
    "strophic-wind": _dragon_curve,
}'''

    new_fns_close = '''    "5x5-anchor": _anchor_ring,
    "12-dark-cells": _16_cell_starve,
    "strophic-wind": _dragon_curve,
    "kill-switch": _kill_switch,
    "spoke-wheel": _spoke_wheel,
    "hypercube-net": _hypercube_net,
    "planar-grid": _planar_grid,
    "slit-rhombus": _slit_rhombus,
    "gloss-helix": _gloss_helix,
    "severed-eye": _severed_eye,
    "torn-parchment": _torn_parchment,
    "priestess-mask": _priestess_mask,
    "prometheus-lantern": _prometheus_lantern,
    "echo-vault": _echo_vault,
    "serpent-wings": _serpent_wings,
    "cyclic-dial": _cyclic_dial,
}'''

    content = content.replace(old_fns_close, new_fns_close)

    # FIX 2: Add 15 function definitions after _anchor_ring
    anchor_func = '''def _anchor_ring(w, h):
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
'''

    new_funcs = '''def _anchor_ring(w, h):
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


def _kill_switch(w, h):
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


def _spoke_wheel(w, h):
    b = bytearray([8, 8, 12, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    for i in range(12):
        a = 2 * math.pi * i / 12 - math.pi / 2
        x = cx + 0.28 * min(w, h) * math.cos(a)
        y = cy + 0.28 * min(w, h) * math.sin(a)
        xi, yi = int(x), int(y)
        if 0 <= xi < w and 0 <= yi < h:
            b[4 * (yi * w + xi) + 0] = 0xff
            b[4 * (yi * w + xi) + 1] = 0xd7
            b[4 * (yi * w + xi) + 2] = 0x7a
    return b


def _hypercube_net(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    for x in range(0, w, 2):
        for y in range(0, h, 2):
            if (x * y + 13) % 5 == 0:
                b[4 * (y * w + x) + 0] = 0xff
                b[4 * (y * w + x) + 1] = 0xd7
                b[4 * (y * w + x) + 2] = 0x7a
    return b


def _planar_grid(w, h):
    b = bytearray([8, 8, 12, 255]) * (w * h)
    for x in range(0, w, 2):
        for y in range(0, h, 2):
            b[4 * (y * w + x) + 0] = 0xff
            b[4 * (y * w + x) + 1] = 0xd7
            b[4 * (y * w + x) + 2] = 0x7a
    return b


def _slit_rhombus(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    for i in range(3):
        a = 2 * math.pi * i / 3 - math.pi / 2
        x = cx + 0.30 * min(w, h) * math.cos(a)
        y = cy + 0.30 * min(w, h) * math.sin(a)
        xi, yi = int(x), int(y)
        if 0 <= xi < w and 0 <= yi < h:
            b[4 * (yi * w + xi) + 0] = 0xff
            b[4 * (yi * w + xi) + 1] = 0xd7
            b[4 * (yi * w + xi) + 2] = 0x7a
    return b


def _gloss_helix(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    r = min(w, h) * 0.44
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            if d < r:
                t = 1 - d / r
                b[4 * (y * w + x) + 0] = chr(0x24 + int(t * 0x60))
                b[4 * (y * w + x) + 1] = chr(0x2a + int(t * 0x5a))
                b[4 * (y * w + x) + 2] = chr(0x1c + int(t * 0x40))
    return b


def _severed_eye(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    r = min(w, h) * 0.35
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            if d < r:
                t = 1 - d / r
                b[4 * (y * w + x) + 0] = chr(0xd8 + int(t * 0x88))
                b[4 * (y * w + x) + 1] = chr(0xc4 + int(t * 0x88))
                b[4 * (y * w + x) + 2] = chr(0x8f + int(t * 0x88))
    return b


def _torn_parchment(w, h):
    b = bytearray([20, 20, 40, 255]) * (w * h)
    for x in range(w):
        for y in range(h):
            if (x * y + 17) % 7 == 0:
                b[4 * (y * w + x) + 0] = 0xd8
                b[4 * (y * w + x) + 1] = 0xc4
                b[4 * (y * w + x) + 2] = 0x8f
    return b


def _priestess_mask(w, h):
    b = bytearray([8, 8, 12, 255]) * (w * h)
    colors = [[0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a]]
    for i in range(3):
        a = 2 * math.pi * i / 3 - math.pi / 2
        x = w / 2 + 0.25 * min(w, h) * math.cos(a)
        y = h / 2 + 0.25 * min(w, h) * math.sin(a)
        xi, yi = int(x), int(y)
        if 0 <= xi < w and 0 <= yi < h:
            b[4 * (yi * w + xi) + 0] = colors[i][0]
            b[4 * (yi * w + xi) + 1] = colors[i][1]
            b[4 * (y * w + xi) + 2] = colors[i][2]
    return b


def _prometheus_lantern(w, h):
    b = bytearray([20, 20, 40, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            if d < min(w, h) * 0.4:
                if (x * y + 13) % 3 == 0:
                    b[4 * (y * w + x) + 0] = 0xff
                    b[4 * (y * w + x) + 1] = 0xd7
                    b[4 * (y * w + x) + 2] = 0x7a
    return b


def _echo_vault(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    for i in range(16):
        a = 2 * math.pi * i / 16
        x = w / 2 + 0.35 * min(w, h) * math.cos(a)
        y = h / 2 + 0.35 * min(w, h) * math.sin(a)
        xi, yi = int(x), int(y)
        if 0 <= xi < w and 0 <= yi < h:
            b[4 * (yi * w + xi) + 0] = 0xff
            b[4 * (yi * w + xi) + 1] = 0xd7
            b[4 * (yi * w + xi) + 2] = 0x7a
    return b


def _serpent_wings(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    colors = [[0x1c, 0x8a, 0xfa], [0x1c, 0x8a, 0xfa], [0x1c, 0x8a, 0xfa]]
    for i in range(3):
        a = 2 * math.pi * i / 3 - math.pi / 2
        r = 0.30 * min(w, h)
        n = 20
        for j in range(n):
            a2 = 2 * math.pi * j / n
            x = w / 2 + r * math.cos(a) + r * 0.4 * math.cos(a2)
            y = h / 2 + r * math.sin(a) + r * 0.4 * math.sin(a2)
            xi, yi = int(x), int(y)
            if 0 <= xi < w and 0 <= yi < h:
                b[4 * (yi * w + xi) + 0] = colors[i][0]
                b[4 * (yi * w + xi) + 1] = colors[i][1]
                b[4 * (y * w + xi) + 2] = colors[i][2]
    return b


def _cyclic_dial(w, h):
    b = bytearray([8, 8, 12, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    r = min(w, h) * 0.42
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            if abs(d - r) < 5:
                b[4 * (y * w + x) + 0] = 0xff
                b[4 * (y * w + x) + 1] = 0xd7
                b[4 * (y * w + x) + 2] = 0x7a
    return b


def canvas_art(key, w=1600, h=900):'''

    content = content.replace(anchor_func, new_funcs)

    # FIX 3: Add trailing commas to 60 appended round-6/7 themes (lines 755-872)
    lines = content.split('\n')
    fixed = 0
    for i in range(754, 872):
        stripped = lines[i].rstrip()
        if stripped.endswith(')') and not stripped.endswith('),'):
            # Skip if it's a comment line
            if not stripped.startswith('#'):
                lines[i] = stripped + ',\n'
                fixed += 1

    content = '\n'.join(lines)

    # Verify
    try:
        ast.parse(content)
        print("ast.parse: OK")
    except SyntaxError as e:
        print(f"ast.parse: FAIL: {e}")
        sys.exit(1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Fixed trailing commas on {fixed} lines")
    print(f"Total lines: {content.count(chr(10)) + 1}")
    print("All fixes applied successfully!")

if __name__ == '__main__':
    fix_build_rome_gods('build_rome_gods.py')
