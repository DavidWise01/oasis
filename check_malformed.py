#!/usr/bin/env python3
"""Find malformed single-line tuples in build_rome_gods.py."""
import re

with open('build_rome_gods.py', 'rb') as f:
    content = f.read()

# Split by CRLF
chunks = content.split(b'\r\n')
print(f'Total CRLF chunks: {len(chunks)}')

# Check the sapphon section
for i in range(810, 870):
    chunk = chunks[i]
    # Check if it's a sapphic/persian tuple
    if b'("sapphon' in chunk or b'("apollo' in chunk or b'("jupiter' in chunk or b'("hermes' in chunk or b'("zeus' in chunk or b'("themis' in chunk or b'("poseidon' in chunk or b'("mnemosyne' in chunk or b'("natura' in chunk or b'("atlas' in chunk:
        stripped = chunk.rstrip()
        # Check if ends with '), not just )
        if not stripped.endswith(b'"'):
            print(f'Line {i+1}: {chunk[:120]}...')
