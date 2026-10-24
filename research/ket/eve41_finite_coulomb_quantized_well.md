# E.V.E. 41 — Finite uniformly charged nuclear sphere and quantized Woods–Saxon well

Executed 2026-10-23 against NUBASE2020 mirror `PavelStransky/NuclearProperties/nubase_4.mas20.txt`, blob `05ec424175847f6ee948a075dc08963e4a688418`.
Physics reference Duarte and Siegel American Journal of Physics 78, 949 (2010), https://siegelsoft.com/reprints/ajp_78_949_2.pdf.

Potential: Woods–Saxon −V0/[1+exp((r−R)/0.65)] plus uniform sphere Coulomb C(3R²−r²)/(2R³) for 0<=r<=R and C/r beyond R. R=1.2[(A−4)^(1/3)+4^(1/3)] fm, C=2(Z−2)1.43996448 MeV fm; reduced mass 4(A−4)/A*931.49410242 MeV.
Even-even cohort, partial alpha decay half-life log10 seconds. Quantization condition integral r=0..inner turning point sqrt[2μ(Q−V)]/(ħc)dr=(G+1)π/2; G(N) 18 for N<=82,20 for 82<N<=126,22 above 126. This boundary differs from point-Coulomb interior two-turning-point quantization, so the two models cannot be regarded as changing only Coulomb charge size while holding the complete boundary condition fixed.
Outer barrier integral via Simpson's rule (80 panels), radial root scan 0.055fm, binary turning-point precision 24 bisections, depth 20..350MeV with 19 bisections, no centrifugal term. Assault frequency same simplified rule as v40. Fit one average residual offset on training isotope regions only, compare on common converged nuclei.

Results:
```json
{
  "eligible": 73,
  "convergedFinite": 72,
  "convergedPoint": 72,
  "failures": {
    "finite": [
      {
        "Z": 4,
        "A": 8,
        "reason": "target not bracketed by depth upper limit"
      }
    ],
    "point": [
      {
        "Z": 4,
        "A": 8,
        "reason": "target not bracketed by depth upper limit"
      }
    ]
  },
  "Be8Finite": null,
  "common": 72,
  "metric": {
    "finite": {
      "MAE": 0.218451244104229,
      "RMSE": 0.28730540815744193
    },
    "point": {
      "MAE": 0.24312232816989696,
      "RMSE": 0.31367633841543224
    }
  },
  "folds": [
    {
      "fold": 0,
      "Zmin": 52,
      "Zmax": 64,
      "n": 5
    },
    {
      "fold": 1,
      "Zmin": 66,
      "Zmax": 76,
      "n": 4
    },
    {
      "fold": 2,
      "Zmin": 78,
      "Zmax": 84,
      "n": 14
    },
    {
      "fold": 3,
      "Zmin": 86,
      "Zmax": 92,
      "n": 33
    },
    {
      "fold": 4,
      "Zmin": 94,
      "Zmax": 102,
      "n": 16
    }
  ],
  "depthFinite": [
    99.22793388366699,
    112.48425483703613
  ],
  "maxQuantResidual": 0.00007734082483779048
}
```

Limits: the finite-sphere electrostatic model is idealized, the G assignment assumed, the action at origin uses uncorrected l=0 radial WKB quantization and may require Langer/phase corrections; errors from root mesh and Simpson discretization unquantified. Parameter depth is tuned to each known alpha Q but not to lifetime. Failure of root convergence is logged. Best physical interpretation is a controlled numerical benchmark, not a novel nuclear stability discovery.
KET stable shell baseline unchanged. Next: include centrifugal Langer correction and root convergence tests.