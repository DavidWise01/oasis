# AETHER-098 — Deterministic Diodic Decision Path

**Phase II · Turn 3 of 8 — Accepted in synthetic tests; 37.5% complete.**

## Invariant 098

The controller's decision at tick *t* depends exclusively on evidence acquired no later than *t*. Later evidence may change later decisions, but **cannot rewrite previous actions, certificates or reasons**.

## Executed test design

The canonical Python source was executed on **80 seeds × 3 environments × 96 ticks = 23,040 ticks**. Environments were repeated switches, decoy switches and stationary safety. Every tick has 140 independently simulated audit measurements and 150 independently simulated held-out action outcomes. The controller may purchase another 80 sentinel measurements depending on the context and risk bound.

One deterministic governing rule updates context (burst signal, contradiction-based revocation), computes the **one-sided 95% fixed-time Clopper–Pearson binomial upper bound** over the five most recent audit batches, and issues exactly one action:

- **HOLD** if the current risk bound exceeds 2% or a purchased sentinel alarms.
- **ACT** otherwise.

Evidence is serialized canonically to JSON. Each decision record is linked using SHA-256 of the previous record hash plus the current decision. The generated audit has immutable prior hash, current decision and resulting hash.

## Tests and results

| Test | Passes |
|---|---:|
| Full deterministic replay | 240 / 240 |
| Future-data perturbation leaves tick-0–47 prefix unchanged | 240 / 240 |
| Hash-chain recomputation | 240 / 240 |
| Unsampled sentinel changes cannot influence actions or record hashes | 240 / 240 |

| Scenario | ACT ticks | HOLD ticks | Wrong authorized outcomes | Context revocations | Cost |
|---|---:|---:|---:|---:|---:|
| Switch | 3,757 | 3,923 | 1,814 | 239 | 58,493.7 |
| Decoy | 4,219 | 3,461 | 2,612 | 145 | 62,949.5 |
| Stable safe | 7,568 | 112 | 3,360 | 0 | 45,192.0 |
| **All** | **15,544** | **7,496** | **7,786** | **384** | **166,635.2** |

Cost = 10 per wrong authorized outcome + 0.05 per withheld action + 0.01 per evidence label. Values are illustrative.

The first local implementation used a too-conservative Hoeffding bound that led to **zero authorized ticks**. It was corrected to the fixed-time Clopper–Pearson bound *before* the accepted run. This failed diagnostic is recorded here as a limitation of choosing excessively restrictive confidence gates.

## Reproduction

Requires Python and SciPy:

```bash
python aether/098/experiment.py
```

Regenerates `seed_results.csv`, `results.csv`, `trace_samples.csv` (one complete example trace per environment), and `manifest.json`. Save the generated output and compare the hash chain with the source.

## Scope and limitations

- Synthetic independent Bernoulli measurements; no field or production certification.
- A fixed-time confidence bound describes historical audit samples; it does **not** guarantee the actual current risk immediately after drift.
- The hash chain demonstrates internal tamper evidence, not external trusted storage, independent custodians, or future immutability guarantees.
- No distributed authority or quorum is required in Phase II. One controller chooses ACT or HOLD with a deterministic order.
- Acceptance concerns **causal determinism and directionality**, not economic optimality or zero wrong actions.

[GitHub Pages report](https://davidwise01.github.io/oasis/aether/098/) · [Phase status](../PHASE-II-STATUS.md) · [Previous bound](../097/)

## Next natural bound — AETHER-099: Revocation Latency

Now measure the delay between changing circumstances and revocation of decision authority, not just context classification, under fast transitions and delayed evidence. Report unsafe authorized ticks, avoidable error cost, interruption cost and the earliest observable alarm.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
