#!/usr/bin/env python3
"""
Fix build_rome_gods.py: The committed HEAD has 60 appended round-6/7 themes
(sapphon 30 + pershan 30) that are embedded as bare tuple expressions
after the CANVAS_FNS dict and before def main(). They lack trailing commas,
causing a SyntaxError when running the build script.

This script:
1. Finds the THEMES list (starts at line 568)
2. Finds the closing ] of THEMES (after base themes, before 'def main()')
3. Finds the 60 appended themes (lines 816-875)
4. Removes them from their current location
5. Inserts them into the THEMES list before the closing ]
6. Adds trailing commas to each appended tuple
"""
import ast

with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Find THEMES list
themes_start = None
for i, line in enumerate(lines):
    if line.strip() == 'THEMES = [' and 500 < i < 600:
        themes_start = i
        break
assert themes_start is not None, "THEMES not found"

# 2. Find the closing ] of THEMES (NOT CANVAS_HISTORY)
themes_end = None
for i in range(themes_start, len(lines)):
    if lines[i].strip() == ']':
        context = ''.join(lines[i-30:i+5])
        if 'CANVAS_HISTORY' not in context:
            themes_end = i
            break
assert themes_end is not None, "THEMES close not found"

# 3. Find def main
main_line = None
for i, line in enumerate(lines):
    if line.strip() == 'def main():' and i > 800:
        main_line = i
        break
assert main_line is not None, "def main not found"

# 4. Find appended themes (sapphon-agon to pershan-agon-star)
appended_start = None
for i in range(main_line - 60, main_line):
    if lines[i].strip().startswith('(') and 'sapphon-agon' in lines[i]:
        appended_start = i
        break
assert appended_start is not None, "appended start not found"

# Find appended end
appended_end = appended_start
while appended_end < main_line and not (lines[appended_end].strip() == ']' or 
    (lines[appended_end].strip() == '' and appended_end > appended_start + 50)):
    appended_end += 1

# Find the actual end (after last appended, before blank lines)
while appended_end < main_line and lines[appended_end].strip() == '':
    appended_end += 1

# Assert: appended_end should be just after the last appended theme
last_appended = None
for i in range(appended_start, main_line):
    if lines[i].strip().startswith('(') and ('sapphon-' in lines[i] or 'pershan-' in lines[i]):
        last_appended = i
assert last_appended is not None, "no appended themes found"
appended_end = last_appended + 1

print(f"THEMES list: lines {themes_start+1}-{themes_end+1}")
print(f"def main: line {main_line+1}")
print(f"Appended themes: lines {appended_start+1}-{appended_end}")
print(f"Appended count: {appended_end - appended_start}")
print(f"THEMES size: {themes_end - themes_start}")
print(f"Expected THEMES size: 100 (40 base + 60 appended)")

# 5. Extract appended themes
appended_lines = lines[appended_start:appended_end]
print(f"First appended: {appended_lines[0].strip()[:60]}")
print(f"Last appended: {appended_lines[-1].strip()[:60]}")

# 6. Remove them from current location
del lines[appended_start:appended_end]

# 7. Add commas to appended tuples (if missing)
fixed_nb = 0
for i, line in enumerate(appended_lines):
    stripped = line.rstrip()
    if stripped.endswith(')'):
        appended_lines[i] = stripped + ',\n'
        fixed_nb += 1
print(f"Added {fixed_nb} commas")

# 8. Insert before the closing bracket of THEMES
for j, line in enumerate(appended_lines):
    lines.insert(themes_end + j, line)

# 9. Verify new structure
# Find the closing bracket again
new_themes_end = None
for i in range(themes_start, len(lines)):
    if lines[i].strip() == ']':
        context = ''.join(lines[i-30:i+5])
        if 'CANVAS_HISTORY' not in context:
            new_themes_end = i
            break

new_size = new_themes_end - themes_start
print(f"New THEMES size: {new_size} (expected 100)")

# 10. Verify with ast.parse
try:
    ast.parse(''.join(lines))
    print("ast.parse: OK")
except SyntaxError as e:
    print(f"ast.parse: FAIL: {e}")
    exit(1)

# 11. Write
with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("File written successfully")
