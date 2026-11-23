# AETHER-117 — Time-Anchor Freshness and Counter Continuity

**Phase V · Turn 5 of 8 — FAILED acceptance gate. Phase remains 4/8 = 50%.**

## Evidence and decision

Replayed anchors, stale schedule anchors, counter rollback, interrupted epoch continuity, a root-authorized restart bridge and delayed anchor delivery were tested against the prior permissive verifier. A stronger verifier requires authenticated monotonic anchor sequence, a strictly advancing packet counter, anchor-age ≤4 inspections and a signed bridge for epoch changes.

**280 synthetic cases** (40 seeds × 7 scenarios), 36 inspection ticks each and two paired policies. **2,240/2,240 replay/hash/action/fail-closed checks passed.**

| Scenario | Weak unsafe | Strong unsafe | Strong safe ACT |
|---|---:|---:|---:|
| Clean | 0 | 0 | 1,440 |
| Stale anchor | 440 | 0 | 839 |
| Counter rollback | 440 | 0 | 560 |
| Verified restart | 440 | 0 | 800 |
| Unverified restart | 440 | 0 | 560 |
| Anchor replay | 400 | 0 | 840 |
| **Delayed anchor** | **440** | **40** | **999** |
| **Total** | **2,600** | **40** | **6,038** |

**Gates:** replay/hash/one-action/fail-closed PASS; fewer unsafe than weak PASS; clean availability PASS; signed-bridge restart PASS; unverified restart fails closed PASS; **zero unsafe FAIL**.

The primary failure is not clock continuity: when a valid new anchor arrives at an unsafe tick, timing authentication alone cannot establish that the attached risk observations are trustworthy. The synthetic scenario deliberately supplies a validly signed but falsely clean audit count during a hazard.

The 40 unsafe authorizations are a **preserved counterexample**. Phase V remains at 50%, with no turn credit.

## Reproduce

`python aether/117/experiment.py` with NumPy and SciPy. Generates summary, seed audit, deterministic checks, decision-trace examples and machine-readable manifest. This is a simulated trust model, not cryptographic or field certification. Signing keys, epoch metadata, and root-issued bridges are assumed uncompromised.

## Next within the bound — AETHER-117B

A fresh timing certificate may restore **chronology**, but a separate post-recovery risk certificate must reestablish **permission to ACT**. Test both on independent, untouched seeds. Do not change the phase percentage until the zero-unsafe gate passes without destroying clean availability.

[GitHub Pages laboratory](https://davidwise01.github.io/oasis/aether/117/) · [Phase V tracker](../PHASE-V-STATUS.md) · [Previous AETHER-116](../116/)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
