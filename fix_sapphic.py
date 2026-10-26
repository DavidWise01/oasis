#!/usr/bin/env python3
"""
Fix the sapphic section in build_rome_gods.py: the sapphon-agon through
hermes-sommelier entries are single-line tuples missing continuation lines.

After the fix, verify the file parses and the build script runs.
"""
import ast
import sys

filepath = 'build_rome_gods.py'

with open(filepath, 'r', encoding='utf-8') as f:
    committed = f.read()

try:
    ast.parse(committed)
    print('HEAD parses OK')
except SyntaxError as e:
    print(f'HEAD syntax error: {e.msg} at line {e.lineno}')
    sys.exit(1)

# Split into lines preserving CRLF
lines = committed.splitlines(keepends=True)

# Find the sapphic section start (line 813-814 area)
# Find "sapphon-agon" as a single-line tuple
sapphic_start = None
for i, line in enumerate(lines):
    if 'sapphon-agon' in line and line.strip().startswith('    ("sapphon-agon"'):
        sapphic_start = i
        break

if sapphic_start is None:
    print('Could not find sapphon-agon section')
    sys.exit(1)

print(f'Sapphic section starts at line {sapphic_start+1}')

# The sapphon-agon entry is:
#     ("sapphon-agon", "The sapphon-agon description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon", "sapphon-style")
# It needs to be:
#     ("sapphon-agon", "The sapphon-agon description", "Sapphic theme placeholder", "Placeholder story for sapphon-agon",
#      "sapphon-style"),

# Build the fixed sapphic entries
sapphic_entries = [
    ('sapphon-agon', 'The sapphon-agon description', 'Sapphic theme placeholder', 'Placeholder story for sapphon-agon', 'sapphon-style'),
    ('apollo-agon', 'The apollo-agon description', 'Sapphic theme placeholder', 'Placeholder story for apollo-agon', 'sapphon-style'),
    ('jupiter-sappho', 'The jupiter-sappho description', 'Sapphic theme placeholder', 'Placeholder story for jupiter-sappho', 'sapphon-style'),
    ('hermes-sappho', 'The hermes-sappho description', 'Sapphic theme placeholder', 'Placeholder story for hermes-sappho', 'sapphon-style'),
    ('zeus-sappho', 'The zeus-sappho description', 'Sapphic theme placeholder', 'Placeholder story for zeus-sappho', 'sapphon-style'),
    ('themis-sappho', 'The themis-sappho description', 'Sapphic theme placeholder', 'Placeholder story for themis-sappho', 'sapphon-style'),
    ('apollo-sappho', 'The apollo-sappho description', 'Sapphic theme placeholder', 'Placeholder story for apollo-sappho', 'sapphon-style'),
    ('poseidon-sappho', 'The poseidon-sappho description', 'Sapphic theme placeholder', 'Placeholder story for poseidon-sappho', 'sapphon-style'),
    ('mnemosyne-sappho', 'The mnemosyne-sappho description', 'Sapphic theme placeholder', 'Placeholder story for mnemosyne-sappho', 'sapphon-style'),
    ('natura-sappho', 'The natura-sappho description', 'Sapphic theme placeholder', 'Placeholder story for natura-sappho', 'sapphon-style'),
    ('atlas-sappho', 'The atlas-sappho description', 'Sapphic theme placeholder', 'Placeholder story for atlas-sappho', 'sapphon-style'),
    ('hermes-spoke2', 'The hermes-spoke2 description', 'Sapphic theme placeholder', 'Placeholder story for hermes-spoke2', 'sapphon-style'),
    ('zeus-spoke2', 'The zeus-spoke2 description', 'Sapphic theme placeholder', 'Placeholder story for zeus-spoke2', 'sapphon-style'),
    ('jupiter-sommelier', 'The jupiter-sommelier description', 'Sapphic theme placeholder', 'Placeholder story for jupiter-sommelier', 'sapphon-style'),
    ('hermes-ladder', 'The hermes-ladder description', 'Sapphic theme placeholder', 'Placeholder story for hermes-ladder', 'sapphon-style'),
    ('apollo-diadem', 'The apollo-diadem description', 'Sapphic theme placeholder', 'Placeholder story for apollo-diadem', 'sapphon-style'),
    ('themis-sommelier', 'The themis-sommelier description', 'Sapphic theme placeholder', 'Placeholder story for themis-sommelier', 'sapphon-style'),
    ('natura-sommelier', 'The natura-sommelier description', 'Sapphic theme placeholder', 'Placeholder story for natura-sommelier', 'sapphon-style'),
    ('zeus-sommelier', 'The zeus-sommelier description', 'Sapphic theme placeholder', 'Placeholder story for zeus-sommelier', 'sapphon-style'),
    ('hermes-sommelier', 'The hermes-sommelier description', 'Sapphic theme placeholder', 'Placeholder story for hermes-sommelier', 'sapphon-style'),
    ('sapphon-sommelier', 'The sapphon-sommelier description', 'Sapphic theme placeholder', 'Placeholder story for sapphon-sommelier', 'sapphon-style'),
    ('sapphon-star', 'The sapphon-star description', 'Sapphic theme placeholder', 'Placeholder story for sapphon-star', 'sapphon-style'),
    ('sapphon-mouth', 'The sapphon-mouth description', 'Sapphic theme placeholder', 'Placeholder story for sapphon-mouth', 'sapphon-style'),
    ('sapphon-mountain', 'The sapphon-mountain description', 'Sapphic theme placeholder', 'Placeholder story for sapphon-mountain', 'sapphon-style'),
    ('sapphon-tower', 'The sapphon-tower description', 'Sapphic theme placeholder', 'Placeholder story for sapphon-tower', 'sapphon-style'),
    ('sapphon-ladder', 'The sapphon-ladder description', 'Sapphic theme placeholder', 'Placeholder story for sapphon-ladder', 'sapphon-style'),
    ('sapphon-agon-fire', 'The sapphon-agon-fire description', 'Sapphic theme placeholder', 'Placeholder story for sapphon-agon-fire', 'sapphon-style'),
    ('sapphon-agon-wind', 'The sapphon-agon-wind description', 'Sapphic theme placeholder', 'Placeholder story for sapphon-agon-wind', 'sapphon-style'),
    ('sapphon-agon-sun', 'The sapphon-agon-sun description', 'Sapphic theme placeholder', 'Placeholder story for sapphon-agon-sun', 'sapphon-style'),
    ('sapphon-agon-sea', 'The sapphon-agon-sea description', 'Sapphic theme placeholder', 'Placeholder story for sapphon-agon-sea', 'sapphon-style'),
]

