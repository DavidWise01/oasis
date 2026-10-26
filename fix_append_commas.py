#!/usr/bin/env python3
"""Fix the THEMES list in build_rome_gods.py by adding trailing commas to appended round-6/7 themes."""
with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The appended round-6/7 themes are at lines 813-872 (0-indexed 812-871)
# They are bare tuples without trailing commas
# We need to add commas to each of them

fixed = 0
for i in range(812, 872):
    line = lines[i]
    stripped = line.rstrip()
    # Check if it's a theme tuple (starts with spaces + ( and has description)
    if stripped.startswith('    ("') and 'description' in stripped:
        # It doesn't end with comma
        if not stripped.endswith(','):
            lines[i] = stripped + ',\n'
            fixed += 1
            print(f'Fixed line {i+1}')

print(f'Total fixed: {fixed}')

with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Written')
