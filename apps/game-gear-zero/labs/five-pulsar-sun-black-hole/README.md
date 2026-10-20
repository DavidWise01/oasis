# Five Pulsars · Sun · Black Hole — Grounded Hex v4

A zero-dependency, single-file HTML/Canvas2D/ASCII simulation, continuing the user's GG-ZERO / KET symbolic dot-box experiments.

## Run

Open `index.html` directly in any modern browser. Nothing is downloaded, and no packages or server are needed.

## Topology

```text
                     Z[-!+] / 720
                    /           \
       V[-!+] / 0                W[-!+] / 0
              |         ☼         |
       X[-!+] / 360              Y[-!+] / 360
                    \           /
                   [SEA RETURN]
                        |
                (BLACK-HOLE GROUND)
```

The SIX hex corners are the **five pulsars V,Z,W,Y,X** plus the **sea-cable return**. The SUN is the central dot, not a sixth pulsar; the BLACK HOLE is drawn below, outside the hex, as a separate abstract sink. The exact angular-rate anchor is preserved: `{{ v:0 w:0 x:360 y:360 z:720 }}`.

- Every pulsar cycles through the emitted signed symbols `[-!+]` = `{-1,0,+1}`, with `!` an active witness pulse state.
- Pulsar **emission modulation runs on a separate clock from its gyro rate**. Thus V/W can emit although their reference angular rates remain 0.
- Rates determine the relative pulse carrier frequency (`1 + |rate| / 360`) and the original X/Y and Z phase-lock checks.
- Four colored strength registers G/R/B/P stay 0..3, giving exactly **4^4 = 256** states. V→green, W→red, X→blue, Y→purple. Z is a fifth crown pulsar with mean four-color strength, not a fifth base-four digit.
- Four sea-cable ports still delay complex-valued signals and return a signed vector to the sun.
- The black-hole ground takes a configurable, nonnegative capacity-limited *amount of symbolic residual*, so it can hold the simulated sun below its flare threshold. Disconnect it to compare identical emission and return conditions without drainage.

## Equations

Let `G(t)` be the preexisting gyro residual, `C(t)` the coupled sea-cable residual and `P(t)` the **difference** of current pulsar phasors from the ideal five-pulsar reference at the same cycle time. Then:

```
raw_sun_stress  = hypot(G(t), C(t), pulseGain * P(t))
black_hole_drain = groundConnected ? min(capacity, raw_sun_stress) : 0
sun_stress       = max(0, raw_sun_stress - black_hole_drain)
flare            = sun_stress > 0.30 AND four-petal excitation > 0.60
```

This intentionally tracks a **differential lock**: the nominal five-pulsar pulses are time-varying yet give zero phase-deviation relative to their matching ideal reference. This is a testable symbolic feedback model, not physical energy or gravitational dynamics. In particular, the black hole is not electrical ground and the model makes no claims about actual pulsars bracing a Sun.

## Controls / experiment

- Click `DELAY P / COMPARE`: applies an 8-tick additional delay to the purple return. With default ground capacity `0.45`, the sun can absorb the residual below its flare threshold.
- Click `GROUND CONNECTED` to **disconnect** the black-hole ground, revealing the flare without changing the delayed pulses.
- Reconnect ground or reduce its capacity below the load to watch the flare recover or recur.
- Click `RELOCK + GROUND` to match the cable paths again while preserving the original rate registers.
- Other previous controls remain: Z slip, purple strength, rotor rates, mode/theme, ASCII, step, TXT/PNG download.

## Tests

Run in this directory:

```bash
node tests/model.test.cjs
python3 tests/browser.py
```

**17,844 deterministic assertions passed** on the pure model. Chromium desktop and mobile were tested for grounded zero, all five emissions, raw stress, purple delay, disconnect/reconnect, capacity underflow, four themes, ASCII, PNG/TXT and a zero-page-error check. The source is self-contained and the tests run against that same embedded engine.

## Physics / accuracy boundary

This is a stylized **classical** phasor and scalar stress model. Actual pulsars are rotating magnetized neutron stars; a solar flare involves the Sun's plasma and magnetic fields; and a black hole is a gravitating region of spacetime, **not a wire sink or electrical ground**. The `[-!+]` alphabet and 256-color-state scheme are symbolic KET conventions, not discoveries about astrophysics or QCD.
