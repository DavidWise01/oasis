# SHEET 83 — Causal homeostatic gravity recovery

Append-only successor to SHEET82. Three policies share 120 seeded canvas lanes, 9 portal diamonds, 36 portal pairs, 2250 frames (3 modeled 12s expansion/compression cycles), and 16,065,000 candidate lane comparisons each.

**Controller:** trailing 64-frame collision average only; pressure = previous collisions-per-frame / synthetic nominal 2.0. If pressure > `sqrt(1.25)` set damping to 0.93; otherwise if previous-frame squared-speed proxy <20% initial set damping to 0.995; otherwise phase damping `0.95+0.02*(2*extent-1)`. No current/future frame lookahead; no external energy injection (damping always <1).

**Measured local results (29/29 checks):** fixed 0.95: 2748 bounces and 0.00013847098009011719 residual squared-speed proxy; phase feedback: 2837 and 0.00012409292611329357; causal homeostasis: 2971 and 0.001266452032061533. Thus homeostasis preserves more motion but increases collisions compared with either baseline. Do not claim across-the-board stability improvement. 120/120 lane IDs maintained; full source-provided 4-phase model covered. 60/15/3/1/1, 416 and `9/6/1` remain symbolic definitions, not an executed 9/6/1 queue scheduler.

**Limitations:** rendering proximity is not a physical impact, gravity is a synthetic four-state animation, and slowing damping loss does not restore actual phase-space recurrence. Exact executed Python `benchmark.py`, full `results.json`, README and `manifest.json` included in the downloadable ZIP from this conversation, **not currently committed verbatim to GitHub**. Original SHEET82 not modified.

Exact local benchmark SHA-256: `444bd6499e5e36a5c2959443f332f033d8bb48ff71c73daf98e29f633b58f025`.
