# SHEET 81 — Big Bang / Big Crunch × 120 lane bounce

Append-only successor to SHEET80, sourced from user-provided compiled React cosmic expansion/contraction artifact. Source contains states `collapsed`, `expanding`, `expanded`, `collapsing`, auto-pulse, 13 accent objects, 300/100/16 particles. It is NOT itself a 120-lane collision engine.

**Adapter (experimental, not source-specified physics):** deterministic auto-pulse durations 4.8s expanding / 1.6s expanded / 4.8s collapsing / 0.8s collapsed; coefficient `damping=0.95+0.02*(2*extent-1)` bounded [0.93,0.97]. Compare with original fixed 0.95 bounce rule. Nine portals, 36 unordered portal pairs, 120 lane IDs, threshold <8 canvas px, 0.15 seconds cooldown. Shared deterministic seed 80, 512 frames, 7140 unique candidate lane pairs per frame.

**Executed local test:** 27/27 checks passed. Baseline 835 collisions, final squared-speed proxy 0.0022434875223058008. Phase-coupled 825 collisions, final squared-speed proxy 0.002609744514317501. Identities 120/120. **Mixed effect:** 10 fewer collisions, but more residual squared speed; not an unconditional improvement. Original candidate stage coverage check failed when sampled too narrowly; corrected to test full period. 512-frame experiment spans 8.192s, so collapsed phase was only tested in phase unit checks and not reached during lane run.

Benchmark SHA256 `e4dff5e036aaef1a90acd4bb3a747e786248af3e36b9749057970eec3df3f12a`. Exact executed source/JSON/README in conversation ZIP `sheet81_gravity_cycle_lane.zip` (ZIP CRC validated); GitHub stores audit/results, not a byte-identical source file. No Newtonian gravity or 9/6/1 scheduler actually executed. 60/15/3/1/1 and 416 registry metadata preserved. Earlier numbered sheets unchanged.
