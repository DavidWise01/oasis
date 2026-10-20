# N184 Arc Phase Time v8.1 — n × 1.25%

**User directive:** "phase time is n x 1.25%"

This new **additive symbolic clock** refines the preceding [v8.0 internal 360° cycle](../arc-cycle-v80/) without altering frozen models.

## Cycle indexing

```text
n ∈ {0,1,...,80}
normalized phase time τ(n) = n × 1.25% = n / 80
angle θ(n) = (360° / 80) × n = n × 4.5°
relative time elapsed = (n/80) × T_cycle
```

| n | percent | internal angle |
| -: | -: | -: |
| 0 | 0% | 0° |
| 1 | 1.25% | 4.5° |
| 20 | 25% | 90° |
| 40 | 50% | 180° |
| 60 | 75% | 270° |
| 80 | 100% | 360° |

**An absolute cycle duration in seconds has not yet been specified.** The formula gives a normalized time **fraction**. A user-set value for `T_cycle` in the interactive demo yields `(n/80)T_cycle`, but does not modify the canonical JSON. The standard Planck time is not automatically the duration of this symbolic arc cycle.

The 80 internal ticks are different from the **six optional 60° external visualization slots** in v7.9. Since `80/6 = 13 1/3`, those display-slot boundaries do not fall exactly on an integer 80-tick index.

## Preserved length semantics

```text
nominal 360° arc length       = 2.697 × 10^-36 m
nominal length per n step     = nominal / 80
CODATA-calibrated full length = (Planck length) / 6
calibrated length per n step  = calibrated / 80
```

The nominal v8.0 length is around 0.12034% larger than the calibration. No velocity, rotation period in seconds, measured sub-Planck structure, or astrophysical physical time dilation is inferred from the user-defined phase rule.

## Sources and navigation

- [Interactive 80-step dial](./index.html) with phase slider, play/pause, and optional independent cycle-duration input
- [Canonical phase-time spec](./spec.json)
- [Deterministic tests](./test_phase_time.mjs): `node n184/arc-phase-time-v81/test_phase_time.mjs`
- [Previous arc cycle v8.0](../arc-cycle-v80/)
- [Planck time/length reference v7.8](../scale-xyz-v78/)
- XYZ grammar unchanged: `x:state :: y:space :: z:state+time`
- T/M/B symbolic scales unchanged: star / Earth-planet / atom

**Classification:** software-defined normalized phase-time clock. Verifying the code cannot establish physical quantum time, faster/slower proper time, or astronomical multiverses.
