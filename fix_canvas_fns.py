#!/usr/bin/env python3
"""
Fix build_rome_gods.py: add missing canvas functions to CANVAS_FNS.

The committed HEAD's CANVAS_FNS only has 22 entries, but CANVAS_HISTORY
references 120 canvas names. The build fails with:
  KeyError: 'kill-switch'

Missing canvas functions (about 15):
  kill-switch, planar-grid, slit-rhombus, gloss-helix, hypercube-net,
  cyclic-dial, echo-vault, priestess-mask, prometheus-lantern, serpent-wings,
  severed-eye, torn-parchment, spoke-wheel, 12-dark-cells, strophic-wind
"""
with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the CANVAS_FNS section
import re
# Find CANVAS_FNS = { ... }
fns_match = re.search(r'CANVAS_FNS = \{(.*?)\n\}', content, re.DOTALL)
if not fns_match:
    print("ERROR: CANVAS_FNS not found!")
    exit(1)

fns_block = fns_match.group(1)

# Find the closing brace of CANVAS_FNS
# It ends with } followed by a blank line
# We'll add new entries before the closing }

# The new functions to add (15 total)
new_functions = '''    "kill-switch": _kill_switch`,
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
    "strophic-wind": _strophic_wind,
    "12-dark-cells": _12_dark_cells,
'''

# Find where to insert (before the closing brace)
# The CANVAS_FNS block ends with:
#     "strophic-wind": _dragon_curve,
# }
# So we insert before the }

# Simple approach: replace the last function entry + closing brace
# Find the last entry
lines = content.split('\n')
for i in range(len(lines) - 1, -1, -1):
    if lines[i].strip() == 'CANVAS_FNS = {' or 'CANVAS_FNS = {' in lines[i]:
        # Found start, find the close
        for j in range(i + 1, len(lines)):
            if lines[j].strip() == '}':
                # Check if this is the CANVAS_FNS close (block should be small)
                # Look at the previous line to confirm
                if j < len(lines) - 1 and lines[j + 1].strip() == '':
                    # This is the close
                    insert_pos = j
                    break
        break

if insert_pos is None or insert_pos == 0:
    print("ERROR: Could not find CANVAS_FNS close")
    exit(1)

print(f"Found CANVAS_FNS end at line {insert_pos + 1}")

# Insert the new functions before the closing brace
# Split into lines
new_lines = []
for idx, line in enumerate(lines):
    new_lines.append(line)
    if idx == insert_pos:
        # Insert new functions before the closing brace
        # Add each new function
        for func in new_functions.strip().split('\n'):
            new_lines.append(func.strip())
        new_lines.append(line)  # closing brace

# Actually, let's just replace the specific pattern
# Remove the old function entry and add new ones
# The last entry before closing is:     "strophic-wind": _dragon_curve,
# We want to add new entries before the closing }

# Let's do a cleaner approach: find "strophic-wind": _dragon_curve, and add new entries
# Then remove the old closing and add back

# Actually, the cleanest approach:
# Find the "strophic-wind" line and add new functions after it
# But that modifies the file differently

# Let me just do a direct string replacement approach
# The current state has:
#     "strophic-wind": _dragon_curve,
# }
# We want:
#     "strophic-wind": _dragon_curve,
#     "kill-switch": _kill_switch,
#     "spoke-wheel": _spoke_wheel,
#     ...
# }

# Replace "strophic-wind": _dragon_curve,\n} with the new entries + closing
old_pattern = r'(    "strophic-wind": _dragon_curve,\n)(})'
new_pattern = r'''\    "strophic-wind": _dragon_curve,
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
    "12-dark-cells": _12_dark_cells,
}'''

# Use regex to add the new functions
import re
new_content = re.sub(old_pattern, new_pattern, content)

if new_content == content:
    print("ERROR: Pattern not found!")
    exit(1)

# Now we need to add the function definitions after _anchor_ring
# Find _anchor_ring and add the new functions after it
# First, find where _anchor_ring ends and its content ends

# The functions to add after _anchor_ring
new_fn_defs = '''
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
    cols = [[0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a], [0xff, 0xd7, 0x7a]]
    for i in range(3):
        a = 2 * math.pi * i / 3 - math.pi / 2
        x = w / 2 + 0.25 * min(w, h) * math.cos(a)
        y = h / 2 + 0.25 * min(w, h) * math.sin(a)
        xi, yi = int(x), int(y)
        if 0 <= xi < w and 0 <= yi < h:
            b[4 * (yi * w + xi) + 0] = cols[i][0]
            b[4 * (yi * w + xi) + 1] = cols[i][1]
            b[4 * (yi * w + xi) + 2] = cols[i][2]
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
    cols = [[0x1c, 0x8a, 0xfa], [0x1c, 0x8a, 0xfa], [0x1c, 0x8a, 0xfa]]
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
                b[4 * (yi * w + xi) + 0] = cols[i][0]
                b[4 * (yi * w + xi) + 1] = cols[i][1]
                b[4 * (yi * w + xi) + 2] = cols[i][2]
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


def _12_dark_cells(w, h):
    b = bytearray([5, 5, 10, 255]) * (w * h)
    for y in range(h):
        for x in range(w):
            if (x * y + 7) % 12 == 0:
                b[4 * (y * w + x) + 0] = 0xb4
                b[4 * (y * w + x) + 1] = 0x8c
                b[4 * (y * w + x) + 2] = 0xff
    return b


'''

# Find _anchor_ring and insert new functions after it
# Find the position of the closing brace of CANVAS_FNS again
# Actually, let's find where _anchor_ring is defined and its end
import re
# Find the line numbers of _anchor_ring function
anchor_start = None
anchor_end = None
in_anchor = False
for i, line in enumerate(lines):
    if line.strip().startswith('def _anchor_ring'):
        anchor_start = i
        in_anchor = True
    elif in_anchor and line.strip() == '}' and i > anchor_start + 5:
        anchor_end = i
        break

if anchor_start is None or anchor_end is None:
    print("ERROR: Could not find _anchor_ring function")
    exit(1)

print(f"_anchor_ring at lines {anchor_start + 1}-{anchor_end + 1}")

# Insert new functions after _anchor_ring (before the blank line)
# Actually, let's insert after the closing brace and its following blank line
new_fn_lines = new_fn_defs.split('\n')
for line in new_fn_lines:
    lines.insert(anchor_end + 1, line)

# Now fix the CANVAS_FNS missing entries (add the 15 entries)
# We need to find where to insert them in CANVAS_FNS
# The CANVAS_FNS currently ends at line 451
# Let's find the CANVAS_FNS close bracket
fns_close = None
for i in range(420, 460):
    if lines[i].strip() == '}':
        fns_close = i
        break

if fns_close is None:
    print("ERROR: Could not find CANVAS_FNS close bracket")
    exit(1)

print(f"CANVAS_FNS close at line {fns_close + 1}")

# Insert missing entries before the closing }
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
    '    "12-dark-cells": _12_dark_cells,',
]

for line in new_fns:
    lines.insert(fns_close, line)

# Write the file
with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Written")

import ast
try:
    ast.parse(''.join(lines))
    print("ast.parse: OK")
except SyntaxError as e:
    print(f"ast.parse: FAIL: {e}")
