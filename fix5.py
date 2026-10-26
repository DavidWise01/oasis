with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check lines 813-815 (0-indexed 812-814) and 873 (close bracket)
for i in [812, 813, 814, 872]:
    line = lines[i]
    stripped = line.rstrip()
    print(f'Line {i+1}: {stripped[-15:]!r}')
    print(f'  len={len(stripped)}')
    print()

# The appended themes are at 0-indexed 812-872 (lines 813-873)
# They currently end with ")))," but need "),"
# Current:     "sapphon-style")))
# Desired:     "sapphon-style"),
# So: remove 2 close parens, add 1 comma

fixed = 0
for i in range(812, 815):
    line = lines[i]
    stripped = line.rstrip()
    if stripped.endswith('))),'):
        # Remove "))" -> keep ")" at end, add ","
        # ")))," -> "),"
        lines[i] = stripped[:-3] + '),\n'
        fixed += 1
        print(f'Fixed line {i+1}')
    else:
        print(f'Line {i+1}: unexpected {stripped[-10:]!r}')

print(f'Total fixed: {fixed}')
with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Written')
