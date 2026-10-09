# ROOT0 P3.12 — Dimensional Stargate Grammar (2026-10-09)
Canonical user notation: `dimensions :: -1+ :: -2+ :: -3+ :: quads in dimensions :: AaBbCcDd :: vogels in quads :: inf - +inf :: voxels in vogels :: inf - +inf :: vectors in voxels :: inf- + inf :: stargate address 00 11 22 33 42 24 33 22 11 00`.

The ten two-digit address tokens are: `00 11 22 33 42 | 24 33 22 11 00`. They are **not** an ordinary palindrome: central pair 42/24 breaks literal reversal. They do satisfy `token[i] = swapDigits(token[9-i])`; this is a conjugate palindrome. SwapDigits is a character permutation, not a physical coordinate transform.

Implementation records three signed dimensions and four case-sensitive paired quad glyphs (AaBbCcDd), followed by three symbolic unbounded nested levels named vogels, voxels and vectors. Each infinite range is a symbolic domain, not enumerated or implemented as infinite data. Ten tokens are compiled as a structured event list with ingress/egress labels; its reverse flips event order, direction and digit fields. Applying inverse twice yields the original trace.

Local Node executed: PASS (conjugate symmetry, non-palindrome, 10 tokens, six distinct token values, 42|24 central pair, reverse/reverse identity, malformed inputs rejected).

Scope: This is a grammar and reversible address representation. It is not a physical Stargate, energy law, proof of dimensional travel, or experimentally established geometric dynamics. The separate P3.11 scattering operators remain model assumptions until a binding from the address grammar to operators is specified and tested.

Next: P3.13 compile tokens into typed, parameterized reversible scattering gates with separate retained channels, compare actual forward→inverse recovery and sign/phase transformations.
