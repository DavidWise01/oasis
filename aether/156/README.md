# AETHER-156 — Calibration ancestry and uncertainty-budget intake

**Phase X Turn 4/8 · Synthetic software setup readiness 50% · physical qualification 0%.**

The exact local experiment executed **25 seeds × eight scenarios × 20 ticks = 200 episodes per policy and 4,000 decisions per policy**, passing **3,200/3,200** deterministic replay, hash chain, sequencing, modeled safety, and operational HOLD checks. A signed-only comparator made **1,200 unsafe dry-run ACT**; a conservative uncertainty-gated controller made **zero**, while preserving **2,800 safe dry-run ACT** (500 clean and 500 valid reference rotation).

The modeled four-part standard uncertainty budget includes calibration (.0010), repeatability (.0005), resolution (.0004) and drift (.0006). Combined standard uncertainty is `sqrt(sum(u_i^2))` and the expansion factor is `k=2`. The test requires 120 synthetic held-out observations with a one-sided 90% Wilson lower bound at or above a 95% coverage target. These constants are **synthetic protocol settings**, not physical reference accuracy findings.

Six fault conditions fail closed: omitted drift contributor, shared calibration root, understated resolution contribution, expired calibration, unsupported held-out coverage, and a false reference reading contradicted by a modeled bench.

**Physical evidence is absent:** No real reference certificate, issuer accreditation, calibration genealogy, uncertainty budget or captured physical measurements has been authenticated. The [physical uncertainty register](physical_uncertainty_register.json) contains nulls rather than fictional measurements. **All actual operational actions remain HOLD.**

Local fully executed Python SHA-256: `05a2bd83fa637c3030fc284384f92c406e99f66db3bcefe96139ee7d3a400db8`. GitHub's `experiment.py` is separately authored and shorter; matching checkout execution and live Pages deployment are unverified. Full source, test checks, seed cases and SHA-256-chained traces are in the accompanying ZIP.

[Python demonstration](experiment.py) · [Local results](results.csv) · [Manifest](manifest.json) · [Blank physical register](physical_uncertainty_register.json) · [Interactive laboratory](index.html) · [Phase X tracker](../PHASE-X-STATUS.md).
