#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent / "more_garbage_v05.py"

spec = importlib.util.spec_from_file_location("mgv05_chapter", RUNTIME)
mg = importlib.util.module_from_spec(spec)
sys.modules["mgv05_chapter"] = mg
assert spec.loader is not None
spec.loader.exec_module(mg)

def corrupt(text: str, path: tuple[str, ...]) -> str:
    cur = text
    for enc in path:
        cur = cur.encode("utf-8").decode(enc)
    return cur

paragraphs = []
for i in range(1, 21):
    paragraphs.append(
        f"Section {i}. François carried a café ledger through München while König checked the margin twice. "
        f"He wrote, “A naïve parser shouldn’t guess what it cannot prove,” then marked the next line with 😂 and an em dash — before continuing. "
        f"The record kept xDEADBEEFX intact because the 32-bit island was already coherent, while ordinary words flowed around it without special handling. "
        f"Later, façade, mañana, Pokémon, smörgåsbord, and São Tomé appeared in the same passage, giving the decoder several different Unicode shapes to recover. "
        f"Nothing in the clean structure required the damaged primitive to remember its former identity; the surrounding token only needed to become coherent again."
    )

clean = "\n\n".join(paragraphs)
replacements = [
    ("François", ("cp1252","cp1252")),
    ("café", ("mac_roman","mac_roman")),
    ("München", ("cp1252",)),
    ("König", ("mac_roman","latin1")),
    ("naïve", ("latin1","latin1")),
    ("shouldn’t", ("cp1252",)),
    ("😂", ("latin1",)),
    ("façade", ("cp1252","latin1")),
    ("mañana", ("latin1",)),
    ("Pokémon", ("cp1252",)),
    ("smörgåsbord", ("mac_roman",)),
    ("São Tomé", ("latin1",)),
]

damaged = clean
for token, path in replacements:
    damaged = damaged.replace(token, corrupt(token, path))

start = time.perf_counter()
result = mg.process_stream(damaged, max_window=96, max_depth=10)
elapsed = time.perf_counter() - start

sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
report = {
    "status": "PASS" if result["output"] == clean else "FAIL",
    "paragraphs": len(paragraphs),
    "clean_words": len(clean.split()),
    "clean_chars": len(clean),
    "damaged_chars": len(damaged),
    "repaired_primitives": result["repaired_primitives"],
    "paused_primitives": result["paused_primitives"],
    "search_checks": result["search_checks"],
    "elapsed_seconds": round(elapsed, 4),
    "damaged_sha256": sha(damaged),
    "expected_sha256": sha(clean),
    "decoded_sha256": sha(result["output"]),
}
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["status"] == "PASS" else 1)
