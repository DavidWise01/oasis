#!/usr/bin/env python3
"""
Clean comprehensive fix for build_rome_gods.py (committed HEAD state, 883 lines):
1. Add _anchor_ring function (after _moirai_spiral) + 13 canvas_* functions
2. Add 60 trailing commas to appended round-6/7 themes

Committed HEAD structure:
- 22 CANVAS_FNS entries (lines 428-451)
- _moirai_spiral at line 268, no _anchor_ring after it
- 60 appended themes at lines 755-872 (bare tuples, no commas)
"""
import ast


def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # FIX 1: Add 15 canvas functions after _moirai_spiral
    # _moirai_spiral is at lines 268-283 in committed HEAD
    # Find the end of _moirai_spiral (return b + blank line)
    old_anchor = '''def _moirai_spiral(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    cx, cy = w / 2, h / 2
    r = 0.32 * min(w, h)
    n = 24
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        xi, yi = int(x), int(y)
        if 0 <= xi < w and 0 <= yi < h:
            b[4 * (yi * w + xi) + 0] = 0xff
            b[4 * (yi * w + xi) + 1] = 0xd7
            b[4 * (yi * w + xi) + 2] = 0x7a
    return b
'''

    funcs = []
    funcs.append('')
    funcs.append('def _anchor_ring(w, h):')
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
    funcs.append('            b[4 * (y * w + x) + 2] = 0x7a')
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

    new_content = ''.join(funcs)
    if old_anchor in content:
        content = content.replace(old_anchor, new_content)
        print("FIX 1: Added 15 function definitions")
    else:
        print("ERROR: anchor not found")
        # Show what's around _moirai_spiral
        idx = content.find('_moirai_spiral')
        if idx != -1:
            print("Found _moirai_spiral at " + str(idx) + ": " + repr(content[idx:idx+300]))
        sys.exit(1)

    # FIX 2: Add 60 trailing commas to appended themes
    lines = content.split('\n')
    # Find appended theme lines (sapphon-agon through pershan-agon-star)
    # They are lines 755-872 of the committed HEAD (0-indexed 754-871)
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
