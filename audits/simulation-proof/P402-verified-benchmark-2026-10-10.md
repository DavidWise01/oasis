# P4.02 verified benchmark — 2026-10-10

Executed Node.js regression from P4.02 conversation artifact on 2026-10-10. **PASS: 44,634 assertions**.

| Statistic | Value |
|---|---:|
| Clock cycles | 121 |
| Total layer views | 24,200 |
| Accepted | 20,181 |
| Quarantined | 3,942 |
| Simulated missed deadlines | 77 |
| Max injected residual | 0.30 ms |
| Acceptance tolerance | ±0.25 ms |
| Latest measured run | 234.114 ms |

100-layer OSI mapping repeated over 200 layers and one 200ms logical cycle. Signed calibration uses HMAC-SHA256 with a test-owned key. The exact timestamp register uses BigInt at 10^-36 second symbolic precision. The canonical blockade remains `{-{+{%}+}-}`.

**Security limitations:** This is simulated calibration with known true offsets and injected errors, not empirical independent-clock metrology. Late events are injected classifications, not measured real-time scheduler misses. HMAC cannot defend against a stolen key, and retained reference-state durability is not implemented. The reference kernel imports `p399_exact_time.mjs` and `p401_drift.mjs`, which must be provided in the same directory before executing.

Source and independent benchmark evidence are checked in separately to avoid claiming more than was tested.
