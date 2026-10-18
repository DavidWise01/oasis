# Z323 — Tribitrium (Tbt): lossless symbolic RGB marker round-trip

Classification: Layer 1 / MN PRIME / OCTAVIA experimental cipher. No physical electron-orbital or chemical-element claims.

## Frozen inputs
Tun reference RGB occupancy=(3,1,2), six markers. Cr24 optional overlay offers R/G/B × 8 indexed addresses = 24 possible address positions. KET governance (5,3,1) and independent structural motif (1,2,1) are not altered.

## Deterministic codec
Encode each RGB occupancy tuple by allocating slots 0..n-1 within each named lane (R,G,B), canonical order R then G then B. Decoder requires unique, valid and contiguous canonical addresses. Rotation is (R,G,B)->(B,R,G); mirror is (R,G,B)->(B,G,R). There are exactly six unique permutations.

## Evidence
Executed local Python `test_z323.py`: **15/15 PASS**, including all six round trips, conserved totals, reversible rotation/mirror, unique addresses and malformed input rejection. These are software invariants, not tests of electrons or physics.

## Scope
Optional Cr24 address overlay only; no mutations to the frozen KET baseline. No unverified name-to-axis decoding assigned. The executable test is committed alongside this document.