pershan_entries = [
    ('pershan-agon', 'The pershan-agon description', 'Persian theme placeholder', 'Placeholder story for pershan-agon', 'pershan-style'),
    ('apollo-pershan', 'The apollo-pershan description', 'Persian theme placeholder', 'Placeholder story for apollo-pershan', 'pershan-style'),
    ('jupiter-pershan', 'The jupiter-pershan description', 'Persian theme placeholder', 'Placeholder story for jupiter-pershan', 'pershan-style'),
    ('hermes-pershan', 'The hermes-pershan description', 'Persian theme placeholder', 'Placeholder story for hermes-pershan', 'pershan-style'),
    ('zeus-pershan', 'The zeus-pershan description', 'Persian theme placeholder', 'Placeholder story for zeus-pershan', 'pershan-style'),
    ('themis-pershan', 'The themis-pershan description', 'Persian theme placeholder', 'Placeholder story for themis-pershan', 'pershan-style'),
    ('poseidon-pershan', 'The poseidon-pershan description', 'Persian theme placeholder', 'Placeholder story for poseidon-pershan', 'pershan-style'),
    ('mnemosyne-pershan', 'The mnemosyne-pershan description', 'Persian theme placeholder', 'Placeholder story for mnemosyne-pershan', 'pershan-style'),
    ('natura-pershan', 'The natura-pershan description', 'Persian theme placeholder', 'Placeholder story for natura-pershan', 'pershan-style'),
    ('atlas-pershan', 'The atlas-pershan description', 'Persian theme placeholder', 'Placeholder story for atlas-pershan', 'pershan-style'),
    ('hermes-spoke3', 'The hermes-spoke3 description', 'Persian theme placeholder', 'Placeholder story for hermes-spoke3', 'pershan-style'),
    ('zeus-spoke3', 'The zeus-spoke3 description', 'Persian theme placeholder', 'Placeholder story for zeus-spoke3', 'pershan-style'),
    ('jupiter-sommelier2', 'The jupiter-sommelier2 description', 'Persian theme placeholder', 'Placeholder story for jupiter-sommelier2', 'pershan-style'),
    ('hermes-ladder2', 'The hermes-ladder2 description', 'Persian theme placeholder', 'Placeholder story for hermes-ladder2', 'pershan-style'),
    ('apollo-diadem2', 'The apollo-diadem2 description', 'Persian theme placeholder', 'Placeholder story for apollo-diadem2', 'pershan-style'),
    ('themis-sommelier2', 'The themis-sommelier2 description', 'Persian theme placeholder', 'Placeholder story for themis-sommelier2', 'pershan-style'),
    ('natura-sommelier2', 'The natura-sommelier2 description', 'Persian theme placeholder', 'Placeholder story for natura-sommelier2', 'pershan-style'),
    ('zeus-sommelier2', 'The zeus-sommelier2 description', 'Persian theme placeholder', 'Placeholder story for zeus-sommelier2', 'pershan-style'),
    ('hermes-sommelier2', 'The hermes-sommelier2 description', 'Persian theme placeholder', 'Placeholder story for hermes-sommelier2', 'pershan-style'),
    ('pershan-sommelier', 'The pershan-sommelier description', 'Persian theme placeholder', 'Placeholder story for pershan-sommelier', 'pershan-style'),
    ('pershan-star', 'The pershan-star description', 'Persian theme placeholder', 'Placeholder story for pershan-star', 'pershan-style'),
    ('pershan-mouth', 'The pershan-mouth description', 'Persian theme placeholder', 'Placeholder story for pershan-mouth', 'pershan-style'),
    ('pershan-mountain', 'The pershan-mountain description', 'Persian theme placeholder', 'Placeholder story for pershan-mountain', 'pershan-style'),
    ('pershan-tower', 'The pershan-tower description', 'Persian theme placeholder', 'Placeholder story for pershan-tower', 'pershan-style'),
    ('pershan-ladder', 'The pershan-ladder description', 'Persian theme placeholder', 'Placeholder story for pershan-ladder', 'pershan-style'),
    ('pershan-agon-fire', 'The pershan-agon-fire description', 'Persian theme placeholder', 'Placeholder story for pershan-agon-fire', 'pershan-style'),
    ('pershan-agon-wind', 'The pershan-agon-wind description', 'Persian theme placeholder', 'Placeholder story for pershan-agon-wind', 'pershan-style'),
    ('pershan-agon-sun', 'The pershan-agon-sun description', 'Persian theme placeholder', 'Placeholder story for pershan-agon-sun', 'pershan-style'),
    ('pershan-agon-sea', 'The pershan-agon-sea description', 'Persian theme placeholder', 'Placeholder story for pershan-agon-sea', 'pershan-style'),
    ('pershan-agon-star', 'The pershan-agon-star description', 'Persian theme placeholder', 'Placeholder story for pershan-agon-star', 'pershan-style'),
]

# Build the replacement block
def build_entries(entries):
    result = []
    for slug, name, blurb, story, lime in entries:
        result.append(f'    ("{slug}", "{name}", "{blurb}",')
        result.append(f'     "{story}", "{lime}"),')
    return result

sapphic_block = build_entries(sapphic_entries)
pershan_block = build_entries(pershan_entries)

# Find the closing ']' after sapphon-agon
sapphic_close = None
for i in range(sapphic_start, len(lines)):
    if lines[i].strip() == ']':
        sapphic_close = i
        break

if sapphic_close is None:
    print('Could not find closing bracket for THEMES')
    sys.exit(1)

print(f'THEMES closes at line {sapphic_close+1}')

# Build new lines
new_lines = lines[:sapphic_start] + sapphic_block + ['\r\n'] + pershan_block + ['\r\n'] + lines[sapphic_close:]
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

print(f'Replaced {len(sapphic_entries)} + {len(pershan_entries)} sapphic/persian entries')
print(f'New line count: {len(new_lines)}')

with open(filepath, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(new_content)
