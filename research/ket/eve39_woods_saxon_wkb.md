# E.V.E. Experiment 39 — Woods–Saxon smooth potential WKB comparison

Executed 2026-10-23. Source NUBASE2020 `PavelStransky/NuclearProperties/nubase_4.mas20.txt`, blob SHA `05ec424175847f6ee948a075dc08963e4a688418`. Evaluated source: https://amdc.impcas.ac.cn/web/nubase_en.html . Physical reference for potential plus Coulomb: https://www.siegelsoft.com/reprints/ajp_78_949_2.pdf .

**Sample and holdout**: 175 alpha-dominant ground state nuclides with evaluated non-# parent/daughter/neighbor masses, numeric alpha branches/half-lives, positive Qalpha. Partial alpha lifetime target log10(s). Same five contiguous whole-atomic-number holdout regions as v38.

**Potential:** V(r) = 2(Z−2)*1.43996448/r − 40/[1+exp((r−R)/a)] MeV; R=1.2[(A−4)^(1/3)+4^(1/3)] fm. Reduced mass 4(A−4)/A × 931.49410242 MeV/c². No centrifugal term in this test. Solve V(r)=Qalpha by radial sign-change search followed by 40 bisection steps per crossing. Integrate 2/(ħ ln 10)∫[inner,outer]sqrt(2μ(V−Q))dr via 200 Simpson subintervals, ħc=197.3269804 MeV fm. Assault frequency from the prior v38 approximate interior-speed prescription. WKB T=(ln2)/(nu * exp(−2S)), with either (A) one training-fold residual offset, or (B) ridge-fitted composition + gap + smooth WKB action + log Q covariates. Therefore (B) is **not** a prediction from a pure ab initio potential.

| Potential depth MeV | Diffuseness fm | Numerical integral cases | Offset MAE (log10 s) | Offset RMSE | Fitted MAE | Fitted RMSE |
|---:|---:|---:|---:|---:|---:|---:|
| 40 | 0.50 | 175 | 0.473247 | 0.676098 | 0.428089 | 0.664954 |
| 40 | 0.65 | 175 | 0.474292 | 0.682029 | 0.431812 | 0.679050 |
| 40 | 0.80 | 175 | 0.478225 | 0.690959 | 0.436764 | 0.695321 |

Comparators from previous separately executed runs: v36 fitted external WKB MAE 0.421016, RMSE 0.630747; v38 external WKB with one global offset at r0=1.2, V0=40 MAE 0.478511 RMSE 0.672163. Smooth WS with single offset slightly improves MAE but worsens RMSE versus v38; fitted WS is worse than v36 fitted external WKB. Diffuseness grid exploratory based on test errors, not independent held-out hyperparameter selection.

**Outcome:** Structural WKB numerics PASS; claimed improvement over v36 FAIL. Missing angular-momentum centrifugal barriers, alpha preformation microphysics, deformation, quantization condition, model/data uncertainty propagation and nested parameter validation.

KET `[stable{(test-zone)}]`: commit mixed outcomes; frozen baseline 184/257 unchanged.
