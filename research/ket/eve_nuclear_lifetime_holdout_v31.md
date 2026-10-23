# E.V.E. Experiment 31 — Does the shell gap predict nuclear lifetime?

Executed 2026-10-23. Local reproducible code and 13-row selected dataset in `KET_EVE_Nuclear_v31.zip` (conversation attachment). Five leave-one-element-out training/test splits (O, Ni, Sn, Ca, Pb); no held-out element appears in its training fold. Retrospective evaluation, not a prospective blind test.

**Target:** half-life >=1 year or no observed decay (long-lived), vs half-life <1 year. Ca-48 (5.6e19 years two-neutrino beta decay) is long-lived despite being radioactive. Stable nuclides are censored, NOT assigned arbitrary infinity as training values. Underlying physical half-life sources IAEA LiveChart, NUBASE, and PubChem elements:
https://iaea-nds.github.io/lc_api_notebook/
https://pubchem.ncbi.nlm.nih.gov/element/Nickel
https://pubchem.ncbi.nlm.nih.gov/element/Tin
https://pubchem.ncbi.nlm.nih.gov/element/Calcium
https://www.nndc.bnl.gov/nudat3/

| Model | Held-out accuracy | Brier score (lower better) | Log loss |
|---|---:|---:|---:|
| Training-prevalence majority | 8/13 = .61538 | .32247 | .85288 |
| Standardized Z + N/Z logistic | 9/13 = .69231 | .25271 | .89700 |
| Standardized Z + N/Z + measured/estimated shell gap logistic | 9/13 = .69231 | .25664 | .90394 |
| Shell gap alone logistic | 6/13 = .46154 | .33101 | .87196 |

**Interpretation:** On this small selected sample, shell-gap feature did not improve binary long-lived classification and slightly worsened Brier and log-loss when added to composition. This is an important **FAIL of improved predictive value**, not a failure of the physical nuclear shell effect itself. Ni mass and thus shell gaps estimated. The chosen set is heavily selection-biased, with multiple decay channels, and cannot establish general usefulness/unusefulness. Next EVE should acquire broad NUBASE/AME case coverage, pre-register an unseen-chain split and stratify by decay channel.

KET `[stable{(test-zone)}]` stores structural PASS and predictive-value FAIL as distinct typed tests. Existing frozen 184/257 foundation unchanged.