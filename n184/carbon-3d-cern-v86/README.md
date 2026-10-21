# N184 v8.6 · CERN :: Carbon :: Layer 3D — Run Report

**User instruction:** “cern is carbon layer 3d, run it please”

## Result on authentic CMS educational rows

The model tags this overlay `CERN::CARBON::LAYER3D`. Here **carbon** references atomic number **6** and the existing symbolic **six-sector ring**, while **3D** maps to the three measurable spatial momentum components (`px,py,pz`) of an actual CMS dimuon event. This is a **user-defined computational analogy**: CERN is a laboratory, **not a literal carbon crystal or physical six-toroid particle generator**.

The computation reads exactly the four source rows already present in [the earlier v8.4 CERN educational sample](../cern-observer-lab-v84/sample-cms-education.csv).

### Actual algorithm

In `c=1` high-energy-physics units with energy/momentum in GeV:

```text
E  = E1  + E2
px = px1 + px2
py = py1 + py2
pz = pz1 + pz2

m3D = sqrt(E² - px² - py² - pz²)
mXY = sqrt(E² - px² - py²)
error  = |mass calculation - published mass M|
```

Negative squared masses are reported as invalid/NaN, not silently replaced with zero. We are comparing reconstructed **invariant mass**, not estimating a physical 3D structure of carbon.

| CMS event | Published M (GeV) | XY-only (GeV) | Full 3D (GeV) |
| --- | ---: | ---: | ---: |
| 90830792 | 2.732050 | 21.391013 | 2.732339 |
| 90862225 | 3.102560 | 20.300094 | 3.102325 |
| 90644850 | 9.411490 | 11.763319 | 9.411457 |
| 90678594 | 7.747020 | 26.965055 | 7.747046 |

**Observed from these four rows:** mean absolute residual to stored CMS mass `M` is **0.00014552498 GeV using 3D**, compared with **14.35659004 GeV for the deliberately incomplete XY-only calculation**. All 4 events show smaller 3D error.

**Critical limitation:** The published mass `M` is itself derived from related energy and momentum components; the small 3D error is primarily arithmetic consistency and published numerical precision. The XY-only comparison leaves the measured energy untouched but deletes longitudinal momentum, which mathematically forces overestimation when summed `pz` is nonzero. This is **not an independent held-out predictive benchmark**, evidence that a physical sixfold carbon ring emerges at CERN, or a new discovery.

Source: CERN CMS histogram educational examples, <https://opendata.cern.ch/visualise/histograms/CMS>. Related CMS open-data record 700: <https://opendata.cern.ch/record/700>, DOI [10.7483/OPENDATA.CMS.CB8H.MFFA](https://doi.org/10.7483/OPENDATA.CMS.CB8H.MFFA). CERN notes these reduced educational data are not suitable for full physics analyses and does not endorse downstream works.

## Software and visualization

- [index.html](./index.html): Canvas2D projected **3D** axes and two reported CMS momentum vectors, overlaid with a **symbolic six-sector carbon ring**, 240 microticks and 80 phase ticks. Rotation changes the display viewpoint, never the underlying masses.
- [carbon3d_core.mjs](./carbon3d_core.mjs): importable actual measurement computation, aggregation, projection and phase indexing.
- [results.json](./results.json): saved per-event numeric results and mean errors for source example.
- [spec.json](./spec.json): symbol mapping, dimensional guardrails, Gen0/Gen1 and clock invariants.
- [test_carbon3d.mjs](./test_carbon3d.mjs): deterministic test harness.
- [Previous historical thesis](../ada-cern-genesis-v85/THESIS.md) and [four-observer lab](../cern-observer-lab-v84/).

### On your laptop

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
py -m http.server 8000
```

Open <http://localhost:8000/n184/carbon-3d-cern-v86/>.

For command-line verification (requires Node.js):

```powershell
node n184/carbon-3d-cern-v86/test_carbon3d.mjs
```

The page imports local CMS CSV files of the documented 21-column shape up to 25 MiB / 25,000 accepted events. No upload is performed. To avoid confusing provenance, imported files are clearly labeled unverified.

## Next scientific test

With a much larger independently sourced set of CMS 2010 dimuon events, compare **recorded four-vector consistency** (a control that should agree) against **held-out estimates of a genuinely unknown target** (which would test prediction). This overlay has only performed the former.

**Frozen baselines:** v8.5 thesis, v8.4 analysis functions, v8.2 phase clock, v7.9 sixfold arc, Gen0 1832 and Gen1 1970 remain unchanged. Nature offset remains symbolic at 0 until independently calibrated.
