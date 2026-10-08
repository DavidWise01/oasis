# AZ1 historical evolution benchmark — 2026-10-08
Original unmodified source: DavidWise01/az1@02cc70494a620538a35f6cbcb7a5a12f4dfcf612/index.html
Git blob 626d4bbd6245c88dedbba0b224b55bc83436e576
Engine evaluated from original inline JavaScript through a minimal fake DOM/localStorage with a seeded LCG replacing Math.random. No browser rendering or 3D scene tests. 900x540 viewport, 600 generations per seed.

| Seed | Generation | Final agents | Cap | Pooled births | Built ideas | Hybrid agents | Hybrid agents retaining full parents |
|---|---:|---:|---:|---:|---:|---:|---:|
| 7 | 600 | 130 | 130 | 58 | 16 | 58 | 0 |
| 42 | 600 | 130 | 130 | 60 | 14 | 60 | 0 |
| 12345 | 600 | 130 | 130 | 58 | 15 | 58 | 0 |
| 2026 | 600 | 130 | 130 | 56 | 9 | 56 | 0 |
| 98765 | 600 | 130 | 130 | 58 | 16 | 58 | 0 |

## Results
PASS: 5/5 runs completed; population never exceeded 130 in tested steps; coordinate values stayed in bounds; built list successfully persisted to stub storage; original code retains immediate parents for built objects.
OBSERVED LIMITATION: combine(a,b) produces parents:[a.name,b.name], but mkAgent(proto) creates new record omitting proto.parents, so all 56–60 hybrid agents in these runs lose direct ancestry fields while alive. Built objects record only immediate names, not a full immutable graph. This is a genuine implementation gap for append-only lineage audit; not a failure of geometry/simulation per se.
RANDOMNESS: original browser code uses Math.random, so reproducibility here is achieved only by injecting test RNG; seeded determinism not in original browser implementation.
This isolated JS test does NOT prove usability of complete interface or correctness of artistic/physical model.
## Next
Fork tests without altering frozen original; create separate provenance extension with parent IDs, birth tick, source repo identity, deterministic seed, append-only ledger, and receipt. Re-run five seeds; test resilience to name collisions.
