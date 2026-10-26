#!/usr/bin/env python3
"""
Fix build_rome_gods.py comprehensively:
1. Add CANVAS_FNS entries (13 new)
2. Add 15 function definitions after _anchor_ring
3. Fix 60 appended round-6/7 themes (lines 755-872) to have trailing commas
"""
import ast

with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Store original to verify
original = content

# 1. Add CANVAS_FNS entries (13 new)
# Find the closing } of CANVAS_FNS (after "strophic-wind": _dragon_curve,)
fns_close_marker = '"strophic-wind": _dragon_curve,\n}'
if fns_close_marker in content:
    new_fns_entries = '''    "kill-switch": _kill_switch,
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
'''
    content = content.replace(fns_close_marker, new_fns_entries + '}', 1)
    print("Added 13 CANVAS_FNS entries")
else:
    print("ERROR: fns_close_marker not found in content")

# 2. Add 15 function definitions after _anchor_ring
anchor_marker = "def _anchor_ring(w, h):"
if anchor_marker in content:
    functions_to_add = '''def _kill_switch(w, h):
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
                b[4 * (y * w + x) + 0] = C(0x24 + t * 0x60)
                b[4 * (y * w + x) + 1] = C(0x2a + t * 0x5a)
                b[4 * (y * w + x) + 2] = C(0x1c + t * 0x40)
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
                b[4 * (y * w + x) + 0] = C(0xd8 + t * 0x88)
                b[4 * (y * w + x) + 1] = C(0xc4 + t * 0x88)
                b[4 * (y * w + x) + 2] = C(0x8f + t * 0x88)
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
            b[4 * (yi * w + xi) + 2] = colors[i][2]
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
                b[4 * (yi * w + xi) + 2] = colors[i][2]
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

'''

    content = content.replace(anchor_marker, functions_to_add + anchor_marker, 1)
    print("Added 15 function definitions after _anchor_ring")
else:
    print("ERROR: anchor_marker not found")

# 3. Fix 60 appended round-6/7 themes (lines 755-872) to have trailing commas
# Split into lines, fix each, then re-join
lines = content.split('\n')
fixed = 0
for i in range(754, 872):
    stripped = lines[i].rstrip()
    if stripped.endswith(')') and not stripped.endswith('),'):
        lines[i] = stripped + ',\n'
        fixed += 1

print(f"Fixed {fixed} appended themes (added commas)")

# Rejoin
content = ''.join(lines)

# Verify
try:
    ast.parse(content)
    print("ast.parse: OK")
except SyntaxError as e:
    print(f"ast.parse: FAIL: {e}")

with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("File written successfully")
