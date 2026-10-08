# SHEET 85 — Space `-i`: Julia 3-anchor rabbit and 120 orbital dots

Append-only successor to SHEET84. Preserves the user's historical HTML label `SHEET 71 // JULIA RABBIT // -<>-` as source provenance; does **not** overwrite the actual numbered SHEET71 in GitHub.

Source: Julia iteration `z[n+1]=z[n]^2+(0.355+0.355i)` with initial `z[0]=0`, 120 escape-time iterations (bound `|z|^2<=4`) on 860×904 source canvas covering real/imaginary coordinates ±1.6, 3 diamond anchor points and 40 animated orbital dots around each anchor (120 unique source dots). Three diamond points are connected to visually form a triangle; this drawing by itself does not establish a true period-3 orbit.

**Critical numerical check:** `z3` from `z0=0` differs from zero by approximately `0.7940178450146844`. Three-lag differences for the first successive offsets are approx `0.7940`, `0.6305`, `0.5630`. Do not mislabel these as an exact 3-cycle. The conventional Douady rabbit Julia parameter is different; this report does not substitute that parameter for the user's original.

**Space `-i` adapter:** complex conjugation `z -> conjugate(z)` and parameter `c -> conjugate(c)` reflect the imaginary axis of the orbit, while a second conjugation restores all complex positions exactly. This is an explicit mathematical reflection, not proof of new spatial dimensions. For the register adapter, 120 dots map to 60 slots with unique lane IDs and ear labels retained; dropping those identity fields is lossy. Rendering dots are not the 120 collision-resolved travel lanes of SHEET80, and collision-avoidance throughput is **not** benchmarked in this sheet.

Executable benchmark `python benchmark.py > results.json` performs numerical orbit audit, reversible mirror, dot identity, source escape-time checks, and symbolic 60/15/3/1/1 + 416 registry preservation. No actual gravitational field dynamics or 9/6/1 scheduler is executed. All results are reproducible by running the exact script in this directory. Preserve negative result as source-alignment evidence.
