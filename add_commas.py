#!/usr/bin/env python3
"""Add trailing commas to the 60 appended round-6/7 theme lines in build_rome_gods.py."""
with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The appended round-6/7 themes are at lines 813-872 (0-indexed 812-871)
# They are bare tuples without trailing commas: "sapphon-style"))$
# They need to end with "sapphon-style"),"

fixed = 0
for i in range(812, 872):
    line = lines[i]
    stripped = line.rstrip()
    
    # Check if it's a theme tuple line (starts with spaces, has quote, ends with ")
    if stripped.startswith('    ("') and stripped.endswith('"),'):
        # Already fixed
        continue
    if stripped.startswith('    ("') and stripped.endswith(')"'):
        # Needs comma before closing paren
        # The line looks like:     ("sapphon-agon", "The sapphon-agon description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon", "sapphon-style")
        # We need:     ("sapphon-agon", "The sapphon-agon description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon", "sapphon-style"),
        # i.e., add , before the closing )
        lines[i] = stripped[:-1] + '),\n'
        fixed += 1
        print(f'Fixed line {i+1}')

print(f'Total fixed: {fixed}')

with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Written')
