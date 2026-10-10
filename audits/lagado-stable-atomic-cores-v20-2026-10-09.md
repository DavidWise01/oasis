# Lagado Test 020 — Stable Atomic Cores | 2026-10-09

STATUS::EXECUTED_NEGATIVE_STRICT_GATE::FROZEN_SOURCE::NOT_HISTORICAL_DECIPHERMENT
LINEAGE::audits/lagado-atom-extraction-robustness-v19-2026-10-09.md
GEOMETRY_MODEL::16x16_source::255+P16=256::active208::reserve48
NESTING::17→52→104→208::CAPACITIES_CUMULATIVE
PRIMITIVE::1+1+2+(..=4)+8=16
IMAGE_SHA256::bea5f699b53f9306f37708fc81edbd9491ecaf042cd3971c32497c376e0ae21f

## A priori inherited frozen edge gate
Test018 source has 109 bonded adjacent pairs out of 382 original active-grid neighbor edges. Test019 showed **10 bonds** persistent in **all 27** crop/threshold micro-extractions of one engraving (dx,dy=−1,0,+1 px and Δgrayscale=−4,0,+4). Test020 keeps these ten candidate geometric edges unchanged. Dot learning/families from Test014 are NOT used in new topology test.

## Exploratory independent topology-family gate
For each glyph independently reextract 4-vector-quadrant normalized stroke mass and stroke graph counts. Define orientation-neutral coarse family **D×T**:
- D0 if sorted largest quadrant mass <0.35; D1 if <0.45; otherwise D2.
- T0 if junction/(segment+endpoint+junction+1) <0.05; T1 if <0.20; otherwise T2.
- For each of 208 source atoms, modal family is computed from the same 27 extraction variations. Atom qualifies iff modal count is >=24/27 and not missing.
- Edge qualifies if it is among the previous ten 27/27 geometric edges AND both endpoints meet atom stability gate.

These D/T bin edges were selected during this exploratory same-source modeling project. The stable-family rule is an engineered test, not authenticated ancient atomic semantics.

## Actual results
- Original 208 active atoms preserved, original 48 reserved, existing P16 once.
- 30/208 pass family >=24/27; 178 do not.
- Original prior bonds 109, unanimous micro edges 10.
- **Strict family + unanimously stable bond intersection = 0 connections**.
- Relaxed 24/27 bond edges with same atom gate: also zero connections.
- The original ten bonds and their endpoints are retained in audit; none are misrepresented as verified structures.

Nested layers:
| Active capacity | Stable family atoms | Original 27/27 bonds | Strict cores |
|---:|---:|---:|---:|
| 17 | 0 | 0 | 0 |
| 52 | 6 | 1 | 0 |
| 104 | 12 | 5 | 0 |
| 208 | 30 | 10 | 0 |

Ten original bonds and matching family counts:
- B10–C10: 21/27,14/27; heldout bond 4/8
- B12–C12: 27/27,18/27; 4/8
- D7–E7: 15/27,24/27; 5/8
- E2–E3: 21/27,17/27; 0/8
- F5–F6: 27/27,18/27; 8/8
- F12–G12: 17/27,18/27; 5/8
- G4–H4: 18/27,15/27; 7/8
- G11–G12: 24/27,18/27; 2/8
- J2–K2: 21/27,15/27; 2/8
- O7–P7: 27/27,10/27; 4/8.

## Additional heldout settings — SAME SOURCE IMAGE
Eight new crop offsets dx,dy=±2 pixels × grayscale offsets ±8. These shifts were not used in the 27-run label calibration, but are still perturbations of the **same engraved image**, not independent prints. Only **one** original ten bonds, F5–F6, survives all eight. Six of the 30 stable-family atoms retain exactly the same family on all eight. This materially weakens the identification of stable molecules and demonstrates sensitivity to extraction.

## Null controls / interpretation
3,000 seeded permutations of stable atom labels among original cells within 4×4 engraved blocks, holding original ten candidate bond identities fixed: mean 0.313 qualifying core edges, observed 0; p≥observed =1.00. Zero original cores do not support the hypothesized structural decoding. Tests already used one image and exploratory thresholds, so this is not independently verified.

## Deliverables
- `lagado_stable_cores_v20_bundle.zip` SHA256 **8b1d07d2c22cf230079889b6517cb8875c65361de06d0e6e5c598a0adb3abfa5**.
- Includes reproducible Python Test020 experiment and UI builder; exact v10/v12 extraction functions; original source scan, frozen v18/v19 source data, 208 atom/382 edge datasets, 35 source reextraction records, compressed per-run features, JSON data/parameters, report, browser smoke test, full-page screenshot, and standalone self-contained HTML.
- ZIP integrity CRC: PASS; extracted viewer Javascript `node --check`: PASS.
- Chromium Playwright in-memory `page.set_content`: 7/7 internal checks PASS, 30 stable atoms, 0 strict cores, 10 prior bonds, 1 extra-shift stable bond, capacity=52 showing six atoms, family-slider exploratory sensitivity, selecting B10, zero JavaScript page errors. Native `file://` navigation was blocked by environment policy, so the HTML was tested with `set_content`.

## Decision
Do not lower thresholds just to declare success. The ten previous robust **geometric** edges remain hypotheses, but the currently defined topology-first atomic identification fails strict reproducibility. No historical plaintext, physical atomic structure, ancient alchemy or additional spatial dimension is established.

NEXT_TARGET::BLIND_INDEPENDENT_SECOND_ENGRAVING_SCAN::FROZEN_EXTRACTION_AND_AUDITED_THRESHOLDS
