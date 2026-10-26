#!/usr/bin/env python3
"""Fix THEMES tuple trailing commas in build_rome_gods.py."""
with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines 813-815 (0-indexed 812-814) end with "))),\n" but should be "),\n"
# Fix: remove one ")" from the end of each of these 3 lines
fixed = 0
for i in range(812, 815):
    line = lines[i]
    # Current: ... "sapphon-style")),  ->  remove one ")"
    # Result:  ... "sapphon-style"),
    if line.rstrip().endswith(')),'):
        lines[i] = line.rstrip()[:-1] + '),\n'
        fixed += 1
        print(f'Fixed line {i+1}')
    else:
        print(f'Line {i+1}: unexpected ending {line.rstrip()[-15:]!r}')

print(f'Total fixed: {fixed}')
with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Written')
