# SHEET 163 — Parallel Merkle Recovery

Bounded parallel signed Merkle page fetches, strictly ordered durable commits, adaptive 256-record segment boundaries, and replay-safe recovery after lost acknowledgements.

- New checks: 45/45 PASS; inherited SHEET 162 unit checks: 19/19 PASS; network checks: 24/24 PASS.
- Chromium dashboard: 11/11 PASS.
- Matched 400-record A/B test, fixed eight-record commits on both sides: 159.62 → 298.71 records/s (1.871×) and, under 14 ms synthetic page delays, 177.57 → 329.52 records/s (1.856×).
- Published predecessor SHEET 162 ZIP preserved byte-for-byte (729 files).
- Complete historical regression suite not rerun, cross-host safety unverified.

Run new tests with `node gate163.js`. Full frozen dependency tree is in the attached ZIP; this GitHub directory contains the new code only.
