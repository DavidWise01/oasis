# E.V.E. 40 — Bohr–Sommerfeld-constrained Woods–Saxon nuclear well

Executed 2026-10-23. Original NUBASE2020 data mirrored at PavelStransky/NuclearProperties/nubase_4.mas20.txt, blob SHA 05ec424175847f6ee948a075dc08963e4a688418. Citation: Kondev et al., Chinese Physics C 45, 030001 (2021).

Reference for BSQC nuclear-well models: Nguyen et al., Nuclear Physics A 1069 (2026) 123352 https://www.sciencedirect.com/science/article/pii/S0375947426000308 ; https://cpc.ihep.ac.cn/article/doi/10.1088/1674-1137/ad3d4b

Protocol: select 73 even-even alpha-dominant nuclei from the 175-case prior dataset. Require NUBASE2020 non-# masses and half-lives, parent/daughter/neighbor masses, numeric alpha branching, Qalpha>0. Target log10(partial alpha lifetime seconds).

Potential V(r)=2(Z−2)×1.43996448/r−V0/[1+exp((r−R)/0.65)] (MeV), R=1.2[(A−4)^(1/3)+4^(1/3)] fm, reduced mass μ=4(A−4)/A×931.49410242 MeV. Point-Coulomb near origin gives THREE radial roots for positive Q: r1 and r2 bound the *interior allowed* well and r2 and r3 bound the forbidden tunneling region.

Bohr–Sommerfeld condition ∫(r1→r2) sqrt[2μ(Q−V)]/(ħc) dr = (G+1)π/2. G=18 if N<=82, G=20 if 82<N<=126, else G=22 (a convention specific to this model; not an experimentally measured universal assignment). Numerical root search + bisection of V0 in 20..350 MeV, inner/outer root scans 0.05 fm, integral by Simpson 100 panels; 19 iterations depth bisection. To estimate decay half-life, compute external action r2..r3, penetrability exp(−2S), assault frequency from Q+V0 as in v37.

Quantization solved for 72/73 even-even nuclei (unresolved Be-8 due to the chosen potential/energy bracket). Solution V0 range 144.9336..167.8661 MeV and maximum action target discrepancy 6.25e−5. These are model-dependent fitted-to-Q quantization depths, not independent measurements.

Five whole-Z contiguous-region holdout blocks. In each fold train-only single offset = average [observed log10T − raw theoretical log10T], then score held-out nuclei. Compare *on the exact same 72 solved cases* quantized depth versus fixed depth 40 MeV using the same point-Coulomb potential and separate train-only offsets.

| Model | N | MAE log10 seconds | RMSE log10 seconds |
|---|---:|---:|---:|
| Fixed 40 MeV depth | 72 | 0.268753 | 0.337243 |
| Quantized depth | 72 | 0.242363 | 0.313535 |

MAE improves ≈9.82%. This is an **in-sample model-design / out-of-region lifetime** benchmark, not independent blind validation. In particular Qalpha comes from evaluated nuclear masses, and G assignments are externally chosen. The 2026 referenced study's own potential differs, so outputs are not direct replication. Be-8 failure remains logged, no extrapolation to Og-294 made. No spin-coupled angular momentum, deformation or error propagation.

KET [stable{(test-zone)}]: store success count 72/73 and failure Be-8, preserve frozen 184/257 baseline. Next: finite-sized Coulomb, consistent centrifugal terms, root failure and model uncertainty.
