# N184 v8.8 — CERN Four-Port Fault Witness

**Status:** Synthetic-fault benchmark on authentic CERN CMS 2010 Run2010B educational records. Additive to the frozen [100,000-event v8.7 holdout](../cern-heldout-v87/). New source is [recovery.mjs](./recovery.mjs), with [test_recovery.mjs](./test_recovery.mjs), [spec.json](./spec.json), [index.html](./index.html), and GitHub workflow `.github/workflows/n184-cern-fault-recovery-v88.yml`.

## Why this test

v8.7 showed no extra mass-prediction benefit from four named software ports when extra fields weren't actually used. The next more meaningful experiment: **detect one broken input and restore a complete result using a redundant representation already provided by CMS**. This is not multiple independently built physical instruments—`pt1`, `eta1` and `pz1` can all arise from *the same muon track reconstruction*.

## Data and provenance

- Public CERN CMS Run2010B selected dimuon dataset, 100,000 educational events.
- CERN [Open Data record 700](https://opendata.cern.ch/record/700), DOI **10.7483/OPENDATA.CMS.CB8H.MFFA**, CC0.
- Official ROOT-hosted CSV: <https://root.cern.ch/files/tutorials/df014_CsvDataSource_MuRun2010B.csv>.
- Exactly the **v8.7 SHA-256** `373f0f56120998d4dad626abb1229ceef91523c262e154fb1e1e541bbb8be3a5` is required for the CI 100k run.
- Same deterministic 20%-by-event-hash holdout as v8.7: **19,993 events** expected; original mass M is not read by detection/recovery decisions.
- The source is education/outreach data and is unsuitable for full particle-physics discovery analysis.

## Fixed, preregistered synthetic fault cases

Each held-out event is assigned a scenario using `fnv1a32("fault:"+Run+":"+Event)%3`. This salt is distinct from the holdout selector and the assignment doesn't use measured mass.

| Case | Input mutation | Expected response |
| --- | --- | --- |
| Healthy | None | Preserve original `pz1`; false alarms counted |
| Missing | Set `pz1=null` | Detect and substitute estimated `pz1` |
| Drift | Add exactly **+5 GeV** to `pz1` | Detect if inconsistency exceeds fixed tolerance and substitute |

All physical input data comes from the actual CERN rows. **The missing values and biases are injected by OASIS**, not recorded CERN hardware failures.

## Redundancy and reconstruction

Using high-energy-physics natural units:

```text
p_z,estimate = pt1 × sinh(eta1)
threshold    = 0.05 + 0.005 × |p_z,estimate|   [GeV]
alarm        = missing(pz1) OR |pz1 - p_z,estimate| > threshold

if alarm AND estimate finite:
    pz1 := p_z,estimate
else:
    pz1 := reported pz1

m² = (E1+E2)² - (px1+px2)² - (py1+py2)² - (pz1+pz2)²
```

The **naive comparison** fills a missing `pz1` with zero or trusts the +5 GeV biased value. It returns a **nonfinite result** when squared mass is negative instead of silently clamping it. Scoring reports **both coverage and error**; an algorithm that produces a number for only the easy events must not be rewarded for discarding hard events.

### Four named software ports (analogical)

```text
ATLAS software port -> Energy fields E1,E2 (mass reconstruction context)
ALICE software port -> Longitudinal angle eta1
CMS software port   -> Transverse magnitude pt1
LHCb software port  -> Longitudinal pz1, potentially faulty

Fault → disagreement between redundant columns → witness → correction → mass
```

Actual ATLAS, ALICE, CMS and LHCb are distinct experiments at different LHC interaction points. **This script does not have their independent measurements.** The names are software conventions.

## Completed 100,000-event benchmark (verified)

Original production run: [GitHub Actions 39540715071](https://github.com/DavidWise01/oasis/actions/runs/39540715071). The full numeric report is preserved in [results.json](./results.json) alongside the initial successful [source-matched run 39540543778](https://github.com/DavidWise01/oasis/actions/runs/39540543778).

- **100,000** genuine CERN educational records accepted; **0** parsing errors; source CSV SHA-256 matches v8.7.
- **19,993** deterministic held-out records, **80,007** untouched reserved records.
- **6,744 healthy**, **6,655 missing-pz1**, and **6,594 drift+5GeV** fault scenarios.
- **Healthy:** zero false alarms, all masses unchanged.
- **Missing:** **6,655/6,655 detected** and repaired; every result finite.
- **Drift:** **6,593/6,594 detected**, **one missed**; **6,593/6,594** finite recovered outputs.
- **Overall:** Naive outputs finite on **17,785/19,993 (88.96%)**; recovered outputs finite on **19,992/19,993 (99.995%)**.

| Scenario | Naive mass MAE vs original clean mass, valid rows (GeV) | Repaired MAE vs original clean mass, valid rows (GeV) |
|---|---:|---:|
| Healthy | 0 | 0 |
| Missing pz1 | 12.710310455 | 0.000383307 |
| +5 GeV drift | 6.065149521 (4,386 valid only) | 0.000362351 (6,593 valid) |
| Overall | 6.251833673 (17,785 valid) | 0.000247093 (19,992 valid) |

**Known failure, retained rather than tuned away:** event `Run 146514 / Event 147609488` had `pz1=3309.59 GeV`; the +5-GeV-corrupted value was `3314.59 GeV` while redundant `pt1*sinh(eta1)` predicted `3309.607068 GeV`. Their difference was only **4.982932 GeV**, below the predeclared **16.598035 GeV** tolerance, so no alarm was issued. The resulting mass-squared became negative, and the recovered output remained invalid. This is a failure mode of a relative tolerance at very high momentum. Do **not** retrofit the threshold based on this outcome and then reclassify the present result as a clean pass.

The recovery result is an important software demonstration, but the redundant coordinates come from the same original track, so one should **not** treat the difference as independent four-detector corroboration. Scores for naive and repaired outputs have **different valid denominators**; both coverage and errors must be reported.

## Evidence standard

The primary reference is the **unmodified clean event's computed full four-vector mass**; the provided CMS `M` column is a second arithmetic-consistency reference. Neither is a truly independent hidden physical quantity.

For each scenario, report clean false alarms, caught versus missed corruptions, valid-output coverage, MAE to the clean mass and stored `M`, and **paired** better/worse/tied comparisons where both methods output a finite value. In particular, if naive calculations become NaN, compare coverage separately; don't conceal those failures within a small MAE.

The threshold may fail on correlated faults or changes below tolerance; the test must keep negative results.

## Run on your laptop

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
curl.exe -L "https://root.cern.ch/files/tutorials/df014_CsvDataSource_MuRun2010B.csv" -o MuRun2010B.csv
node n184/cern-fault-recovery-v88/test_recovery.mjs
node n184/cern-fault-recovery-v88/recovery.mjs MuRun2010B.csv local-v88-report.json 100000
py -m http.server 8000
```

Viewer: <http://localhost:8000/n184/cern-fault-recovery-v88/> or [published GitHub Pages](https://davidwise01.github.io/oasis/n184/cern-fault-recovery-v88/).

The full CSV is not committed to the repo. The script emits only a limited number of example events and scenario aggregates. The preexisting 1832 Ada / 1970 Gen 1 reference, Mother Nature zero symbolic offset, carbon-layer analogy, 6 sectors, 80 steps and 240 microticks remain unchanged.

## Next acceptance threshold

A genuine fault-tolerance benefit would require reliable detection/recovery under independent-column corruption **without an unacceptable clean-input false-alarm rate**, robust to parameter sweeps and multi-field correlated errors. This specific test checks **only one field** at a time; do not extrapolate it to physical detector independence or new Planck-scale physics.
