# E.V.E. 38 — Alpha preformation calibration and parameter sensitivity

2026-10-23. Source NUBASE2020 `PavelStransky/NuclearProperties/nubase_4.mas20.txt` blob `05ec424175847f6ee948a075dc08963e4a688418`; Kondev et al., CPC 45, 030001 (2021); https://amdc.impcas.ac.cn/web/nubase_en.html .

**Evaluated set:** 175 alpha-dominant parent nuclei with non-estimated mass excesses for parent, alpha daughter, adjacent same-Z isotope pair, He-4; non-extrapolated half-lives, reported numeric alpha branching 0-100%, 0<Qalpha<20 MeV. Target is log10 of alpha *partial* half-life.

**Physical formula:** Coulomb-only exterior WKB action with surface radius R=r0[(A-4)^(1/3)+4^(1/3)] fm. An interior square-well depth V0 determines an attempt frequency v/(2R) only; the finite nuclear profile is NOT integrated. The raw log half-life presumes preformation=1.

**Calibration:** for each of 5 contiguous whole-Z held-out folds fit *one* train-only offset equal to mean_train(log10Tobserved−log10Traw). Apply to test nuclei unchanged. The offset confounds alpha preformation, nuclear interior and assault-frequency errors; do not interpret it as a measured physical preformation value. No test half-lives enter the fitted offset.

| r0 fm | V0 MeV | MAE log10 s | RMSE log10 s | Bias log10 s |
|---:|---:|---:|---:|---:|
| 1.10 | 40 | 0.466907 | 0.661643 | -0.021520 |
| 1.15 | 40 | 0.469172 | 0.663550 | -0.024866 |
| 1.20 | 20 | 0.479450 | 0.673720 | -0.028802 |
| 1.20 | 40 | 0.478511 | 0.672163 | -0.027962 |
| 1.20 | 60 | 0.478148 | 0.671567 | -0.027629 |
| 1.25 | 40 | 0.489731 | 0.686748 | -0.030818 |
| 1.30 | 40 | 0.502702 | 0.706522 | -0.033441 |

**Training offset logs by fold** (grounded all values):
```json
[{"radius":1.1,"well":40,"MAE":0.46690684816724226,"RMSE":0.6616433994969753,"bias":-0.021520238593112365,"folds":[{"fold":0,"from":4,"to":68,"test":9,"offset":0.04904228671690621},{"fold":1,"from":69,"to":79,"test":13,"offset":0.04169150203169885},{"fold":2,"from":80,"to":86,"test":51,"offset":0.02363456257512357},{"fold":3,"from":87,"to":93,"test":77,"offset":-0.016558006274763032},{"fold":4,"from":94,"to":102,"test":25,"offset":0.050323764136072174}]},{"radius":1.15,"well":40,"MAE":0.469172461795988,"RMSE":0.6635500850205417,"bias":-0.0248660379446689,"folds":[{"fold":0,"from":4,"to":68,"test":9,"offset":0.6953383210358343},{"fold":1,"from":69,"to":79,"test":13,"offset":0.6838044654090034},{"fold":2,"from":80,"to":86,"test":51,"offset":0.6658689014462574},{"fold":3,"from":87,"to":93,"test":77,"offset":0.6127861605745258},{"fold":4,"from":94,"to":102,"test":25,"offset":0.6749671893594043}]},{"radius":1.2,"well":20,"MAE":0.4794496457070896,"RMSE":0.6737204864321704,"bias":-0.028802125151138808,"folds":[{"fold":0,"from":4,"to":68,"test":9,"offset":1.203390734437851},{"fold":1,"from":69,"to":79,"test":13,"offset":1.187308706777287},{"fold":2,"from":80,"to":86,"test":51,"offset":1.169091646316069},{"fold":3,"from":87,"to":93,"test":77,"offset":1.1020580690328128},{"fold":4,"from":94,"to":102,"test":25,"offset":1.1615252117110235}]},{"radius":1.2,"well":40,"MAE":0.4785108633020185,"RMSE":0.6721628063420855,"bias":-0.027962110754038753,"folds":[{"fold":0,"from":4,"to":68,"test":9,"offset":1.3233877261765594},{"fold":1,"from":69,"to":79,"test":13,"offset":1.3078383707288241},{"fold":2,"from":80,"to":86,"test":51,"offset":1.290128138930611},{"fold":3,"from":87,"to":93,"test":77,"offset":1.2248199920988523},{"fold":4,"from":94,"to":102,"test":25,"offset":1.2818660359982323}]},{"radius":1.2,"well":60,"MAE":0.4781479613587657,"RMSE":0.6715670407400177,"bias":-0.027628591863377204,"folds":[{"fold":0,"from":4,"to":68,"test":9,"offset":1.400201666582773},{"fold":1,"from":69,"to":79,"test":13,"offset":1.384850546142711},{"fold":2,"from":80,"to":86,"test":51,"offset":1.367335273066417},{"fold":3,"from":87,"to":93,"test":77,"offset":1.3027286898634987},{"fold":4,"from":94,"to":102,"test":25,"offset":1.3588016857910712}]},{"radius":1.25,"well":40,"MAE":0.48973069621576226,"RMSE":0.6867483128506057,"bias":-0.030817802575154155,"folds":[{"fold":0,"from":4,"to":68,"test":9,"offset":1.9341690500814954},{"fold":1,"from":69,"to":79,"test":13,"offset":1.9147635947246346},{"fold":2,"from":80,"to":86,"test":51,"offset":1.897379723615282},{"fold":3,"from":87,"to":93,"test":77,"offset":1.8204834554261478},{"fold":4,"from":94,"to":102,"test":25,"offset":1.871967868020342}]},{"radius":1.3,"well":40,"MAE":0.5027015507840576,"RMSE":0.7065221941707169,"bias":-0.03344142433339327,"folds":[{"fold":0,"from":4,"to":68,"test":9,"offset":2.528564727248861},{"fold":1,"from":69,"to":79,"test":13,"offset":2.505455212635683},{"fold":2,"from":80,"to":86,"test":51,"offset":2.4884961384434265},{"fold":3,"from":87,"to":93,"test":77,"offset":2.400624553471893},{"fold":4,"from":94,"to":102,"test":25,"offset":2.446127128113381}]}]
```

For context, v37 direct parity-preformation approximation MAE=0.834605, fully formed S=1 MAE=1.291200; v36 multivariate empirical WKB fit MAE=0.421016 (different number of fitted parameters). Comparison establishes sensitivity, **not** that the tuned grid has independently generalized: seven parameter sets were compared against the same held-out outcomes, which makes any best-selection exploratory. No source measurement uncertainty was propagated. Still does not calculate full finite interior WKB or individual microscopic alpha-cluster formation.

KET `[stable{(test-zone)}]` retains previous structural validation and numerical limitations. Frozen 184/257 unchanged.
