#!/usr/bin/env python3
"""
Fix build_rome_gods.py: add trailing commas to 60 appended round-6/7 themes.

The committed HEAD's build_rome_gods.py has 180 themes in the THEMES list
(lines 568-873). The 60 appended round-6/7 themes (sapphon 30 + pershan 30)
are at lines 755-872 and lack trailing commas.

This causes:
  File "build_rome_gods.py", line 813, in <module>
    ("sapphon-agon", ...)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ("apollo-agon", ...)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'tuple' object is not callable

Fix: add trailing commas to all 60 appended theme lines.
"""
import ast
import sys

with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"File has {len(lines)} lines")

# Find the appended themes (755-872 = 0-indexed 754-871)
# These are bare tuples without commas

# Check first and last
print(f"Line 755: {lines[754].rstrip()[-10:]!r}")
print(f"Line 872: {lines[871].rstrip()[-10:]!r}")

fixed = 0
for i in range(754, 872):
    stripped = lines[i].rstrip()
    # Check if it ends with ')' but not '),'
    if stripped.endswith(')') and not stripped.endswith('),'):
        lines[i] = stripped + ',\n'
        fixed += 1

print(f"Fixed {fixed} lines (added trailing commas)")

# Write
with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify
try:
    ast.parse(''.join(lines))
    print("ast.parse: OK")
except SyntaxError as e:
    print(f"ast.parse: FAIL: {e}")
    sys.exit(1)

# Verify git status
import subprocess
result = subprocess.run(['git', 'status', '--porcelain', 'build_rome_gods.py'], 
                       capture_output=True, text=True)
print(f"git status: {result.stdout}")

print("Done")
