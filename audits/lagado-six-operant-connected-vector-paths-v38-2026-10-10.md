# Lagado Test038 — Six-Operant Signed Vector Path Search
Date: 2026-10-10
Status: ENGINEERING_PASS / TWO_LOCAL_MATCHES / NO_ENRICHMENT / EXPLORATORY
Parent: audits/lagado-six-operant-mirrored-port-graph-v37-2026-10-10.md

## Fixed invariants and test question
- Frozen 16x16 original source addresses: 208 active atoms + 42 passive reserve slots + 6 modeled operant slots = 256.
- Canonical operant sequence left `-+-` right `+-+`, combined `-+-+-+`; **two signed three-place groups**. The prior provisional operant positions A5/C2/L1 and A12/C15/L16 are unchanged, not recovered historical signs. P16 remains a witness within the 256.
- Original frozen v22 graph: 208 nodes / 382 spatial adjacencies / 109 selected geometry-similarity bonds. These source objects and all prior files remain immutable.
- Unlike six source vertices (which would represent only five changes), six OPERANT TRANSITIONS require seven connected distinct atoms, hence simple paths of **six original bonds**. Exactly **47** unoriented six-bond paths exist (and 61 five-bond, six-atom paths are explicitly distinguished).
- Canonical traversal orientation is preassigned by earliest row-major source endpoint. On each bond measure the sign of successive differences of the frozen scalar node fields `vx`, `vy`, `z_squared`, and `charge`. Difference exactly zero yields token `0` and does not count as either sign. Test both exact `-+-+-+` (user's ordered phase) and `+-+-+-` (inverted phase), and correct implicitly for searching across four features using the UNION of matched paths.

## Two matched paths, with exact source IDs
1. **p002**: A7 -> A8 -> A9 -> A10 -> B10 -> C10 -> C11: `z_squared` successive-difference signs **-+-+-+**, exact original operant phase. Other X/Y/charge step signs do not match. This 7-node route crosses left/center/right regions of the previously identified 18-node source-model component. The earlier larger component had image extraction instability.
2. **p046**: L5 -> K5 -> K6 -> L6 -> M6 -> N6 -> N7: `vx` successive-difference signs **+-+-+-**, exact opposite phase. The path stays in the left source region. No existing bonds were invented.
Across all 47 paths: exact either-phase matching counts X=1,Y=0,Z²=1,charge=0, total 2 distinct paths matching at least one feature; exact **specified phase** count is 1. Aggregate valid adjacent ± flips out of five positions per path: X=121,Y=124,Z²=134,charge=26 (counts are dependent across paths).

## Three graph-preserving 3,000-trial control ensembles
Every randomized trial keeps the exact 109 frozen graph bonds, the 47 path-address sequences, six modeled operant positions, and all source cell positions unchanged. All four node-feature values are shuffled jointly as a packet to preserve covariance. Three group constraints: global; 4×4 geographic source cell tile; and original connected bond component. No glyphs or labels are retrained.

| Null design | Mean paths matching at least one feature | Observed | p(null>=observed) | p(null<=observed) |
|---|---:|---:|---:|---:|
| Global | 13.931667 | 2 | 0.988004 | 0.023326 |
| Within 4×4 source tile | 13.520667 | 2 | 0.989337 | 0.023659 |
| Within pre-existing graph component | 13.524000 | 2 | 0.991336 | 0.023992 |

Primary upper-tail hypothesis (excess six-operant alternation) definitively **not supported** in these controls. The weak lower-tail depletion of alternation is **exploratory** and can result from the original bond algorithm itself choosing nearby/similar source geometry: it is not a new independent mathematical law or historical hidden code. Not all earlier model / threshold searches were independently pre-registered.

## QA and deliverables
- 19-file offline ZIP `lagado_operant_v38_bundle.zip`, verified SHA256 `f0e27e563af9d41e88c613a684780bf0536cb285a06888b908e5125ab8bf1783`; per-file SHA-256 manifest and ZIP CRC PASS.
- Included: two executable Python builders, Chromium regression, source image, frozen V22 nodes/edges, v36 capacity and v37 operant/atlas inputs; 47-path CSV, 282 step transition CSV, 9,000-trial null CSV and stats summary, JSON result, full V38 ASCII kernel, technical report and offline interactive HTML with screenshot.
- Browser Chromium Playwright in-memory validation **14/14 PASS**, tested the 208-node/109-bond/6-operant/47-path invariants, path p002 exact Z², path p046 inverse X, all-path toggle and selectors, bond/reserve/operant visibility toggles, saved screenshot, no JS errors; inline JS `node --check` PASS.
- All derived text files exclude prior deprecated annotation; no original source raster, node/bond records or historical audits overwritten.
- The separate second source photograph available as of Test035 covers A–E only; all seven original lower-plate loop anchors remain outside crop, hence full archival replication is PENDING.

NEXT: study source-ink extraction stability of X/Z² on p002 and p046 and predeclare a test on a complete independently digitized plate. Alternatively treat sign alternation as a controller applied *to* the graph rather than assuming it was encoded *by* the source.
AUDIT::APPEND_ONLY::TWO_MATCHES_NOT_A_CODE