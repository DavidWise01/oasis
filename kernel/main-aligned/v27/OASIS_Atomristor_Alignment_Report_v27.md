# OASIS ATOMRISTOR Alignment Report — v27

## Decision

**Keep.** The useful part is a compact thresholded, nonvolatile state machine.

The source itself says the device is a conceptual simulation and that its resistances/thresholds are representative rather than measured. v27 preserves that boundary.

## Verified fixture behavior

Source parameters:

- Vset = +1.2 V
- Vreset magnitude = 1.2 V
- Goff = 1/10^7 S
- Gon = 1/10^4 S
- k = 0.9
- evolve dt = 0.18

Independent reproduction results:

- Gon/Goff = **1000**
- I(V=0) = 0 for all tested memory states: **PASS**
- state holds throughout inclusive dead-band [-1.2 V,+1.2 V]: **PASS**
- with power off, state is unchanged under tested voltages -3..+3 V: **PASS**
- auto-sweep produces path-dependent current bins: **PASS**
- near-origin current remains near zero: **PASS**

## Source UI discrepancy

The page's buttons are labelled:

- `SET -> ON`
- `RESET -> OFF`

But each click applies only one evolve step at ±2.5 V.

From w=0:
- one SET click -> w = **0.2106**
- display threshold is ON only when w > 0.5
- therefore one SET click remains **OFF**

From w=1:
- one RESET click -> w = **0.7894**
- therefore one RESET click remains **ON**

Repeated identical clicks:
- SET reaches displayed ON after **3** clicks
- RESET reaches displayed OFF after **3** clicks

So the buttons correctly indicate direction, but not one-click completion.

## Auto-sweep

Exact source triangle sweep reproduced:

- steps: **84**
- final w: **0.000000**
- hysteresis witness bins with differing current at similar voltage: **27**

The model therefore really is path-dependent.

## What entered v27

- thresholded SET/HOLD/RESET direction
- retained memory state
- power-off hold
- zero-current origin
- 1000× conductance-ratio metadata
- explicit one-click UI discrepancy
- `AtomristorSupportLaw`

## What did not enter as truth

- ±1.2 V as a measured universal switching threshold
- 10 MΩ / 10 kΩ as measured device values
- 0.33 nm as a measured sample in this artifact
- single-atom bridge mechanism as a theorem of OASIS
- the visualization as experimental data

## What falls out

This provides a clean model of **state retention separate from active transport**:

`write threshold -> retained state -> remove power -> state persists -> later read`

That is directly useful for testing OASIS persistence/finality semantics because it separates "stored state" from "current flow/action."
