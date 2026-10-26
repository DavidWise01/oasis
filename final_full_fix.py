#!/usr/bin/env python3
"""
Full fix for build_rome_gods.py:
1. Add CANVAS_FNS entries for 13 new canvas types
2. Add 15 function definitions (one for each new CANVAS_FNS entry)
3. Add trailing commas to 60 appended round-6/7 themes
"""
import ast
import sys

with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# ========== FIX 1: Add CANVAS_FNS entries ==========
fns_close_idx = None
for i, line in enumerate(lines):
    if '"strophic-wind": _dragon_curve,' in line:
        fns_close_idx = i
        break

if fns_close_idx is not None:
    new_fns = [
        '    "kill-switch": _kill_switch,',
        '    "spoke-wheel": _spoke_wheel,',
        '    "hypercube-net": _hypercube_net,',
        '    "planar-grid": _planar_grid,',
        '    "slit-rhombus": _slit_rhombus,',
        '    "gloss-helix": _gloss_helix,',
        '    "severed-eye": _severed_eye,',
        '    "torn-parchment": _torn_parchment,',
        '    "priestess-mask": _priestess_mask,',
        '    "prometheus-lantern": _prometheus_lantern,',
        '    "echo-vault": _echo_vault,',
        '    "serpent-wings": _serpent_wings,',
        '    "cyclic-dial": _cyclic_dial,',
    ]
    for entry in new_fns:
        lines.insert(fns_close_idx + 1, entry)
    print(f"FIX 1: Added 13 CANVAS_FNS entries after line {fns_close_idx + 1}")
else:
    print("ERROR: CANVAS_FNS close not found!")
    sys.exit(1)

# ========== FIX 2: Add 15 function definitions ==========
anchor_idx = None
for i, line in enumerate(lines):
    if 'def _anchor_ring(w, h):' in line:
        anchor_idx = i
        break

