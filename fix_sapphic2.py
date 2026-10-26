#!/usr/bin/env python3
"""
Fix build_rome_gods.py: add missing continuation lines to sapphon-agon
and the other single-line sapphic/persian entries.

The committed HEAD has these entries on one line instead of two:
    ("sapphon-agon", "...", "...", "...", "...")
This is a syntax error in Python (a tuple as the first statement in a block).

Fix: rewrite those entries as proper two-line tuples with trailing commas.
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
    print(f'HEAD syntax error: {e}')
    sys.exit(1)

# Read committed lines
lines = committed.splitlines(keepends=True)

# Find sapphon-agon entry (line 813 of the committed file, index 812)
# It's a single-line tuple that needs a continuation line added
fixed_lines = []
skip_until = None

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Detect the sapphic/persian single-line tuple entries
    if stripped.startswith('    ("sapphon-agon"') or \
       stripped.startswith('    ("apollo-agon"') or \
       stripped.startswith('    ("jupiter-sappho"') or \
       stripped.startswith('    ("hermes-sappho"') or \
       stripped.startswith('    ("zeus-sappho"') or \
       stripped.startswith('    ("themis-sappho"') or \
       stripped.startswith('    ("apollo-sappho"') or \
       stripped.startswith('    ("poseidon-sappho"') or \
       stripped.startswith('    ("mnemosyne-sappho"') or \
       stripped.startswith('    ("natura-sappho"') or \
       stripped.startswith('    ("atlas-sappho"') or \
       stripped.startswith('    ("hermes-spoke2"') or \
       stripped.startswith('    ("zeus-spoke2"') or \
       stripped.startswith('    ("jupiter-sommelier"') or \
       stripped.startswith('    ("hermes-ladder"') or \
       stripped.startswith('    ("apollo-diadem"') or \
       stripped.startswith('    ("themis-sommelier"') or \
       stripped.startswith('    ("natura-sommelier"') or \
       stripped.startswith('    ("zeus-sommelier"') or \
       stripped.startswith('    ("hermes-sommelier"') or \
       stripped.startswith('    ("sapphon-sommelier"') or \
       stripped.startswith('    ("sapphon-star"') or \
       stripped.startswith('    ("sapphon-mouth"') or \
       stripped.startswith('    ("sapphon-mountain"') or \
       stripped.startswith('    ("sapphon-tower"') or \
       stripped.startswith('    ("sapphon-ladder"') or \
       stripped.startswith('    ("sapphon-agon-fire"') or \
       stripped.startswith('    ("sapphon-agon-wind"') or \
       stripped.startswith('    ("sapphon-agon-sun"') or \
       stripped.startswith('    ("sapphon-agon-sea"') or \
       stripped.startswith('    ("pershan-agon"') or \
       stripped.startswith('    ("apollo-pershan"') or \
       stripped.startswith('    ("jupiter-pershan"') or \
       stripped.startswith('    ("hermes-pershan"') or \
       stripped.startswith('    ("zeus-pershan"') or \
       stripped.startswith('    ("themis-pershan"') or \
       stripped.startswith('    ("poseidon-pershan"') or \
       stripped.startswith('    ("mnemosyne-pershan"') or \
       stripped.startswith('    ("natura-pershan"') or \
       stripped.startswith('    ("atlas-pershan"') or \
       stripped.startswith('    ("hermes-spoke3"') or \
       stripped.startswith('    ("zeus-spoke3"') or \
       stripped.startswith('    ("jupiter-sommelier2"') or \
       stripped.startswith('    ("hermes-ladder2"') or \
       stripped.startswith('    ("apollo-diadem2"') or \
       stripped.startswith('    ("themis-sommelier2"') or \
       stripped.startswith('    ("natura-sommelier2"') or \
       stripped.startswith('    ("zeus-sommelier2"') or \
       stripped.startswith('    ("hermes-sommelier2"') or \
       stripped.startswith('    ("pershan-sommelier"') or \
       stripped.startswith('    ("pershan-star"') or \
       stripped.startswith('    ("pershan-mouth"') or \
       stripped.startswith('    ("pershan-mountain"') or \
       stripped.startswith('    ("pershan-tower"') or \
       stripped.startswith('    ("pershan-ladder"') or \
       stripped.startswith('    ("pershan-agon-fire"') or \
       stripped.startswith('    ("pershan-agon-wind"') or \
       stripped.startswith('    ("pershan-agon-sun"') or \
       stripped.startswith('    ("pershan-agon-sea"') or \
       stripped.startswith('    ("pershan-agon-star"'):
        
        # This is a malformed single-line tuple - add continuation line
        # Extract the values
        import json
        # Parse the line to extract values
        # Format:     ("slug", "name", "blurb", "story", "lime"),
        # Take everything after the first (
        content = stripped
        
        # Build the corrected two-line version
        fixed_lines.append(line)  # Keep the original line
        fixed_lines.append('     "", "", "", ""),\n')
        continue
    
    fixed_lines.append(line)

new_content = ''.join(fixed_lines)

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

print(f'Applied fix to {new_content.count("sapphon-agon") + new_content.count("pershan-agon")} single-line entries')

with open(filepath, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(new_content)
