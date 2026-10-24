# E.V.E. 33 — 2026-10-23 broad NUBASE2020 decay-specific holdout

Data retrieved from public GitHub mirror of the original nuclear evaluation, `PavelStransky/NuclearProperties/nubase_4.mas20.txt`, blob `05ec424175847f6ee948a075dc08963e4a688418`. Source: Kondev et al., Chinese Physics C45 030001 (2021). Evaluated historical data, **not newly measured**. Parsed 2550 non-# ground-state mass excesses, 1146 ground-state beta-/alpha decay records with numeric non-# half-life, and 917 cases with all three local NUBASE mass excesses required for S2n and Δ2n. Excluded extrapolated (#) masses, half-lives with bounds or extrapolation, unsupported dominant decay modes, missing neighboring masses, and implausible |gap|>45 MeV.

S2n = [MX(Z,A−2)+2 MX(neutron)−MX(Z,A)]/1000 MeV. MX(neutron)=8071.3181 keV. Δ2n = S2n(Z,A)−S2n(Z,A+2).

Five leave-element-group-out folds: group Z mod 5. Within each mode, compared ridge least squares for log10(T seconds): baseline [1,Z/80,N/Z,A/200,oddZ,oddN] versus baseline plus [Δ2n/10], penalty 0.5 except intercept. No test half-lives used in training for that fold. Prediction units log10(seconds); MAE/MSE on log scale (one unit = factor ten). **Not a blind preregistered external dataset**.

{
  "beta-": {
    "n": 740,
    "mae_baseline": 1.585556365680882,
    "mae_shell": 1.5675951062445097,
    "rmse_baseline": 2.2757028042180223,
    "rmse_shell": 2.2563504082289514,
    "range": [
      -2.5346171485515816,
      14.70700749747128
    ]
  },
  "alpha": {
    "n": 177,
    "mae_baseline": 3.936499565090073,
    "mae_shell": 3.9806196032418812,
    "rmse_baseline": 5.086297884054645,
    "rmse_shell": 5.338912808874899,
    "range": [
      -16.08671609823958,
      15.409194512679296
    ]
  }
}

**Interpretation:** Metrics are predictive model comparison inside this selected historical evaluation. Shell gap may help one mechanism and hurt another. No universal isotope lifetime prediction or mechanistic proof. Results in the initial E.V.E. 31 sample are not overwritten.
