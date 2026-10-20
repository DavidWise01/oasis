# OASIS N184 · XYZ scale correction v7.6

**Canonical user correction (2026-10-20):** "it's just scale, think x : state y: space : z :state+time".

```text
         scale = T (strong)  :: star   :: plank bubble
            or M (medium)  :: planet :: plank foam  :: Earth observer
            or B (floor)   :: atom   :: plank

       x :: state
       y :: space
       z :: state+time

       SAME xyz grammar at every scale.
```

## Correction of v7.5 interpretation

T/M/B identify **scale viewpoints**, not three separately validated physical domains, force strengths, spacetime dimensions, or distinct coordinate systems. The visual vertical ordering is a diagram convention. Star / planet / atom are user-selected scale analogies. "Plank bubble / plank foam / plank" are retained exactly as spelled and are not claims of physically observed Planck foam.

The `z :: state+time` token is intentionally a **state–time composite**; because `state` is not declared a physical numeric quantity in seconds, `+` is a symbolic combination, **not** ordinary dimensional arithmetic.

Scale ratios are **not** specified. The model uses the same axis labels at each scale; it does not assert that orbital dynamics, atomic energy levels or the spacetime near a black hole are identical.

## Preserved lineage

- `T`: five upper instances U1..U5 from [web v7.3](../jellyfish-web-v73/)
- `M`: Earth reference, not universe #10
- `B`: four lower instances L1..L4
- All nine refer to the same [Sag A v7.2 symbolic universe](../universe-sag-a-v72/)
- The user time literal `13/8B:1:1x10^-35` and provisional `10^-35 s` model tick remain preserved from [v7.4](../time-stack-tmb-v74/). `13/8B` remains undefined.
- The observational HD 110067 six-planet resonance record is unchanged at [evidence/relay](../../evidence/relay/ITD_HD110067_SIX_PLANET_RESONANCE_REDDIT_2026-10-20.md): observations are not evidence of fundamental physical time dilation.

## Files

- [Interactive scale selection](./index.html): switch T/M/B without changing XYZ coordinates
- [Machine-readable correction](./spec.json)
- [Regression](./test_xyz.mjs): `node n184/scale-xyz-v76/test_xyz.mjs`
- CI: `.github/workflows/n184-scale-xyz-v76.yml`

**Classification:** symbolic modeling clarification; physical equivalence and new physics **not demonstrated**.
