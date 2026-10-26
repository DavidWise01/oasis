#!/usr/bin/env python3
"""Fix the THEMES list in build_rome_gods.py: ensure all tuples have trailing commas."""

with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the THEMES list (starts at line 568)
themes_start = None
for i, line in enumerate(lines):
    if line.strip() == 'THEMES = [' and 500 < i < 600:
        themes_start = i
        break

print(f'THEMES starts at line {themes_start + 1}')

# The appended round-6/7 themes are at lines 816-874 (0-indexed 815-873)
# They are tuples without trailing commas (currently ending with ")),")
# We need them to end with "),\n" (close paren + comma + newline)

# Current state (after previous fixes):
# Lines 813-815 (0-indexed 812-814) end with "))),\n" (three close parens + comma)
# We need "),\n" (one close paren + comma + newline)

# Fix the 3 lines (813-815, 0-indexed 812-814)
fixed = 0
for i in range(812, 815):
    line = lines[i]
    # Current: ends with "))," (two close parens + comma) - wait, let me check
    stripped = line.rstrip()
    if stripped.endswith(')),'):
        # Remove one close paren: "))," -> "),"
        new_line = stripped[:-1] + ',\n'
        lines[i] = new_line
        fixed += 1
        print(f'Fixed line {i+1}: {new_line[-20:]!r}')
    elif stripped.endswith(')'):
        print(f'Line {i+1}: still ends with ")", need comma')
    else:
        print(f'Line {i+1}: unexpected ending {stripped[-10:]!r}')

print(f'Total fixed: {fixed}')

with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Written')
