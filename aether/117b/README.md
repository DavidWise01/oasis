# AETHER-117B — Fresh Risk Certification After Timing Recovery

**Phase V · Turn 5/8 · PASS (synthetic) · 62.5%**

The AETHER-117 experiment failed when an authenticated time anchor renewed while the environment remained hazardous. The clock-continuity policy incorrectly allowed **40 unsafe authorizations** from otherwise correctly signed but stale low-risk packets. That failure is preserved at [117](../117/).

## Corrected authority model

Time authority and action authority are separate.

1. **Clock authority:** A trusted signed anchor, bounded lease and a continuous local monotonic counter/epoch authorize the current time context.
2. **Action authority:** A **separately signed, newly sampled, current-time risk audit** matching the epoch and counter must satisfy the 2.5% Clopper–Pearson risk gate.
3. Any missing, mismatched, stale or uncertified audit means **HOLD**. A clock renewal alone does **not** authorize ACT.
4. Records are append-only, hash-linked, replay deterministic and issued by one governing controller.

The risk-audit acquisition process is a separate trusted input. **No distributed witness agreement or Byzantine consensus is introduced.**

## Experiment

- 40 synthetic seeds, 7 scenarios, 36 ticks per episode = **280 episodes** and 10,080 ticks per policy.
- Policies: weak cached-time baseline, original strong clock-continuity verifier, corrected fresh-risk verifier.
- Synthetic risk source: safe rate 0.3%; hazardous interval 8.5%. The controller does not receive true risk, only signed, simulated error counts.
- Current-risk audit uses 560 new Bernoulli observations per accepted packet, with additional cost 0.01 per audit observation.

| Controller | Unsafe authorized ticks | Clean safe ACT | Verified restarts | Total cost |
|---|---:|---:|---:|---:|
| Weak cached-time | 2,600 | 1,440 | Not certified | 1,421,974.4 |
| Strong clock continuity (AETHER-117 logic) | 40 | 1,440 | 40/40 | **288,982.4** |
| **Fresh risk + clock continuity** | **0** | **1,440** | **40/40** | 305,121.6 |

The corrected controller removed all 40 of the remaining observed unsafe authorizations. Clean availability and authenticated restart recovery were preserved. Fresh audit cost increased total cost by **16,139.2** over the original clock-only strong verifier.

**Acceptance:** 3,360/3,360 deterministic checks passed across replay, hash integrity, single action and fail-closed behavior; zero observed unsafe actions, improvement over strong, full clean availability, verified restart and unverified-restart closure all passed.

## Limits

All cryptographic materials and observations are synthetic, with a trusted HMAC root, independent risk-audit signer, integrity-protected counter and correct simulated risk model. A valid signature does not itself prove independent or truthful data, and no general or real-world assurance follows from zero observed failures. This study does not independently certify sensor hardware, key protection, transport, or adversarial corruption.

**Reproduce:** `python aether/117b/experiment.py` (NumPy and SciPy); regenerate `results.csv`, `checks.csv`, `seed_results.csv`, `trace_samples.csv`, `manifest.json`.

[Interactive Pages lab](https://davidwise01.github.io/oasis/aether/117b/) · [Phase V status](../PHASE-V-STATUS.md)

**Next bound — AETHER-118: Current Risk Audit Freshness Under Interrupted Acquisition.** Target 75% only after new tests pass.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
