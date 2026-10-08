#!/usr/bin/env python3
"""Inventory all current OaSIs Lean sources and compile each, fail closed."""
import pathlib
import subprocess
import json
import sys

root = pathlib.Path(__file__).resolve().parents[2]
paths = sorted((root / "lean").rglob("*.lean"))
# Archived, historical and frozen code remains included in inventory, but
# only current main-line Lean sources are compiled in the active check.
def archived(p):
    return any(part.lower() in {"legacy", "archive", "archived", "historical", "frozen"} for part in p.relative_to(root).parts)
active = [p for p in paths if not archived(p)]
results = []
for p in paths:
    item = {"source":str(p.relative_to(root)), "active":not archived(p)}
    if not archived(p):
        run = subprocess.run(["lean", str(p)], cwd=root, capture_output=True, text=True)
        item["exit_code"] = run.returncode
        item["output"] = (run.stdout + run.stderr)[-3000:]
    else:
        item["status"] = "preserved_not_compiled"
    results.append(item)
out = root / "kernel/main-aligned/lean-inventory-result.json"
out.write_text(json.dumps({"total":len(paths),"active":len(active),"results":results},indent=2),encoding="utf-8")
print(f"Lean inventory: {len(paths)} files, {len(active)} active compile targets")
failures = [x for x in results if x.get("active") and x.get("exit_code") != 0]
for item in failures[:20]:
    print("FAILED", item["source"])
    print(item["output"][-700:])
if not active:
    print("BLOCKED: no active Lean sources located")
    sys.exit(2)
if failures:
    print(f"BLOCKED: {len(failures)} active Lean files did not compile independently")
    sys.exit(1)
print("0e: all inventoried active Lean files compiled independently")
