# N184 · Arc Bubble v7.9 — one-sixth Planck length

**User directive (2026-10-20):** "one arc bubble is 1/6 plank length."

```
ℓP = 1.616255 × 10^-35 m          [CODATA Planck length]
1 arc bubble := ℓP / 6
            ≈ 2.693758333 × 10^-36 m
6 arc bubbles = ℓP
```

This is an **exact symbolic fraction of the recommended, rounded Planck length**. It does not imply that a Planck length has a physically observable subdivision, can be measured at this scale, or is a proven shortest length. The user's `plank` spelling is retained as the symbolic syntax; the scientific name is `Planck`.

## Geometric representation versus measured physics

The interactive Canvas offers **six equal circular arc segments**. The circle is a convenient graphic for the existing six-slot hex-compatible kernel:

- Optional circle model: full circumference (C=ℓ_P).
- Each of the six equal arcs subtends 60° and has arc length (C/6=ℓ_P/6).
- Conditional drawn radius: (r=ℓ_P/(2π)).
- The *chord length* between arc endpoints is (2r\sin(π/6)=r), which differs from arc length. Do not identify the two.
- A circle and its radius are **not** logically entailed by the user's length-fraction rule; only the arc length is canonical.

## Independent Planck time

```
tP = 5.391247 × 10^-44 seconds  [unchanged v7.8]
ℓP = 1.616255 × 10^-35 meters  [unchanged v7.8]
one arc bubble = ℓP / 6        [new symbolic length]
```

`ℓP = c × tP` holds to reported rounding. The new arc rule does **not** assign a time duration to an arc bubble. Any such conversion would need an explicit speed or process assumption.

## Preserved framework

- XYZ: `x:state :: y:space :: z:state+time`
- T: star/plank bubble, M: planet/plank foam (Earth reference), B: atom/plank
- Nine Sag A symbolic universe instances, 5 upper / 4 lower
- The frozen original N184 files and all versions v7.0–v7.8
- Historical `13/8B:1:1x10^-35` time notation

## Files and test

- [Live visualization](./index.html)
- [Canonical v7.9 specification](./spec.json)
- [Deterministic test](./test_arc_bubble.mjs): `node n184/arc-bubble-v79/test_arc_bubble.mjs`
- GitHub workflow: `.github/workflows/n184-arc-bubble-v79.yml`
- Scientific constants: [NIST CODATA 2022](https://physics.nist.gov/cuu/pdf/all.pdf)

Physical sub-Planck circles, foam and bubbles **have not been verified** by this mathematical definition.
