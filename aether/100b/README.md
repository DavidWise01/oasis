# AETHER-100B — Conditional Fresh-Certificate Recovery

**Phase II, Turn 5 of 8: ACCEPTED in the synthetic holdout; 62.5% complete.**

## Invariant

A permission revoked after a hazard cannot be restored using pre-revocation evidence. New observations must earn a new certificate. Repeated alarms during the **same suspended episode** do not discard already collected fresh audit measurements, but **a new alert after recovery revokes the permission again**.

## Architecture and operational rule

One controller observes current audit error count and sensor signal, updates its revocation state, and emits one ACT or HOLD decision. A high proxy (≥2.5) accompanied by ≥3 audit errors revokes the current certificate. A newly suspended controller collects **post-revocation** audit batches.

The selected candidate **fresh2** releases suspension only when two most recent 140-label post-revocation batches satisfy the one-sided fixed-time 95% Clopper–Pearson upper bound ≤2%, the latest signal is quiet, and the current tick is not alarming. Its fresh certificate remains active until the normal five-batch rolling risk gate catches up or a new alarm revokes it.

The repeated-alarm change is important: unlike the failed AETHER-100 implementation, additional warning signals within one continuous suspension do not reset fresh evidence.

## Independent selection and evaluation

The development set comprises **40 seeds, 100301–100340**, each in abrupt hazard/recovery, repeated hazards, and a misleading sensor scenario. Policies tested: stale-history recovery, fresh2, fresh2 with extra quiet restriction, and fresh3.

Candidates were selected before holdout on no greater unsafe authorizations, ≤5% additional safe holds, no greater cost, and no greater average recovery delay than stale-history. Among eligible candidates, minimize cost then select by stable name.

Fresh2 was selected on development results. It was then evaluated once on **80 unseen seeds, 100501–100580**, across the same three scenario families, 100 ticks per seed. True hazard intervals are hidden from the controller and used only for scoring.

## Holdout summary: 240 cases per policy

| Metric | Stale baseline | Selected fresh2 |
|---|---:|---:|
| Unsafe authorized inspections | 12 | **12** |
| Safe inspections withheld | 1,354 | **739** |
| Mean recovery delay (ticks) | 3.041 | **1.106** |
| Authorized inspection ticks | 17,618 | **18,233** |
| ACT/HOLD transitions | 758 | 760 |
| Incorrect authorized action outcomes | **8,078** | 8,352 |
| Illustrative total cost | 167,045.0 | **165,172.5** |

Fresh2 reduced safe holds by 615, shortened average recovery delay by 1.935 inspections (approximately 63.6%), and saved **1,872.5 units** under the declared cost schedule. No additional truly unsafe authorized inspection was observed. But it authorized more actions and produced **274 additional incorrect action outcomes** overall. Do not describe this as improved per-action reliability.

Cost = 10 per wrong authorized outcome + 0.05 per withheld action + 0.01 per audit label + 0.2 per observed sensor per tick.

### Acceptance outcome

All four prespecified gates passed on unseen holdout seeds: unsafe auth no higher, safe holds ≤1.05× baseline, total cost no higher, and average recovery delay no longer.

**The synthetic Turn 5 acceptance is PASS.** This does **not** imply a mathematical risk guarantee under unknown nonstationarity, nor a production deployment.

## Reproduce

```bash
python aether/100b/experiment.py
```

Requires NumPy and SciPy. Outputs `development_options.csv`, `seed_results.csv`, `trace_samples.csv`, `results.csv`, and `manifest.json`. The prior failed AETHER-100 is unchanged.

## Limits / next bound

The risk upper bound applies to the recent samples, not instantaneous future risk; a good-looking fresh certificate can still become stale after an unobserved shift. Both policies share simulator-generated independent evidence roots, and the cost coefficients are illustrative.

**Next: AETHER-101 — Deterministic Best-Admissible Action Selection.** Given risk, evidence quality and costs, define one total order over admissible actions with HOLD as the safe fallback. Test stability, constraint precedence, deterministic ties, and pathological costs without creating voting or distributed consensus.

[Interactive GitHub Pages-ready lab](https://davidwise01.github.io/oasis/aether/100b/) · [Phase tracker](../PHASE-II-STATUS.md) · [Failed 100](../100/)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
