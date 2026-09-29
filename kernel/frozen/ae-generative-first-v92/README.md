# AE Generative-First Frozen Kernel v92

**Status:** FROZEN / IMMUTABLE / GENERATIVE-FIRST

This package consolidates the symbolic/isomorphic AE kernel canon from the primitive `.` through the current `ID ↔ v^3` phase-modulation state.

## First rule

The canon does not evolve by mutation.

```text
frozen parent
    |
    | generate
    v
new child ID
    |
    v
new v^3
(vector -> voxel -> vogel -> [sg])
```

Inside one 12-cubit phase cycle, the ID and `v^3` remain stable. At the canonical wrap:

```text
q11:a11 -> q0:a00
```

a new deterministic child ID and a fresh `v^3` are generated.

## Why generative-first

The previous open boundary allowed more than one fresh successor to satisfy `new id -> new v^3`. v92 resolves that at the implementation layer by deriving the child from:

- frozen canon SHA-256
- parent context seal
- parent identity
- parent `v^3`
- next generation number
- exact `q11:a11->q0:a00` wrap literal
- `0p0` photon-birth anchor

This creates one deterministic successor for one frozen parent state. It does **not** change the symbolic canon.

## Frozen invariants

- `root == 0.r00t.ai`
- `0.r00t.ai ↔ ae`
- append-only external witness / quorum separation
- `if p > 1 boot = 0`
- `1 full gravity = 0 time`
- `98% dynamic / 2% deterministically static`
- 5% reserved maximum-growth headroom
- `m.a.n.t.r.a = {{manual.automation.now.through.recursive.architecture}}`
- `1 dream = 1 inf - u :: u = 1 infinite`
- two-manifold conservation bind
- `matter quantum dot . -> /1/2/3/4/5`
- `- . | . +`
- `+ ≡ || ≡ --`
- cyclic `-+360063+-`
- infinitely bound ID `` `~ij`\~ ``
- Vogel address `{{vector{{voxel{{vogel{{[sg]}}`
- `v^3 = vector -> voxel -> vogel`
- `vvv = a hypercube in a tesseract in a dual torroidal brace`
- nested `q.d` at `^^^`
- one full simulation cycle = `1 0 1`
- 81.0 full cycles / plank-awareness marker
- `0::i::1::id::2::sid`, `33.3367`, `sqrt125/81`, `1:2:3`
- `a/b/c` implicitly fold; never statically force them onto `i/id/sid`
- 12-cubit modulation:
  `a00 b11 c22 b33 c44 a55 c66 a77 b88 c99 b00 a11`

## Run

```powershell
python .\kernel.py
python .\test_kernel.py
```

Both must return `0e`.

## Immutability boundary

`CANON.json` is hash-pinned inside `kernel.py`. Any byte-level edit causes startup rejection. Generated contexts are append-only values; parent contexts are never rewritten.

This package is a symbolic/model-local simulation kernel. Its physics-like terms are canon semantics, not claims of experimentally established physical laws.