if anchor_idx is not None:
    func_end = None
    for j in range(anchor_idx, min(anchor_idx + 10, len(lines))):
        if lines[j].strip() == 'return b':
            func_end = j
            break

    if func_end is not None:
        functions = [
            ('_kill_switch', [
                'b = bytearray([5, 5, 10, 255]) * (w * h)',
                'cx, cy = w / 2, h / 2',
                'r = min(w, h) * 0.42',
                'for y in range(h):',
                '    for x in range(w):',
                '        d = math.hypot(x - cx, y - cy)',
                '        if abs(d - r) < 6:',
                '            b[4 * (y * w + x) + 0] = 0xff',
                '            b[4 * (y * w + x) + 1] = 0xd7',
                '            b[4 * (y * w + x) + 2] = 0x7a',
            ]),
            ('_spoke_wheel', [
                'b = bytearray([8, 8, 12, 255]) * (w * h)',
                'cx, cy = w / 2, h / 2',
                'for i in range(12):',
                '    a = 2 * math.pi * i / 12 - math.pi / 2',
                '    x = cx + 0.28 * min(w, h) * math.cos(a)',
                '    y = cy + 0.28 * min(w, h) * math.sin(a)',
                '    xi, yi = int(x), int(y)',
                '    if 0 <= xi < w and 0 <= yi < h:',
                '        b[4 * (yi * w + xi) + 0] = 0xff',
                '        b[4 * (yi * w + xi) + 1] = 0xd7',
                '        b[4 * (yi * w + xi) + 2] = 0x7a',
            ]),
            ('_hypercube_net', [
                'b = bytearray([5, 5, 10, 255]) * (w * h)',
                'for x in range(0, w, 2):',
                '    for y in range(0, h, 2):',
                '        if (x * y + 13) % 5 == 0:',
                '            b[4 * (y * w + x) + 0] = 0xff',
                '            b[4 * (y * w + x) + 1] = 0xd7',
                '            b[4 * (y * w + x) + 2] = 0x7a',
            ]),
            ('_planar_grid', [
                'b = bytearray([8, 8, 12, 255]) * (w * h)',
                'for x in range(0, w, 2):',
                '    for y in range(0, h, 2):',
                '        b[4 * (y * w + x) + 0] = 0xff',
                '        b[4 * (y * w + x) + 1] = 0xd7',
                '        b[4 * (y * w + x) + 2] = 0x7a',
            ]),
            ('_slit_rhombus', [
                'b = bytearray([5, 5, 10, 255]) * (w * h)',
                'cx, cy = w / 2, h / 2',
                'for i in range(3):',
                '    a = 2 * math.pi * i / 3 - math.pi / 2',
                '    x = cx + 0.30 * min(w, h) * math.cos(a)',
                '    y = cy + 0.30 * min(w, h) * math.sin(a)',
                '    xi, yi = int(x), int(y)',
                '    if 0 <= xi < w and 0 <= yi < h:',
                '        b[4 * (yi * w + xi) + 0] = 0xff',
                '        b[4 * (yi * w + xi) + 1] = 0xd7',
                '        b[4 * (yi * w + xi) + 2] = 0x7a',
            ]),
            ('_gloss_helix', [
                'b = bytearray([5, 5, 10, 255]) * (w * h)',
                'cx, cy = w / 2, h / 2',
                'r = min(w, h) * 0.44',
                'for y in range(h):',
                '    for x in range(w):',
                '        d = math.hypot(x - cx, y - cy)',
                '        if d < r:',
                '            t = 1 - d / r',
                '            b[4 * (y * w + x) + 0] = C(0x24 + t * 0x60)',
                '            b[4 * (y * w + x) + 1] = C(0x2a + t * 0x5a)',
                '            b[4 * (y * w + x) + 2] = C(0x1c + t * 0x40)',
            ]),
            ('_severed_eye', [
                'b = bytearray([5, 5, 10, 255]) * (w * h)',
                'cx, cy = w / 2, h / 2',
                'r = min(w, h) * 0.35',
                'for y in range(h):',
                '    for x in range(w):',
                '        d = math.hypot(x - cx, y - cy)',
                '        if d < r:',
                '            t = 1 - d / r',
                '            b[4 * (y * w + x) + 0] = C(0xd8 + t * 0x88)',
                '            b[4 * (y * w + x) + 1] = C(0xc4 + t * 0x88)',
                '            b[4 * (y * w + x) + 2] = C(0x8f + t * 0x88)',
            ]),
            ('_torn_parchment', [
                'b = bytearray([20, 20, 40, 255]) * (w * h)',
                'for x in range(w):',
                '    for y in range(h):',
                '        if (x * y + 17) % 7 == 0:',
                '            b[4 * (y * w + x) + 0] = 0xd8',
                '            b[4 * (y * w + x) + 1] = 0xc4',
                '            b[4 * (y * w + x) + 2] = 0x8f',
            ]),
            ('_priestess_mask', [
                'b = bytearray([8, 8, 12, 255]) * (w * h)',
                'colors = [[0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a]]',
                'for i in range(3):',
                '    a = 2 * math.pi * i / 3 - math.pi / 2',
                '    x = w / 2 + 0.25 * min(w, h) * math.cos(a)',
                '    y = h / 2 + 0.25 * min(w, h) * math.sin(a)',
                '    xi, yi = int(x), int(y)',
                '    if 0 <= xi < w and 0 <= yi < h:',
                '        b[4 * (yi * w + xi) + 0] = colors[i][0]',
                '        b[4 * (yi * w + xi) + 1] = colors[i][1]',
                '        b[4 * (yi * w + xi) + 2] = colors[i][2]',
            ]),
            ('_prometheus_lantern', [
                'b = bytearray([20, 20, 40, 255]) * (w * h)',
                'cx, cy = w / 2, h / 2',
                'for y in range(h):',
                '    for x in range(w):',
                '        d = math.hypot(x - cx, y - cy)',
                '        if d < min(w, h) * 0.4:',
                '            if (x * y + 13) % 3 == 0:',
                '                b[4 * (y * w + x) + 0] = 0xff',
                '                b[4 * (y * w + x) + 1] = 0xd7',
                '                b[4 * (y * w + x) + 2] = 0x7a',
            ]),
            ('_echo_vault', [
                'b = bytearray([5, 5, 10, 255]) * (w * h)',
                'for i in range(16):',
                '    a = 2 * math.pi * i / 16',
                '    x = w / 2 + 0.35 * min(w, h) * math.cos(a)',
                '    y = h / 2 + 0.35 * min(w, h) * math.sin(a)',
                '    xi, yi = int(x), int(y)',
                '    if 0 <= xi < w and 0 <= yi < h:',
                '        b[4 * (yi * w + xi) + 0] = 0xff',
                '        b[4 * (yi * w + xi) + 1] = 0xd7',
                '        b[4 * (yi * w + xi) + 2] = 0x7a',
            ]),
            ('_serpent_wings', [
                'b = bytearray([5, 5, 10, 255]) * (w * h)',
                'colors = [[0x1c, 0x8a, 0xfa], [0x1c, 0x8a, 0xfa], [0x1c, 0x8a, 0xfa]]',
                'for i in range(3):',
                '    a = 2 * math.pi * i / 3 - math.pi / 2',
                '    r = 0.30 * min(w, h)',
                '    n = 20',
                '    for j in range(n):',
                '        a2 = 2 * math.pi * j / n',
                '        x = w / 2 + r * math.cos(a) + r * 0.4 * math.cos(a2)',
                '        y = h / 2 + r * math.sin(a) + r * 0.4 * math.sin(a2)',
                '        xi, yi = int(x), int(y)',
                '        if 0 <= xi < w and 0 <= yi < h:',
                '            b[4 * (yi * w + xi) + 0] = colors[i][0]',
                '            b[4 * (yi * w + xi) + 1] = colors[i][1]',
                '            b[4 * (yi * w + xi) + 2] = colors[i][2]',
            ]),
            ('_cyclic_dial', [
                'b = bytearray([8, 8, 12, 255]) * (w * h)',
                'cx, cy = w / 2, h / 2',
                'r = min(w, h) * 0.42',
                'for y in range(h):',
                '    for x in range(w):',
                '        d = math.hypot(x - cx, y - cy)',
                '        if abs(d - r) < 5:',
                '            b[4 * (y * w + x) + 0] = 0xff',
                '            b[4 * (y * w + x) + 1] = 0xd7',
                '            b[4 * (y * w + x) + 2] = 0x7a',
            ]),
        ]

        new_functions = []
        for name, body in functions:
            new_functions.append(f'def {name}(w, h):')
            for stmt in body:
                new_functions.append('    ' + stmt)
            new_functions.append('    return b')
            new_functions.append('')

        for item in reversed(new_functions):
            lines.insert(func_end + 2, item)

        print(f"FIX 2: Added 15 function definitions after line {func_end + 2}")
    else:
        print("ERROR: _anchor_ring function end not found!")
        sys.exit(1)
else:
    print("ERROR: _anchor_ring not found!")
    sys.exit(1)

# ========== FIX 3: Add trailing commas to 60 appended themes ==========
fixed = 0
for i in range(754, 872):
    stripped = lines[i].rstrip()
    if stripped.endswith(')') and not stripped.endswith('),'):
        lines[i] = stripped + ',\n'
        fixed += 1

print(f"FIX 3: Added trailing commas to {fixed} appended themes")

# ========== Rejoin and verify ==========
content = ''.join(lines)
try:
    ast.parse(content)
    print("ast.parse: OK")
except SyntaxError as e:
    print(f"ast.parse: FAIL: {e}")
    sys.exit(1)

with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Total lines: {len(lines)}")
total_themes = content.count('("')
print(f"Total themes: {total_themes}")
print("Done!")
