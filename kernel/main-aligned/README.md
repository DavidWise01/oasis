# OASIS Main Aligned Kernel

Canonical aligned trunk as of 2026-10-07.

## Current

Current aligned version: **v31 — corpus A→Z→A round-trip alignment**

Current monolithic source SHA-256:

`4404fcedb9b2448f9ae9f8dd8ecc139bf3c4290abe1d3ac447c953b228f1f888`

Browseable v31 structural module:

`lean/Oasis.Fallout.CorpusRoundTrip.v31.lean`

Detailed report and manifest:

`kernel/main-aligned/v31/`

## v31 fallout

The uploaded corpus page embeds a deterministic 859-repository snapshot, sorted case-insensitively from `0root-provenance` to `zoolander`.

The exact structural result is the constructed round trip:

`roundTrip(xs) = xs ++ reverse(xs)`

which is palindromic by construction. This does not imply that the forward corpus list is itself a palindrome.

The page's "live" network request updates only the public repository count; repository names remain the embedded snapshot.

The nested lens renderer is recursive but anisotropic: x scale = 0.32 and y scale = 0.34, so it is not exact Euclidean self-similarity.

Interpretive claims such as "every part reseeds the whole" remain quarantined until an executable reconstruction rule demonstrates them.

All v31 structures remain HOLD-only and do not override Root, durable/finality rules, verified-only truth advancement, or human-gated authority.

## Verification status

Snapshot ordering, uniqueness, round-trip palindrome, traversal return, and nesting anisotropy were executed in the alignment runtime. Lean was not installed, so the combined trunk is structurally checked but not Lean-compiler-certified.
