#!/usr/bin/env python3
"""
Fix the malformed single-line sapphic/persian tuples in build_rome_gods.py.

The committed HEAD (bae0eecb) has tuples like:
    ("sapphon-agon", "The sapphon-agon description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon", "sapphon-style")
    ("apollo-agon", ...)
    ...

Each needs to become a two-line tuple with a trailing comma:
    ("sapphon-agon", "The sapphon-agon description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon",
     "sapphon-style"),
"""
import ast
import re
import sys

filepath = 'build_rome_gods.py'

with open(filepath, 'r', encoding='utf-8') as f:
    committed = f.read()

# Verify HEAD parses
try:
    ast.parse(committed)
    print('HEAD parses OK')
except SyntaxError as e:
    print(f'HEAD syntax error: {e.msg}')
    sys.exit(1)

# Read committed lines
lines = committed.splitlines(keepends=True)

# Pattern matching single-line tuples with sapphic/persian slugs
# These are malformed - they need continuation lines
slug_pattern = re.compile(
    r'    \(\"(sapphon-agon|apollo-agon|jupiter-sappho|hermes-sappho|zeus-sappho|'
    r'themis-sappho|apollo-sappho|poseidon-sappho|mnemosyne-sappho|natura-sappho|'
    r'atlas-sappho|hermes-spoke2|zeus-spoke2|jupiter-sommelier|hermes-ladder|'
    r'apollo-diadem|themis-sommelier|natura-sommelier|zeus-sommelier|'
    r'hermes-sommelier|sapphon-sommelier|sapphon-star|sapphon-mouth|'
    r'sapphon-mountain|sapphon-tower|sapphon-ladder|sapphon-agon-fire|'
    r'sapphon-agon-wind|sapphon-agon-sun|sapphon-agon-sea|'
    r'pershan-agon|apollo-pershan|jupiter-pershan|hermes-pershan|'
    r'zeus-pershan|themis-pershan|poseidon-pershan|mnemosyne-pershan|'
    r'natura-pershan|atlas-pershan|hermes-spoke3|zeus-spoke3|'
     r'jupiter-sommelier2|hermes-ladder2|apollo-diadem2|'
     r'themis-sommelier2|natura-sommelier2|zeus-sommelier2|'
     r'hermes-sommelier2|pershan-sommelier|pershan-star|pershan-mouth|'
     r'pershan-mountain|pershan-tower|pershan-ladder|pershan-agon-fire|'
     r'pershan-agon-wind|pershan-agon-sun|pershan-agon-sea|pershan-agon-star)"\s*\)\s*$'
)

fixed_count = 0
new_lines = []

for line in lines:
    stripped = line.strip()
    
    if slug_pattern.match(stripped):
        # Extract the slug from the line
        match = slug_pattern.search(stripped)
        if match:
            slug = match.group(1)
            # Build the fixed two-line tuple
            fixed_line = (
                f'    ("{slug}", "The {slug} description", "Sapphic theme placeholder", '
                f'"Placeholder story for {slug}", '
                f'"{slug.split("-")[0]}-style")\r\n'
                f'     "", "", "", ""),\r\n'
            )
            new_lines.append(fixed_line)
            fixed_count += 1
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

new_content = ''.join(new_lines)

# Verify parses
try:
    ast.parse(new_content)
    print('New content parses OK')
except SyntaxError as e:
    print(f'Syntax error: {e.msg} at line {e.lineno}')
    lines_err = new_content.split('\n')
    for i in range(max(0, e.lineno-3), min(len(lines_err), e.lineno+3)):
        print(f'{i+1}: {repr(lines_err[i])}')
    sys.exit(1)

print(f'Fixed {fixed_count} malformed single-line entries')

with open(filepath, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(new_content)
