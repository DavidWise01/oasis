# T/M/B symbolic scale crosswalk — v7.5

Additive naming and evidence layer for OASIS/N184, created 2026-10-20. Frozen source systems remain unchanged.

## Canonical bands

```text
T :: strong :: plank bubble :: star   :: U1 U2 U3 U4 U5
M :: medium :: plank foam   :: planet :: Earth (reference, not universe #10)
B :: floor  :: plank        :: atom   :: L1 L2 L3 L4

time :: 13/8B:1:1x10^-35
unit :: 10^-35 seconds per symbolic tick
```

The exact word `plank` is **user-defined nomenclature**; these band aliases do not assert verified Planck-scale physical structures, an observed atomic-planetary-stellar isomorphism, or a new fundamental time constant. `13/8B` remains an undefined symbolic operator. The middle Earth marker remains a reference and does not count as a tenth Sag A universe.

## Anchored observational reference

2023 Nature discovery of six sub-Neptunes orbiting HD 110067, with approximate **3:2 × 3, then 4:3 × 2** adjacent orbital-period ratios. The system's planets belong to the `M / planet` comparison only. They do not orbit Sag A and they do not demonstrate relativistic time dilation.

The provenance record is additive, with four distinct evidence clocks:

1. **2023-11-29** original paper, Luque et al. (Nature, DOI 10.1038/s41586-023-06692-3)
2. **2026-05-06** BBC Sky at Night secondary reporting
3. **2026-10-16** Reddit r/exoplanets post `1x7hvba`
4. **2026-10-20** user observation and OASIS ledger entry

The detailed source, orbital periods, uncertainty limits and truth-state separation live in [the time-distillation evidence record](../../evidence/relay/ITD_HD110067_SIX_PLANET_RESONANCE_REDDIT_2026-10-20.md).

## Files

- [index.html](./index.html): interactive-in-the-sense-of-source-linked, responsive research view
- [spec.json](./spec.json): exact aliases, time notation, orbital period reference, nine-instance lineage
- [test_crosswalk.mjs](./test_crosswalk.mjs): deterministic regression; run `node n184/time-stack-tmb-v75/test_crosswalk.mjs`
- CI: `.github/workflows/n184-time-stack-tmb-v75.yml`

The visuals and labels in this register are a **cross-scale analogy**; no physical time dilation or quantum foam observation is inferred.
