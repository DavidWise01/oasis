#!/usr/bin/env python3
"""
Fix build_rome_gods.py: add trailing commas to 60 appended round-6/7 theme lines.

Committed HEAD structure:
  Line 568: THEMES = [
  Lines 569-754: 120 base themes (with trailing commas)
  Lines 755-872: 60 appended round-6/7 themes (NO trailing commas)
  Line 873: ] (THEMES close)
  Lines 874-875: blank
  Line 876: def main():

The appended themes at 755-872 need commas: "...")" -> "..."),"
"""
with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The 60 appended themes are at lines 755-872 (0-indexed 754-871)
print(f"Verifying line 755 (0-indexed 754): {lines[754].rstrip()[-10:]!r}")
print(f"Verifying line 872 (0-indexed 871): {lines[871].rstrip()[-10:]!r}")

fixed = 0
for i in range(754, 872):
    line = lines[i]
    stripped = line.rstrip()
    # Current: ("slug", "name", "desc", "story", "archetype")
    # Need: ("slug", "name", "desc", "story", "archetype"),
    if stripped.endswith(')') and not stripped.endswith('),'):
        lines[i] = stripped + ',\n'
        fixed += 1

print(f"Total fixed (added trailing commas): {fixed}")

with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Written")

import ast
try:
    ast.parse(''.join(lines))
    print("ast.parse: OK")
except SyntaxError as e:
    print(f"ast.parse: FAIL: {e}")
