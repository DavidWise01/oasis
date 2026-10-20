# OASIS N184 — Plank-Bubble Phase Duration v8.2

**User correction:** "the duration is 1 plank bubble length."

**Interpretation:** One complete 80-step, 360° internal phase cycle is referenced to the **length of one whole Plank bubble**, distinct from the individual arc-bubble length. The inherited user-defined `plank` spelling is retained.

## Exact dimensioned registers

```text
one whole Plank bubble length = ℓP = 1.616255 × 10^-35 m
one of six arc bubbles        = ℓP / 6 ≈ 2.693758333 × 10^-36 m
v8.0 nominal internal arc     = 2.697 × 10^-36 m
```

These are **three distinct things**: full bubble length, one of its six exact calibrated arc segments, and the separately preserved user-nominal internal phase arc length. v8.0–v8.1 are unchanged.

The user refers to duration by a *length* unit. To produce an ordinary time unit without identifying meters and seconds directly, v8.2 introduces the explicit **conditional light-travel-time equivalence**:

```text
c = 299,792,458 m/s (exact SI)
c × T_cycle = ℓP
T_cycle = ℓP / c ≈ 5.391246366844893 × 10^-44 s
```

The scientific Planck time as separately rounded in CODATA 2022 is **5.391247 × 10^-44 s**. The tiny difference is from displayed rounded values, not an independent observation of the user model. This conversion is a chosen correspondence; it does **not** prove a particle travels at speed c along the nominal bubble arc, or that a physical Planck bubble exists and has an observed duration.

## 80-step normalized phase clock

```text
n:              integer [0,80]
phase fraction: n × 1.25% = n / 80
angle:          4.5° × n
length basis:   L(n) = (n / 80) × ℓP
seconds equiv:  t(n) = L(n) / c
one step:       ℓP/80 = 2.02031875 × 10^-37 m
one step:       ℓP/(80 c) = 6.739057958556115 × 10^-46 s
```

The **six 60° outer visual segments** remain optional and distinct from **one 360° internal phase** of each clock cycle; one segment's arc length does not directly determine the cycle duration.

## Invariants

- X state, Y space, Z state+time
- T star/plank bubble, M Earth/planet/plank foam, B atom/plank
- Five upper, four lower, nine symbolic Sag A clones
- Historical `13/8B:1:1x10^-35` register
- Parent [v8.1 phase clock](../arc-phase-time-v81/), [v8.0 internal arc cycle](../arc-cycle-v80/), [v7.9 arc geometry](../arc-bubble-v79/) and [v7.8 Planck units](../scale-xyz-v78/)

## Implementation

- [Interactive phase-length/time-equivalent dial](./index.html)
- [Machine-readable canonical v8.2 spec](./spec.json)
- [Deterministic regression checks](./test_duration.mjs) — `node n184/arc-phase-duration-v82/test_duration.mjs`
- GitHub CI `.github/workflows/n184-arc-phase-duration-v82.yml`

**Evidence standard:** Passed software checks confirm the definitions and math are consistent; they do not validate spacetime discretization or a new law of physical time dilation.
