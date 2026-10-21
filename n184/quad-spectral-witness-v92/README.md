# OASIS N184 v9.2 · Four-Quad Spectral Witness

**Purpose:** let four logically separate software observers inspect one immutable **Gen 0–8 color with Weak/Medium/Strong** and compare their reports. This is the next additive layer above the [v9.1 generational RGB wheel](../generational-color-lattice-v91/) and the [v9.0 A/B/C/D CERN inventory](../cern-quad-discovery-v90/), without editing either baseline.

## Input and stable identity

The sole color source is `createColorRecord(g, i, s)`, using v9.1 `swatch(g,i,s)` and v9.1 `hueAt(g,i)` for the generating rules:

- `g`: integer generation 0–8; Gen0 primaries RGB, Gen1 secondaries YCM, Gen2 six tertiaries, Gen3+ midpoint refinements.
- `i`: hue ordinal, with exactly `3,3,6,12,24,48,96,192,384` new hues for generations 0–8 respectively.
- `s`: **W** (HSV value 1/3), **M** (2/3), or **S** (1).
- Identity: `g<generation>:i<hue_index>:s<strength_key>`.
- Source registry: previously defined nearest `hue` address, fixed to 1–370 and orbits 1–122, 123–244, 245–370.
- All original source-field values remain unchanged, including the fact that Gen 7 has **384 cumulative hues**, causing **14 collisions** in the indexed 370-address view.

## Quad assignments (not physical detector observations)

| Logical quad | CERN label | CERN IP | Derived software view | Consistency check |
| --- | --- | ---: | --- | --- |
| A | ALICE | 2 | Hue angle, 6-sector position, 80-phase step, 240-microtick index | Hue derived from immutable `g,i` matches source hue |
| B | ATLAS | 1 | RGB channels, hexadecimal color, maximum RGB channel | HSV-to-RGB rendering agrees with source hex |
| C | CMS | 5 | Weak/Medium/Strong lane, all three brightness swatches | Selected amplitude and color agree with other same-hue lanes |
| D | LHCb | 8 | 370-index address, source orbit, source hue-mode preview | Nearest registry address, orbit and source preview match fixed formula |

All four software observers read **the same single synthetic RGB swatch**. Their algorithms validate different aspects, but they are **not physically, statistically or instrumentally independent**. CERN's real detector magnet count remains **A=0, B=3, C=0, D=0** complete toroidal magnets; this virtual quadranted color ring makes no claim that CERN detected these swatches. The 360° phase wheel, 6 arcs, 80 steps and 240 microticks remain a software display model.

## 3-out-of-4 report quorum (bounded diagnostic)

A report contains its quad ID, identity key, consistency-pass flag and its quad-specific numeric/text features. Each recognized quad gets **at most one vote**. At least **three distinct locally valid reports with the same identity** are required to accept.

| Deliberate injected report fault | Votes on original identity | Software quorum | Interpretation |
| --- | ---: | --- | --- |
| No alteration | 4/4 | ACCEPT | Baseline algorithmic agreement |
| A's identity label altered | 3/4 | ACCEPT (A dissent recorded) | One inconsistent report visible |
| A and B identity altered | 2/4 | HOLD | Not enough original matching reports |
| All four labels altered **coherently** | 0/4 original, 4/4 identical false key | ACCEPT **incorrectly** | Demonstrates consensus alone does not verify authenticity |

This is a **report-identity corruption demonstration**, not measurement noise, a signature system or a cryptographically secure consensus implementation. No mechanism in this model can prove the truth of a collectively forged consistent input. The coherent failure is deliberately exposed in the page and regression suite.

**Do not infer physical emergence** from mathematical agreement, force-tier labels, or a color-wheel coincidence. Weak / Medium / Strong are symbolic sRGB display brightness and do not map to weak nuclear, electromagnetic or strong nuclear coupling measurements.

## Tests and reproducibility

- [spec.json](./spec.json) — immutable promises and physical boundaries
- [witness_core.mjs](./witness_core.mjs) — quad-specific projections, 3/4 report quorum, injected spoof reports, exhaustive generation survey
- [test_witness.mjs](./test_witness.mjs) — exhaustive verification of **2,304** color-strength records × **4** views = **9,216** software observations, plus fault/quorum tests
- [index.html](./index.html) — responsive Canvas2D four-quad color ring, live generation selector, all strengths, source address, report features and adversarial quorum
- CI: `.github/workflows/n184-quad-spectral-witness-v92.yml`

Windows/local:

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
node n184/quad-spectral-witness-v92/test_witness.mjs
py -m http.server 8000
```

Then visit <http://localhost:8000/n184/quad-spectral-witness-v92/>.

GitHub Pages URL: <https://davidwise01.github.io/oasis/n184/quad-spectral-witness-v92/> once deployed.

The available browser demo does not communicate with CERN instrumentation or use connected real particle/detector data. Prior CERN data analyses (v8.4–v8.9), the A/B/C/D magnet inventory, historical 1832/1970 anchors, Gen 0–8 RGB source palette, and original 370-color registry remain unchanged.

**Recommended next engineering benchmark:** compare **signed, independently acquired sensor records with known provenance**, rather than generating four projections from a single software swatch. That would be a distinct future experiment with a genuine independence requirement, not an implication of current results.
