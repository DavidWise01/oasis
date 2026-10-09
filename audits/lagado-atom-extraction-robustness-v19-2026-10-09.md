# Lagado Test019 — 208-atom XYZ² re-extraction stability
DATE::2026-10-09
STATUS::EXECUTED_ENGINEERING_PASS::18_MEMBER_MOLECULE_STABILITY_FAIL
PREDECESSOR::audits/lagado-three-axis-atom-assemblies-v18-2026-10-09.md

## Frozen experiment
Image-derived source 16×16=256=255+1; fixed Test015 active 208/256 and reserve 48; existing P16 witness included exactly once. Original 784×788 source image SHA256: bea5f699b53f9306f37708fc81edbd9491ecaf042cd3971c32497c376e0ae21f.
Test018 X=(B+D)−(A+C), Y=(C+D)−(A+B), Z²=((J+1)/(S+E+J+1))². Keep Test018 feature means, SD and squared-distance threshold **1.2115025117320817**, graph of 382 possible neighboring edges, 208 atom identities, and original 18 member list fixed. Source functions for skeleton/vector extraction are read from immutable Test010/Test012 builders, without executing their entire scripts.

Run 27 direct pixel re-extractions from SAME source image: crop shifts x,y in {-1,0,+1} pixels and local grayscale threshold offsets {-4,0,+4}. One setting = baseline, 26 perturbed. The original dot-family optimizer is NOT consulted and the distance cutoff is never refit.

## Exact reproduction gate
Baseline 208/208 original 16-bit codes reproduced, XYZ² features agree to 0.00025 (source CSV had previous decimal rounding), and **all 109/109 original candidate edges** match Test018 exactly. Original 18-member component remains fully connected at baseline.

## Results across 26 altered source-image extractions (baseline excluded)
| Metric | Median | Range |
|---|---:|---|
| Exact source code matches of active 208 | 61.5 | 35–117 |
| XYZ² bonds | 109.5 | 99–129 |
| Original 109 bonds retained | **65.5** | 53–81 |
| Jaccard on 382 potential graph edges | **0.409838** | per-run CSV |
| Largest connected component, any atoms | **25.5** | see run table |
| Most original 18 in any new one component | **10** | 5–15 |
| Original 18 internal baseline edges retained | **12 / 18** | see run table |
| XY-only original bonds retained | **61 / 109** | see run table |
| XYZ²-added original 12 bond edges retained | **5.5 / 12** | see run table |

- The exact original 18-member molecular candidate remains in one connected component in **0/26 altered** extractions (1/27 overall, the unaltered baseline).
- Across all 27 settings **10 bonds** from the original 109 survive unanimously; 76 original bonds survive at least 14 of the 27 runs.
- Of the 18 original edges internal to the 18-member assembly, **2** are unanimous.
- The majority edge graph keeps **14 / 18** original assembly members together, not all 18.
- The total bond COUNT appears superficially stable (109.5 vs 109 baseline), but **bond identity and original component membership are highly unstable**.
- No invented 257th record, no alteration to 1+1+2+(..=4)+8=16 primitive, no new chemical evidence or plaintext.

## Fair interpretation
Earlier Test018 p-value for intact-4×4-block-preserving permutations of original 109 bond COUNT was **≈0.5335** (null mean 108.606), so baseline total was unexceptional. Test019 tests extraction robustness, not a new independent etching, and does not rerun parameterized shuffled nulls for each variant. This is a **negative result for exact 18-member geometry**, not proof that all possible encodings fail. Next physically meaningful step is an independently printed and photographed copy with locked vector pipeline, or a much more stable endpoint/line-segment topological family descriptor with locked thresholds.

## Reproducibility
Artifact `lagado_atom_stress_v19_bundle.zip` SHA256: `5a7092cc2cfd6dfffbd2ba946c3a905311eeb34f2ff042ff4453d384b775b7dc`.
Includes Test019 builder + UI builder, audited Test010 and Test012 source function definitions, unmodified original image and Test018/010/012 base tables, 27-run stress CSV, 382-edge frequency table, JSON exact statistics, report, offline interactive HTML, screenshot, Chromium smoke test.
Checks: deterministic baseline 109/109 match; ZIP CRC PASS; Node JS syntax PASS; Chromium Playwright set_content PASS, 208 source choices, 27 test setting choices, 8/8 on-page assertions, P16 selection, A7 selection, threshold slider update and zero page errors.

NEXT::TOPOLOGY_FIRST_STABLE_ATOM_FAMILIES::OR_INDEPENDENT_PRINTING_REPLICATION
