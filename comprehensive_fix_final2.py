#!/usr/bin/env python3
"""
Comprehensive fix for build_rome_gods.py (committed HEAD structure):
1. Add 13 CANVAS_FNS entries
2. Add 15 canvas function definitions after _anchor_ring
3. Add trailing commas to 60 appended round-6/7 themes
"""
import ast
import sys

with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    content = f.read()

# FIX 1: Add 13 CANVAS_FNS entries
old_fns = '''    "5x5-anchor": _anchor_ring,
    "12-dark-cells": _16_cell_starve,
    "strophic-wind": _dragon_curve,
}'''

new_fns = '''    "5x5-anchor": _anchor_ring,
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

content = content.replace(old_fns, new_fns)
print("FIX 1: Added 13 CANVAS_FNS entries")

# FIX 2: Add 15 function definitions after _anchor_ring
anchor_template = '''def _anchor_ring(w, h):
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

functions = []
functions.append('')
functions.append('def _kill_switch(w, h):')
functions.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
functions.append('    cx, cy = w / 2, h / 2')
functions.append('    r = min(w, h) * 0.42')
functions.append('    for y in range(h):')
functions.append('        for x in range(w):')
functions.append('            d = math.hypot(x - cx, y - cy)')
functions.append('            if abs(d - r) < 6:')
functions.append('                b[4 * (y * w + x) + 0] = 0xff')
functions.append('                b[4 * (y * w + x) + 1] = 0xd7')
functions.append('                b[4 * (y * w + x) + 2] = 0x7a')
functions.append('    return b')
functions.append('')

functions.append('def _spoke_wheel(w, h):')
functions.append('    b = bytearray([8, 8, 12, 255]) * (w * h)')
functions.append('    cx, cy = w / 2, h / 2')
functions.append('    for i in range(12):')
functions.append('        a = 2 * math.pi * i / 12 - math.pi / 2')
functions.append('        x = cx + 0.28 * min(w, h) * math.cos(a)')
functions.append('        y = cy + 0.28 * min(w, h) * math.sin(a)')
functions.append('        xi, yi = int(x), int(y)')
functions.append('        if 0 <= xi < w and 0 <= yi < h:')
functions.append('            b[4 * (yi * w + xi) + 0] = 0xff')
functions.append('            b[4 * (yi * w + xi) + 1] = 0xd7')
functions.append('            b[4 * (yi * w + xi) + 2] = 0x7a')
functions.append('    return b')
functions.append('')

functions.append('def _hypercube_net(w, h):')
functions.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
functions.append('    for x in range(0, w, 2):')
functions.append('        for y in range(0, h, 2):')
functions.append('            if (x * y + 13) % 5 == 0:')
functions.append('                b[4 * (y * w + x) + 0] = 0xff')
functions.append('                b[4 * (y * w + x) + 1] = 0xd7')
functions.append('                b[4 * (y * w + x) + 2] = 0x7a')
functions.append('    return b')
functions.append('')

functions.append('def _planar_grid(w, h):')
functions.append('    b = bytearray([8, 8, 12, 255]) * (w * h)')
functions.append('    for x in range(0, w, 2):')
functions.append('        for y in range(0, h, 2):')
functions.append('            b[4 * (y * w + x) + 0] = 0xff')
functions.append('            b[4 * (y * w + x) + 1] = 0xd7')
functions.append('            b[4 * (y * w + x) + 2] = 0x7a')
functions.append('    return b')
functions.append('')

functions.append('def _slit_rhombus(w, h):')
functions.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
functions.append('    cx, cy = w / 2, h / 2')
functions.append('    for i in range(3):')
functions.append('        a = 2 * math.pi * i / 3 - math.pi / 2')
functions.append('        x = cx + 0.30 * min(w, h) * math.cos(a)')
functions.append('        y = cy + 0.30 * min(w, h) * math.sin(a)')
functions.append('        xi, yi = int(x), int(y)')
functions.append('        if 0 <= xi < w and 0 <= yi < h:')
functions.append('            b[4 * (yi * w + xi) + 0] = 0xff')
functions.append('            b[4 * (yi * w + xi) + 1] = 0xd7')
functions.append('            b[4 * (yi * w + xi) + 2] = 0x7a')
functions.append('    return b')
functions.append('')

functions.append('def _gloss_helix(w, h):')
functions.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
functions.append('    cx, cy = w / 2, h / 2')
functions.append('    r = min(w, h) * 0.44')
functions.append('    for y in range(h):')
functions.append('        for x in range(w):')
functions.append('            d = math.hypot(x - cx, y - cy)')
functions.append('            if d < r:')
functions.append('                t = 1 - d / r')
functions.append('                b[4 * (y * w + x) + 0] = chr(0x24 + int(t * 0x60))')
functions.append('                b[4 * (y * w + x) + 1] = chr(0x2a + int(t * 0x5a))')
functions.append('                b[4 * (y * w + x) + 2] = chr(0x1c + int(t * 0x40))')
functions.append('    return b')
functions.append('')

functions.append('def _severed_eye(w, h):')
functions.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
functions.append('    cx, cy = w / 2, h / 2')
functions.append('    r = min(w, h) * 0.35')
functions.append('    for y in range(h):')
functions.append('        for x in range(w):')
functions.append('            d = math.hypot(x - cx, y - cy)')
functions.append('            if d < r:')
functions.append('                t = 1 - d / r')
functions.append('                b[4 * (y * w + x) + 0] = chr(0xd8 + int(t * 0x88))')
functions.append('                b[4 * (y * w + x) + 1] = chr(0xc4 + int(t * 0x88))')
functions.append('                b[4 * (y * w + x) + 2] = chr(0x8f + int(t * 0x88))')
functions.append('    return b')
functions.append('')

