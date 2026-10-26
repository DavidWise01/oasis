#!/usr/bin/env python3
"""
FINAL FIX for build_rome_gods.py (committed HEAD state, 883 lines):
1. Add 13 CANVAS_FNS entries (lines 448-451 area)
2. Add 15 canvas function definitions after _anchor_ring 
3. Add trailing commas to 60 appended round-6/7 themes

Committed HEAD structure (verified:
- CANVAS_FNS: 22 entries, lines 428-451
- _anchor_ring: 12 lines (287-298)
- THEMES list: 180 themes (lines 568-873) 
- 60 appended round-6/7 themes: lines 755-872 (bare tuples, NO commas)
- def main(): at line 876
"""
import ast
from collections import OrderedDict
import sys

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # FIX 1: Add 13 CANVAS_FNS entries after CANVAS_FNS close
    old_fns_close = '    "5x5-anchor": _anchor_ring,\n    "12-dark-cells": _16_cell_starve,\n    "strophic-wind": _dragon_curve,\n}'

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

    if old_fns_close in content:
        content = content.replace(old_fns_close, new_fns_close)
        print("FIX 1: Added 13 CANVAS_FNS entries")
    else:
        print("ERROR: CANVAS_FNS close not found")
        sys.exit(1)

    # FIX 2: Add 15 function definitions after _anchor_ring
    # The _anchor_ring function is exactly 12 lines
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

    # Build 15 new functions
    new_funcs = []
    new_funcs.append('')
    new_funcs.append('def _kill_switch(w, h):')
    new_funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    new_funcs.append('    cx, cy = w / 2, h / 2')
    new_funcs.append('    r = min(w, h) * 0.42')
    new_funcs.append('    for y in range(h):')
    new_funcs.append('        for x in range(w):')
    new_funcs.append('            d = math.hypot(x - cx, y - cy)')
    new_funcs.append('            if abs(d - r) < 6:')
    new_funcs.append('                b[4 * (y * w + x) + 0] = 0xff')
    new_funcs.append('                b[4 * (y * w + x) + 1] = 0xd7')
    new_funcs.append('                b[4 * (y * w + x) + 2] = 0x7a')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def _spoke_wheel(w, h):')
    new_funcs.append('    b = bytearray([8, 8, 12, 255]) * (w * h)')
    new_funcs.append('    cx, cy = w / 2, h / 2')
    new_funcs.append('    for i in range(12):')
    new_funcs.append('        a = 2 * math.pi * i / 12 - math.pi / 2')
    new_funcs.append('        x = cx + 0.28 * min(w, h) * math.cos(a)')
    new_funcs.append('        y = cy + 0.28 * min(w, h) * math.sin(a)')
    new_funcs.append('        xi, yi = int(x), int(y)')
    new_funcs.append('        if 0 <= xi < w and 0 <= yi < h:')
    new_funcs.append('            b[4 * (yi * w + xi) + 0] = 0xff')
    new_funcs.append('            b[4 * (yi * w + xi) + 1] = 0xd7')
    new_funcs.append('            b[4 * (yi * w + xi) + 2] = 0x7a')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def _hypercube_net(w, h):')
    new_funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    new_funcs.append('    for x in range(0, w, 2):')
    new_funcs.append('        for y in range(0, h, 2):')
    new_funcs.append('            if (x * y + 13) % 5 == 0:')
    new_funcs.append('                b[4 * (y * w + x) + 0] = 0xff')
    new_funcs.append('                b[4 * (y * w + x) + 1] = 0xd7')
    new_funcs.append('                b[4 * (y * w + x) + 2] = 0x7a')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def _planar_grid(w, h):')
    new_funcs.append('    b = bytearray([8, 8, 12, 255]) * (w * h)')
    new_funcs.append('    for x in range(0, w, 2):')
    new_funcs.append('        for y in range(0, h, 2):')
    new_funcs.append('            b[4 * (y * w + x) + 0] = 0xff')
    new_funcs.append('            b[4 * (y * w + x) + 1] = 0xd7')
    new_funcs.append('            b[4 * (y * w + x) + 2] = 0x7a')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def _slit_rhombus(w, h):')
    new_funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    new_funcs.append('    cx, cy = w / 2, h / 2')
    new_funcs.append('    for i in range(3):')
    new_funcs.append('        a = 2 * math.pi * i / 3 - math.pi / 2')
    new_funcs.append('        x = cx + 0.30 * min(w, h) * math.cos(a)')
    new_funcs.append('        y = cy + 0.30 * min(w, h) * math.sin(a)')
    new_funcs.append('        xi, yi = int(x), int(y)')
    new_funcs.append('        if 0 <= xi < w and 0 <= yi < h:')
    new_funcs.append('            b[4 * (yi * w + xi) + 0] = 0xff')
    new_funcs.append('            b[4 * (yi * w + xi) + 1] = 0xd7')
    new_funcs.append('            b[4 * (yi * w + xi) + 2] = 0x7a')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def _gloss_helix(w, h):')
    new_funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    new_funcs.append('    cx, cy = w / 2, h / 2')
    new_funcs.append('    r = min(w, h) * 0.44')
    new_funcs.append('    for y in range(h):')
    new_funcs.append('        for x in range(w):')
    new_funcs.append('            d = math.hypot(x - cx, y - cy)')
    new_funcs.append('            if d < r:')
    new_funcs.append('                t = 1 - d / r')
    new_funcs.append('                b[4 * (y * w + x) + 0] = chr(0x24 + int(t * 0x60))')
    new_funcs.append('                b[4 * (y * w + x) + 1] = chr(0x2a + int(t * 0x5a))')
    new_funcs.append('                b[4 * (y * w + x) + 2] = chr(0x1c + int(t * 0x40))')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def _severed_eye(w, h):')
    new_funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    new_funcs.append('    cx, cy = w / 2, h / 2')
    new_funcs.append('    r = min(w, h) * 0.35')
    new_funcs.append('    for y in range(h):')
    new_funcs.append('        for x in range(w):')
    new_funcs.append('            d = math.hypot(x - cx, y - cy)')
    new_funcs.append('            if d < r:')
    new_funcs.append('                t = 1 - d / r')
    new_funcs.append('                b[4 * (y * w + x) + 0] = chr(0xd8 + int(t * 0x88))')
    new_funcs.append('                b[4 * (y * w + x) + 1] = chr(0xc4 + int(t * 0x88))')
    new_funcs.append('                b[4 * (y * w + x) + 2] = chr(0x8f + int(t * 0x88))')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def _torn_parchment(w, h):')
    new_funcs.append('    b = bytearray([20, 20, 40, 255]) * (w * h)')
    new_funcs.append('    for x in range(w):')
    new_funcs.append('        for y in range(h):')
    new_funcs.append('            if (x * y + 17) % 7 == 0:')
    new_funcs.append('                b[4 * (y * w + x) + 0] = 0xd8')
    new_funcs.append('                b[4 * (y * w + x) + 1] = 0xc4')
    new_funcs.append('                b[4 * (y * w + x) + 2] = 0x8f')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def _priestess_mask(w, h):')
    new_funcs.append('    b = bytearray([8, 8, 12, 255]) * (w * h)')
    new_funcs.append('    colors = [[0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a]]')
    new_funcs.append('    for i in range(3):')
    new_funcs.append('        a = 2 * math.pi * i / 3 - math.pi / 2')
    new_funcs.append('        x = w / 2 + 0.25 * min(w, h) * math.cos(a)')
    new_funcs.append('        y = h / 2 + 0.25 * min(w, h) * math.sin(a)')
    new_funcs.append('        xi, yi = int(x), int(y)')
    new_funcs.append('        if 0 <= xi < w and 0 <= yi < h:')
    new_funcs.append('            b[4 * (yi * w + xi) + 0] = colors[i][0]')
    new_funcs.append('            b[4 * (yi * w + xi) + 1] = colors[i][1]')
    new_funcs.append('            b[4 * (y * w + xi) + 2] = colors[i][2]')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def _prometheus_lantern(w, h):')
    new_funcs.append('    b = bytearray([20, 20, 40, 255]) * (w * h)')
    new_funcs.append('    cx, cy = w / 2, h / 2')
    new_funcs.append('    for y in range(h):')
    new_funcs.append('        for x in range(w):')
    new_funcs.append('            d = math.hypot(x - cx, y - cy)')
    new_funcs.append('            if d < min(w, h) * 0.4:')
    new_funcs.append('                if (x * y + 13) % 3 == 0:')
    new_funcs.append('                    b[4 * (y * w + x) + 0] = 0xff')
    new_funcs.append('                    b[4 * (y * w + x) + 1] = 0xd7')
    new_funcs.append('                    b[4 * (y * w + x) + 2] = 0x7a')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def _echo_vault(w, h):')
    new_funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    new_funcs.append('    for i in range(16):')
    new_funcs.append('        a = 2 * math.pi * i / 16')
    new_funcs.append('        x = w / 2 + 0.35 * min(w, h) * math.cos(a)')
    new_funcs.append('        y = h / 2 + 0.35 * min(w, h) * math.sin(a)')
    new_funcs.append('        xi, yi = int(x), int(y)')
    new_funcs.append('        if 0 <= xi < w and 0 <= yi < h:')
    new_funcs.append('            b[4 * (yi * w + xi) + 0] = 0xff')
    new_funcs.append('            b[4 * (yi * w + xi) + 1] = 0xd7')
    new_funcs.append('            b[4 * (y * w + xi) + 2] = 0x7a')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def _serpent_wings(w, h):')
    new_funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    new_funcs.append('    colors = [[0x1c, 0x8a, 0xfa], [0x1c, 0x8a, 0xfa], [0x1c, 0x8a, 0xfa]]')
    new_funcs.append('    for i in range(3):')
    new_funcs.append('        a = 2 * math.pi * i / 3 - math.pi / 2')
    new_funcs.append('        r = 0.30 * min(w, h)')
    new_funcs.append('        n = 20')
    new_funcs.append('        for j in range(n):')
    new_funcs.append('            a2 = 2 * math.pi * j / n')
    new_funcs.append('            x = w / 2 + r * math.cos(a) + r * 0.4 * math.cos(a2)')
    new_funcs.append('            y = h / 2 + r * math.sin(a) + r * 0.4 * math.sin(a2)')
    new_funcs.append('            xi, yi = int(x), int(y)')
    new_funcs.append('            if 0 <= xi < w and 0 <= yi < h:')
    new_funcs.append('                b[4 * (yi * w + xi) + 0] = colors[i][0]')
    new_funcs.append('                b[4 * (yi * w + xi) + 1] = colors[i][1]')
    new_funcs.append('                b[4 * (y * w + xi) + 2] = colors[i][2]')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def _cyclic_dial(w, h):')
    new_funcs.append('    b = bytearray([8, 8, 12, 255]) * (w * h)')
    new_funcs.append('    cx, cy = w / 2, h / 2')
    new_funcs.append('    r = min(w, h) * 0.42')
    new_funcs.append('    for y in range(h):')
    new_funcs.append('        for x in range(w):')
    new_funcs.append('            d = math.hypot(x - cx, y - cy)')
    new_funcs.append('            if abs(d - r) < 5:')
    new_funcs.append('                b[4 * (y * w + x) + 0] = 0xff')
    new_funcs.append('                b[4 * (y * w + x) + 1] = 0xd7')
    new_funcs.append('                b[4 * (y * w + x) + 2] = 0x7a')
    new_funcs.append('    return b')

    new_funcs.append('')
    new_funcs.append('def canvas_art(key, w=1600, h=900):')

    # Add the new functions after _anchor_ring
    new_content = ''.join(new_funcs)
    if anchor_func in content:
        content = content.replace(anchor_func, new_content)
        print("FIX 2: Added 15 function definitions")
    else:
        print("ERROR: anchor_func not found")
        sys.exit(1)

    # FIX 3: Add trailing commas to 60 appended round-6/7 themes
    lines = content.split('\n')
    fixed = 0
    for i in range(754, 872):
        stripped = lines[i].rstrip()
        if stripped.endswith(')') and not stripped.endswith('),'):
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

    print(f"Fixed {fixed} trailing commas on appended themes")
    print(f"Total lines: {content.count(chr(10)) + 1}")
    print("All fixes complete!")

if __name__ == '__main__':
    fix_file('build_rome_gods.py')
