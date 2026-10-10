# Lagado Test037 — Six Mirrored Operant Vector Ports
Date: 2026-10-10
Status: ENGINEERING PASS / PROVISIONAL ADDRESS MAPPING / NO DISTINCTIVE SOURCE ENRICHMENT
Parent: audits/lagado-208active-42reserve-6operants-v36-2026-10-10.md

## Frozen source counts and the user's six-operant specification
208 immutable active source atoms + 42 passive reserve positions + 6 newly designated operant positions = 256 existing original 16×16 image cells. The six operants are chosen from the 48 original non-active positions, NOT appended beyond 256. Original P16 stays a source witness in the 208. All 382 original active-grid adjacency pairs and 109 v22 model-selected similarity bonds are unchanged. Six ordered control signs are LEFT - + - and RIGHT + - +. These roles are invented control-layer semantics rather than historic inscriptions.

## Provisional non-semantic placement
Rule: among the frozen 48 non-active IDs, take mirrored left/right pairs about column 8.5 with one pair per source row-zone A–B, C–E and L–P. No non-active source cells occur in F–K. Select the pair in each zone that maximizes minimum 4-neighbor contact count on both sides, then total contacts, tie broken by earliest source row/column. Selection is an algorithmic convention, not a decoded position identification.

Upper: LEFT - A5 touches A6,B5 ; RIGHT + A12 touches A11,B12.
Shoulder: LEFT + C2 touches C3,D2 ; RIGHT - C15 touches C14,D15.
Lower: LEFT - L1 touches K1,L2 ; RIGHT + L16 touches K16,L15.
Exactly 6 source addresses and 12 read-only operant→original-active four-neighbor spatial contacts. These are annotations and do not add physical or model bond edges.

## Exact constrained alternative comparison
The max-contact criterion leaves 2 eligible mirrored upper pairs, 2 shoulder and 3 lower: 2×2×3=12 complete layouts, each having exactly 2 active direct grid contacts per operant. Compare graph reachability, oriented signed neighbor vx/charge averages and mirror geometry. Because the rule selected for contact count, testing raw contact enrichment would be circular.

|Metric|Observed|Null mean|Extreme-or-tied alternative layouts / 12|
|---|---:|---:|---:|
|Left-right operant-pair connectivity along frozen 109-bond graph|0 / 9|0|12/12|
|Unique frozen graph components touched by 12 contact atoms|11|10.75|9/12|
|Absolute signed X projection|0.20335|0.31876|9/12|
|Absolute signed charge|0|1.08333|12/12|
|Mirrored X error, low preferred|1.62555|1.3809|8/12|
|Mirrored Y error, low preferred|0.33875|0.4062167|2/12|
|Mean existing original bond degree of contacted atoms|0.58333|0.66667|11/12|
The minimum exploratory exact fraction is 2/12 = 0.1667; none shows a robust unusual source pattern. Sign alternation and six-position arithmetic are specified by the user, not recovered from pixels. No cross-hemisphere communication through the fixed graph is made possible by merely labeling formerly non-active positions.

## Validation and code
Release: lagado_operant_v37_bundle.zip (18 files), exact ZIP SHA256 **779514070aadd6381b50fed50a73a6931b6cdc4e4d10b415e43b51602395d52b**, CRC and all SHA-256 member digests passed.
- build_lagado_operants_v37.py (standalone deterministic parser, atlas, exact 12-null enumeration)
- build_lagado_operants_v37_ui.py (self-contained HTML renderer)
- test_lagado_operants_v37_browser.py (Chromium Playwright **12/12 checks PASS**, including original 208/109, 256 circles, signs, 12 selectable alternatives, active P16 selection, toggling source ink and original bonds, zero page JS errors)
- lagado_operant_v37_lab.html, lagado_operant_v37_preview.png
- lagado_full_ascii_v37.txt, per-address atlas/operant/12 contact edge CSV, 12 exact alt layouts CSV, metrics CSV and JSON, source v22 frozen node/edge tables, full input source raster and v36 logical partition JSON.
All newly derived text files exclude retired legacy marker; prior frozen image, source graph and historical audit files remain append-only.

Historical second photograph in v35 only shows complete rows A–E; none of the seven original-scan stable ink-loop centers (I6 I15 K11 M5 N5 O10 P7) can be verified in that crop. New operant assignment is explicitly *provisional* and should not be represented as a historical glyph decoding.

NEXT: Test038 prospectively test a six-step alternating sign pattern along actual original *connected graph* paths or measurable source stroke turn sequences; reject if results disappear under source-geometry/graph-preserving nulls.
