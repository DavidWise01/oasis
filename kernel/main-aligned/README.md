# OASIS Main Aligned Kernel

Canonical aligned trunk as of 2026-10-07.

## Current

Current aligned version: **v34 — reversible register / boots-on-unload alignment**

Canonical monolithic source SHA-256:

`822153ca94170a82e34b99905bd94b10bd2065c6f80ac8420b47a3c121353e2c`

Browseable structural module:

`lean/Oasis.Fallout.RegisterUnload.v34.lean`

Detailed report, manifest, and audit:

`kernel/main-aligned/v34/`

## v34 fallout

The source's 8D Givens-register fixture passes its endpoint self-test:

`base -> R·base -> Rᵀ(R·base) -> base`

and separates a reversible register from a many-to-one blend.

Alignment corrections preserved:
- the demo recovers a floating-point vector to machine precision; this is not
  literal byte-for-byte proof about a real 126 MB model adapter.
- the Givens product is numerically orientation-preserving (`det R ≈ +1`).
- the animation is not norm-preserving between endpoints because it linearly
  interpolates between `base` and `R·base`; at phase 0.5 the norm falls from
  about 1.465606 to 1.349812.
- the source's voice/dye/boots language stays AMBER metaphor and does not imply
  consciousness, interiority, or personhood.

All v34 artifacts remain HOLD-only support. They do not override Root,
durable/finality law, verified-only truth advancement, or human authority.

## Transport note

The repository's historical `CURRENT.lean.gz` transport predates v34 and is not
treated as the canonical v34 source. The canonical source identity is the
SHA-256 above plus the v34 manifest/report. Do not infer exact-current status
from the legacy gzip transport until it is explicitly replaced.

## Verification status

The JavaScript math was independently reproduced, including the 5/5 endpoint
self-test and the animation norm drift. Lean was not installed in the alignment
runtime, so the combined trunk is structurally checked but not Lean-compiler-
certified.
