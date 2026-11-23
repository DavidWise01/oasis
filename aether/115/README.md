# AETHER-115 — Rotation-Schedule Freshness and Delayed Notices

**Phase V / Turn 3: accepted under a synthetic fixed-policy gate. 3/8 = 37.5%.**

## Mechanism
Each observation packet carries a keyed HMAC, current inspection time, sequence number, sample count and simulated independence claim. Independently, the schedule authority issues a signed monotonic rotation announcement with four-tick validity. The hegemonic verifier accepts a packet only when its key matches the most recently authenticated schedule **and** that schedule lease is still valid. Unknown, replayed, rolled-back or signature-invalid schedules do not renew authorization. Expiry leads to HOLD, not an inferred clean observation.

**No true environmental risk or hidden rotation truth is used in runtime acceptance**; truth is used by the simulator to label unsafe authorization.

## Synthetic evaluation
80 seeds (115001–115080) × 6 conditions × 28 ticks per controller = **13,440 decisions per policy**. Paired policies receive the same packet and notice stream.

| Environment | Cached unsafe | Leased unsafe | Cached cost | Leased cost |
|---|---:|---:|---:|---:|
| Clean rotation | 0 | 0 | 55,563.2 | 55,563.2 |
| Delayed retirement notice | 480 | 0 | 230,283.2 | 57,355.2 |
| Credential feed outage | 480 | 0 | 232,064.0 | 57,344.0 |
| Schedule rollback | 320 | 0 | 172,043.2 | 55,563.2 |
| Untrusted renewal | 320 | 0 | 172,032.0 | 55,552.0 |
| Outage recovery | 0 | 0 | 55,563.2 | 57,355.2 |
| **Total** | **1,600** | **0** | **917,548.8** | **338,732.8** |

**Net cost saving: 578,816 simulated units.** The leased design withheld 484 safe ticks versus 164 for the naive cache; part of its safety gain incurs lost useful work during delayed restoration.

The declared gate requires: no additional unsafe authorizations, strictly fewer unsafe authorizations, no lost clean-rotation safe actions, no added total cost, and deterministic replay. All passed. The trial also contains 960 full replay comparisons and 2,880 individually recorded invariant checks; the hash-chain test verifies digest formatting, not a separate external integrity anchor.

## Reproduction
`python aether/115/experiment.py` (requires NumPy and SciPy). Outputs `results.csv`, `checks.csv`, `seed_results.csv`, `trace_samples.csv`, and `manifest.json`.

**Limitations:** The fixture HMAC key and signing authority are assumed secure and are not deployable credentials. Key compromise before expiry, falsified time, data-provenance fraud, and correlated observations are not solved. The packet's independence boolean is asserted by the synthetic source, not independently verified. A correctly signed old packet cannot be deemed current merely because the verifier has not yet received a retirement notice.

[Interactive Pages lab](https://davidwise01.github.io/oasis/aether/115/) · [Phase V tracker](../PHASE-V-STATUS.md) · [Previous AETHER-114](../114/).

**Next AETHER-116 — clock rollback, expiry ambiguity and schedule clock drift.** One controller, forward-only evidence, no consensus or Byzantine expansion.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
