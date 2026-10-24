# E.V.E. 42 — Langer radial correction and convergence audit

Executed 2026-10-23. NUBASE2020 source `PavelStransky/NuclearProperties/nubase_4.mas20.txt` (Kondev et al. CPC 45 030001 2021), same 73 even-even alpha-dominant candidate records as EVE40–41. Spin-zero alpha emission taken as orbital l=0 for this structural test.

**Potential:** finite uniformly charged nuclear sphere plus Woods–Saxon nuclear attractive well V0/[1+exp((r-R)/0.65)] with added Langer centrifugal term ħ²(l+1/2)²/(2μr²), even for l=0. Quantize the 2-turning-point inner classically allowed region using action target (G+1)π/2; G=18,20,22 by N, following the previous prototype convention. Outer forbidden region integrated by Simpson. Root search begins at r=.001 fm to capture the narrow inner turning point created by 1/r² divergence.

**Solver convergence (test at two resolutions):**
- Langer/coarse: radial scan 0.04 fm, Simpson 80 panels; 72/73 solved, Be-8 unresolved; max absolute Bohr–Sommerfeld action residual 3.979754e−5.
- Langer/fine: radial scan 0.02 fm, Simpson 160 panels; 72/73 solved, Be-8 unresolved; max residual 3.763900e−5.
- Maximum per-nucleus difference in solved well depth between coarse and fine = 0.200157 MeV.
- The *uncorrected implementation in this run* unexpectedly converged for only 35/73 at coarse settings, unlike the 72/73 previously recorded under the v41 implementation. This is a **solver regression** requiring root bracketing examination; a 72-versus-72 comparison against v41 is NOT validated.

**Matched 34-nucleus diagnostic**, only nuclei converging under original/coarse Langer/fine Langer. All models fit a single log-lifetime offset within five held-out contiguous sorted-Z blocks for this reduced matched set (this split differs from the 72-case v41 split):
| Solver | Matched N | MAE log10(s) | RMSE log10(s) |
|---|---:|---:|---:|
| Uncorrected fresh solver | 34 | 0.304463 | 0.401583 |
| Langer coarse | 34 | 0.255065 | 0.351486 |
| Langer fine | 34 | 0.254056 | 0.351925 |

**Interpretation:** Langer quantization numerically viable for 72/73 at two resolutions. Reduced-subset numerical comparison suggests improvement but is not enough to claim full-model superiority. The uncorrected regression and Be-8 unresolved are explicit FAIL/PENDING gates. Spin/parity-specific centrifugal effects for l>0 not included, physical uncertainty, and independent measurements of well depth not demonstrated. The use of unchanged G values after modifying radial phase conditions is a model assumption requiring check.

KET `[stable{(test-zone)}]` freezes only converged facts; previous 184/257 baseline untouched. Next EVE: repair v41 vs v42 matched full dataset and check root bracketing plus adaptive quadrature.
