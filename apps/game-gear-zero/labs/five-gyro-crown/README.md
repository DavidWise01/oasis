# FIVE GYRO CROWN v2 — RECIPROCAL DOT / SEA-CABLE RETURN

[**Run the live lab**](https://davidwise01.github.io/oasis/apps/game-gear-zero/labs/five-gyro-crown/) · [Executable single-file HTML](./index.html) · [Frozen v1](https://github.com/DavidWise01/oasis/tree/freeze/five-gyro-crown-v1/apps/game-gear-zero/labs/five-gyro-crown)

The exact five-gyro seed is unchanged: `{{ v:0 w:0 x:360 y:360 z:720 }}`. The four-color strength space stays `4^4=256`. The **new part** is a deterministic four-port return circuit coupled into the central dot's residual and flare logic.

## Reciprocal dot

```text
        Z:720
          |
  V:0 --- . --- W:0
          |
       X:360 Y:360
          |
    [G|R|B|P] → .|.|.|.|
          |
  FOUR DELAYED SEA CABLES
          |
          .   (SAME CORE)
```

Each colored port's **signed** complex packet is sampled at the tick when it entered its return line. Time units are `1/64` of a shared model cycle. Its delayed response is:

```text
packet_j(tick) =
  0                                                  if tick < delay_j
  atten * level_j/3 * exp(i*(2π(tick-delay_j)/64+jπ/2)) otherwise

return_vector = Σ packet_j            (j = 0..3, G/R/B/P)
return_residual = |return_vector|
returned_light = Σ |packet_j| × (1+sin(packet_phase_j))/2
combined_dot_residual = hypot(gyro_residual, gain * return_residual)
containment = 1/(1 + 2 * combined_dot_residual)
flare = combined_dot_residual > 0.30 && excitation > 0.60
```

Matched 8-tick cable paths cancel the net return vector while carrying **1.8 normalized returned light units** at full four-petal strength (gain 0.85, attenuation 0.9). If only purple is delayed eight more ticks, the residual return magnitude is approximately **0.6888**, giving a **0.5855** combined center residual and a flare. BYPASS removes the return's contribution to the center without erasing returned light. RELOCK restores matching delays.

The model includes one-cycle traces of emitted light, returned light and combined center stress. The oscilloscope reads the same pure functions as the core renderer. Controls add RETURN COUPLED, DELAY PURPLE +8, RELOCK CABLES, common delay, purple additional delay, return gain, and one 1/64-cycle tick. Existing controls, 256 states, ASCII and PNG/TXT exports remain.

## Tests

```sh
node tests/sea-cable.test.cjs
```

Tests check **25,727 deterministic assertions**: 4,097 matched signal points, 224 skew samples, all 256 state addresses, bypass, relock and uneven-strength propagation. The earlier v1 five-gyro regression remains green (7,734 assertions). Chromium desktop and mobile verified lock, cable skew, bypass, relock, strength/gyro controls, ASCII/PNG/TXT and no JavaScript page errors.

## Model boundary

This is **classical symbolic complex-valued delay-line propagation**. The sea-cable return is a modeled information channel, not a real ocean cable current, stellar magnetic loop, photon interaction, or gluon configuration. Its feedback contributes an extra stress term; it is not an active controller that automatically corrects gyro speeds. Zero signed-vector sum is not zero emitted light.

---

## Frozen v1 background (retained below)

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
node tests/model.test.cjs
python test-browser.py
```

Local verified results: **7,734 deterministic mathematical assertions** passed across 1,441 full-cycle samples and 256 states, including Z slip, strength imbalance, detuned rate and phase restoration. Chromium desktop/mobile interaction regression passed, including ASCII mode and TXT/PNG exports, with zero page errors.

## Physics boundary

This is an exploratory **symbolic phase-control and visualization model**. Stars, sea cables, and atoms are alternative renderings of the same abstract five-rotor state machine. Actual solar flares arise from magnetic field reconnection and related plasma processes, and gluons mediate QCD color interactions involving quarks/gluons—not a literal four-gluon shell around an electron. No new stellar, atomic, or quantum law is established by numerical closure of this software model.
