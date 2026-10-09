# Lagado Translation Pass 001 / Test 016 (2026-10-09)
STATUS::STRUCTURAL_TRANSLITERATION_PASS::NO_VERIFIED_PLAINTEXT
FROZEN_INPUT::v12 quad-vector, v14 active dots, v15 nested rank
USER_CAPACITY::208_ACTIVE_OF_255_PLUS_1
SOURCE::1726_JONATHAN_SWIFT_FICTIONAL_ACADEMY_OF_LAGADO_ENGRAVING

## Exact scope
Original source image 16×16=256 cells, 255 source symbols plus existing P16 final witness. 208 active by the PREVIOUSLY FROZEN v15 ranking: P16 first then 207 by center distance; 48 reserved. This is not equivalent to first 13 historical rows despite 208=13×16. All 256 sources kept; inactive source cells retain raw code; no Gen0 modifications. Checkpoints 17⊂52⊂104⊂208. Per-cell 1+1+2+(dot_minus+dot_plus)+8=16, dot pair sums to 4. Source array signed-address axes ±118 and ±250 unchanged.

## Machine transliteration, not historic translation
- Canonical basic label is `charge.topology`: `M2,M1,Z,P1,P2` for user-model dot-derived polarity charge (dot_plus-dot_minus)/2, and `H C V` three binary topology flags. H means a continuous four-neighbor occupied path across the original 4×4 image-derived glyph left-to-right. C means a cycle exists in that graph. V is a continuous path top-to-bottom.
- Example `Z.111` means dot-balanced + horizontal spanning path + graph cycle + vertical spanning path, **not** an authentic cuneiform reading or English word.
- Optional `.VXX` suffix is derived logical v12 eight-bit voxel register encoded in hex; raw 16-slot source string always preserved.
- Source image is a historical illustration from 1726 satire, NOT an identified ancient cuneiform tablet, so no valid phonetic/sign meanings can be assigned from that visual analogy.

## Computed exactly from frozen 208
- Active source codes: 196 unique of 208, basic sign class count 26; combined with voxel suffix 57 detailed classes.
- Most frequent `Z.111` occurs 43 times; `Z.110` occurs 38 times.
- Active dot-charge frequencies: −2:3, −1:40, 0:123, +1:39, +2:3.
- 191 horizontally adjacent pairs and 191 vertically adjacent pairs inside active mask. Non-first repeated token-bigrams: horizontal 75, vertical 81.
- Frozen nested first eight cells and tokens:
  `P16 M1.111`, `H8 M1.010`, `H9 M1.111`, `I8 M1.011`, `I9 Z.110`, `G8 M1.010`, `G9 M1.011`, `H7 Z.110`.
- Significant at uncorrected .05 only for repeated vertical bigrams compared to the intact-block spatial shuffle; **not** against the whole-column shuffle (p≈.223), and many metrics were inspected. No verified language model or semantic decoding.

## Equal-frozen-token spatial nulls: 2500 runs each
Metric: count all repeated adjacent bigram occurrences after the first type instance, considering only source-neighbor pairs inside fixed active mask.
| Null | Expected horizontal repeats | p(≥75) | Expected vertical repeats | p(≥81) |
|---|---:|---:|---:|---:|
| All original cell labels shuffled | 71.288 | .24190 | 71.195 | .02399 |
| Intact columns permuted | 73.842 | .42783 | 78.768 | .22271 |
| Intact 4×4 regional blocks permuted | 72.502 | .32227 | 73.056 | .04038 |

The negative, structured controls are material. Neither transliteration nor motif repetition proves an original cipher, real atomic elements or a cuneiform sign language. Detailed low-resolution topological extraction is unstable to small digital capture shifts per Test009.

## Artifact contents verified locally
`lagado_translation_v16_bundle.zip` SHA256 `0c55482f359a2ab115ffbb36f24dab4221f8eef8e340f577cb510ec32c3cbe40`; includes source image, frozen v12/v14/v15 inputs, Python deterministic analysis and HTML-builder scripts, Chromium browser regression script, 256-row raw+token CSV, 26-type lexicon CSV, 208-token two-read-order transliteration TXT, Monte Carlo JSON, full report, preview screenshot and SHA256 manifest.
Standalone HTML browser-tested Chromium: 256 selectable cells, exactly 208 active/48 reserve, P16 root, both row-major and frozen nested orders, raw/basic/full token switching, source and 4×4 view, sign dictionary, and internal checks PASS with zero JS errors. Node JS syntax and ZIP CRC PASS.

## Next hypothesis
Conduct repeatability and boundary discovery with preregistered token vocabulary, prospective independent edition, baseline from actual cataloged cuneiform sign images if external comparison is still desired, and avoid assigning English translations without evidence.
