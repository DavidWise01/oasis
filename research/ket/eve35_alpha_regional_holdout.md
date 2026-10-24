# E.V.E. 35 — alpha branching and contiguous-region holdout

2026-10-23, NUBASE2020 (Kondev et al., Chinese Physics C 45, 030001, 2021). Source mirror `PavelStransky/NuclearProperties/nubase_4.mas20.txt` blob 05ec424175847f6ee948a075dc08963e4a688418. https://amdc.impcas.ac.cn/web/nubase_en.html

**Dataset:** 175 alpha-dominant ground-state nuclides with unflagged parent/daughter/neighbor nuclear mass excesses, unflagged numeric half-life, strictly numeric 0<branch<=100%; 71 with alpha branching under 100%. Excludes 2 previously eligible nuclides with no numeric alpha branching; also estimated (#), censored, missing neighbor entries. All 175 have Qalpha>0 and Qalpha<20 MeV and |Δ2n|<45 MeV.

Half-life prediction target is partial alpha half-life `log10(T_total_seconds) - log10(alpha_branch/100)`. Qalpha=(ME_parent−ME_daughter−ME_He4)/1000 MeV. Δ2n=(ME(Z,A−2)+ME(Z,A+2)−2ME(Z,A))/1000 MeV. Feature `(Z−2)/sqrt(Qalpha)` is barrier-inspired Geiger–Nuttall proxy, **not** numerical WKB action. Odd Z and odd N flags used, but **spin/parity hindrance NOT FIT** in this run. `log10(Qalpha)` final additive kinetic feature. Ridge penalty 0.5 except intercept, training-only per fold.

**Held-out split:** whole contiguous blocks of sorted atomic numbers, 5 folds, no train/test duplicate Z:
- Fold 0: Z 4–68, 9 test nuclides
- Fold 1: Z 69–79, 13 test nuclides
- Fold 2: Z 80–86, 51 test nuclides
- Fold 3: Z 87–93, 77 test nuclides
- Fold 4: Z 94–102, 25 test nuclides

| Model | Held-out MAE log10(s) | RMSE log10(s) |
|---|---:|---:|
| composition | 4.725263 | 5.995279 |
| barrier | 0.709868 | 1.225982 |
| barrier+gap | 0.561252 | 0.894856 |
| barrier+gap+logQ | 0.506163 | 0.672229 |

**Integrity:** 175 out-of-region predictions, no test labels in training; regional folds uneven and some low-Z extrapolations are severe. Unlike v34, this tests contiguous element regions and partial alpha half-life. The added shell gap helps relative to composition+barrier *in this dataset*, and empirical logQ helps further; not a proof of generalizability. Full WKB tunneling integral, measured spin/parity hindrance, uncertainty-weighted refits remain future work.

KET `[stable{(test-zone)}]`: store typed barrier and shell evidence, do not treat structural closure alone as lifetime certification. Frozen 184/257 unchanged.
