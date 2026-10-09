#!/usr/bin/env python3
"""Re-embed a compiled WASM binary into this standalone SVG viewer."""
from pathlib import Path
import re, base64
p=Path(__file__).resolve().parent
view=p/'index.html'
s=view.read_text(encoding='utf-8')
b=base64.b64encode((p/'kernel.wasm').read_bytes()).decode('ascii')
t,n=re.subn(r"const WASM_B64='[^']+';",lambda m:"const WASM_B64='"+b+"';",s,count=1)
assert n==1
view.write_text(t,encoding='utf-8')
print('WASM embedded:',len(b),'base64 characters')
