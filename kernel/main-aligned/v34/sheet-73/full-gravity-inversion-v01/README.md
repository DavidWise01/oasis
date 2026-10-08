# SHEET 73 — Full binary gravity inversion cycle

Linear append-only successor to SHEET 72. Preserve `/inf/fni/inf\` and the involution `1 -> 0 -> 1` via **two simulator boundary contacts**.

Uses the SHEET71 toy radial equation `r''=-mu/r²+lambda*r` with two **imposed** walls, `rmin=2`, `rmax=6`, and kick-drift-kick velocity Verlet. Each reflection reverses radial momentum and toggles the binary register using XOR 1. Starting `(r=4,v=-0.8,b=1)`, `dt=.002`: lower reflection at tick 1331 changes 1→0; upper reflection at tick 3721 changes 0→1.

Local executable: **14/14 checks passed.** Reversing 3,721 steps returned radius to within `1.78e-15`, velocity to within `5.55e-16`, and the bit exactly to 1. All 416 symbolic registry IDs (300 strong, 100 medium, 16 weak) remain unchanged.

**Crucial caveat:** At the second wall encounter, forward state is `(r=5.999583372788702,v=-1.1279981069308271,b=1)`, different from the original. Thus this verifies a **complete bit inversion cycle but NOT a complete phase-space orbit**. Reflecting walls are explicitly imposed control laws, not predictions of Newtonian gravity; no physical cosmic recurrence is established.

Run `python benchmark.py > results.json`. Prior numbered sheets are not altered. `9/6/1` and `sqrt(1.25)` remain independent scheduling metadata.
