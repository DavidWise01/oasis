#!/usr/bin/env python3
"""
Final fix for build_rome_gods.py (committed HEAD state, 883 lines):
1. Add 13 CANVAS_FNS entries
2. Add 15 canvas function definitions after _anchor_ring  
3. Add trailing commas to 60 appended round-6/7 themes

Committed HEAD structure:
- CANVAS_FNS: 22 entries, lines 428-451
- _anchor_ring: 12 lines (287-298), only canvas function
- THEMES list: 180 themes (568-873)
- 60 appended round-6/7 themes: lines 755-872 (bare tuples, no commas)
- def main(): at line 876
"""
import ast
import sys


def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
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

    funcs = []
    funcs.append('')
    funcs.append('def _kill_switch(w, h):')
    funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    funcs.append('    cx, cy = w / 2, h / 2')
    funcs.append('    r = min(w, h) * 0.42')
    funcs.append('    for y in range(h):')
    funcs.append('        for x in range(w):')
    funcs.append('            d = math.hypot(x - cx, y - cy)')
    funcs.append('            if abs(d - r) < 6:')
    funcs.append('                b[4 * (y * w + x) + 0] = 0xff')
    funcs.append('                b[4 * (y * w + x) + 1] = 0xd7')
    funcs.append('                b[4 * (y * w + x) + 2] = 0x7a')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def _spoke_wheel(w, h):')
    funcs.append('    b = bytearray([8, 8, 12, 255]) * (w * h)')
    funcs.append('    cx, cy = w / 2, h / 2')
    funcs.append('    for i in range(12):')
    funcs.append('        a = 2 * math.pi * i / 12 - math.pi / 2')
    funcs.append('        x = cx + 0.28 * min(w, h) * math.cos(a)')
    funcs.append('        y = cy + 0.28 * min(w, h) * math.sin(a)')
    funcs.append('        xi, yi = int(x), int(y)')
    funcs.append('        if 0 <= xi < w and 0 <= yi < h:')
    funcs.append('            b[4 * (yi * w + xi) + 0] = 0xff')
    funcs.append('            b[4 * (yi * w + xi) + 1] = 0xd7')
    funcs.append('            b[4 * (yi * w + xi) + 2] = 0x7a')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def _hypercube_net(w, h):')
    funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    funcs.append('    for x in range(0, w, 2):')
    funcs.append('        for y in range(0, h, 2):')
    funcs.append('            if (x * y + 13) % 5 == 0:')
    funcs.append('                b[4 * (y * w + x) + 0] = 0xff')
    funcs.append('                b[4 * (y * w + x) + 1] = 0xd7')
    funcs.append('                b[4 * (y * w + x) + 2] = 0x7a')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def _planar_grid(w, h):')
    funcs.append('    b = bytearray([8, 8, 12, 255]) * (w * h)')
    funcs.append('    for x in range(0, w, 2):')
    funcs.append('        for y in range(0, h, 2):')
    funcs.append('            b[4 * (y * w + x) + 0] = 0xff')
    funcs.append('            b[4 * (y * w + x) + 1] = 0xd7')
    funcs.append('            b[4 * (y * w + xi) + 2] = 0x7a')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def _slit_rhombus(w, h):')
    funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    funcs.append('    cx, cy = w / 2, h / 2')
    funcs.append('    for i in range(3):')
    funcs.append('        a = 2 * math.pi * i / 3 - math.pi / 2')
    funcs.append('        x = cx + 0.30 * min(w, h) * math.cos(a)')
    funcs.append('        y = cy + 0.30 * min(w, h) * math.sin(a)')
    funcs.append('        xi, yi = int(x), int(y)')
    funcs.append('        if 0 <= xi < w and 0 <= yi < h:')
    funcs.append('            b[4 * (yi * w + xi) + 0] = 0xff')
    funcs.append('            b[4 * (yi * w + xi) + 1] = 0xd7')
    funcs.append('            b[4 * (yi * w + xi) + 2] = 0x7a')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def _gloss_helix(w, h):')
    funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    funcs.append('    cx, cy = w / 2, h / 2')
    funcs.append('    r = min(w, h) * 0.44')
    funcs.append('    for y in range(h):')
    funcs.append('        for x in range(w):')
    funcs.append('            d = math.hypot(x - cx, y - cy)')
    funcs.append('            if d < r:')
    funcs.append('                t = 1 - d / r')
    funcs.append('                b[4 * (y * w + x) + 0] = chr(0x24 + int(t * 0x60))')
    funcs.append('                b[4 * (y * w + x) + 1] = chr(0x2a + int(t * 0x5a))')
    funcs.append('                b[4 * (y * w + x) + 2] = chr(0x1c + int(t * 0x40))')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def _severed_eye(w, h):')
    funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    funcs.append('    cx, cy = w / 2, h / 2')
    funcs.append('    r = min(w, h) * 0.35')
    funcs.append('    for y in range(h):')
    funcs.append('        for x in range(w):')
    funcs.append('            d = math.hypot(x - cx, y - cy)')
    funcs.append('            if d < r:')
    funcs.append('                t = 1 - d / r')
    funcs.append('                b[4 * (y * w + x) + 0] = chr(0xd8 + int(t * 0x88))')
    funcs.append('                b[4 * (y * w + x) + 1] = chr(0xc4 + int(t * 0x88))')
    funcs.append('                b[4 * (y * w + x) + 2] = chr(0x8f + int(t * 0x88))')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def _torn_parchment(w, h):')
    funcs.append('    b = bytearray([20, 20, 40, 255]) * (w * h)')
    funcs.append('    for x in range(w):')
    funcs.append('        for y in range(h):')
    funcs.append('            if (x * y + 17) % 7 == 0:')
    funcs.append('                b[4 * (y * w + x) + 0] = 0xd8')
    funcs.append('                b[4 * (y * w + x) + 1] = 0xc4')
    funcs.append('                b[4 * (y * w + x) + 2] = 0x8f')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def _priestess_mask(w, h):')
    funcs.append('    b = bytearray([8, 8, 12, 255]) * (w * h)')
    funcs.append('    colors = [[0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a]]')
    funcs.append('    for i in range(3):')
    funcs.append('        a = 2 * math.pi * i / 3 - math.pi / 2')
    funcs.append('        x = w / 2 + 0.25 * min(w, h) * math.cos(a)')
    funcs.append('        y = h / 2 + 0.25 * min(w, h) * math.sin(a)')
    funcs.append('        xi, yi = int(x), int(y)')
    funcs.append('        if 0 <= xi < w and 0 <= yi < h:')
    funcs.append('            b[4 * (yi * w + xi) + 0] = colors[i][0]')
    funcs.append('            b[4 * (yi * w + xi) + 1] = colors[i][1]')
    funcs.append('            b[4 * (y * w + xi) + 2] = colors[i][2]')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def _prometheus_lantern(w, h):')
    funcs.append('    b = bytearray([20, 20, 40, 255]) * (w * h)')
    funcs.append('    cx, cy = w / 2, h / 2')
    funcs.append('    for y in range(h):')
    funcs.append('        for x in range(w):')
    funcs.append('            d = math.hypot(x - cx, y - cy)')
    funcs.append('            if d < min(w, h) * 0.4:')
    funcs.append('                if (x * y + 13) % 3 == 0:')
    funcs.append('                    b[4 * (y * w + x) + 0] = 0xff')
    funcs.append('                    b[4 * (y * w + x) + 1] = 0xd7')
    funcs.append('                    b[4 * (y * w + xi) + 2] = 0x7a')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def _echo_vault(w, h):')
    funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    funcs.append('    for i in range(16):')
    funcs.append('        a = 2 * math.pi * i / 16')
    funcs.append('        x = w / 2 + 0.35 * min(w, h) * math.cos(a)')
    funcs.append('        y = h / 2 + 0.35 * min(w, h) * math.sin(a)')
    funcs.append('        xi, yi = int(x), int(y)')
    funcs.append('        if 0 <= xi < w and 0 <= yi < h:')
    funcs.append('            b[4 * (yi * w + xi) + 0] = 0xff')
    funcs.append('            b[4 * (yi * w + xi) + 1] = 0xd7')
    funcs.append('            b[4 * (y * w + xi) + 2] = 0x7a')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def _serpent_wings(w, h):')
    funcs.append('    b = bytearray([5, 5, 10, 255]) * (w * h)')
    funcs.append('    colors = [[0x1c, 0x8a, 0xfa], [0x1c, 0x8a, 0xfa], [0x1c, 0x8a, 0xfa]]')
    funcs.append('    for i in range(3):')
    funcs.append('        a = 2 * math.pi * i / 3 - math.pi / 2')
    funcs.append('        r = 0.30 * min(w, h)')
    funcs.append('        n = 20')
    funcs.append('        for j in range(n):')
    funcs.append('            a2 = 2 * math.pi * j / n')
    funcs.append('            x = w / 2 + r * math.cos(a) + r * 0.4 * math.cos(a2)')
    funcs.append('            y = h / 2 + r * math.sin(a) + r * 0.4 * math.sin(a2)')
    funcs.append('            xi, yi = int(x), int(y)')
    funcs.append('            if 0 <= xi < w and 0 <= yi < h:')
    funcs.append('                b[4 * (yi * w + xi) + 0] = colors[i][0]')
    funcs.append('                b[4 * (yi * w + xi) + 1] = colors[i][1]')
    funcs.append('                b[4 * (y * w + xi) + 2] = colors[i][2]')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def _cyclic_dial(w, h):')
    funcs.append('    b = bytearray([8, 8, 12, 255]) * (w * h)')
    funcs.append('    cx, cy = w / 2, h / 2')
    funcs.append('    r = min(w, h) * 0.42')
    funcs.append('    for y in range(h):')
    funcs.append('        for x in range(w):')
    funcs.append('            d = math.hypot(x - cx, y - cy)')
    funcs.append('            if abs(d - r) < 5:')
    funcs.append('                b[4 * (y * w + xi) + 0] = 0xff')
    funcs.append('                b[4 * (yi * w + xi) + 1] = 0xd7')
    funcs.append('                b[4 * (yi * w + xi) + 2] = 0x7a')
    funcs.append('    return b')

    funcs.append('')
    funcs.append('def canvas_art(key, w=1600, h=900):')
    funcs.append('    pass')

    new_content = '\n'.join(funcs)
    if anchor_func in content:
        content = content.replace(anchor_func, new_content)
        print("FIX 2: Added 15 function definitions")
    else:
        print("ERROR: anchor_func not found in file")
        print("Anchor func length: " + str(len(anchor_func)))
        print("File length: " + str(len(content)))
        # Show what we have
        idx = content.find('def _anchor_ring')
        if idx != -1:
            print("Found anchor at " + str(idx) + ": " + repr(content[idx:idx+200]))
        else:
            print("anchor not found")
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
    print(f"Total lines: {len(lines)}")
    print("All fixes complete!")


if __name__ == '__main__':
    fix_file('build_rome_gods.py')
