# Lagado Test009 — Pixel perturbation falsification (2026-10-09)
STATUS::EXPERIMENTAL::NEGATIVE_ROBUSTNESS_RESULT
LINEAGE::audits/lagado-nested-9631-v8-topology-2026-10-09.md
MODEL::{{n}}^{{n}}::9/6/3/1
SOURCE::lagado_16x16_source.png::IMAGE_DERIVED_16BITS_PER_CELL
INVARIANT::REPRODUCES_PREVIOUS_256_GLYPHS_EXACTLY
GEN4_BOND_BASELINE::129/63/59/56/47

## Fixed features
Same 784×788 engraving, line-removal and skeleton pipeline, 16×16 grid, 4×4 binary codes per glyph, v8 9/6/3/1 gates, graph rules and 53 *fixed index* shell swaps from v5. Change only brightness threshold by [-24,-16,-8,0,8,16,24] and grid crop offsets dx,dy in [-2,0,2]: 63 parameter combinations. The 53 swaps were not reoptimized on perturbed images.

## Results from 62 nonbaseline perturbations
| Measure | Minimum | Median | Maximum |
|---|---:|---:|---:|
| Exact glyphs (/256) | 3 | 17.5 | 88 |
| 4x4 bit agreement | 70.3% | 77.5% | 89.8% |
| Exact topological 3-register labels (/256) | 74 | 102.5 | 165 |
| Final bonds | 20 | 33.5 | 87 |
| Same original 47 bonds retained | 3 | 8 | 19 |
| Final bond Jaccard vs v8 | 0.0417 | 0.1013 | 0.2754 |

**Zero candidate bonds survived all 63 extraction settings.** Only one edge appeared in a strict majority of them.

## Micro-stress
Additional 27 variants use shifts [-1,0,1] pixels and grayscale offsets [-4,0,4]. Just 4 of 47 original bonds survived all variants; 26 nonbaseline variants retained median 14.5/47 bonds and 74/256 exact glyph codes. Instability is not restricted to extreme settings.

## Null against intact 4x4 engraved regions
Baseline (unperturbed) 47 observed final bonds versus 44.943 average across 400 4×4 intact-block shuffles, p=0.16459. 12 baseline/extremal settings tested, 400 shuffles per selected setting, no multiplicity-adjusted discovery claim: the extremal settings were selected after the sweep and cannot count as independent proof.

## Decision
**FAIL** robustness for bitmap-based historical cipher inference; **PASS** exact regeneration and reproducible parameter sensitivity engine. This is a 2D print/image processing model; there is no verified semantic plaintext, atomic encoding, or historical alchemical key. Next: robust grid rectification and source-independent high-resolution edition replication, with the algorithm locked in advance.

## Reproducibility
Local bundle `lagado_9631_v9_bundle.zip`: code, source engraving, original atom CSV and v5 ledger, v8 bond baseline, test009 63-run and 27-micro-run CSV, bond occupancy frequency CSV, JSON, interactive HTML, audit report. ZIP integrity and JavaScript syntax pass; headless browser rendering timed out, not asserted.
