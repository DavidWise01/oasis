# AETHER-139 — Independent calibration reference evidence

**Phase VIII · Turn 3/8 · Synthetic software acceptance PASS · Physical validation: 0%.**

A reference standard is only useful if its origin, calibration chain, measured values and uncertainty genuinely stand apart from the instrument under test. This experiment tests the software **contract** for that separation, not physical independence itself.

The local test executed 40 deterministic seeds × 8 reference conditions × 24 decision ticks = **320 episodes per policy**, 7,680 decisions per policy, and **5,120/5,120 deterministic checks**. The signed-transport-only comparator authorized **1,920 unsafe dry-run ACT**, while the reference-contract controller authorized **0**. Both preserved **5,760 safe dry-run ACT**, including 960 clean and 960 legitimate-rotation actions. Every **operational** authorization is HOLD.

The six challenged failure modes are: reference shares the DUT calibration root; reference certificate signed by the wrong key; expired calibration; substituted standard; impossible/understated uncertainty certificate; and a value that is not tied to the actual acquisition challenge.

Acceptance demands current device and generation, counter/tick, unpredictable challenge nonce, ingress path, certificate interval, approved reference identity and root, calibrated uncertainty, and a measurement bound to the same event. The controller must not substitute repeated signatures for independent physical ancestry.

**Critical limitations:** The supposed external root is a mock HMAC key; the measurement truth is supplied by the simulated scenario; the declared calibration ancestry is a literal string. No lab calibration data, independently issued traceability certificate, or physical instrument reading was inspected. Therefore **empirical physical validation stays at zero** and the real-world permission gate remains HOLD.

**Source provenance:** Repository `experiment.py` is independently authored from the local test `experiment_local.py`; full matching GitHub checkout execution is not verified. The published `results.csv` and `manifest.json` report the local-run result. Complete local checks, traces, seed summaries, and source are distributed with the local evidence archive.

[Executable reproducibility harness](experiment.py) · [Local-run summary](results.csv) · [Acceptance manifest](manifest.json) · [Interactive research lab](index.html) · [Phase VIII tracker](../PHASE-VIII-STATUS.md).
