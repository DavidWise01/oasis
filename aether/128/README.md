# AETHER-128 — Phase VI bounded integration and evidence freeze

**Local synthetic integration PASS:** 25 new seeds × 8 conditions = 200 cases, 6,400 decisions, **1,600 / 1,600 acceptance checks**, **0 unsafe ACT** and 2,870 legitimate safe ACT decisions. The complete program's eight accepted turn gates and five failed versions were found in the local evidence inventory.

The final test imported the accepted AETHER-127C single-controller logic without modifying its ACT/HOLD policy, and independently checked replay, append-only hash chains, exactly one action per tick, authenticated current packets, coverage before ACT, frozen source fingerprints, and bounded microprobe purchase.

**Archived failed versions (must not be erased):** AETHER-123 identity-margin regression; AETHER-124 wrong uncertainty inequality; AETHER-125 invalid recovery definition; AETHER-127 nonlinear sensor blind spot; AETHER-127B uncovered random calibration gaps.

The source hashes in `archive_inventory.csv` are **local test copies**. Their byte identity to each path on GitHub is **not yet verified**, and the published repository-compatible harness is a separate authored version. `results.csv` and `manifest.json` preserve the completed local-run output; they are **not** represented as new CI logs or verified remote-checkout replay.

**Critical limits:** The sensor's response to test stimuli is supplied by a trusted synthetic oracle. The hidden same-path probe assumption and a bound on response variation between probe inputs cannot be established from these finite software experiments. Therefore this is an experimental acceptance freeze, not a physical security proof or general solution to selectively dishonest sensors. The original 127C requirement for 88 microprobes per tick makes calibration expensive. Pointwise risk bounds are not a familywise multi-tick guarantee.

**Closure accounting:** eight accepted bounds 121, 122, 123B, 124B, 125B, 126, 127C and 128, = **Phase VI 8/8 = 100%** on its declared constrained synthetic acceptance program. The next phase starts at its own zero baseline. No quorum/Byzantine distributed trust was introduced.

[Local-run results](results.csv) · [Manifest](manifest.json) · [Local-source inventory](archive_inventory.csv) · [Executable repository harness](experiment.py) · [Interactive lab](index.html).
