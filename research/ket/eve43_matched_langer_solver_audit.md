# E.V.E. 43 — Matched Langer / finite-Coulomb solver repair

Date: 2026-10-23. Source NUBASE2020 mirror `PavelStransky/NuclearProperties/nubase_4.mas20.txt`, blob `05ec424175847f6ee948a075dc08963e4a688418`. Ground-state alpha-dominant even-even nuclei with unflagged masses, numeric partial alpha half-life, and neighboring masses. Input n=73.

Potential and quantization same as v41/42: uniform charged sphere + Woods–Saxon (a=.65fm), R=1.2[(A−4)^(1/3)+4^(1/3)]fm, with optional Langer ħ²/(8μr²). Inner allowed action target (G+1)π/2 with G by N as v41. Solver uses 28-step bisection for sign-change roots, 21 depth bisections 20..350MeV, 100 or 200 Simpson panels. Langer's scan begins at .005fm, uncorrected finite sphere at 0. The starting position matters for the narrow inner Langer root.

Results:
```json
{
  "cohort": 73,
  "runs": [
    {
      "name": "finite-base",
      "converged": 72,
      "fail": [
        "4-8"
      ],
      "maxResidual": 0.000018177573970490357
    },
    {
      "name": "langer",
      "converged": 72,
      "fail": [
        "4-8"
      ],
      "maxResidual": 0.000019722106365804848
    },
    {
      "name": "base-fine",
      "converged": 72,
      "fail": [
        "4-8"
      ],
      "maxResidual": 0.000018590394816442313
    },
    {
      "name": "langer-fine",
      "converged": 72,
      "fail": [
        "4-8"
      ],
      "maxResidual": 0.00001950803296324466
    }
  ],
  "matched": 72,
  "scores": [
    {
      "name": "finite-base",
      "mae": 0.21824033536192564,
      "rmse": 0.2873510583059363
    },
    {
      "name": "langer",
      "mae": 0.2190414447118293,
      "rmse": 0.2881685185562636
    },
    {
      "name": "base-fine",
      "mae": 0.21829161364335298,
      "rmse": 0.2876225296629545
    },
    {
      "name": "langer-fine",
      "mae": 0.21910925100249676,
      "rmse": 0.2884358952082274
    }
  ],
  "refineDelta": [
    {
      "name": "finite-base",
      "maxDepthChange": 0.014634132385253906
    },
    {
      "name": "langer",
      "maxDepthChange": 0.14209270477294922
    }
  ]
}
```

All predictive comparison scores are computed on the exact same `72` matched nuclei with five contiguous-Z leave-region-out fits. **Calibration one train-only offset per model and fold.** Baseline and Langer quantization conditions have different inner radial boundary phases, so this is numerical model comparison, not isolation of only an added physical term. The two resolutions share retrospective isotope data, not prospectively independent validation.

Interpretation: do not claim general improvement if Langer exceeds baseline error. Numerical convergence judged on both depth and score; Be-8 exceptions remain explicit. Frozen KET baseline unchanged.
