#!/usr/bin/env python3
"""
Fix build_rome_gods.py: relocate 60 appended round-6/7 themes (30 sapphic + 30 pershan)
from their current position (after CANVAS_HISTORY, before def main) into the THEMES list.

Committed HEAD structure:
  Lines 568-754: THEMES list (20 base themes)
  Lines 754: ] (THEMES closes)
  Lines 755-872: CANVAS_HISTORY dict (close at 873)
  Lines 813-872: 60 appended themes as bare tuples (outside THEMES list)
  Lines 876: def main()

The appended themes need to be moved inside the THEMES list, after the 20 base themes.

Plan:
1. Read all lines
2. Find THEMES opening and closing brackets
3. Find the 60 appended themes (sapphon-agon to pershan-agon-star)
4. Remove them from current location
5. Add commas to each
6. Insert them into THEMES before the closing bracket
7. Verify with ast.parse
8. Write result
"""
import ast

with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Find THEMES opening
themes_start = None
for i, line in enumerate(lines):
    if line.strip() == 'THEMES = [' and 500 < i < 600:
        themes_start = i
        break
assert themes_start is not None, "THEMES not found!"
print(f"THEMES starts at line {themes_start+1}")

# 2. Find THEMES closing ]
themes_end = None
for i in range(themes_start, len(lines)):
    if lines[i].strip() == ']':
        context = ''.join(lines[i-30:i+5])
        if 'CANVAS_HISTORY' not in context:
            themes_end = i
            break
assert themes_end is not None, "THEMES close not found!"
print(f"THEMES closes at line {themes_end+1} (0-indexed {themes_end})")

# 3. Find def main
main_line = None
for i, line in enumerate(lines):
    if line.strip() == 'def main():' and i > 800:
        main_line = i
        break
assert main_line is not None, "def main not found!"
print(f"def main at line {main_line+1}")

# 4. Find appended themes (sapphon-agon to pershan-agon-star)
appended_start = None
appended_end = None
for i in range(810, main_line):
    if 'sapphon-agon' in lines[i] and 'agon' in lines[i]:
        appended_start = i
        break
assert appended_start is not None, "sapphon-agon not found!"

for i in range(appended_start + 50, main_line):
    if 'pershan-agon-star' in lines[i]:
        appended_end = i + 1
        break
assert appended_end is not None, "pershan-agon-star not found!"

appended_count = appended_end - appended_start
print(f"Appended themes: lines {appended_start+1}-{appended_end+1} ({appended_count} themes)")

# 5. Extract and remove
appended = lines[appended_start:appended_end]
del lines[appended_start:appended_end]

# 6. Add commas to each
fixed = 0
for i, line in enumerate(appended):
    stripped = line.rstrip()
    if not stripped.endswith(','):
        appended[i] = stripped + ',\n'
        fixed += 1
print(f"Added {fixed} commas to appended themes")

# 7. Insert before themes_end
for j, line in enumerate(appended):
    lines.insert(themes_end + j, line)

# 8. Verify new THEMES size
themes_end = None
for i in range(themes_start, len(lines)):
    if lines[i].strip() == ']':
        context = ''.join(lines[i-30:i+5])
        if 'CANVAS_HISTORY' not in context:
            themes_end = i
            break

new_size = themes_end - themes_start
print(f"New THEMES size: {new_size} (expected 80: 20 base + 60 appended)")

# 9. Verify ast.parse
try:
    ast.parse(''.join(lines))
    print("ast.parse: OK")
except SyntaxError as e:
    print(f"ast.parse: FAIL: {e}")
    exit(1)

# 10. Write
with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("File written successfully")
