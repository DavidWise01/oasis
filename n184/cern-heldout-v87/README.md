# OASIS N184 · CERN held-out event benchmark v8.7

**Question:** After `CERN::Carbon-6::Layer3D` and the successful four-event momentum consistency check, does adding an independent angular-observer channel improve a common numerical target on **thousands of actual CMS educational collision records**, without conflating feature count with scientific discovery?

## Verified public source and scale

2010 CERN/CMS educational dimuon dataset, from the Run2010B Mu public release:
- CERN Open Data record: <https://opendata.cern.ch/record/700>
- DOI: **10.7483/OPENDATA.CMS.CB8H.MFFA**
- Size: **100,000 selected events** available in CSV format; selected for outreach, **unsuitable for a full scientific physics analysis**.
- Official CERN ROOT CSV tutorial uses <https://root.cern.ch/files/tutorials/df014_CsvDataSource_MuRun2010B.csv> and documents it at <https://root.cern.ch/doc/v622/df014__CSVDataSource_8C_source.html>.
- License: **CC0 1.0**; CERN/CMS do **not** endorse downstream works.

**No CSV rehost or large dataset commit.** The GitHub Actions workflow fetches a source file from `root.cern.ch`, computes SHA-256, and uploads a compact JSON report. Imported data can also be evaluated entirely on your Windows laptop.

## Benchmark registration (before numerical results)

This is a **training-free feature-ablation** on real dimuon events. Event IDs are split deterministically with FNV-1a over `Run:Event`: 20% are designated holdout, 80% reserved. No estimator is fitted. The stored mass `M` is **not accessed by any prediction function**; it is read only when scoring the predictions on held-out rows. The mass target does derive from the same physical detector kinematics, so a successful result is a consistency test, not proof of a genuinely independent particle discovery.

Compare the *same recorded mass M* under three main formulas:

1. **Transverse-only:** `m_T = sqrt(2*pt1*pt2*(1-cos(phi1-phi2)))`
2. **Transverse + longitudinal angular:** `m_angular = sqrt(2*pt1*pt2*(cosh(eta1-eta2)-cos(phi1-phi2)))`
3. **Physics control:** `m_4vec=sqrt((E1+E2)^2-(px1+px2)^2-(py1+py2)^2-(pz1+pz2)^2)`

Both formulas 1 and 2 use the massless-muon approximation; formula 3 uses the original reconstructed four-vectors. The four-port software overlay supplies all available features but **must not leak the 4-vector-derived mass into the angular predictor**. Its result is *intentionally identical* to formula 2 until a defensible additional estimator is defined. A **zero gain** from adding unconsumed ports is a valid null result.

Metrics on held-out records: mean absolute error (MAE), RMSE, median absolute error, 95th-percentile absolute error, valid prediction count, invalid count, charged-pair composition. Preserve SHA-256 and file bytes for source identity. Sample summaries are not astrophysics or Planck-time observations.

## How to run locally

Windows PowerShell:

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
py -m http.server 8000
```

Download the official CSV from CERN using a browser or:

```powershell
curl.exe -L "https://root.cern.ch/files/tutorials/df014_CsvDataSource_MuRun2010B.csv" -o MuRun2010B.csv
node n184/cern-heldout-v87/benchmark.mjs MuRun2010B.csv n184/cern-heldout-v87/local-results.json 100000
```

The CSV may have the required CERN 21-column educational field format. If any source layout differs, the parser **fails with a precise missing-column error** rather than silently fabricating fields. The maximum accepted valid rows is 100,000. The raw data remains local to the host where the script runs.

Tests:

```powershell
node n184/cern-heldout-v87/test_benchmark.mjs
```

GitHub Actions workflow:
`.github/workflows/n184-cern-heldout-v87.yml`. It performs the local fixture checks before the real 100,000-event input test. An external-source failure is considered an uncompleted real-data run, not an invented success.

## OASIS scientific boundaries

The inherited symbolic 6-sector, 80-step, 240-microtick ring and the Gen0 1832 / Gen1 1970 thesis are unchanged.

```text
CERN :: symbolic Carbon layer 3D
hist: Ada 1832 -> Gen1 1970
obs: 4 software lenses on CMS data
test: common M target -> transverse-only vs angular fusion vs fourvector control
claim: validated dimensional feature-ablation, not physical emergence
```

An improvement from adding the pseudorapidity difference is mathematically expected from the standard massless-muon formula. The test establishes that the implementation and actual data exhibit that expected behavior. It does not establish that four toroids create matter, Planck time is an elementary clock, or a new theory of physical space has been experimentally supported.
