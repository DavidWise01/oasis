from pathlib import Path
import base64
import hashlib

root = Path(__file__).parent
binary = (root / 'vector_toroid.wasm').read_bytes()
digest = hashlib.sha256(binary).hexdigest()
template = (root / 'index.template.html').read_text()
assert "__WASM_BASE64__" in template and "__WASM_SHA__" in template
out = template.replace("__WASM_BASE64__", base64.b64encode(binary).decode()).replace("__WASM_SHA__", digest)
(root / 'index.html').write_text(out)
print("Embedded compiled 3D WASM SHA256:", digest)
