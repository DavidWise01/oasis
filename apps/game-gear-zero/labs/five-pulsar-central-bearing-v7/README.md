# Five Pulsars / Counter-Rotating Center Ring v7

This build **replaces** the v6 floating clockwise gyro with a **central CW bearing around the sun**, while keeping the 5 pulsars + sixth return port hex, outer CCW carrier, black-hole sink, five-gyro rates and 256 colored four-level states.

## Geometry and motion
- Five pulsars and a return port rotate as a hexagonal carrier CCW (the historical `29.75 km/s` label).
- A concentric ring around the sun spins CW in an opposing signed direction.
- The sun rotates CCW **inside** its ring, as an independent sun rotor.
- The symbolic black-hole ground remains beneath the center, not on the orbit.
- The ring and sun follow a chosen restorative-feedback law after rate disturbances instead of teleporting back to lock. This feedback is a simulation assumption, not a demonstrated passive physical mechanism.

## Bearing balance model

Signed rotor rates in turns per simulated carrier cycle: carrier `+1` CCW, ring equilibrium `−1` CW, sun equilibrium `+1` CCW.

```text
ring(t) = −1 + (ring0+1) exp(−Δt/τ)
sun(t)  = +1 + (sun0−1) exp(−Δt/(1.5τ))
error = |carrier+ring| + 0.4|sun−carrier|
score = 1 / (1 + error + 0.75·groundAdjustedSunStress)
```

Displayed `score` uses unit `g*`, a **dimensionless 1g-equivalent lock indicator**: 1.000 means ideal model balance, **not** measured gravity, Newtonian force cancellation, or an actual 9.81 m/s² field. Equal-and-opposite spins don't inherently cancel centrifugal acceleration. A real centripetal acceleration requires a radius: `a=v²/r`, which has not been given. The 29.75 km/s label alone does not determine acceleration or orbit period; the animation uses a separate display-clock period.

## Controls
- START FROM REST: ring and sun begin with zero spin, then counter-spin toward their targets.
- KICK INNER RING: introduces a signed rate disturbance; modeled feedback recovers continuously.
- RELOCK INNER RING: sets a normalized zero-error state for comparison.
- τ: recovery time in simulated carrier cycles.
- Existing sea-cable disturbance, ground toggle, 256-state petals, ASCII ledger and exporting remain operational.

## Tests
Run `node tests/bearing.test.cjs` for pure closed-form model verification. Browser smoke: `python tests/browser.py` if Playwright and Chromium are installed.

Classical symbolic control/graphics model only: real suns, pulsars, black holes, gluons and gravity behave according to different laws.
