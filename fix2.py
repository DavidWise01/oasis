with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check lines 813-815 (0-indexed 812-814)
for i in range(812, 815):
    line = lines[i]
    stripped = line.rstrip()
    print(f'Line {i+1}: ends_with_paren={stripped.endswith(")")}')
    print(f'  ends_with_paren_comma={stripped.endswith("),")}')
    print(f'  last_10={stripped[-10:]!r}')
    print(f'  last_bytes={line[-20:]!r}')
    print()

# The issue: lines 813-815 end with "))," but should end with "),"
# Fix: remove one close paren from each of these lines
fixed = 0
for i in range(812, 815):
    line = lines[i]
    stripped = line.rstrip()
    if stripped.endswith(')),'):
        # Remove one ")": change "))," to "),"
        # Keep only the newline if present
        if line.endswith('\n'):
            new_line = stripped[:-2] + '),\n'
            lines[i] = new_line
            fixed += 1
            print(f'Fixed line {i+1}: {new_line[-20:]!r}')
        else:
            new_line = stripped[:-2] + '),'
            lines[i] = new_line
            fixed += 1
            print(f'Fixed line {i+1}: {new_line[-20:]!r}')
    elif stripped.endswith(')'):
        print(f'Line {i+1}: still ends with ")", needs comma')
    else:
        print(f'Line {i+1}: unexpected ending {stripped[-10:]!r}')

print(f'\nTotal fixed: {fixed}')

with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Written')
