#!/usr/bin/env python3
"""
Fix: add trailing commas to the 60 appended round-6/7 theme lines
(0-indexed 754-871, lines 755-872) so the THEMES list is valid.

Verified:
- working tree and HEAD both have 883 lines
- THEMES list at 568-873 has 180 '^\s*(\"' matches
- lines 569-754 (120 base themes) have trailing commas
- lines 755-872 (60 appended themes) lack trailing commas

Fix: for each of lines 755-872, change "..." )\n to "..." ),\n
"""
with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The 60 appended themes are at lines 755-872 (0-indexed 754-871)
# They end with ')' instead of '),'

# Verify current state
print(f"Line 755 starts with: {lines[754].strip()[:50]!r}")
print(f"Line 755 ends with: {lines[754][-15:]!r}")
print(f"Line 872 ends with: {lines[871][-20:]!r}")

fixed = 0
for i in range(754, 872):
    line = lines[i]
    # Current:     ("slug", "name", "desc", "story", "archetype")
    # Need:        ("slug", "name", "desc", "story", "archetype"),

    # Check: line ends with ')' then newline (not '),')
    stripped = line.rstrip()
    if stripped.endswith(')') and not stripped.endswith('),'):
        # Replace the final ')' with '),'
        lines[i] = stripped + ',\n'
        fixed += 1

print(f"Total fixed (added commas): {fixed}")

with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Written")

# Verify ast.parse
import ast
try:
    ast.parse(''.join(lines))
    print("ast.parse: OK")
except SyntaxError as e:
    print(f"ast.parse: FAIL: {e}")
