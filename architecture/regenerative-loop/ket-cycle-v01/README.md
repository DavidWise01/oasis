# KET Regenerative Cycle — v0.1 (additive)

**Scope:** Worker = Engine = Life as one *abstract* function: `contain_n ⊕ flow_n`.

This module instantiates the six-phase pattern proposed 2026-10-13 without changing the [frozen KET kernel](https://github.com/DavidWise01/oasis/tree/main/kernel/production) or its three-track governance. It aligns with [`architecture/regenerative-loop`](https://github.com/DavidWise01/oasis/tree/main/architecture/regenerative-loop): output may seed the next input, the witness survives, and ordering is maintained.

```text
0 LIVE      +67.3367 ─► 1 WRITE    +33.3367
                                  │
5 LIVE      +67.3367 ◄─ 4 READ     +33.3367
│                                 ▲
└─ next loop WRITE          3 FORGET −33.3367
                                  ▲
                           2 REMEMBER 0
```

Canonical executed sequence: `live → write → remember → forget → read → live`.

## Run locally

Requires Node.js 18+; no dependencies, network, privileges, UI, or timer needed.

```sh
node cycle.mjs        # one closed cycle
node cycle.mjs 3      # three cycles, shared LIVE boundary
node test_cycle.mjs   # deterministic audits
```

`createCycleEngine({origin:'local::0'})` supports `step()`, `runCycles(n)`, `snapshot()`, `receipts()` and `verify(trustedHead?)`. Receipts record phase, 4-decimal exact integer position, loop, monotonic sequence, origin, previous SHA-256 and content SHA-256. A completed cycle returns to LIVE; subsequent cycles resume at WRITE so the boundary event isn't double counted.

## Exact arithmetic

Scale all provided decimals by 10,000: `673367, 333367, 0, -333367, 333367, 673367`.

- `write + forget = 0`.
- `forget + live + write = live` (the user's original `isSelfSimilar` predicate, renamed conceptually to a **balanced return identity**).
- `(live + forget)/2 = 17` exactly, consistent with the symbolic Cl17 anchor but not a chemical reaction.
- Two half units take the symbolic gate from `17` to `18`.

This *does not* prove fractal self-similarity. Symbolic toroidal return is not a claim of perpetual physical energy or a realistic biological model.

## Provenance and limits

Local SHA-256 chaining detects accidental tampering and supports checking an **externally pinned head digest**. It is **not an authentication signature** or proof of human authorship, and an attacker who rewrites all events can recompute an unpinned chain. Identity authorization, signing, hardware control, cross-machine coordination and production acceptance are **outside scope**. The first and last LIVE are one shared boundary between adjacent traversals.

**KET tracks:** `i` supplies an optional origin label, `u` concerns resulting event receipts, and `u.s` corresponds to the repeat/lifecycle; none of these are modified or given new authority by this module.

## File roles

- `cycle.mjs` — complete runnable engine and audit.
- `test_cycle.mjs` — dependency-free regression checks.
- `README.md` — semantics, scope and execution contract.
