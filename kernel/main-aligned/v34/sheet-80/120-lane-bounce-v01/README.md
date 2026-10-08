# SHEET 80 — 120 lanes collide / bounce

Append-only successor to SHEET79; preserves original user HTML title `SHEET 66 // 120 LANES COLLIDE // BOUNCE` as provenance and does **not** overwrite historical SHEET66.

The user-supplied canvas draws nine `-<>-` portal diamonds, 36 unordered pairs, and 120 moving lanes. Its pair loop is `i<j`, meaning **7140** unique pairs per frame (rather than the square estimate of 14400 in the source comment). Bounce trigger: display-point distance <8 px, cooldown 0.15 in source animation time; bounce rule `(si,sj) -> (-0.95*sj,-0.95*si)`. This changes progress-frame speed but does not model Newtonian forces. Flash yellow #ff0.

### Local reproducible test

Seeded standalone Python, 512 frames: **831 bounces**, first on frame 1 between lanes [4,76], distance 3.2558625 display px. Checks **28/28 pass**. 3,655,680 candidate unordered pair visits; all 120 IDs remain unique and stable. Sum squared progress speeds decays from 0.008842262720929283 to 0.002251849268555446. This energy-like proxy is in arbitrary animation units, and `0.95²` dissipates 9.75% of paired squared speeds on each hit. 60/15/3/1/1, 416 metadata IDs, 9/6/1 and sqrt(1.25) preserved conceptually as independent control layers. The local exact benchmark, README and JSON are packaged in `sheet80_lane_bounce.zip` attached to the conversation.

### Limitations

- These are **proximity events**, not validated intersections of actual straight path segments or physical collisions; new positions are not solved after a collision in the same frame.
- The original uses `Math.random()`, so each page load produces a different collision history. This benchmark seeds initialization for reproducibility.
- No real gravity force model is coupled into the bounce calculation yet. The gravity breathing lattice from SHEET79 remains separate.
- The executable is distributed as the local ZIP; GitHub currently contains an audit report and summary rather than an exact copy of the tested executable.
