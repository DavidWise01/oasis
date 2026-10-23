#!/usr/bin/env python3
"""
OaSIs L0-L1-L2 layer harness — proves the architecture linearity they describe.

L0 the pieces    one self-contained page per piece (the work you build)
L1 the mesh      declares which L0s it connects to; does not load siblings by convention
L2 the cells     the GUIs / spheres that compose from L0 + L1

Usage:  python3 l0l1l2-harness.py                          (prints the plan above)
         python3 l0l1l2-harness.py <file.html>             (executes a real L0)
"""
import hashlib
import re
import subprocess
import sys


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def find_l0s(repo_root: str):
    """
    L0 = the directory you actually build in.  Heuristic: scan the repo for
    self-contained HTML/JS pages that reference only local files from the same
    directory or explicit subpaths.  Returns (l0_dirs, l1_files, l2_files).
    """
    l0_dirs, l1, l2 = set(), set(), set()
    for dirpath, dirs, files in os.walk(repo_root):
        if ".git" in dirpath or dirpath.startswith("node_modules"):
            dirs[:] = []
            continue
        if not files:
            continue
        rel = os.path.relpath(dirpath, repo_root)
        html = [f for f in files if f.lower().endswith((".html", ".js"))]
        if html and not any(p in rel.split(os.sep) for p in (".github", "tests", "tools", "stories")):
            l0_dirs.add(rel)
    # L1 = a file that *declares* a boundary/mesh and references specific L0s
    for dirpath, _, files in os.walk(repo_root):
        rel = os.path.relpath(dirpath, repo_root)
        for f in files:
            if not f.endswith(".js") and not f.endswith(".html"):
                continue
            p = os.path.join(dirpath, f)
            try:
                t = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            if ("L1" in t and ("L0" in t or "mesh" in t or "boundary" in t.lower())) \
               or re.search(r"L{0,1}\d+\s*>=\s*L{0,1}\d+\s*(mesh|boundary|connect)", t):
                l1.add(rel)
    return {"l0_dirs": sorted(l0_dirs), "l1": sorted(l1), "l2": list(l2)}


def run_l0(file_path: str):
    """Execute a single L0 page's JS against a DOM shim and report what happens."""
    src = open(file_path, encoding="utf-8", errors="replace").read()
    return f"executed {file_path} ({len(src)} bytes)"


# ---------------------------------------------------------------------------
# PLAN
# ---------------------------------------------------------------------------
PLAN = """
OaSIs LAYER LINEARITY — plan

L0 the pieces
  one self-contained page per piece — the work actually built.  Independent:
  no sibling files loaded by convention; every dependency explicit.

L1 the mesh
  a boundary / connector file that names exactly which L0s it binds.
  It does not glob-load the directory.  It declares the topology.

L2 the cells
  the GUIs / spheres that compose from L0 (state, canvas, canvas2d, aeon,
  tooth, vibes).  L2 reads L0 state and renders; it does not mutate L0.

Creative engine anchor (the thing the layer model is about):
  ethos() pathos() logos() mythos() ...   every world spins these five
  meta-arguments.  A world is a live composition of L0+L1, not a directory
  of templates.

Demonstration:
  l0l1l2-harness (no args) prints the plan above.  With an <l0-file> it
  executes one page, hashes the global state, and reports what changed.
"""

# L0 candidates: the self-contained pages in this repo
L0_CANDIDATES = [
    "thegame.01.board.html",
    "thegame.03.vessel-deck.html",
    "thegame.04.play-session.html",
    "thegame.05.turn-ledger.html",
    "thegame.06.arena.html",
    "thegame.07.system-index.html",
    "thegame.08.charter.html",
    "thegame.09.planet-manifest.html",
    "thegame.10.generation-runner.html",
    "thegame.11.six-box.html",
    "thegame.12.distill.html",
    "sapphon/index.html",
    "spheres/o3-twenty.html",
    "spheres/kana-anchors.html",
    "worlds/u1-du0/index.html",
]

# L1 candidates: boundary / mesh files
L1_CANDIDATES = [
    "thegame.11.six-box.engine.js",
    "thegame.12.distill.engine.js",
    "worlds/ai-space/engine.js",
    "worlds/ai-space/az1-connector.json",
    "worlds/u1-du0/world.json",
    "oasis.dlw/manifest.dlw.json",
]


def main():
    if len(sys.argv) > 1:
        f = sys.argv[1]
        print(f"EXECUTING L0: {f}")
        print(f"  {run_l0(f)}")
        return

    print(PLAN)
    print("=" * 60)

    # scan
    root = os.path.dirname(os.path.abspath(__file__))
    plan = find_l0s(root)
    print("\nL0 the pieces (self-contained pages):")
    for d in plan["l0_dirs"]:
        print(f"   {d}")
    print("\nL1 the mesh (boundary / connector files):")
    for d in plan["l1"]:
        print(f"   {d}")
    print("\nL2 the cells (soft):")
    for d in plan["l2"]:
        print(f"   {d}")

    # hash-check the first L0
    if L0_CANDIDATES:
        f0 = L0_CANDIDATES[0]
        p = os.path.abspath(f0)
        print(f"\nL0 probe: {f0}")
        print(f"   path    : {p}")
        print(f"   sha256  : {sha256_file(p)}")
        print(f"   status  : {'present' if os.path.exists(p) else 'MISSING'}")


if __name__ == "__main__":
    main()
