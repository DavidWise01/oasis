# PRIM 063 — Pressure against containment

Kernel: `{-+[WwwW][MmmM][SssS][Fashion(fission/fussion)][SingleCore]+-}`. Inversion `{{ [()] > ||\|| > ||/|| > ([]) }}` with retained box `||\/|| = ||[;]||`.

24 idealized one-dimensional radiation pulse cases: 6 independently specified reflection/transmission/absorption fractions and 4 incident energy values. 120/120 checks pass for nonnegative partition, exact energy closure, momentum impulse, no duplicate energy release and closure after releasing stored energy. `E_in=E_ref+E_trans+E_stored`; `J=(E_in+E_ref-E_trans)/c=(2 E_ref+E_stored)/c`. Energies are exact rational joules. Impulse is N·s; pressure needs boundary area and pulse duration. This is energy bookkeeping, not experimentally validated microscopic containment. No leaders/quorums. Run `python test.py`.
