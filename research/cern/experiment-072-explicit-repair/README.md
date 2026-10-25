# PRIM 072 — Latched failure and explicit repair

`−1` stays failed while energy is vented and the damage register heals. A separate repair operation is needed to restore `0`. Conditions: held energy zero, damage index below 0.020, symbolic resource budget at least 0.030. Tested five 20-tick scenarios: no repair, too-early repair, too-little budget, repair at tick 12, repair at tick 20. **438/438 checks in complete conversation ZIP** (`prim_exp072.zip`, which includes the more extensive runnable `test.py`, `sweep.csv`, `results.json`, README). Repository script is a compact 5-scenario smoke test.

Inputs 0.100 J held, 0.060 damage index, 0.020 J/tick vent, 0.005/tick damage reduction. Damage is not an independent energy reservoir and the repair-resource budget is symbolic, not a measured physical joule cost. No quorums, leaders or votes. This is software-state recovery, not quantum-material repair.