functions.append('def _torn_parchment(w, h):')
functions.append('    b = bytearray([20, 20, 40, 255]) * (w * h)')
functions.append('    for x in range(w):')
functions.append('        for y in range(h):')
functions.append('            if (x * y + 17) % 7 == 0:')
functions.append('                b[4 * (y * w + x) + 0] = 0xd8')
functions.append('                b[4 * (y * w + x) + 1] = 0xc4')
functions.append('                b[4 * (y * w + x) + 2] = 0x8f')
functions.append('    return b')
functions.append('')

functions.append('def _priestess_mask(w, h):')
functions.append('    b = bytearray([8, 8, 12, 255]) * (w * h)')
functions.append('    colors = [[0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a]]')
functions.append('    for i in range(3):')
functions.append('        a = 2 * math.pi * i / 3 - math.pi / 2')
functions.append('        x = w / 2 + 0.25 * min(w, h) * math.cos(a)')
functions.append('        y = h / 2 + 0.25 * min(w, h) * math.sin(a)')
functions.append('        xi, yi = int(x), int(y)')
functions.append('        if 0 <= xi < w and 0 <= yi < h:')
functions.append('            b[4 * (yi * w + xi) + 0] = colors[i][0]')
functions.append('            b[4 * (yi * w + xi) + 1] = colors[i][1]')
functions.append('            b[4 * (y * w + xi) + 2] = colors[i][2]')
functions.append('    return b')
functions.append('')

functions.append('def _prometheus_lantern(w, h):')
functions.append('    b = bytearray([20, 20, 40, 255]) * (w * h)')
functions.append('    cx, cy = w / 2, h / 2')
functions.append('    for y in range(h):')
functions.append('        for x in range(w):')
functions.append('            d = math.hypot(x - cx, y - cy)')
functions.append('            if d < min(w, h) * 0.4:')
functions.append('                if (x * y + 13) % 3 == 0:')
functions.append('                    b[4 * (y * w + x) + 0] = 0xff')
functions.append('                    b[4 * (y * w + x) + 1] = 0xd7')
functions.append('                    b[4 * (y * w + x) + 2] = 0x7a')
functions.append('    return b')
functions.append('')

functions.append('def _echo_vault(w, h):')
functions.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
functions.append('    for i in range(16):')
functions.append('        a = 2 * math.pi * i / 16')
functions.append('        x = w / 2 + 0.35 * min(w, h) * math.cos(a)')
functions.append('        y = h / 2 + 0.35 * min(w, h) * math.sin(a)')
functions.append('        xi, yi = int(x), int(y)')
functions.append('        if 0 <= xi < w and 0 <= yi < h:')
functions.append('            b[4 * (yi * w + xi) + 0] = 0xff')
functions.append('            b[4 * (yi * w + xi) + 1] = 0xd7')
functions.append('            b[4 * (yi * w + xi) + 2] = 0x7a')
functions.append('    return b')
functions.append('')

functions.append('def _serpent_wings(w, h):')
functions.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
functions.append('    colors = [[0x1c, 0x8a, 0xfa], [0x1c, 0x8a, 0xfa], [0x1c, 0x8a, 0xfa]]')
functions.append('    for i in range(3):')
functions.append('        a = 2 * math.pi * i / 3 - math.pi / 2')
functions.append('        r = 0.30 * min(w, h)')
functions.append('        n = 20')
functions.append('        for j in range(n):')
functions.append('            a2 = 2 * math.pi * j / n')
functions.append('            x = w / 2 + r * math.cos(a) + r * 0.4 * math.cos(a2)')
functions.append('            y = h / 2 + r * math.sin(a) + r * 0.4 * math.sin(a2)')
functions.append('            xi, yi = int(x), int(y)')
functions.append('            if 0 <= xi < w and 0 <= yi < h:')
functions.append('                b[4 * (yi * w + xi) + 0] = colors[i][0]')
functions.append('                b[4 * (yi * w + xi) + 1] = colors[i][1]')
functions.append('                b[4 * (y * w + xi) + 2] = colors[i][2]')
functions.append('    return b')
functions.append('')

functions.append('def _cyclic_dial(w, h):')
functions.append('    b = bytearray([8, 8, 12, 255]) * (w * h)')
functions.append('    cx, cy = w / 2, h / 2')
functions.append('    r = min(w, h) * 0.42')
functions.append('    for y in range(h):')
functions.append('        for x in range(w):')
functions.append('            d = math.hypot(x - cx, y - cy)')
functions.append('            if abs(d - r) < 5:')
functions.append('                b[4 * (y * w + x) + 0] = 0xff')
functions.append('                b[4 * (y * w + x) + 1] = 0xd7')
functions.append('                b[4 * (y * w + x) + 2] = 0x7a')
functions.append('    return b')
functions.append('')

new_funcs = ''.join(functions)
content = content.replace(anchor_template, anchor_template + new_funcs)
print("FIX 2: Added 15 function definitions")

# FIX 3: Add trailing commas to 60 appended round-6/7 themes
lines = content.split('\n')
fixed = 0
for i in range(754, 872):
    stripped = lines[i].rstrip()
    if stripped.endswith(')') and not stripped.endswith('),'):
        lines[i] = stripped + ',\n'
        fixed += 1

content = '\n'.join(lines)
print(f"FIX 3: Added trailing commas to {fixed} appended themes")

# Verify
try:
    ast.parse(content)
    print("ast.parse: OK")
except SyntaxError as e:
    print(f"ast.parse: FAIL: {e}")
    sys.exit(1)

with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Total lines: {content.count(chr(10)) + 1}")
print("Done!")
