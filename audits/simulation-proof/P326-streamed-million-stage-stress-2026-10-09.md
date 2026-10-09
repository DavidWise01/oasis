# ROOT0 P3.26 — million-stage streamed gate stress (2026-10-09)

**Result:** PASS on 136 randomized trials over seven even/odd arm pairs in both orientations, with longest sequence 1,000,001 stages. Maximum energy norm discrepancy 4.82049955508046e-11, maximum complex-component inverse discrepancy 1.832600737827761e-11, all within configured 1e-8 absolute error tolerance. Node v22.16.0 process RSS at completion 39.42 MiB; RSS includes runtime overhead and is not a direct allocation measurement. Forward and backward gates are regenerated from index, not saved as a gate array. Executed locally: `/mnt/data/p326/test_p326.mjs`; JSON results `/mnt/data/p326/results.json`.

Repo files `p326_stream.mjs` and `test_p326.mjs` implement the same streaming equations. The standalone executed local file has slightly different source formatting, and the committed test runs equivalent cases but calculates branch counts more extensively. GitHub CI and execution of the exact committed file are not verified.

**Gate convention:** index k selects alternating arms while both have stages remaining, then the longer side; phase and rotation depend deterministically on k. Inverse traverses decreasing k with conjugate-transposed transformations. The root is a fixed reference, not a sink; mixing parameters are test conventions, not experimentally measured physics.

**Limit:** Increasing traversal count accumulates roundoff; testing to a million stages is not an unbounded guarantee. The next target is to compare run time, error and performance of cached vs streamed gates across powers of ten and introduce checkpointed inverse audit for larger traversals.
