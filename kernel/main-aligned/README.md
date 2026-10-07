# OASIS Main Aligned Kernel

Canonical aligned trunk as of 2026-10-07.

## Current

Current monolithic source SHA-256:

`846ff2bd464139506fdc0db1f16f1392d14e22eaf6d7e27c144008732082ab69`

The exact v25 source is stored in this directory as:

`v25/OASIS_Main_Kernel_FalloutAligned_v25_2026-10-07.lean.gz`

Recover it with:

```sh
gzip -dc v25/OASIS_Main_Kernel_FalloutAligned_v25_2026-10-07.lean.gz > CURRENT.lean
sha256sum CURRENT.lean
```

Expected SHA-256:

`846ff2bd464139506fdc0db1f16f1392d14e22eaf6d7e27c144008732082ab69`

A small browsable standalone statement of the new v25 structural fallout is also committed under:

`lean/Oasis.Fallout.AtomicAddress.v25.lean`

## v25 fallout

The v24 atomic/address family yields a backend-neutral structural result:

- LAPORTE-DUST depth 8: `7^8 = 5,764,801`
- Atom Instrument 7x7 pair-address depth 4: `49^4 = 5,764,801`
- exhaustive address pairing/unpairing test: 5,764,801 cases, 0 failures
- active bands nest strictly: `{4..8} ⊂ {3..8} ⊂ {2..8}`
- per-level 2D branch counts: `25 < 36 < 49`
- quadrant mirror `ul<->lr`, `ur<->ll` is involutive
- source/runtime discrepancies remain review evidence, not silently corrected truth
- append-only witness integrity remains distinct from durable authority

No physical equivalence is inferred from the finite address equality.

## Authority boundary

Historical fixtures may contribute laws, state machines, data formats, tests, provenance, and witnesses. They do not silently override the current Root, durable/finality rules, verified-only truth advancement, or human-gated HOLD/resume controls.

## Verification status

The extracted runtime/arithmetic/hash tests recorded in the report were executed. The active runtime used for this fold does not have the Lean executable installed, so the combined Lean trunk is structurally checked but not Lean-compiler-certified in this run.
