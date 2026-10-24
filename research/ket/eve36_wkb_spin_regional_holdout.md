# E.V.E. 36 — WKB alpha barrier and spin/parity test

2026-10-23; NUBASE2020 from `PavelStransky/NuclearProperties/nubase_4.mas20.txt`, blob 05ec424175847f6ee948a075dc08963e4a688418; original nuclear evaluation Kondev et al. 2021 https://amdc.impcas.ac.cn/web/nubase_en.html . WKB reference: https://cpc.ihep.ac.cn/article/doi/10.1088/1674-1137/ad3d4b .

**Physical barrier approximation:** surface R=1.2 [(A−4)^(1/3)+4^(1/3)] fm; daughter charge Zd=Z−2, Coulomb V(r)=2Zd×1.43996448/r MeV, reduced mass μ=[4(A−4)/A]×931.49410242 MeV/c²; ħc=197.3269804 MeV fm. Numerical Simpson 120 subdivisions evaluates `S=int_R^b sqrt(2μ(Vc(r)+hbar²l(l+1)/(2μr²)−Q))/hbar dr` and `−log10(P)=2S/ln(10)`; outer turning point quadratic root for l≥0. No inner nuclear potential, realistic preformation, assault frequency, deformations, or excited daughter level treatment. Spin/parity l derived only from unambiguous parent+daughter Jπ with triangle and parity selection for emitted alpha 0+.

**Dataset:** 175 evaluable alpha-dominant, observed/assigned unflagged masses, numeric half-lives, alpha branching fractions and two-neutron gap, 86 unambiguous parent/daughter spin/parity pairs, 1 with nonzero required angular momentum.

**Test protocol:** five contiguous sorted-Z holdouts; ridge regression λ=0.5 on log10(partial alpha half-life, seconds), covariates [1,Z/80,N/Z,A/200,Z%2,N%2,gap/10,log10 Q] plus empirical (Z−2)/sqrt Q or computed WKB action. All fit coefficients trained without held-out atomic numbers. Same folds for compared models within each cohort.

## Full cohort 175

{
  "emp": {
    "MAE": 0.5061631684001714,
    "RMSE": 0.6722288621988806
  },
  "wkb": {
    "MAE": 0.4210161489614197,
    "RMSE": 0.6307470135345126
  }
}

## Matched spin-known cohort 86

{
  "emp": {
    "MAE": 0.5244147723630376,
    "RMSE": 0.702363981293954
  },
  "wkb": {
    "MAE": 0.3276739257035411,
    "RMSE": 0.5140412449739613
  },
  "wkbL": {
    "MAE": 0.32697452077822275,
    "RMSE": 0.5285762184409369
  }
}

Full folds: [{"fold":0,"Zmin":4,"Zmax":68,"n":9},{"fold":1,"Zmin":69,"Zmax":79,"n":13},{"fold":2,"Zmin":80,"Zmax":86,"n":51},{"fold":3,"Zmin":87,"Zmax":93,"n":77},{"fold":4,"Zmin":94,"Zmax":102,"n":25}]
Spin-known folds: [{"fold":0,"Zmin":4,"Zmax":64,"n":6},{"fold":1,"Zmin":66,"Zmax":78,"n":6},{"fold":2,"Zmin":79,"Zmax":86,"n":29},{"fold":3,"Zmin":87,"Zmax":91,"n":22},{"fold":4,"Zmin":92,"Zmax":102,"n":23}]

**Limits:** WKB implemented for external Coulomb and centrifugal barriers only and calibrated with other covariates. The spin-known subset is selected, may not generalize to unknown transitions; nominal nuclear spins sometimes uncertain in evaluation and omitted. Comparing full-cohort score to matched-cohort score is invalid; compare models within matched cohort. No literal measurement of alpha preformation. Uncertainties not propagated. Baseline frozen.
