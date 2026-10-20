# N184 Arc Bubble Cycle v8.0 — 360° per nominal bubble

User instruction (2026-10-20): **`one cycle is 2.697x10^-36/360 x 360`**.

## One phase cycle

```text
nominal length (user):   L0 = 2.697 × 10^-36 m
nominal per degree:          L0 / 360 = 7.49166666667 × 10^-39 m / degree

L(θ) := (2.697 × 10^-36 m / 360°) × θ
L(360°) = 2.697 × 10^-36 m
```

**360° is one arc bubble's internal phase cycle.** The 60° spacing among six *different* arc bubbles in the v7.9 illustrative ring is an external display angle. Do not conflate them.

## Two separate length modes, with intentional precision difference

v7.9 preserved the exact numerical one-sixth of the CODATA 2022 Planck length (`ℓP=1.616255×10^-35 m`, displayed precision):

| Mode | One complete 360° phase cycle | Six complete cycles |
| --- | ---: | ---: |
| User nominal | 2.697 × 10^-36 m | 1.6182 × 10^-35 m |
| Calibrated to `ℓP/6` | 2.6937583333333336 × 10^-36 m | 1.616255 × 10^-35 m |

The nominal is roughly **0.12034% longer** than `ℓP/6`. It is retained literally, rather than treating it as the exact CODATA subdivision. Select *nominal* or *calibrated* in the new interactive dial to evaluate phase-angle progression under either convention.

## No phase-duration inference

Planck time is separately recorded as **`tP ≈ 5.391247×10^-44 s`**. The formula is a **spatial length-per-degree parameterization**, not a physical angular velocity or an independently observed timing cycle. A duration for 360° has **not been specified**.

The same user coordinate grammar persists:
```text
x :: state
y :: space
z :: state+time

T :: star / plank bubble
M :: planet / plank foam / Earth
B :: atom / plank
```

The nine Sag A copies, the HD 110067 evidence, and previous N184 kernel layers remain unchanged.

## Files

- [Interactive dial](./index.html)
- [Spec](./spec.json)
- [31 deterministic checks](./test_cycle.mjs): `node n184/arc-cycle-v80/test_cycle.mjs`
- [Previous six-arc ring](../arc-bubble-v79/)
- [Planck time/length reference](../scale-xyz-v78/)

The mathematics proves internal software consistency of this defined symbolic parameterization, **not physical subdivisions of spacetime**.
