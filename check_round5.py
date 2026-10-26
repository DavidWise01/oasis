#!/usr/bin/env python3
"""Fix round-5 (Roman gods) content and add round-6 (French gods)."""
import sys

filepath = 'build_rome_gods.py'
with open(filepath, 'r') as f:
    lines = f.readlines()

# Find ROUND FIVE marker
round5_start = None
for i, line in enumerate(lines):
    if '# ── ROUND FIVE' in line:
        round5_start = i
        break

if round5_start is None:
    print("ROUND FIVE marker not found!")
    sys.exit(1)

# Find def main after ROUND FIVE
def_main = None
for i in range(round5_start, len(lines)):
    if 'def main()' in lines[i]:
        def_main = i
        break

if def_main is None:
    print("def main() not found after ROUND FIVE")
    sys.exit(1)

print(f"ROUND FIVE starts at line {round5_start}")
print(f"def main() at line {def_main}")

# Check for sapphic round-6 and persian round-7 markers
sapphic_start = None
persian_start = None
for i in range(round5_start, def_main):
    if '# ── ROUND SIX' in lines[i]:
        sapphic_start = i
    if '# ── ROUND SEVEN' in lines[i]:
        persian_start = i

print(f"Sapphic (round-6) starts at line {sapphic_start}")
print(f"Persian (round-7) starts at line {persian_start}")
