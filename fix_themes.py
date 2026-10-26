#!/usr/bin/env python3
with open('build_rome_gods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check lines 813-815 (0-indexed 812-814)
for i in range(812, 815):
    line = lines[i]
    print(f'Line {i+1}: ends_with_paren={line.rstrip().endswith(")")}')
    print(f'  ends_with_comma_paren={line.rstrip().endswith(",)")}')
    print(f'  last_5={line.rstrip()[-5:]!r}')
    print()

# Fix: the issue is that these lines end with ')' - they need '),'
# The tuple is: ("sapphon-agon", "...", "...", "...", "sapphon-style")
# But it has: "sapphon-style)") -> needs "sapphon-style"),
# Wait, actually it's: "sapphon-style")" which means the tuple closes with ')' and there's an extra ')'
# Actually looking at the Python source: the line is
#     ("sapphon-agon", "...", "...", "...", "sapphon-style")
# The cat -A shows: ... "sapphon-style")$
# So the $ is the end-of-line marker, and the line ends with ')'
# But wait, the line 813 is:
#     ("sapphon-agon", "The sapphon-agon description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon", "sapphon-style")
# It ends with "sapphon-style") - the tuple closes with ')', followed by the line ending
# But we need to add a comma: "sapphon-style"),

# After the previous fix attempt, the lines became:
#     ("sapphon-agon", "...", "...", "...", "sapphon-style")),
# Wait, let me check again

fixed = 0
for i in range(812, 815):
    line = lines[i]
    stripped = line.rstrip()
    if stripped.endswith('))'):
        # This has an extra close paren at the end
        # Let's check: "sapphon-style"))
        # We want: "sapphon-style"),
        # So: remove the last ')' and add '),'
        new_line = stripped[:-1] + '),\n'
        # But also we need to handle the newline
        if line.endswith('\n'):
            new_line = new_line[:-1] + '\n'
        lines[i] = new_line
        fixed += 1
        print(f'Fixed line {i+1}')
    elif stripped.endswith(')'):
        # Just need to add a comma before the close paren
        # No wait, the line already ends with ')' (close paren of tuple)
        # We need to add ',' before the ')'
        # But the tuple already has ')' at the end
        # Actually looking at the original: the line was
        #     ("sapphon-agon", "The sapphon-agon description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon", "sapphon-style")
        # This is a tuple literal ending with ')' - no comma
        # We need: ... "sapphon-style"),
        # So: remove the ')' and add '),'
        if line.rstrip().endswith(')"'):
            new_line = line.rstrip()[:-1] + '),\n'
            if line.endswith('\n'):
                new_line = new_line[:-1] + '\n'
            lines[i] = new_line
            fixed += 1
            print(f'Fixed line {i+1}')
        else:
            print(f'Line {i+1}: ends with ) but not )"')
    else:
        print(f'Line {i+1}: unexpected ending {stripped[-10:]!r}')

print(f'Total fixed: {fixed}')
with open('build_rome_gods.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Written')
