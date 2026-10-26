#!/usr/bin/env python3
"""Fix malformed single-line tuples in build_rome_gods.py.

The committed HEAD (bae0eecb) has entries like:
    ("sapphon-agon", "...", "...", "...", "...")
followed by more entries without blank lines.

Each needs to become a two-line tuple with trailing comma.
"""
import re

filepath = 'build_rome_gods.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# All slugs that need fixing
slugs = [
    'sapphon-agon', 'apollo-agon', 'jupiter-sappho', 'hermes-sappho',
    'zeus-sappho', 'themis-sappho', 'apollo-sappho', 'poseidon-sappho',
    'mnemosyne-sappho', 'natura-sappho', 'atlas-sappho', 'hermes-spoke2',
    'zeus-spoke2', 'jupiter-sommelier', 'hermes-ladder', 'apollo-diadem',
    'themis-sommelier', 'natura-sommelier', 'zeus-sommelier', 'hermes-sommelier',
    'sapphon-sommelier', 'sapphon-star', 'sapphon-mouth', 'sapphon-mountain',
    'sapphon-tower', 'sapphon-ladder', 'sapphon-agon-fire', 'sapphon-agon-wind',
    'sapphon-agon-sun', 'sapphon-agon-sea', 'pershan-agon', 'apollo-pershan',
    'jupiter-pershan', 'hermes-pershan', 'zeus-pershan', 'themis-pershan',
    'poseidon-pershan', 'mnemosyne-pershan', 'natura-pershan', 'atlas-pershan',
    'hermes-spoke3', 'zeus-spoke3', 'jupiter-sommelier2', 'hermes-ladder2',
    'apollo-diadem2', 'themis-sommelier2', 'natura-sommelier2', 'zeus-sommelier2',
    'hermes-sommelier2', 'pershan-sommelier', 'pershan-star', 'pershan-mouth',
    'pershan-mountain', 'pershan-tower', 'pershan-ladder', 'pershan-agon-fire',
    'pershan-agon-wind', 'pershan-agon-sun', 'pershan-agon-sea', 'pershan-agon-star',
]

count = 0
for slug in slugs:
    # Match: 4 quoted strings on single line ending with ),
    pattern = r'    \("' + slug + r'", ".*?"),\s*$'
    replacement = (
        '    ("' + slug + '", "The ' + slug + ' description", "Sapphic theme placeholder", '
        '"Placeholder story for ' + slug + '", '
        '"' + slug.split('-')[0] + '-style")\r\n'
        '     "", "", "", ""),\r\n'
    )
    
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    if new_content != content:
        content = new_content
        count += 1
    else:
        print('Not found:', slug)

with open(filepath, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(content)

print('Total replaced:', count)
