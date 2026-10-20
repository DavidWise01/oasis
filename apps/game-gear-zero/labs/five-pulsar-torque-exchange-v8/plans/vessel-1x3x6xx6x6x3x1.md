# V9 vessel envelope — `1x3x6xx6x6x3x1`

**Status: literal vessel recorded; junction and layer semantics not yet frozen.**

The user defines the 19-rail Hall network as a vessel for the exact expression:

```text
1x3x6xx6x6x3x1

             [1]        origin / folded dot?
              ×
             [3]        three ingress sensor views?
              ×
             [6]        six hex vertex ports?
             [xx]       junction / crossover — UNASSIGNED
             [6]        sixfold routed shell?
              ×
             [6]        second sixfold shell?
              ×
             [3]        three egress sensor views?
              ×
             [1]        terminal / folded dot?
```

Question marks denote **candidate projections**, not user-confirmed definitions. The exact doubled `xx` is a distinct unresolved token. It must not be simplified into a single multiply, erased, or automatically assigned a physical meaning.

## Existing v9 instrumentation inside the proposed envelope

- **19 uniquely identified vector rails**, `HR01` through `HR19`, with exact symbolic grammar `{{-+000+-}}`.
- **3 virtual Hall samples** per rail (`H0,H1,H2`), giving 57 observation positions.
- A previously modeled **five-pulsar hex** with 6 perimeter locations including the return corner, a central sun, a counter-rotating ring, four return cables, and separate ground accounting.
- The six perimeter links are still *geometric* in the running v8; rail sensors remain a proposed read-only layer.

If all seven numeric factors were **ordinary multiplication**, their arithmetic product would be `1 × 3 × 6 × 6 × 6 × 3 × 1 = 1944`. That calculation says **nothing by itself** about hardware components, new sensor readings, physical dimensions, or the meaning of `xx`.

## Integration constraint

The vessel is a new **outer symbolic topology**. Preserve the tested v8 powered reaction-torque model, its v9 rail manifest and the unmodified code until the `xx` operator is specified. Instrument source values before enabling any new control-loop feedback.

## What needs definition next

The **single unresolved central junction**, `xx`: should it denote two coupled interfaces, a mirrored crossing, a multiplication at another scale, or another user-defined operator? Its exact meaning determines how the proposed sixfold layers interconnect.

[Machine-readable vessel notation](./vessel-1x3x6xx6x6x3x1.json) · [V9 rail placement](./hall-rails-v9.md) · [19-rail manifest](./hall-rails-v9.manifest.json).
