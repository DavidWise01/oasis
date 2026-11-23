# AETHER-116 — Clock Rollback, Drift and Expiry Ambiguity

**Phase V Turn 4 of 8: ACCEPTED · 50%.** Standalone reproducible synthetic evaluation.

## Decision invariant

**Uncertain wall-clock time cannot extend an evidence credential.** A one-way verifier checks HMAC-signed credential schedules, independently signed time anchors, local monotonic inspection counts, a conservative drift margin and the evidence packet signature before selecting ACT or HOLD. Untrusted measurements and expired leases fail closed. The controller never receives the simulator's true risk or true time for action selection.

## Frozen test

- 60 independent evaluation seeds, 116001–116060, for each of six scenarios (360 episodes, 32 ticks each).
- Paired comparator trusts local wall-clock time for schedule expiry. Revised verifier uses an authenticated anchor and monotonic counter.
- Six scenarios: clean rotation; backward clock jump; forward clock jump; slow drift; ambiguous expiry boundary; authenticated-anchor outage.
- Four deterministic checks per policy-case: replay equality, recomputed SHA-256 hash chain, exactly one action, no action without accepted evidence.
- One-sided binomial upper risk bound; 560 synthetic observations/tick; 2.5% admissibility limit. Cost units are illustrative.

## Independent evaluation

| Scenario | Unsafe wall-clock authorizations | Unsafe monotonic authorizations |
|---|---:|---:|
| Clean rotation | 0 | 0 |
| Backward jump | 420 | **0** |
| Forward jump | 0 | 0 |
| Slow drift | 240 | **0** |
| Expiry boundary | 180 | **0** |
| Anchor outage | 360 | **0** |
| **TOTAL** | **1,200** | **0** |

Both policies preserved **1,499** safe ACT decisions during clean key rotation. Under forward clock jumps, the monotonic verifier preserved 1,500 safe ACT decisions versus 660 in the wall-clock comparator.

**Total cost:** wall-clock 766,774.4 versus monotonic 288,982.4, saving 477,792 synthetic cost units. These figures are strongly conditioned on the specific modeled misuse and penalty structure, and are not a measured field benefit.

## Acceptance criteria

1. Full deterministic replay/record-integrity/fail-closed test suite — **PASS (2,880/2,880)**.
2. No unsafe monotonic authorization — **PASS**.
3. Fewer unsafe authorizations than wall-clock comparator — **PASS**.
4. Preserve clean-rotation safe actions — **PASS**.
5. No higher total modeled cost — **PASS**.

## Reproduction

`python aether/116/experiment.py` requires NumPy and SciPy. It generates `results.csv`, `seed_results.csv`, `checks.csv`, `trace_samples.csv`, and `manifest.json`.

**Bounded claim:** the simulated verifier requires an uncompromised time-anchor signing authority, an unrollbackable monotonic counter and a correct worst-case clock drift bound. If any of those assumptions fail, the security conclusion does not follow. Synthetic HMAC keys are testing fixtures, not deployable secrets.

Next: **AETHER-117 — Authenticated Time-Anchor Freshness and Counter Continuity.** Test whether a temporarily stale authenticated time anchor or reset monotonic counter can be recognized without presuming an unavailable trusted wall clock.

[Phase V tracker](../PHASE-V-STATUS.md) · [Interactive GitHub Pages-ready lab](https://davidwise01.github.io/oasis/aether/116/)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
