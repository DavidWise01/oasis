# N184 XYZ three-scale register v7.8 — Planck time **and** length

**Date:** 2026-10-20. **Status:** additive dimensional correction; prior history immutable.

## Correct scientific constants, recorded independently

CODATA 2022 / NIST:
- **Planck time** `t_P = 5.391 247(60) × 10^-44 s` — time / seconds.
- **Planck length** `l_P = 1.616 255(18) × 10^-35 m` — length / meters.
- **Speed of light** `c = 299792458 m/s` exactly.
- Dimensional relation `l_P = c × t_P`, within rounding in the displayed coefficients.
- Original source: <https://physics.nist.gov/cuu/pdf/all.pdf>, p. 1.

The numbers in parentheses denote the CODATA standard uncertainty of the reported trailing digits. Neither Planck time nor length is experimentally confirmed as a hard minimum possible unit; they are quantities constructed from fundamental constants.

## Preserved T/M/B and XYZ interpretation

```text
T :: strong :: star   :: plank bubble :: 13.8 billion years
M :: medium :: planet :: plank foam   :: 1 year :: Earth reference
B :: floor  :: atom   :: plank        :: t_P = 5.391247e-44 s

B :: length metadata       :: l_P = 1.616255e-35 m

X :: state
Y :: space
Z :: state+time
```

The T/M/B frame is user-defined correspondence among scales, **not equality of measured durations**; assigning Planck units to B does not assert that atom-sized structures actually have Planck length or Planck time.

User's older literal:
`13.8byears = 1 year = 1x1.6161^10-35seconds`

Earlier v7.7 recorded `1.6161e-35 s` as a symbolic B-time anchor. This was **not** the physical Planck time. Rather than overwriting the historical file, v7.8 uses the CODATA Planck time for B and records the Planck length separately. The historic symbolic `13/8B:1:1x10^-35` tick from v7.4 remains in the lineage, not treated as the physical Planck time.

## Validation and navigation

- [UI](./index.html)
- [Canonical dimensional data](./spec.json)
- [Regression test](./test_planck_units.mjs)
- [Prior v7.7 register](../scale-xyz-v77/)
- [T/M/B Earth-scale view](../time-stack-tmb-v74/)
- [HD 110067 research evidence](../../evidence/relay/ITD_HD110067_SIX_PLANET_RESONANCE_REDDIT_2026-10-20.md)

Run locally: `node n184/scale-xyz-v78/test_planck_units.mjs`.

**Do not infer** experimentally established quantization, physical multiverses, a star/planet/atom isomorphism or relativistic time-dilation validation from this registry. Existing N184, Sag A and T/M/B sources are unchanged.
