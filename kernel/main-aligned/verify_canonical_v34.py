#!/usr/bin/env python3
"""Find and compile the exact manifest-pinned v34 monolithic Lean source.

Scans the checked-out DavidWise01/oasis tree, never substitutes other source.
"""
import gzip
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "kernel/main-aligned/v34/manifest.json"

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> int:
    meta = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = meta["current_source_sha256"]
    expected_name = meta["current_source"]
    examined = 0
    found = None
    matched_path = None
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        if not (path.name.endswith(".lean") or path.name.endswith(".lean.gz")):
            continue
        examined += 1
        raw = path.read_bytes()
        try:
            payload = gzip.decompress(raw) if path.name.endswith(".gz") else raw
        except (gzip.BadGzipFile, EOFError, OSError):
            print("WARN: unreadable gzip:", path.relative_to(ROOT))
            continue
        if sha(payload) == expected:
            found, matched_path = payload, path
            break

    if found is None:
        print("BLOCKED: exact canonical v34 source not located in checkout")
        print("Expected filename:", expected_name)
        print("Expected SHA-256:", expected)
        print("Lean candidates examined:", examined)
        print("Restore manifest-pinned source into repository, not an approximation.")
        return 2

    print("SOURCE VERIFIED:", matched_path.relative_to(ROOT), sha(found))
    # For a compressed match, compile verified decompressed bytes in a
    # temporary directory rather than modifying the frozen source.
    if matched_path.suffix == ".gz":
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / expected_name
            target.write_bytes(found)
            result = subprocess.run(["lean", str(target)], cwd=ROOT, check=False)
    else:
        result = subprocess.run(["lean", str(matched_path)], cwd=ROOT, check=False)
    if result.returncode:
        print("BLOCKED: full monolithic Lean compilation failed:", result.returncode)
        return result.returncode
    print("0e: exact canonical v34 monolithic source compiled")
    return 0

if __name__ == "__main__":
    sys.exit(main())
