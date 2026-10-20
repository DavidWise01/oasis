# FOUR PULSARS · 0-STABLE QUADRATURE (v2)

A standalone, offline **gothic four ice-cube pulsar / dot-box ASCII + Canvas2D simulator**. Open `index.html` in a browser. No libraries, network requests, shaders, hardware laser or external assets.

## The user-defined quarter-phase proposal

The green, red, blue and purple emitters keep rotating and emit pulses offset by one quarter of a full rotation:

| Source | Initial phase | Turns | Color | Symbol |
|---|---:|---:|---|---|
| Terbium / Green | 0° | 0 | green | G |
| Europium / Red | 90° | ¼ | red | R |
| Neodymium / Blue | 180° | ½ | blue | B |
| Erbium / Purple | 270° | ¾ | purple | P |

Each emitter's angular position is `θᵢ(t) = 2π(t/T + k/4 + δᵢ)`, with `k=0,1,2,3`, `T=6400 ms` at 1× speed, and `δ₃` adjustable on the **PURPLE PHASE SLIP** slider. Rotation, sweeping light beams, ring geometry and traveling pulse packets share this same phase state.

Two separate registers are computed:

- **Center phase-balance vector**: `V(t) = Σ enabledᵢ · (cos θᵢ, sin θᵢ)`. With all emitters enabled at 0/90/180/270°, `V=(0,0)`, so `|V| ≈ 0` throughout the cycle. This is the **0-STABLE** reading.
- **Nonnegative pulsed emission**: `Iᵢ(t) = enabledᵢ · [1 + cos θᵢ]/2`. All four enabled and locked implies `ΣIᵢ = 2` normalized units at all times. **Zero vector imbalance is not zero light output.** The separate GLOW slider changes visual brightness, not these normalized test values.

These are illustrative equal-amplitude phase-vector / intensity-envelope rules, not a coherent optical-field interference calculation among four differently colored lasers, and not a physical stability guarantee for a real pulsar system.

## Test the stabilizer

Start with all four emitters enabled, purple phase slip at 0°, and watch the **NET PHASE / CENTER** register remain 0.000 / LOCKED as the cubes spin and emit. Turn off one colored emitter, or move purple phase slip to 45°, to see the **center residual** become nonzero. Click **LOCK FOUR QUARTERS · RESET Δ** to restore all four emitters and their 90° separations. You can also use PLAY / PAUSE, STEP, PULSE, RESET, speed/glow, and GRAPHICS / ASCII controls, then export PNG or TXT.

### Reference outcomes

| Test | Center residual | Total emitted normalized intensity |
|---|---:|---:|
| Four emitters, 0° slip | ~0 | 2.000 constant |
| Purple +45° slip | ~0.765367 | varies over the rotation |
| Purple +90° slip | ~1.414214 | varies over the rotation |
| Blue disabled | 1.000000 | varies over the rotation |

**Checks performed:** `test_quadrature.py` verified 63 assertions, including 11 timestamps spanning many complete rotations, center balance, pulsed emission, per-source phases, intentional drift, relocking, disabled emitters, snapshots, old controls, reset, desktop/mobile Chromium behavior and zero page exceptions. Legacy `test_browser.py` was rerun successfully on the v2 viewer.

## Repo and preservation

Hosted alongside the GG-ZERO project at `apps/game-gear-zero/labs/four-pulsars-gothic/index.html`. Original v1 was frozen at branch `freeze/four-pulsars-gothic-v1` before v2 update. This viewer is independent of and does not change the Game Gear emulator, Z80 ROMs or the earlier DOT-BOX diffusion lab.
