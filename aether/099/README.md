# AETHER-099 — Revocation Latency and Unsafe Exposure

**Phase II Turn 4 status: FAILED. Phase remains 3/8 = 37.5% complete.**

## Experiment

One deterministic governing controller is compared with a sensor-assisted revocation variant. Runtime policies never access the hidden true risk. The simulation observes 140 fresh Bernoulli audit errors and 150 held-out action outcomes per inspection. The sensor policy additionally reads a noisy proxy signal, costing 0.2 units each tick, and suspends action when the proxy is ≥2. It resumes following three consecutive quiet (<1) readings. The original rolling-only controller authorizes if the one-sided 95% fixed-time Clopper–Pearson upper bound on the last five audit batches is ≤2%.

The experiment uses **80 paired seeds (99001–99080) × 3 environments × 100 inspections**, for 24,000 ticks per policy. Scenarios: abrupt actual hazard, gradual actual hazard and an adversarial **decoy proxy shift where true action risk remains 0.3%**.

True risk and shift start are used only for measuring unsafe authorizations and revocation delay, never for choosing an action.

## Results

| Policy | Unsafe authorizations | Safe inspections withheld | Wrong actions | Cost |
|---|---:|---:|---:|---:|
| Rolling-only | 44 | **942** | 9,081 | **160,545** |
| Sensor-assisted | **1** | 4,827 | 6,911 | 173,105 |

**97.73% fewer unsafe authorizations**, but **3,885 additional safe holds** and **12,560 additional cost units**. Under decoy shifts alone, safe holds rise from 114 to 2,843 and total cost from 47,335 to 57,482. Reducing wrong authorized actions by withholding almost everything is not an admissible victory.

Illustrative loss: 10 per wrong authorized action + 0.05 per withheld action + 0.01 per audit label + 0.2 per sensor observation.

### Prespecified acceptance gate

1. Reduce unsafe authorizations by at least 20% — **PASS**.
2. Do not increase total cost over rolling-only — **FAIL**.
3. Add no more than five percentage points of safe-inspection withholding — **FAIL**.

Overall: **FAIL. Do not promote the sensor policy.**

## Reproduce

`python aether/099/experiment.py`, requiring NumPy and SciPy. Generates `results.csv`, `tick_audit.csv`, `events.csv`, `manifest.json`. The full tick audit preserves proxy observations, error count, controller decision, risk truth for evaluation, and per-tick costs.

## Important limitations

The proxy is a synthetic normally distributed signal whose hazard-associated shift is deliberately copied into the decoy condition. Its role is to test revocation against misleading evidence, not to model a validated physical sensor. Fixed-time historical confidence bounds are not guarantees after an unseen shift. The observed unsafe-onset time is available to the evaluator but not to the controller.

**Next within Turn 4: AETHER-099B — Conditional Sensor Revocation.** Train a conservative alarm on separate development seeds, then test on fresh holdout seeds with the decoy condition and explicit cost budget. The phase tracker must remain at 37.5% until all three gates pass.

[Pages-ready interactive report](https://davidwise01.github.io/oasis/aether/099/) · [Phase II tracker](../PHASE-II-STATUS.md) · [Previous AETHER-098](../098/).

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
