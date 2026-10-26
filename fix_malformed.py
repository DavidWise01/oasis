#!/usr/bin/env python3
"""Fix malformed single-line tuples in build_rome_gods.py.

The committed HEAD has:
    ("sapphon-agon", "...", "...", "...", "...")

Each needs to become:
    ("sapphon-agon", "...", "...", "...",
     "..."),
"""
import ast
import sys

filepath = 'build_rome_gods.py'

with open(filepath, 'r', encoding='utf-8') as f:
    committed = f.read()

# Verify HEAD parses
try:
    ast.parse(committed)
    print('HEAD parses OK')
except SyntaxError as e:
    print(f'HEAD syntax error: {e.msg} at line {e.lineno}')
    sys.exit(1)

# Read committed lines (preserving CRLF)
lines = committed.splitlines(keepends=True)

# All slugs to fix
all_slugs = [
    'sapphon-agon', 'apollo-agon', 'jupiter-sappho', 'hermes-sappho',
    'zeus-sappho', 'themis-sappho', 'apollo-sappho', 'poseidon-sappho',
    'mnemosyne-sappho', 'natura-sappho', 'atlas-sappho', 'hermes-spoke2',
    'zeus-spoke2', 'jupiter-sommelier', 'hermes-ladder', 'apollo-diadem',
    'themis-sommelier', 'natura-sommelier', 'zeus-sommelier', 'hermes-sommelier',
    'sapphon-sommelier', 'sapphon-star', 'sapphon-mouth', 'sapphon-mountain',
    'sapphon-tower', 'sapphon-ladder', 'sapphon-agon-fire', 'sapphon-agon-wind',
    'sapphon-agon-sun', 'sapphon-agon-sea',
    'pershan-agon', 'apollo-pershan', 'jupiter-pershan', 'hermes-pershan',
    'zeus-pershan', 'themis-pershan', 'poseidon-pershan', 'mnemosyne-pershan',
    'natura-pershan', 'atlas-pershan', 'hermes-spoke3', 'zeus-spoke3',
    'jupiter-sommelier2', 'hermes-ladder2', 'apollo-diadem2',
    'themis-sommelier2', 'natura-sommelier2', 'zeus-sommelier2',
    'hermes-sommelier2', 'pershan-sommelier', 'pershan-star', 'pershan-mouth',
    'pershan-mountain', 'pershan-tower', 'pershan-ladder', 'pershan-agon-fire',
    'pershan-agon-wind', 'pershan-agon-sun', 'pershan-agon-sea', 'pershan-agon-star',
]

fix_count = 0
new_lines = []

for line in lines:
    stripped = line.strip()
    
    # Check if this is a malformed single-line tuple
    is_malformed = False
    slug = None
    
    for s in all_slugs:
        if stripped.startswith(f'("{s}"'):
            is_malformed = True
            slug = s
            break
    
    if is_malformed:
        # Extract the 4 strings
        import re
        # Match:    "slug", "name", "blurb", "story"
        m = re.match(r'^(\s*"[^"]*",\s*"[^"]*",\s*"[^"]*",\s*"[^"]*")\s*\)\s*$', stripped)
        if m:
            parts = re.findall(r'"([^"]*)"', m.group(1))
            if len(parts) == 4:
                slug, name, blurb, story = parts
                lime = slug.split('-')[0] + '-style'
                # Build fixed two-line tuple
                fixed = f'    ("{slug}", "{name}", "{blurb}", "{story}",\r\n     "{lime}"),\r\n'
                new_lines.append(fixed)
                fix_count += 1
                continue
    
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

print(f'Fixed {fix_count} malformed single-line entries')

with open(filepath, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(new_content)
