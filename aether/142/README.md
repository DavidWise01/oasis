# AETHER-142 — Measured drift and alarm contract (synthetic)

**Phase VIII Turn 6 of 8 · 75% software readiness · 0% empirical physical qualification.**

## Tested result
A local deterministic program ran **40 seeds × 8 scenarios × 24 ticks = 320 episodes per policy**, **7,680 decisions/policy**. **5,120/5,120 acceptance checks passed**.

- Signed-only: **1,600 unsafe dry-run ACT**, **6,080 safe ACT**.
- Reference-and-drift-bound gate: **0 unsafe dry-run ACT**, **6,080 safe ACT**.
- **Real operational ACT: 0**, without exception.
- Clean, valid replacement and slow-drift cases each retained **960/960 safe dry-run ACT**.

The five synthetic failure scenarios were: concealed abrupt jumps, missed alarms, certificates understating permitted drift, stale reference acquisition, and software-forged alarms. The guarded policy binds a fresh simulated external measurement to device identity, generation, nonce, ingress, tick, bounded drift interval and conservative uncertainty. When the reference diverges from the operational measurement or evidence is stale/invalid, the dry-run controller chooses HOLD.

## Limits of what is established
This is **not an empirical experiment on measured drift**. Both the reference's observed value and true risk come from the same deterministic test fixture. The purported external issuer is an HMAC mock. The physical credibility of its calibration, independence, alarm reliability, accuracy, timing and acquisition path **has not been demonstrated**. The model's zero unsafe ACT result does not generalize to unnoticed real-world sensor faults. The true operational safety controller remains fail-closed HOLD.

The local executed source SHA-256 is `77bfcbd0b8a803654df92e487cb127b58a2708a24f25af6aa6640552cc68c2d7`. The committed `experiment.py` is a separately authored GitHub-checkout reproducer; byte identity and numerical checkout replay remain unverified. The committed `checks.csv` preserves all 5,120 local individual checks, with 640 seed-level rows and 384 sample traces (one seed per scenario and policy). Historical evidence is append-only. No witnesses, Byzantine voting or alternate controllers introduced.

[Repository source](experiment.py) · [Local aggregate](results.csv) · [All checks](checks.csv) · [Seed data](seed_results.csv) · [Traces](trace_samples.csv) · [Manifest](manifest.json) · [Interactive lab](index.html).
