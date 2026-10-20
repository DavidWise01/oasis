# HAL / Hall Rail v9 — Wiring Layout (design only)

> Status: **SPECIFIED, NOT IMPLEMENTED**. This does not change the running v8 model. Exact user signature: `{{-+000+-}}`.

## Mechanical origin

The verified v8 foundation uses five pulsars `V/W/X/Y/Z`, symbolic rates `{v:0,w:0,x:360,y:360,z:720}`, a CCW carrier, a central CW bearing and CCW sun, four color return cables, and separate black-hole stress and rotor-momentum sink accounting. The bearing actuator exchanges equal and opposite torques, with work and momentum ledgers. Preserve the existing `1g*` **dimensionless balance score**, not actual gravity.

## Fixed topology

```text
                          Z  (crown)
                       /           \
                  V                       W
                  |    [ CW BEARING ]     |
                  |      [ ☼ SUN ]        |
                  |       [ . ]           |
                  |                       |
                  X                       Y
                       \    RETURN     /
                          \
                          BLACK HOLE
                            GROUND

        Each named edge = {{ - + H0 H1 H2 + - }}
              5 pulsars / 6 hex corners / 1 sun
```

## Seven slots / each rail

```text
SOURCE A ─── [−] [ + ] [ H0 ] [ H1 ] [ H2 ] [ + ] [−] ─── B
              left bias  entry midpoint  exit   mirror
```

`−/+` elements denote **signed magnetic poles in the design grammar**, not actual modeled magnets. H0/H1/H2 are **virtual Hall-style sample positions**, initially reported in normalized signal units. Real Hall sensors require physical magnetic fields, electrical bias, calibration, and field/temperature modeling; the v8 app supplies none of these.

Preserve all three sensor readings as raw virtual samples, then derive:
- `gradient = H2 − H0` (spatial/path imbalance)
- `center_deviation = H1 − (H0+H2)/2` (departure from interpolated midpoint)
- `temporal_drift = H1(t) − H1(t−1)` (sample-to-sample change)

Start with noiseless, deterministic readings from the **actual v8 model signal fields**; do not invent an external physical flux source. Mirror rails with reversed direction must reverse signed polarity consistently.

## Canonical rail manifest

| IDs | Connection | Purpose | Model status |
|---|---|---|---|
| HR01–05 | V, Z, W, Y, X → SUN | Five live pulsar emission witnesses | Source model has pulsar emission states; rail sensors new |
| HR06–09 | V→RETURN (G), W→RETURN (R), X→RETURN (B), Y→RETURN (P) | Four delayed color cables | Existing return model; rail sensors new |
| HR10 | RETURN→SUN | Aggregated delayed-return feedback | Existing feedback term |
| HR11 | RING↔SUN | Single bidirectional equal/opposite torque transaction | Existing torque model |
| HR12 | ROTOR_PAIR→BLACK_HOLE | Ground reaction/angular momentum ledger | Existing ground-momentum term |
| HR13 | RETURN→BLACK_HOLE | Scalar stress-drain pathway | Existing symbolic sink logic |
| HR14–19 | V–Z, Z–W, W–Y, Y–RETURN, RETURN–X, X–V | All six visual hex-perimeter edges | **Only visual in v8**; v9 must define synthetic witness signal before claiming a transmitting channel |

Total: **19 rails × 3 sensors = 57 virtual sensor positions**. Six perimeter edges are *planned instrumentation of geometry*, not physically simulated electrical/magnetic pathways already active in v8.

[Machine-readable manifest](./hall-rails-v9.manifest.json).

## One rail packet

```json
{
  "rail_id": "HR11",
  "from": "RING",
  "to": "SUN",
  "pattern": "-+000+-",
  "tick": 320,
  "quantity": "signed-reactive-torque",
  "source_value": 0.0,
  "hall": { "h0": 0.0, "h1": 0.0, "h2": 0.0 },
  "gradient": 0.0,
  "center_deviation": 0.0,
  "temporal_drift": 0.0,
  "active": false,
  "witness": "unverified"
}
```

Example only; no real `320` tick measurement is asserted. Physical units must not be attached to these virtual sensor values.

## Execution order

1. **Read-only sensor overlay**: connect HR01–13 to existing simulated source values; no changes to ring/sun torque, emission, return, ground, or scoring. Animate seven slots on the canvas and in ASCII.
2. **Hex geometric witnesses**: instantiate HR14–19 as explicit diagnostic/visual-only channels; keep their `active` status false until real propagation rules exist.
3. **Receipt ledger**: emit deterministic per-tick packets keyed by `(tick,rail_id)`, log directions, polarity, samples, and provenance. Bound history/ring buffers and avoid unstable feedback recursion.
4. **Diagnostics**: counters for active, delayed, bypassed and invalid channels; largest gradient; largest drift; sensor checksum; signed torque correspondence.
5. **Closed loop (separate opt-in version)**: only after monitoring matches old v8 output and fail-safe tests pass, evaluate whether a sensor-derived controller should influence the simulation; never silently substitute sensors for v8 physics.

## Deterministic acceptance tests

- Manifest validates **19 unique IDs** and **57 positions**, each exact pattern `-+000+-`.
- Every modeled vector carries a source/sink; symmetry and mirrored signs are deterministic.
- At canonical v8 lock, sensor overlay doesn't alter the `1g*` score, actuator work or conservation ledgers.
- Kick bearing: equal-and-opposite HR11 torque matches the model; read-only telemetry exposes recovery.
- Shift purple cable by +8 ticks: HR09 and HR10 detect the resulting delayed-return imbalance; ground on/off remains distinguishable.
- Ground disconnect: HR12 ground-momentum transfer is absent; common drift persists as already measured in v8.
- Perimeter witness rails remain tagged `visual_only` or inactive unless the engine actually transports a quantity over those edges.
- Byte-for-byte original v8 `index.html` and `bearing-engine` remain unchanged by this specification.

## Interpretation boundary

`{{-+000+-}}` is a user-defined symbolic seven-slot Hall-rail grammar. Existing simulations do **not** solve Maxwell's equations or measure field strength in tesla. This plan is a concrete v9 implementation map, not a claim of magnetically stabilized stars, black-hole electrical grounding, physical `1g`, or functional Hall-effect electronics.
