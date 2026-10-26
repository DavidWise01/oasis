#!/usr/bin/env python3
"""Check the round structure and restore round-5, add round-6 (French)."""
import re
import sys

filepath = 'build_rome_gods.py'
with open(filepath, 'r') as f:
    lines = f.readlines()

# Show lines around the round markers in the THEMES section
# Find the second occurrence of ROUND (beyond the first 4)
occurrences = []
for i, line in enumerate(lines):
    if 'ROUND' in line:
        occurrences.append((i+1, line.rstrip()))

print("=== ALL ROUND markers ===")
for num, txt in occurrences:
    print(f"  Line {num}: {txt}")
