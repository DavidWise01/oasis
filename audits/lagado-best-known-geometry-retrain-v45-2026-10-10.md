# Lagado Test045 — Best Known Geometry Retrain and 8^8^5^3^1 Formal Hierarchy
Date: 2026-10-10
STATUS: REBUILT, HELD-OUT SECOND-PHOTOGRAPH TEST EXECUTED, BROWSER 11/11 PASS, CLAIMS EXPLORATORY
PARENTS:
- audits/lagado-leeluu-chemistry-ee-uu-ll-failover-v43-2026-10-10.md
- audits/lagado-leeluu-eleven-gate-exhaustive-v44-2026-10-10.md
- audits/lagado-archival-partial-replication-ascii-v35-2026-10-10.md

## What is frozen vs retrained
- Source artwork is the fictional 16x16 writing-machine engraving in Swift's *Gulliver's Travels*. Two images depict the same historical design, not independent physical phenomena.
- Frozen latest ontology: 256 addresses = 200 atomic role cells + 54 operants + witnesses P1/P16, left and right 128 each; 109 original similarity-model bonds, retained without modification.
- Frozen oldee symbolic chemistry lanes ee/uu/ll are kept as nonphysical tags; CATG/CARBON are unproven symbolic names.
- The eleven previously called "atomic structures" are eleven source-grid-adjacent pairs selected as V43 nine *virtual* gates plus two proposed V44 augmentations I7--I8 and J9--K9. **0 of these 11 are one of the 109 original accepted source-model bonds.** Their frozen original tokens and vector differences are exported without pretending they are chemical bonds.
- User's full formal notation is **8^8^5^3^1**, right-associated as 8^(8^(5^(3^1))) under ordinary exponent precedence. This astronomically large expression is NOT flattened to 960 and is NOT explicitly enumerated.

## Learned finite source sample
Only first-image original geometry enters balanced eight-class unsupervised training. Standardize the 3 HCV topology bits, 8 voxel bits, vx/vy/z^2, signed charge, stroke/end/junction/segment summary; seed 45 KMeans with eight centers and 25-seat-per-center Hungarian assignment, yielding exactly **8 classes of 25 among the 200 atom cells**. The color names red, black, white, green, blue, yellow, purple and orange are arbitrary palette names. Per-atom path indices cover 8 slot indices, five stage indices, three axis indices and fixed P1 or P16 witness identity — deterministic finite addresses, not observed genetic inheritance.
The role words mother, father, tardigrade, diatom and four additional inputs are NOT assigned to actual source glyphs, since genetic or ancestor attribution cannot be inferred from this engraving.

## Held-out second-photograph test
The user-uploaded second plate image contains complete A-E rows only; **56 original v41 atoms** have both source geometry and a second-photo image-junction label: positive=29 / negative=27. Refit supervised LogisticRegression with frozen C=.25 and standard scaling on four complete source rows, predict the held-out fifth, repeat for each of five original rows. Outcome is junction detected in *second photographed image*, not a codon or chemical element label.

| Features | Leave-one-source-row-out bits/glyph | Gain vs prevalence-only |
|---|---:|---:|
| Prevalence-only | 1.017033 | 0 |
| Topology+voxel | 1.091033 | -0.073999 |
| Original geometry without dot charge | 0.985243 | +0.031790 |
| Original geometry + signed dot charge | **0.967965** | **+0.049068** |
| Eight trained color groups alone | 1.021902 | -0.004869 |
| Geometry + colors | 1.073589 | -0.056556 |

Thus the **currently best-tested predictor is source geometry + dot charge**, giving 34/56 0.5-threshold class decisions and a 4.82% reduction in held-out log-loss relative to the prevalence-only comparator. Its 5-row cluster bootstrap 95% interval for gain is [-0.08967,+0.14931] bits/glyph, which includes zero. 350 within-original-row target-label shuffles yielded exploratory one-sided p≈0.0399; multiple candidate models and earlier tests were tried, so this cannot be treated as confirmed independent predictive evidence.
Eight colors do NOT improve geometry: the incremental change is -0.088346 bits/glyph, 5-row bootstrap CI [-0.182855,-0.007891]. In 250 balanced random-color permutations, the learned-color-only log-loss was 1.021902 bits/glyph versus null mean 1.120328, p≈0.11155, not compelling.

## Eleven candidate source adjacencies
Mean Euclidean difference in frozen vx/vy/z^2 for the eleven proposed adjacency pairs 0.549746 vs 0.629740 in 2500 random 11-edge samples of 256 original dormant atom-to-atom grid adjacencies. One-sided p=0.126749; not unusual, and the earlier design is topology-selected. No extra source bonds were added.

## Artifact integrity / release
Standalone `lagado_bestknown_v45_lab.html` interactive 256-address atlas: 200 geometry-learned atom colors, 54 operants, 2 witnesses, original 109 bonds as solid lines and proposed 11 as dashed lines, clickable per-glyph original voxel/token/vectors, six held-out prediction model scores.
Chromium Playwright in-memory `set_content`: **11/11 interaction checks PASS** (all 256, source 109, proposed 11, color count 25, witness count 2, selection and edge visibility, no JS errors). Standalone JS syntax Node --check PASS.
Reproducible local deterministic ZIP `lagado_bestknown_v45_bundle.zip`, **SHA256 393742d55c0896af01dd709f6c6023674484ffa9cc43bd382d4015f76738ea94**, containing Python fit/eval builder, viewer builder, Chromium test, six original input tables, all output reports/data, per-file SHA256 manifest. ZIP CRC and every member digest verified; building twice produced same ZIP hash.
Also: `lagado_full_ascii_v45.txt`, `lagado_v45_atomic_colors.csv`, `lagado_v45_eleven_atomic_vectors.csv`, `lagado_v45_heldout_predictions.csv`, `lagado_v45_report.md`, `lagado_v45_results.json`.
All new derived texts exclude the retired legacy wrapper; original source images and prior audits remain immutable.

DECISION: APPEND ONLY, SYMBOLIC MODEL REBUILT FROM BEST PREDICTOR; EIGHT-COLOR ALPHABET AND 8^8^5^3^1 RETAINED AS HYPOTHESES; NO BIOLOGICAL GENETICS, PHYSICAL CHEMISTRY, HISTORICAL CIPHER, OR TIME-LAW VALIDATION.
NEXT: acquire complete independent high-resolution plate containing the seven previously found lower-row anchors; lock color classifier and extract morphology before reinterpreting additional structure.
