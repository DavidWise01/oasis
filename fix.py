#!/usr/bin/env python3
"""Fix appended round-6/7 themes: add trailing commas."""
with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines 813-872 (0-indexed 812-871) end with ')' no comma
# Need to change: "...sapphon-style")"  ->  "...sapphon-style"),"
# i.e., replace the final ')' before newline with '),'

fixed = 0
for i in range(812, 872):
    line = lines[i]
    # Check: line ends with ')' then newline
    if line.endswith(')\n'):
        # Replace the last ')' with '),'
        lines[i] = line[:-2] + '),\n'
        fixed += 1
        print(f'Fixed line {i+1}')

print(f'Total fixed: {fixed}')

with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Written')
