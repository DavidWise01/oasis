# Z337 — Tritriseptium (Tts): release candidate, not production freeze

**Source snapshot commit:** `7afe006ea81adc2952c682d176d949c29b39c5f2`

Classification: symbolic MN PRIME / OCTAVIA computational research, not a confirmed physical Z337 element.

## Scope

Six executable modules Z328–Z333 are accessible in OASIS as of this snapshot. The consolidated `run_recovery_suite.py` includes exact pinned Git blob SHA-1 identities for all six and aborts before executing a mismatched test. Its test runner reports a successful run only if each module exits zero and its stated passing-check count matches the pinned expectation (20+20+20+20+15+20=115).

## Evidence and limitations

- Earlier local six-suite regression: 115/115 checks passed.
- Z329 and Z330, recovered from the local archive, match committed GitHub blobs byte-for-byte; each passed 20/20 locally.
- Z328, Z331, Z332 and Z333 fetched GitHub sources are verified accessible. Four preexisting local files are **not** exact byte matches for those four GitHub blobs; their prior passing local test results are not a clean-checkout proof.
- GitHub runner `run_recovery_suite.py` committed and then fetched at revision above (blob `e3a785c17e57f1873ea195b1424f582951556187`).
- This environment cannot clone github.com directly; **no fresh GitHub checkout and no CI execution of the committed runner were performed**. Therefore repository-sourced 115/115 is still a pending acceptance check.
- The pinned commit SHA is a stable *reference* but **no release tag, protected branch, external witness, or cryptographic release attestation** has been created.

Run from clean checkout:
```bash
python -m pip install cryptography
python research/mn-prime/experimental-cipher/z337/run_recovery_suite.py
```

Acceptance: expect `PASS Z337 115/115 verified checks` and exit 0. This is research-software regression, not a production security certification. Frozen KET, independent `5/3/1`, RGB `3/1/2`, and optional Chromium-24 analogy unchanged.

Next target: Z338 only if clean-checkout test passes; otherwise debug the exact failing source/test without expanding the model.
