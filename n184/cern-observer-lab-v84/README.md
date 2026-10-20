# OASIS N184 · Four-Observer CERN Data Lab v8.4

**Status:** reproducible laptop-friendly analysis prototype. **Date:** 2026-10-20. **Target platform:** any current desktop browser, including Windows 11 with or without discrete GPU. Uses **Canvas2D**, native JavaScript modules and a local Python HTTP server; no Python scientific stack, WebGL, CUDA or large dependencies required for the prototype.

## Run on a Windows laptop

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
py -m http.server 8000
```

Open <http://localhost:8000/n184/cern-observer-lab-v84/>.

If Python isn't on PATH but Node.js is installed, use `npx http-server . -p 8000` (requires package retrieval if not already installed). Opening `index.html` directly as `file://` may fail because modern browsers restrict ES modules and local `fetch`; serve through localhost as above.

**Standalone online:** <https://davidwise01.github.io/oasis/n184/cern-observer-lab-v84/>.

## Actual CERN educational data — exact provenance

The included `sample-cms-education.csv` contains **four numeric two-muon event rows published in CERN's CMS histogram documentation**:

- Original example and fields: <https://opendata.web.cern.ch/visualise/histograms/CMS>
- Related dataset description: *Events with two muons from 2010*, Thomas McCauley, CERN Open Data record 303, <https://opendata.cern.ch/record/303>
- Preferred attribution for the related record: DOI **10.7483/OPENDATA.CMS.4M97.3SQ9**. Cite any actual imported CERN dataset's **own** record and DOI instead of automatically citing 303.
- The four rows are **real published CMS educational examples**, not invented tracks or synthetic accelerator collisions. They are not a representative statistical sample.
- CERN specifically labels its reduced educational CSV subsets **unsuitable for full physics analysis**. See the actual record for scope, limitations and license (CC0).

Each CSV event has fields `Run,Event,Type1,E1,px1,py1,pz1,pt1,eta1,phi1,Q1,Type2,E2,px2,py2,pz2,pt2,eta2,phi2,Q2,M`. The browser reads up to **25 MiB** from a user-selected local file and processes up to **25,000 valid records**. It reports skipped rows and truncation. User-imported files remain in the browser, are not sent to GitHub or CERN, and their authenticity is **not verified**.

For more events, visit the [CERN Open Data portal](https://opendata.cern.ch/record/303) and download one of its CSV files, then use **Import CSV locally**. Files above the app's cap should be split first if necessary. Most full Level 3 event datasets require specialized formats/environments and are **not** directly compatible with this lightweight CSV importer.

## Four independent analysis *functions*

Four named roles read **the same single CMS event**, a toy four-view computation, not four detector measurements of one event:

| Software role | Data computed from CMS two-muon row | Physical interpretation limit |
| --- | --- | --- |
| ATLAS | four-vector combined invariant mass, residual versus provided `M`, total energy | Not ATLAS reconstruction or ATLAS-generated data |
| ALICE | `Δη`, wrapped `Δφ`, `ΔR=sqrt(Δη²+Δφ²)` | Not ALICE heavy-ion detector reconstruction |
| CMS | scalar `pt1+pt2`, discrepancies between `pt` and `sqrt(px²+py²)` | Not CMS detector calibration or full reconstruction |
| LHCb | charge product, mean pseudorapidity, summed longitudinal momentum | Not LHCb analysis or its measured events |

The four roles use formulas on **CMS input**. Detector names are **labels/analogs**; no claim of experimental collaboration, endorsement, or equivalent detector output is made. CERN's actual detectors have different magnet layouts (ATLAS toroids and solenoid; ALICE solenoid and dipole; CMS solenoid; LHCb dipole).

**"3 → 12" means 3 predefined features from one software lens versus 12 from all four**, because the developer deliberately chose different output features. It is a **coverage statistic**, not proof of causal emergence, Shannon information gain, novel discoveries, additional physical particles, improved accuracy or generalized reconstruction quality.

## OASIS geometry integration

The separate Canvas2D visualizer renders a deliberately synthetic OASIS index system:

```text
one symbolic ring
240 microticks per turn
80 internal phase steps     -> 3 microticks/phase step
6 arc partitions           -> 40 microticks/sector
4 software witness ports   -> cardinal diagram markers, NOT real IP locations
phase angle (visual)       -> 1.5° per microtick
```

Muon arrows use the real row's `phi` and `pt` as **2D diagram inputs**, not reconstructed 3D detector tracks. The 240-microtick OASIS coordinate is not a CERN beam clock, accelerator RF clock, collision duration, or Planck-scale quantum measurement.

The v8.2 Planck bubble length/conditional duration, v8.1 clock, v8.0 nominal internal arc length, v7.9 six-part geometry and v8.3 four-experiment topology all remain unchanged.

## Files and checks

- `observer_core.mjs`: CSV parser, finite numeric validation, four analytical observers, dataset diagnostics, deterministic symbolic phase address mapping.
- `sample-cms-education.csv`: 4 CERN-published sample rows, explicitly cited above.
- `index.html`: 2 Canvas2D views, event navigation, local CSV import, feature cards, histogram and ring controls.
- `test_observer_lab.mjs`: **51 deterministic checks** on CSV handling, kinematic formulas, feature counts, timing grid and source file wiring.
- Workflow: `.github/workflows/n184-cern-observer-lab-v84.yml`.

```sh
node n184/cern-observer-lab-v84/test_observer_lab.mjs
```

**Reproducibility:** the sample CSV and analysis engine are both versioned; keep imported file copies plus the source DOI in an external provenance log for more detailed work. Tests validate **computational consistency** only, not new experimental physics.

**Security/privacy:** CSV contents are displayed via `textContent`, not HTML injection; users control local imports. Do not fetch arbitrary remote URLs into the page. No calls to production CERN instrumentation.
