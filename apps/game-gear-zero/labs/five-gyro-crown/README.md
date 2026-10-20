# FIVE GYRO CROWN — Zero-Stable Stellar / Aquatic / Atomic Lab

A **standalone single-file HTML + Canvas2D / ASCII** interactive simulation. No npm, server or external assets needed.

## Run

Open `index.html` in a browser. The lab operates offline.

## Canonical symbolic seed

```text
{{ v:0  w:0  x:360  y:360  z:720 }}
```

**Units are degrees of angular motion per shared cycle**, not angular positions or physical angular momentum. V/W are active pinned zero-turn references; X and Y each rotate one revolution per cycle, deliberately offset by 180 degrees so their unit phase vectors cancel; Z rotates twice per cycle and checks its 2:1 phase relation to X. The corresponding raw degree sum at baseline is 1440° per cycle, **not** a force or energy conservation quantity.

The 4-color clover is kept: G/R/B/P each independently have strengths `{0,1,2,3}`, forming `4^4=256` discrete combinations. The fifth gyro Z is a crown/phase witness, not a fifth color level.

## Mathematical rule (implemented in `index.html`)

For cycle coordinate `t`, with rates in degrees/cycle:

- `phaseX = 2πt (rateX/360)`
- `phaseY = 2πt (rateY/360) + π`
- `phaseZ = 2πt (rateZ/360) + slipZ`
- `XY = abs(exp(i phaseX)+exp(i phaseY))/2`
- `crown = abs(sin(wrap(phaseZ - 2 phaseX)/2))`
- `anchors = (abs(rateV)+abs(rateW))/180`
- `petals = hypot(G−B,R−P)/(3√2)`
- `residual = hypot(XY, 0.85*crown, 0.6*anchors, 0.9*petals)`
- `containment = 1/(1 + 2*residual)`
- `emission = Σ strength[k]/3 × (0.5 + 0.5*sin(2πt+kπ/2))`, `k=0..3`
- `excitation = (G+R+B+P)/12`
- `flare = residual > 0.30 and excitation > 0.60`

At canonical rates, all strengths 3, and zero Z slip, residual is numerically zero while emission is 2 normalized units for all `t`. The flare indicator is a threshold-based **visualization**, not a physically validated flare prediction.

## Interactive controls

- Pause/play, step 1/32 cycle, restore exact 0-lock.
- Perturb Z +45°, weaken purple, or scan the next base-four 4^4 state.
- Select STELLAR / AQUATIC / ATOMIC / HYBRID views, all reading the same engine.
- Change any of V/W/X/Y/Z angular rates; change Z phase offset; change four color brace strengths.
- View the ASCII ledger, or export rendered PNG/ASCII TXT.

## Test reports

```
node test-model.cjs
python test-browser.py
```

Local verified results: **7,734 deterministic mathematical assertions** passed across 1,441 full-cycle samples and 256 states, including Z slip, strength imbalance, detuned rate and phase restoration. Chromium desktop/mobile interaction regression passed, including ASCII mode and TXT/PNG exports, with zero page errors.

## Physics boundary

This is an exploratory **symbolic phase-control and visualization model**. Stars, sea cables, and atoms are alternative renderings of the same abstract five-rotor state machine. Actual solar flares arise from magnetic field reconnection and related plasma processes, and gluons mediate QCD color interactions involving quarks/gluons—not a literal four-gluon shell around an electron. No new stellar, atomic, or quantum law is established by numerical closure of this software model.
