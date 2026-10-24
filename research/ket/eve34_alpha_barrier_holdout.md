# KET E.V.E. Experiment 34 — Alpha-decay tunneling-barrier feature

**Run date:** 2026-10-23. **Source:** Kondev et al., NUBASE2020 table, reproduced at `PavelStransky/NuclearProperties/nubase_4.mas20.txt`. The prior v33 file already used the same retrospective data source; https://amdc.impcas.ac.cn/web/nubase_en.html . Scientific reference for ground-state atomic-mass Q-alpha definition: https://doi.org/10.1088/1674-1137/abddb0 .

**Sample:** 2550 non-extrapolated masses in loaded file; 227 alpha-dominant records with non-# numeric half-lives; **177** eligible with parent, daughter, A−2 and A+2 mass excesses and 0 < Q-alpha < 20 MeV. Excluded estimated (#) half-lives and masses; no censored outcomes included. Helium-4 mass excess 2424.91587 keV. Ground-state Q-alpha = [MX(parent)−MX(daughter)−MX(He4)] / 1000 MeV; nuclear 2n gap = [MX(Z,A−2)+MX(Z,A+2)−2 MX(Z,A)] / 1000 MeV. Q range: 0.09183826 .. 10.19508413 MeV.

**Validation:** Five folds, entire elemental group withheld by Z mod 5; fold test counts 31,42,32,34,38. Fit separately in each fold by ridge least-squares with penalty 0.5 except intercept, predicting log10(half-life seconds). No held-out half-life used for fitting.

| Features | MAE log10(s) | RMSE log10(s) |
|---|---:|---:|
| composition [1,Z/80,N/Z,A/200,Z%2,N%2] | 3.936499565 | 5.086297884 |
| composition + gap/10 | 3.980619603 | 5.338912809 |
| composition + (Z−2)/sqrt(Q-alpha) | **0.584617725** | **1.089610255** |
| composition + barrier + gap/10 | **0.516400043** | **0.858419554** |

**Conclusion:** Explicit alpha-energy barrier feature greatly improves held-out prediction in this evaluated dataset. Once barrier feature included, adding the gap improves this sample's errors as well. However the mode is known from the evaluation, barriers are highly correlated with decay half-lives, and ground-state nuclei with other decay modes are not predicted. Masses and half-lives are from the same retrospective NUBASE2020 evaluation (not a prospectively preregistered blind evaluation). The feature (Z−2)/sqrt(Q) is simplified Geiger–Nuttall motivation, not a full WKB transmission derivation. Branching ratios not used to correct total half-life into partial alpha half-life; minor competing channels can affect truth labels. Confidence and generalizability remain open.

Symbolic KET `[stable{(test-zone)}]`: energy permission is separate from escape probability and stability. Frozen 184/257 baseline unchanged.

**Next E.V.E. 35:** add alpha branching-corrected partial half-lives, an explicit WKB barrier term, parity/spin-hindrance, and hold out entire *regions* of atomic number rather than interleaved Z%5 groups.
