# SHEET 84 — Dual-objective homeostasis, negative result

Append-only successor to SHEET83. The exact locally executed test is available in the accompanying ZIP (`benchmark.py`, complete `results.json`, `README.md`, SHA256 manifest). SHA256 executable: `5af5859aa57411239a5b320bdca0233cf9ea1fd7dc2c20489d0823a3cc947482`.

Identical seeded workload for fixed 0.95, gravity phase, prior homeostatic, and new causal dual-objective damping policy. 120 stable lane IDs, nine portals, 36 portal pairs, 2250 frames/3 simulated 12-second cycles, 16,065,000 candidate pair visits per policy/seed. Seed 80 and independent seed 81 tested. New controller uses only previous 64-frame counts and previous squared-speed state, clamped to damping [0.90,0.995]; it neither alters collision detection nor injects energy.

**Seed 80 collision events:** fixed 2748, phase 2837, homeo 2971, dual 3004. **Seed 81:** fixed 2759, phase 2814, homeo 2940, dual 3043. Seed 80 residual squared-speed: fixed 0.00013847098009, phase 0.00012409292611, homeo 0.00126645203206, dual 0.00110657549491. Seed 81 dual residual 0.001142279 approximate. **32/32 execution validation checks passed but optimization objective FAILED** on both seeds: dual does not reduce collisions versus fixed or phase and cannot be called a Pareto improvement.

This is screen-space proximity, not Newtonian gravity; the 60/15/3/1/1 wave, 416 registry and 9/6/1 scheduler are conceptual lineage metadata, not the objects being optimized. Original sheets unchanged. Only summary/report committed to GitHub; exact tested executable in ZIP.
