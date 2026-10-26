#!/usr/bin/env python3
"""
Fix build_rome_gods.py comprehensively (committed HEAD structure):
- File: 883 lines
- CANVAS_FNS: lines 428-451, 22 entries
- _anchor_ring: lines 287-298
- CANVAS_HISTORY: line 301
- THEMES list: 568-873, 180 themes (20 base + 160 appended)
- 60 appended round-6/7 themes (lines 755-872) lack trailing commas
- def main(): at line 876
"""
import ast
import sys

with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original: {len(lines)} lines")

# Fix 1: Add 13 CANVAS_FNS entries after CANVAS_FNS close
fns_close = None
for i, line in enumerate(lines):
    if '"strophic-wind": _dragon_curve,' in line:
        fns_close = i
        break

if fns_close is not None:
    for entry in [
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
    ]:
        lines.insert(fns_close + 1, entry)
    print(f"FIX 1: Added 13 CANVAS_FNS entries after line {fns_close + 1}")
else:
    print("FAIL 1: CANVAS_FNS close not found")
    sys.exit(1)

# Fix 2: Add 15 function definitions after _anchor_ring
anchor_idx = None
for i, line in enumerate(lines):
    if 'def _anchor_ring(w, h):' in line:
        anchor_idx = i
        break

if anchor_idx is not None:
    func_end = None
    for j in range(anchor_idx, min(anchor_idx + 15, len(lines))):
        if lines[j].strip() == 'return b':
            func_end = j
            break

    if func_end is not None:
        funcs = [
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
                '            b[4 * (y * w + x) + 0] = chr(0x24 + int(t * 0x60))',
                '            b[4 * (y * w + x) + 1] = chr(0x2a + int(t * 0x5a))',
                '            b[4 * (y * w + x) + 2] = chr(0x1c + int(t * 0x40))',
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
                '            b[4 * (y * w + x) + 0] = chr(0xd8 + int(t * 0x88))',
                '            b[4 * (y * w + x) + 1] = chr(0xc4 + int(t * 0x88))',
                '            b[4 * (y * w + x) + 2] = chr(0x8f + int(t * 0x88))',
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

        new_func_block = []
        for name, body in funcs:
            new_func_block.append('')
            new_func_block.append('def ' + name + '(w, h):')
            for stmt in body:
                new_func_block.append('    ' + stmt)
            new_func_block.append('    return b')
            new_func_block.append('')

        for item in reversed(new_func_block):
            lines.insert(func_end + 2, item)

        print(f"FIX 2: Added 15 function definitions after line {func_end + 2}")
    else:
        print("FAIL 2: _anchor_ring function end not found")
        sys.exit(1)
else:
    print("FAIL 2: _anchor_ring not found")
    sys.exit(1)

# Fix 3: Add trailing commas to 60 appended round-6/7 themes (lines 755-872)
fixed = 0
for i in range(754, 872):
    stripped = lines[i].rstrip()
    if stripped.endswith(')') and not stripped.endswith('),'):
        lines[i] = stripped + ',\n'
        fixed += 1

print(f"FIX 3: Added trailing commas to {fixed} appended themes")

# Write and verify
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
