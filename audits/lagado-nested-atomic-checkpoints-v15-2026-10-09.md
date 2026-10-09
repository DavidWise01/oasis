# Lagado Test 015 — Nested Atomic Checkpoints and Signed Depth (2026-10-09)
STATUS::FROZEN_V14_SOURCE::EXECUTED_EXPLORATORY_REPRESENTATION::NOT_HISTORICAL_DECIPHERMENT
PARENT::audits/lagado-active-dots-v14-2026-10-09.md
FROZEN_FORMULA::1+1+2+(dot_minus+dot_plus)+8=16
SOURCE::255+P16::256
BONDS::134_OF_480

## User correction
These should be tested as **atoms nested inside atoms**, not tested primarily against the visual style of cuneiform. Treat 17,52,104,208 as inclusive cumulative capacity checkpoints **inside the full 256-slot 255+1 register**, rather than replacing 256 with a 208-total stream.

```
256 { 208 { 104 { 52 { 17 { pinned root + 16 local slots } } } } }
```
17=1+16; 52=4×13; 104=2×52; 208=2×104. 256−208=48 extra slots; differences between capacities: 17,35,52,104,48. Note that 17→52 is **not** a simple integer doubling or uniform same-branch expansion.

The signed ranges −118..+118 and −250..+250, if interpreted symmetrically, contain 237 and 501 integer addresses including zero. These cannot both be one-to-one source glyph counts from only 256. In this test they are alternative virtual axial address projections. Modern established atomic numbers are 1..118; the −250/+250 axes are *not* evidence of 250 discovered chemical elements.

## Explicit model choices
Pinned P16 (256th source glyph) is one witness/root *reference*, not a newly generated 257th glyph. For this run, sort the other 255 historical-image-derived cells by Euclidean proximity to center of printed 16×16 grid. This is a modeling choice used to define nested *cumulative* sets at 17,52,104,208,256, **not a deciphered orientation or historical ordering rule**.
Read already frozen v14 `original_raw_dot` r from the original quad-vector measurements. Normalized signed q=clamp(1−r/2, −1,+1). Signed virtual coordinate `round(R*q)`, with R=118 or R=250. Original source code, inferred v14 dot pair, v14 dot family, and 134 compatible edges remain unchanged. No optimization/retraining/threshold changes.

## Actual signed-address compression results
| Axis | Possible integer addresses including zero | Distinct used by the same 256 source glyphs | Unordered pairs colliding |
|---|---:|---:|---:|
| -118..+118 | 237 | 118 | 255 |
| -250..+250 | 501 | 168 | 120 |

Depth expansion decreases collisions but adds no independent source information; raw signed positions are projections. All 256 dots conserve `dot_minus + dot_plus=4` and every complete source register conserves 16.

## Nested cumulative checkpoint test
| Capacity | New occupants vs prior level | Frozen active bonds among sites in container | Eligible local grid edges |
|---:|---:|---:|---:|
| 17 | 17 | 11 | 24 |
| 52 | 35 | 33 | 86 |
| 104 | 52 | 63 | 182 |
| 208 | 104 | 118 | 382 |
| 256 | 48 | 134 | 480 |
The stages **contain** their prior members; no member is overwritten. P16 counts once.

## Family pattern vs location (does nested containment reveal a non-random family gradient?)
Measure mutual information of the five nonoverlapping *incremental bands* with **frozen** v14 dot family labels: observed 0.026575 bits.
3,000 permutations per control, deterministic seed 17052208256:
| Controlled relocation of frozen labels | mean MI | p(null MI>=observed) |
|---|---:|---:|
| All source identities freely shuffled | 0.024251 | 0.35755 |
| Whole columns shuffled | 0.024269 | 0.35921 |
| Whole 4×4 engraved blocks shuffled | 0.032456 | 0.59214 |
The positional family gradient is **not exceptional against any of these controls**. This does not reject every possible nested atom representation; it rejects treating this *particular radial arrangement* as evidence of a discovered historical nested-key structure.

## Provenance and validation
Original frozen v14 atom/edge CSV files are provided unchanged inside the reproducible bundle; their SHA-256 hashes are in the JSON stats and generated report.
The reproducible local Test015 archive `lagado_nested_atoms_v15_bundle.zip` includes builder Python, full input atom/edge CSVs, output 256-atom mapping CSV, stats JSON, report, and standalone HTML viewer.
The program asserts 256/256 unique source identities, P16 root-only-once, all cumulative set containment, 256 capacity invariants and 134 original v14 bonds.
Browser Chromium / Playwright `set_content` interactive smoke-test: 256 buttons present; capacity 208 shows 118/382 bonds; capacity 256 shows 134/480; ±250 shows 168 unique signed addresses; A1 selection works; zero JS runtime errors. Node JavaScript syntax and archive ZIP integrity checks PASS.
NEXT::independent-source engraving comparison with preregistered vector/dot extraction; the current image itself lacks semantic or physical validation.
