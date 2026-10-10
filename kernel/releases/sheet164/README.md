# SHEET 164 — Factorial Merkle Recovery Tuning

**Status:** 68/68 new checks PASS, exit 0. **Inherited SHEET 163:** 45/45 PASS in an isolated copy, exit 0. Full historical nested runner not executed.

This additive build preserves the complete SHEET 163 release under `baseline163/` and introduces a performance-tuning experiment without weakening Merkle or mTLS verification.

## Components

- `transport164.js`: optional TLS connection reuse, pinned certificate verification in both modes.
- `pipeline164.js`: signed quorum recovery with fetch window 1–4, ordered cursor writes and bounded physical segment batches.
- `gate164.js`: randomized 2×2×2 factorial, measured A/B, source-root assertions, TLS connection assertions, segment rollover holdout, real process-kill recovery.
- `benchmark164.json`, `BENCHMARK-REPORT.md`: raw measurements, policy scoring, factor means, caveats.
- `KERNEL-ASCII.txt`: full kernel pipeline, recovery branches, and verification boundaries.
- `index.html`: interactive measured-condition viewer.

## Run

```bash
node gate164.js
python make_docs164.py
python browser-check164.py
bash run-inherited163.sh
```

Tests require Node.js 22, OpenSSL, POSIX fsync/rename, and loopback networking. One physical host only. Full ancestor regressions remain unrerun. See benchmark report for experimental limitations.