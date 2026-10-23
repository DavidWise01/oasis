# KET — General shell closures, not only noble gases (Z1–118)

2026-10-23. The operator `|` closes a verified shell/subshell/group and carries ancestral state into the next generation. The user's example `Li|Be` (Z3→4) terminates the 2s² subshell: noble-gas ring closures are a *subset* of shell-boundary events, not the general rule.

Local exhaustive address scan: **118 neutral atomic addresses**, **117 immediate neighbor pairs**, seven end-of-period closures at 2,10,18,36,54,86,118, **19 formal filled-subshell endpoints** under simplified Madelung/Aufbau orbital occupation.

Examples:
- H→He: 1s² closes.
- Li→Be: 2s² closes.
- F→Ne: 2p⁶ closes.
- Cl→Ar: 3p⁶ closes.

**Do not conflate** (a) sequential electron subshell closure, (b) chemical bonding and stable molecules/solids, or (c) KET symbolic pair containment. A pair in the cipher does not imply a stable LiBe compound. Real ground-state configurations exhibit known exceptions, and high-Z configurations require relativistic theory. A separate chemical-bond evidence workflow must check candidate compounds before assigning physical stability.

Scientific references: 
- NIST orbitals and closed subshells https://www.nist.gov/pml/atomic-spectroscopy-compendium-basic-ideas-notation-data-and-formulas/atomic-spectroscopy-10
- NIST ground-state configurations H through U https://www.nist.gov/pml/atomic-reference-data-electronic-structure-calculations/atomic-reference-data-electronic-8
- Li/Be material phase behavior: https://www.sciencedirect.com/science/article/abs/pii/S002231150980024X

Companion locally executed Python `test_shells.py` and generated `elements_1_118.csv`, `adjacent_pairs_1_118.csv`, `results.json` available as conversation files. This is a **structural first pass**, not exhaustive chemical pair/bond validation across ~6,903 possible distinct unordered element pairs.

Next test: use measured NIST neutral-atom configurations instead of simplified filling, then build a chemical-evidence matrix for actual bonding/coordination/group assemblies (not limited to adjacent atomic numbers). Frozen 184/257 baseline unchanged.
