#!/usr/bin/env python3
"""
Insert round-5 (Roman gods, 30 themes) and round-6 (French gods, 30 themes)
into build_rome_gods.py, then regenerate the sphere pages.
"""
import ast
import sys

filepath = 'build_rome_gods.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the THEMES list boundaries
try:
    tree = ast.parse(content)
except SyntaxError as e:
    print(f"Syntax error in file: {e}")
    sys.exit(1)

# Find the THEMES assignment
themes_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'THEMES':
                themes_node = node
                break

if themes_node is None:
    print("THEMES list not found")
    sys.exit(1)

# Find the closing bracket of the THEMES list
lines = content.split('\n')
themes_start = themes_node.lineno - 1

# Find the end of THEMES list (the ']')
brace_depth = 0
in_list = False
themes_end = None
for i in range(themes_start, len(lines)):
    stripped = lines[i].strip()
    if stripped.startswith('THEMES') or stripped.startswith('THEMES ='):
        in_list = True
        continue
    if in_list:
        # Handle both Windows \r\n and Unix \n line endings
        # Count brackets per line
        open_count = lines[i].count('[')
        close_count = lines[i].count(']')
        # But '[' might be part of a string... check more carefully
        # Simple approach: find the closing bracket
        for ch in lines[i]:
            if ch == '[':
                brace_depth += 1
            elif ch == ']':
                brace_depth -= 1
                if brace_depth == 0:
                    themes_end = i + 1  # 1-indexed
                    break
        if themes_end:
            break

if themes_end is None:
    print("Could not find THEMES list closing bracket")
    sys.exit(1)

print(f"THEMES starts at line {themes_start}")
print(f"THEMES ends at line {themes_end}")
print("Last 5 themes in current file:")
for i in range(max(0, themes_end - 8), themes_end):
    if i < len(lines):
        print(f"  {i+1}: {lines[i].rstrip()[:110]}")
