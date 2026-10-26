with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The lines 813-815 currently end with "))," but should end with "),"
# Find and replace
import re

# Fix: replace ')),' with '),' on lines 813-815 (0-indexed 812-814)
# These are the first 3 appended theme lines

# Find the exact context
lines = content.split('\n')
print(f'First 3 appended theme lines:')
for i in range(812, 815):
    print(f'Line {i+1}: {lines[i][-15:]!r}')

# Fix: remove one ')' from each of these lines
fixed = 0
for i in range(812, 815):
    line = lines[i]
    # Current ends with "))," - remove one ")"
    if line.endswith(')),\n'):
        lines[i] = line[:-2] + '),\n'
        fixed += 1
        print(f'Fixed line {i+1}')

print(f'Total fixed: {fixed}')

new_content = '\n'.join(lines)
with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Written')
