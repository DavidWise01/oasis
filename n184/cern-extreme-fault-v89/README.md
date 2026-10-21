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

## Verified 100,000-event run — results

**[Successful GitHub Actions run 39542863258](https://github.com/DavidWise01/oasis/actions/runs/39542863258)** fetched the exact 15,164,516-byte CERN CSV with matching SHA-256. All 100,000 parsed without error. The new prospective hash shard contains **20,066 records**; the separately reported old retrospective shard contains **19,993**. The complete method/scenario numerical register, including actual missed-fault examples, is preserved in [results.json](./results.json).

### New 20,066-event shard

| Injected case | Number | Legacy detected | Capped detected | Guarded detected | Guarded quarantines |
|---|---:|---:|---:|---:|---:|
| Healthy | 5,051 | 0 false alarms | 0 false alarms | 0 false alarms | 0 |
| Isolated pz +5 GeV | 4,959 | 4,959 | 4,959 | 4,959 | 0 |
| Correlated pz+eta | 4,981 | 0 | 0 | 4,849 | 4,849 |
| Coherent pz+eta+E | 5,075 | 0 | 0 | 0 | 0 |

**Results and limitations:**

- **Capping at 2 GeV produced no extra detection benefit in the new shard**: the original threshold already caught all 4,959 one-field faults there. The historical v8.8 missed fault remains recorded in v8.8, rather than being rewritten here.
- The guarded shell check detected **4,849 / 4,981 = 97.35%** of two-field correlated faults but could not uniquely identify the damaged source field, so it **quarantined** all those cases instead of asserting a recovered correct mass. A further **132 correlated faults were missed**.
- The coordinated `pz+eta+E` alteration was **undetected in all 5,075 cases**. Every altered event remained numerically reconstructable, but the reconstructed mass was not guaranteed to be the original. This is a fundamental *internal-consistency* limitation: several mutually consistent corrupted fields do not become trustworthy because multiple formulas agree.
- Clean input generated **0 false alarms in 5,051 events** under all three policies, as measured for this selected dataset. It is not a universal guarantee of a zero false-positive rate.

**Outcome tradeoff, all fault types combined:** legacy/capped produced valid masses for **18398 / 20,066 (91.69%)**; the guarded policy deliberately quarantined 4,849 uncertain cases, leaving **15217 / 20,066 (75.83%)** valid. Guarded MAE over these fewer outputs is not directly comparable to the other methods' MAE unless coverage and event selection are controlled. The correct claim is *improved detection at a coverage cost*, not recovered true mass in all scenarios.

**Recorded missed-correlated case:** Run 148058, Event 49769785. Its corrupted pz and eta agreed exactly; its energy residual was approximately **0.3476 GeV**, below the predeclared energy threshold **0.5077 GeV**. The computed mass remained finite but differed from the original.

This is software fault-injection testing using redundant representations of one CMS track, not a discovery about actual CERN detector corruption or a new theory of carbon/Planck-scale geometry.

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
