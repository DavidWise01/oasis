#!/usr/bin/env python3
"""
Fix: add trailing commas to the 60 appended round-6/7 theme lines
(lines 755-872) so they become valid list entries in the THEMES list.
"""
with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The 60 appended themes are at lines 755-872 (0-indexed 754-871)
# They currently end with ')' (close paren, no comma)
# Need to change to '),$'

fixed = 0
for i in range(754, 872):
    line = lines[i]
    # Current format:     ("slug", "name", "desc", "story", "archetype")
    # Need:               ("slug", "name", "desc", "story", "archetype"),
    if line.endswith(')\n'):
        lines[i] = line[:-2] + '),\n'
        fixed += 1

print(f'Total fixed: {fixed}')

with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Written')

# Verify ast.parse
import ast
try:
    ast.parse(''.join(lines))
    print('ast.parse: OK')
except SyntaxError as e:
    print(f'ast.parse: FAIL: {e}')
