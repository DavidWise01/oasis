# Lagado Test021 — Conditional Information Gain (2026-10-09)

STATUS::EXECUTED_EXPLORATORY::HISTORICAL_PLAINTEXT_UNVERIFIED
PARENT::audits/lagado-stable-atomic-cores-v20-2026-10-09.md
PRIMITIVE::1+1+2+(DOT_MINUS+DOT_PLUS=4)+8=16
CAPACITY::255+P16=256::208_ACTIVE::48_RESERVE
SOURCE_FROZEN::V16_TRANSLITERATION::V18_VECTOR_FEATURES::382_ACTIVE_GRID_EDGES
V16_CSV_SHA256::f09fdf32794385e7118291a9780ab84a9abbdcb5ea5fa366760ff630c0c48caf
V18_CSV_SHA256::f445d23783095eded983fb0d689a0ab4f50e3a5a9ef731f547bac08ae6a305e3

## Question and method
Given a source atom’s frozen voxel8 and topology3 plus adjacency direction, test whether its preserved dot charge, vector orientation, junction complexity or 17/52/104/208 nested rank band predict either (a) the neighbor's graph-cycle flag or (b) the neighbor's source-vector junction-positive flag. All outcomes use structural geometry; neither is an English-word gloss. 317/382 cycle-positive, 182/382 junction-positive.

Use one-hot encoding and L2-regularized LogisticRegression C=.5, with **leave-one-source-4×4-block-out** cross-validation on the original 16×16 engraving. The result is out-of-fold negative log likelihood in bits per directed right/down grid edge. Strictly frozen prior dot states (v14) are reused unchanged; no new inference training of those dot states.

| Extra feature | Loop gain bits/edge | Junction gain bits/edge |
|---|---:|---:|
| Dot charge | +.011928 | -.001916 |
| Vector-axis quadrant | -.010392 | -.005564 |
| Source junction complexity | +.005160 | +.008344 |
| Nested band | +.001046 | -.007499 |
| All features | +.005234 | -.010328 |

Baseline held-out losses: loop .667644 bits/edge; junction 1.009867 bits/edge.
There are 36 distinct frozen (topology3,voxel8) input classes; 16 repeated classes contain 188 of 208 active atoms, with largest class size 58. In those 16 repeated classes: dot charge splits 14; XY vector quadrant splits 13; coarse junction class splits 13. F5 and F6 both have voxel8 11111111 and topology3 110; signed dot charge F5=0, F6=-1. This demonstrates *descriptive* distinguishing information, not deciphered semantics.

## Permutation and uncertainty tests
For best observed dot→neighbor-loop and junction→neighbor-junction hypotheses, perform 240 independent candidate-feature shuffles WITHIN original geographical 4×4 engraving blocks; repeat 240 within-column shuffles, at the atom level, leaving baseline and neighbor targets fixed, and rerun the identical held-out algorithm. Bootstrap the 16 held-out source-blocks 5000 times to get 95% interval of the paired predictive log-loss gain.

Dot→loop: observed +.011928 bits/edge; within 4×4 mean -.004194, plus-one p=.008299; within column mean -.003275, p=.012448; **block bootstrap 95% CI [-.009776,+.032391] contains zero**.

Junction→junction: observed +.008344 bits/edge; within 4×4 mean -.001112, p=.087137; within column mean -.002232, p=.062241; **block bootstrap 95% CI [-.008093,+.023148] contains zero**.

There were eight single-feature/target comparisons and two combined-feature/target comparisons. Nominal best p~.0083 is NOT sufficient after even a basic 8-comparison Bonferroni correction (~.0664), and exploratory choices have accumulated over many earlier tests. V14 dots also already rewarded neighboring DOT similarities (not neighbor loop target), so no independent semantic/predictive discovery claim is justified.

## Decision and release
- PASS: Every source and edge read from verified frozen CSVs; 208 active atoms, 382 source-neighbor pairs; 36 baseline geometric classes; all algorithm outputs reproducible.
- PASS: Descriptive dot-charge feature can distinguish 14/16 formerly repeated classes.
- CANDIDATE: Small out-of-block dot→neighbor-loop predictive gain.
- NOT VERIFIED: Prediction on an independent engraving, stable historical translation, physical atom identity, matter at 10^-36 m, cuneiform key.
- NEXT: Lock model exactly and predict on a separate independently acquired edition/scan before choosing additional thresholds or claims.

## Local deliverables
- `lagado_information_gain_v21_lab.html`: offline Chromium-tested viewer with 256 slots and 208 selectable atoms, conditional neighbor probabilities and feature contrasts.
- `lagado_information_gain_v21_bundle.zip`: complete reproducible source Python, frozen input CSVs, 208-atom CSV, 382-edge predicted-probability CSV, stats JSON, report, browser smoke test, visual preview and hash manifest.
- `lagado_information_gain_v21_report.md`: method, evidence, failure modes.
- ZIP SHA256 `37c6613e24dfa730ba81e7bcd9f7be47bb8d31e209b16994231d9be3fc6e0d75`.
- Browser Chromium Playwright set_content PASS: 208 atom options, full 256-cell field, selecting F5/F6, view changes, no JS page errors. Node --check and ZIP CRC pass.

STATE::QUARANTINED_EXPLORATORY::APPEND_ONLY_AUDIT
