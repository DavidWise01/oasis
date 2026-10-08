#!/usr/bin/env python3
"""Fail-closed v34 canonical-source gate. Stdlib only."""
import gzip
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "kernel/main-aligned/v34/manifest.json"
SOURCE_DIR = ROOT / "kernel/main-aligned/v34"
def main():
    meta = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = meta["current_source_sha256"]
    filename = meta["current_source"]
    candidates = [SOURCE_DIR / filename, ROOT / "lean" / filename,
                  ROOT / "kernel/main-aligned" / filename]
    source = next((x for x in candidates if x.is_file()), None)
    if source is None:
        print("BLOCKED: v34 monolithic Lean source missing from canonical candidate paths")
        print("Expected:", filename)
        print("Expected SHA-256:", expected)
        return 2
    payload = source.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected:
        print("BLOCKED: source hash mismatch", actual, "!=", expected)
        return 3
    print("SOURCE VERIFIED:", source.relative_to(ROOT), actual)
    result = subprocess.run(["lean", str(source)], cwd=ROOT, check=False)
    if result.returncode:
        print("BLOCKED: monolithic Lean compilation failed:", result.returncode)
        return result.returncode
    print("0e: exact canonical v34 monolithic source compiled")
    return 0

if __name__ == "__main__":
    sys.exit(main())
