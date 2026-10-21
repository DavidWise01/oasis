# OASIS v8.9 · Extreme Momentum + Correlated Fault Witness

The next natural test after v8.8's single missed drift fault. This is an **additive preregistered** investigation using **real CMS educational tracks with synthetic faults**, not a change to any frozen earlier model.

## Scientific question

Can a capped angular-consistency tolerance resolve the **v8.8 high-pz blind spot** without unacceptable false alarms, and can an independent *computed relation* between track momentum and energy detect an **internally correlated** pz+eta corruption? Conversely, can a coordinated pz+eta+E alteration evade both? This assesses limits of **data redundancy inside a single reconstructed muon track**. It does **not** demonstrate four independent CERN detectors, novel particles, or physical carbon toroids.

## Provenance / disjoint validation

- CERN CMS 2010 educational dimuons, [Open Data record 700](https://opendata.cern.ch/record/700), DOI **10.7483/OPENDATA.CMS.CB8H.MFFA**, CC0.
- Official ROOT tutorial CSV: <https://root.cern.ch/files/tutorials/df014_CsvDataSource_MuRun2010B.csv>, 100,000 records.
- The exact source SHA-256 must equal the v8.7/v8.8 digest `373f0f56120998d4dad626abb1229ceef91523c262e154fb1e1e541bbb8be3a5`.
- **Retrospective**: previously evaluated hash bucket 0, `FNV1a(Run:Event)%5===0`. It includes the known v8.8 missed high-momentum fault event.
- **Prospective validation**: newly evaluated disjoint hash bucket 1, `FNV1a(Run:Event)%5===1`. The former v8.8 work did **not** evaluate this bucket for fault recovery. Both buckets come from the **same selected dataset** and should not be called independent experiments.
- Other 60% of the data remain unexamined in this v8.9 campaign.

## Predeclared deterministic synthetic faults

Assign one of four cases per event with `FNV1a("v89-fault:"+Run+":"+Event)%4` before seeing any outcomes.

| Case | Injected changes | Threat |
|---|---|---|
| Healthy | None | False alarms, accidental quarantines |
| Isolated pz drift | `pz1 += 5 GeV` | Extreme-pz scaled thresholds can miss it |
| Correlated pz + eta | `pz1 += 5`; `eta1=asinh(pz1/pt1)` | Algebraically consistent angular relationship conceals the fault |
| Coordinated pz + eta + E | As above, then `E1=sqrt(px1²+py1²+pz1²+m_mu²)` | Energy- and angular-consistency witnesses can both pass |

The last two attacks are **counterexamples**: when the malicious or broken values all satisfy the checked identities, reconstruction of the original truth may be mathematically impossible from the surviving columns alone.

## Three policies under identical inputs

1. **Legacy v8.8**: mismatch alarm when `|pz1 - pt1*sinh(eta1)| > 0.05 + 0.005*|pt1*sinh(eta1)|` GeV; repair from angular estimate on alarm.
2. **Capped threshold**: same but with tolerance `min(2 GeV, legacy tolerance)`. One-field repair when the tolerance fires; potentially more clean false alarms.
3. **Guarded**: same capped angular alarm **plus** energy-shell inconsistency `|E1 - sqrt(px1²+py1²+pz1²+m_mu²)| > 0.5 + 0.001|E1|` GeV or an invalid reconstructed two-muon mass. If the angular witness alone identifies the field and the candidate passes energy and physical consistency, replace pz1. Otherwise **quarantine** rather than guess a culprit.

Muon mass used: **0.1056583755 GeV**. Report alarm detection, clean false alarms, missed faults, output coverage, abstentions/quarantines, valid-only MAE/RMSE against the unmodified four-vector and against recorded CMS mass, plus representative counterexamples. Never treat a quarantined record as successfully reconstructed.

**Guardrails:** clean four-vector mass is a kinematic reference calculated from the same underlying event, not independent physical truth. Real detector accuracy and independence remain untested. No threshold is tuned after the dataset results and retroactively characterized as preregistered.

## Local reproduction

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
curl.exe -L "https://root.cern.ch/files/tutorials/df014_CsvDataSource_MuRun2010B.csv" -o MuRun2010B.csv
node n184/cern-extreme-fault-v89/test_stress.mjs
node n184/cern-extreme-fault-v89/stress.mjs MuRun2010B.csv v89-results-local.json 100000
py -m http.server 8000
```

Then navigate to <http://localhost:8000/n184/cern-extreme-fault-v89/>. Use the published [GitHub Pages viewer](https://davidwise01.github.io/oasis/n184/cern-extreme-fault-v89/) for checked-in results when deployment is confirmed.

Files:
- [spec.json](./spec.json): hypotheses, field mutations, caps, split and limitations
- [stress.mjs](./stress.mjs): read-only 100k CSV loader, fault injection and policy comparator
- [test_stress.mjs](./test_stress.mjs): fixed physics/control checks
- [results.json](./results.json): full aggregate evidence, after actual workflow execution
- [index.html](./index.html): Canvas2D 3D-ring diagnostic dashboard
- Workflow: `.github/workflows/n184-cern-extreme-fault-v89.yml`.

The **Gen0 1832 Ada / Gen1 1970 toroidal model / six sectors / 80 phases / 240 microticks / symbolic Mother Nature offset zero** remain unchanged. CERN is **not** physically composed of the symbolic model's carbon-6 layer.
