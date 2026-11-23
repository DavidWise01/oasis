# AETHER-141 — Empirical same-path insertion readiness

**Local synthetic PASS**, Phase VIII software readiness 5/8 = **62.5%**, empirical physical validation **0%**.

The local executed `experiment.py` tested 40 new seeds × eight acquisition scenarios × 24 ticks, 320 episodes per policy and 7,680 decisions per policy. **5,120/5,120 deterministic checks passed.** Signed-only software permitted **1,920 unsafe dry-run ACT**, while the ingress-bound policy permitted **0 unsafe dry-run ACT**. Both retained **5,760 safe dry-run ACT**, including **960/960 clean** and **960/960 valid rotation**. All operational decisions remained HOLD.

The challenged failure modes were split probe/measurement routes, probe bypass, replayed counters, substituted receipt issuer, mismatched session and implausible acquisition latency. An accepted receipt must bind instrument, generation, current tick, monotone counter, unique nonce, actual probe and measurement route, calibration session, latency window and independently established acquisition issuer.

**Essential limitation:** The so-called ingress issuer is a software HMAC fixture, not an instrument. The test itself knows the true route. An independent laboratory and physical path attestation would be required to turn this readiness test into actual acquisition assurance. A signed route assertion is not evidence that physical signals followed the route. No physical sensor was tested, and operational ACT count is **zero**.

**Source integrity:** Local executed SHA-256 `f851e4a1cea68e3def327ce52e55420c06f7ff705ffe9dc442407ab6ac1c70b0`. The published repository-compatible Python reproducer is a separately authored implementation and has not been verified against an independent GitHub checkout. The summarized `results.csv` and `manifest.json` describe the local test; full executed script, checks and traces are in the downloadable ZIP.

[Python script](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Interactive laboratory](index.html) · [Phase tracker](../PHASE-VIII-STATUS.md).
