# AETHER-113 — Verified Evidence Ingress

**Phase V, Turn 1 of 8 — PASS on synthetic acceptance gate (12.5%).**

## Purpose

Protect the single deterministic action controller from packets that are missing, replayed, altered, self-signed by an unknown key, have forged sample counts, or claim unsupported measurement independence.

**Important distinction:** A matching keyed integrity tag establishes possession of the trusted ingestion key and binds packet fields; it does not establish the truth or statistical independence of the underlying measurements. The trusted key and certified independence are simulation assumptions. This project does not implement witness quorum or Byzantine fault tolerance.

## Reproduce

Requires NumPy and SciPy:

```bash
python aether/113/experiment.py
```

Generates `results.csv`, `checks.csv`, `tick_audit.csv`, and `manifest.json`. The key in this source is a **public toy fixture**, never a deployment secret.

## Frozen evaluation

- Seeds 113001–113050, seven scenarios × 24 ticks each; 350 episodes and 8,400 ticks per policy.
- The trusted policy rejects invalid current MACs, stale sequence/ticks, uncertified roots and absent packets before evaluating the risk upper bound.
- Paired naive policy trusts supplied counts and treats each present report as admissible evidence.
- Risk process: 0.3% before/after ticks 8–15, 5% during the eight hazard ticks.
- One-sided 95% fixed-time binomial upper bound and 2.5% risk cutoff; risk truth used for evaluation only.
- Four deterministic checks per case, 700 total policy/seed/scenario cases.

## Results

| Metric | Naive | Verified ingress |
|---|---:|---:|
| ACT ticks | 7,596 | 5,596 |
| Unsafe authorized ticks | 2,000 | **0** |
| Safe ACT ticks | 5,596 | **5,596** |
| Rejected packets | 400 | 2,400 |
| Illustrative cost | 660,546.8 | **115,546.8** |

All **2,800 / 2,800** replay, internal hash chain, fail-closed and admissibility checks passed.

The five non-missing attack scenarios contributed 400 unsafe approvals each to the naive controller. The trusted controller rejected all 2,000. Missing packets already triggered HOLD in both versions.

**Caveats:** Intrusion detection is a direct consequence of the synthetic trusted-tag assumption. The experiment cannot detect a compromised trusted signer, fraudulent certified uniqueness, or hidden correlation; unmodeled sensing and adversaries remain outside the demonstrated scope. Fixed-time risk bounds are not a distribution-free safety guarantee.

## Acceptance and next bound

1. No additional unsafe authorizations compared with naive — PASS.
2. Preserve at least 95% of clean safe ACT actions — PASS (100%).
3. Fail closed on invalid/missing packets — PASS.
4. Exact deterministic replay and log integrity — PASS.

**Next AETHER-114 — Ingress Key Rotation and Credential Expiry.** One controller; verify that expired credentials, rotations and counter rollback never authorize stale packets. Do not enter independent witness agreement or Byzantine coordination; encountering those requirements closes the phase at its actual completed percentage.

[GitHub Pages lab](https://davidwise01.github.io/oasis/aether/113/) · [Phase V status](../PHASE-V-STATUS.md)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
