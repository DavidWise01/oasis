#!/usr/bin/env python3
"""
Insert round-5 (Roman gods) and round-6 (French gods) into build_rome_gods.py
and regenerate all sphere pages.

Round-5: 30 Roman gods themes (margarits/temples/inscriptions/consuls/pagans)
Round-6: 30 French gods themes (Paris towns/endowments)
"""
import ast
import sys

filepath = 'build_rome_gods.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Find THEMES line
themes_idx = None
for i, line in enumerate(lines):
    if line.strip().startswith('THEMES'):
        themes_idx = i
        break

# Find THEMES closing ']' (unless we have ROUND SIX at the end)
themes_end = None
brace_depth = 0
for i in range(themes_idx, len(lines)):
    stripped = lines[i].strip()
    if stripped.startswith('THEMES'):
        brace_depth += 1
        continue
    open_count = lines[i].count('[')
    close_count = lines[i].count(']')
    brace_depth += open_count - close_count
    if brace_depth == 0:
        themes_end = i
        break

# Find where 'def main()' starts
main_idx = None
for i, line in enumerate(lines):
    if line.strip() == 'def main():':
        main_idx = i
        break

# Find existing round markers in the THEMES section
round_markers = []
for i, line in enumerate(lines):
    if '# ── ROUND' in line or '# round-' in line:
        round_markers.append((i, line.strip()))

print(f"Themes: {themes_idx}-{themes_end}")
print(f"def main(): {main_idx}")
print(f"Round markers: {[m[1] for m in round_markers]}")
print(f"Last 5 lines of THEMES: {[l.rstrip() for l in lines[themes_end-3:themes_end+2]]}")
