# OASIS N184 · XYZ three-anchor time-scale correspondence v7.7

User's exact 2026-10-20 notation: `13.8byears = 1 year = 1x1.6161^10-35seconds`

## Interpretation

The equals signs are recorded as **symbolic scale equivalence / correspondence**, not literal physical equality of times.

| View | Earlier name | Scale analogy | User time anchor |
| --- | --- | --- | --- |
| T | strong · plank bubble | star | 13.8 billion years |
| M | medium · plank foam | planet, Earth reference | 1 year |
| B | floor · plank | atom | 1.6161 × 10^-35 seconds |

Exact grammar at all scales:

```
x :: state
y :: space
z :: state+time
```

The `z` coordinate is a **composite label** of state and time, not addition between numeric state and SI seconds.

For the user-supplied `1x1.6161^10-35seconds`, v7.7 provisionally reads `1 × 1.6161 × 10^-35 s`. The original spelling remains in `spec.json`; this normalization is not a claim that `^` is defined as an arithmetic exponent in the user's language.

Using 365.25 days/year as an explicit conversion convention, the two adjacent **different** scale ratios are:
- 13.8 billion years / 1 year = 13.8 billion
- 1 year / (1.6161e-35 s) ≈ 1.9527 × 10^42

These ratios are not equal. The viewer uses independent piecewise logarithmic interpolation; no fixed universal multiplication factor or physical cosmology is inferred.

## Dimensional physics guard

NIST CODATA 2022:
- Planck **length** ≈ 1.616255 × 10^-35 **meters**
- Planck **time** ≈ 5.391247 × 10^-44 **seconds**

Source: https://physics.nist.gov/cuu/pdf/all.pdf

NASA gives the estimated age of the universe as about 13.8 billion years:
https://science.nasa.gov/exoplanets/what-is-the-universe/

The user's B number resembles the numerical Planck length coefficient, but attaching **seconds** to it makes it a *defined modeling anchor*, not the standard Planck time. This overlay does not demonstrate physical time dilation, identical star/planet/atom physics or the existence of nine real universes.

## Append-only lineage

- [Previous common-axis register v7.6](../scale-xyz-v76/)
- [Older 13/8B symbolic tick v7.4](../time-stack-tmb-v74/)
- [HD 110067 evidence and aliases v7.5](../time-stack-tmb-v75/)
- [Interactive three-anchor scale viewer](./index.html)
- [Deterministic checks](./test_scale_time.mjs)
- [Machine-readable register](./spec.json)

No frozen baseline or earlier symbolic-clock record is modified.
