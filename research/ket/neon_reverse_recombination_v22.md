# Neon reverse shell test: bare Ne10+ → neutral Ne

Date: 2026-10-23. Reverse the previously committed Z10 ionization puncture experiment through 10 electron captures (capture order 1s ×2, 2s ×2, 2p ×6).

Reference: [NIST ASD Neon Ionization Energies](https://physics.nist.gov/cgi-bin/ASD/ie.pl?at_num_out=1&biblio=1&e_out=0&el_name_out=1&ion_charge_out=1&spectra=neon&unc_out=1&units=1).

| Charge before capture | Ionization-equivalent binding difference (eV) | Ground electron count after |
|---|---:|---:|
| +10 | 1362.199256 | 1 |
| +9 | 1195.808200 | 2 |
| +8 | 239.097000 | 3 |
| +7 | 207.271000 | 4 |
| +6 | 157.934000 | 5 |
| +5 | 126.247000 | 6 |
| +4 | 97.190000 | 7 |
| +3 | 63.423300 | 8 |
| +2 | 40.962970 | 9 |
| +1 | 21.564541 | 10 |

**Numerical PASS:** 11 endpoint states, 10 reversals, sum of all ground-state ionization thresholds = **3511.697267 eV**. The first two captures rebuild `1s²`; next two `2s²`; last six `2p⁶`. These are energy differences, not guaranteed individual photon energies or observable colors. Capture may involve radiative recombination, multi-step cascades, or collisional channels. The arbitrary selection of captures directly to ground states isn't a kinetic prediction.

Source examples for neutral neon: selected NIST line wavelengths 585.249 nm (yellow), 640.225 nm (red/orange), 703.241 nm (red), 837.761 nm (near-IR); these are observed transitions and **cannot** be assigned to particular capture steps without state-resolved spectroscopy.

Local executable `reverse_neon.py` and CSV results are available in the associated ChatGPT conversation ZIP. KET mapping: `[stable{(test-zone)}]`, closure at neutral Ne. Frozen 184/257 baseline unchanged.
