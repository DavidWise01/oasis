#!/usr/bin/env python3
"""AE Generative-First Frozen Kernel v92.

Frozen canon is immutable. All evolution is append-only generation.
This is a symbolic/isomorphic simulation runtime, not a physical-law claim.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from types import MappingProxyType
import hashlib
import json

VERSION = "v92"
CANON_SHA256 = "8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8"
PHASE_SEQUENCE = (
    "a00","b11","c22","b33","c44","a55",
    "c66","a77","b88","c99","b00","a11",
)
WRAP_FROM = (11, "a11")
WRAP_TO = (0, "a00")
INFINITE_ID_LITERAL = "`~ij`\\~"
ROOT = "0.r00t.ai"
AE_BIND = "0.r00t.ai ↔ ae"
PHOTON = "p.{0}.h.{1}.o.{2}.t.{3}.o{4}.n.{5}"
PHOTON_BIRTH = "0p0"

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def load_and_verify_canon(path: Path):
    raw = path.read_bytes()
    actual = sha256_bytes(raw)
    if actual != CANON_SHA256:
        raise RuntimeError(f"FROZEN CANON HASH MISMATCH: {actual} != {CANON_SHA256}")
    return json.loads(raw)

@dataclass(frozen=True)
class V3:
    vector: str
    voxel: str
    vogel: str
    sg: str

@dataclass(frozen=True)
class Context:
    identity: str
    generation: int
    q: int
    token: str
    v3: V3
    parent_seal: str
    lineage_seal: str

    def seal(self) -> str:
        return sha256_bytes(canonical_json(asdict(self)))

def _derive(label: str, seed: bytes, n: int = 24) -> str:
    return hashlib.sha256(label.encode("utf-8") + b"|" + seed).hexdigest()[:n]

def genesis() -> Context:
    seed = canonical_json({
        "canon": CANON_SHA256,
        "root": ROOT,
        "birth": PHOTON_BIRTH,
        "id": INFINITE_ID_LITERAL,
        "q": 0,
        "token": PHASE_SEQUENCE[0],
    })
    identity = INFINITE_ID_LITERAL + "#" + _derive("genesis-id", seed)
    v3 = V3(
        vector="vector:" + _derive("vector", seed),
        voxel="voxel:" + _derive("voxel", seed),
        vogel="vogel:" + _derive("vogel", seed),
        sg="[sg:" + _derive("sg", seed, 16) + "]",
    )
    lineage = sha256_bytes(b"GENESIS|" + seed)
    return Context(identity, 0, 0, PHASE_SEQUENCE[0], v3, "0"*64, lineage)

def advance(ctx: Context) -> Context:
    """Advance one cubit position without rewriting the current context."""
    nq = (ctx.q + 1) % len(PHASE_SEQUENCE)
    ntoken = PHASE_SEQUENCE[nq]

    # Same ID and v^3 inside one 12-position modulation cycle.
    if nq != 0:
        lineage = sha256_bytes(canonical_json({
            "canon": CANON_SHA256,
            "parent": ctx.seal(),
            "generation": ctx.generation,
            "q": nq,
            "token": ntoken,
            "identity": ctx.identity,
            "v3": asdict(ctx.v3),
        }))
        return Context(
            identity=ctx.identity,
            generation=ctx.generation,
            q=nq,
            token=ntoken,
            v3=ctx.v3,
            parent_seal=ctx.seal(),
            lineage_seal=lineage,
        )

    # q11 -> q0: deterministic unique child.
    # New ID => new v^3. Canon remains untouched.
    generation = ctx.generation + 1
    seed = canonical_json({
        "canon": CANON_SHA256,
        "parent_context_seal": ctx.seal(),
        "parent_identity": ctx.identity,
        "parent_v3": asdict(ctx.v3),
        "generation": generation,
        "wrap": "q11:a11->q0:a00",
        "photon_birth": PHOTON_BIRTH,
    })
    child_id = INFINITE_ID_LITERAL + "#" + _derive("child-id", seed)
    child_v3 = V3(
        vector="vector:" + _derive("vector", seed),
        voxel="voxel:" + _derive("voxel", seed),
        vogel="vogel:" + _derive("vogel", seed),
        sg="[sg:" + _derive("sg", seed, 16) + "]",
    )
    lineage = sha256_bytes(b"CHILD|" + seed)
    return Context(
        identity=child_id,
        generation=generation,
        q=0,
        token=PHASE_SEQUENCE[0],
        v3=child_v3,
        parent_seal=ctx.seal(),
        lineage_seal=lineage,
    )

def run_steps(steps: int):
    if steps < 0:
        raise ValueError("steps must be >= 0")
    ctx = genesis()
    out = [ctx]
    for _ in range(steps):
        ctx = advance(ctx)
        out.append(ctx)
    return out

def verify_invariants(states):
    if not states:
        return False
    for i, s in enumerate(states):
        if s.token != PHASE_SEQUENCE[s.q]:
            return False
        if i:
            p = states[i-1]
            if s.parent_seal != p.seal():
                return False
            if s.q == 0:
                if not (p.q == 11 and s.generation == p.generation + 1):
                    return False
                if s.identity == p.identity or s.v3 == p.v3:
                    return False
            else:
                if s.generation != p.generation:
                    return False
                if s.identity != p.identity or s.v3 != p.v3:
                    return False
    return True

def main():
    here = Path(__file__).resolve().parent
    load_and_verify_canon(here / "CANON.json")
    states = run_steps(24)
    assert verify_invariants(states)
    print(json.dumps({
        "status": "0e / FROZEN GENERATIVE KERNEL PASS",
        "version": VERSION,
        "canon_sha256": CANON_SHA256,
        "states": len(states),
        "generation": states[-1].generation,
        "q": states[-1].q,
        "token": states[-1].token,
        "identity": states[-1].identity,
        "v3": asdict(states[-1].v3),
        "lineage_seal": states[-1].lineage_seal,
    }, indent=2))

if __name__ == "__main__":
    main()
