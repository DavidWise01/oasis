# SHEET 50 — Geometry-first toroidal period

Append-only test derived without internet milestone dates.

- LCM(360,8,13,11) = **51,480 ticks** = **143 360-degree turns**.
- Exhaustive trajectory: 1,029,600 node operations, 28,800 tagged Exitron crossings.
- 51,481 distinct observed full register states; no full-state return during one schedule period.
- The exact inverse of all 51,480 ticks restored the starting register.
- 12/12 computational checks passed in local runtime.
- The 51,480 period is for the *operator schedule*, not the 10-word dynamical state.
- The selected operators and moduli were implementation choices; they do not infer any real-world internet years.

Script: `sheet50_natural_period_v01.py` (same directory), loads an unchanged local copy of SHEET 45 v01 for reproducibility.

This is a symbolic deterministic transport test; no actual physical quantum or temporal mechanism demonstrated.
