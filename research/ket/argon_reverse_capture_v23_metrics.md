# KET Experiment 23 — Argon reverse-capture cascade metrics

Executed local numerical test 2026-10-23. Input grammar preserved exactly: `. . | | . . | . . . . | | |` (8 dots, 6 bars, 14 operators). KET `|` means close and inherit; it is an independent symbolic register and is **not** forced onto 18 physical electrons.

## Verified atomic test
Rebuild bare Ar18+ with 18 consecutive electron captures to neutral Ar. Source: [NIST ASD 18 sequential argon ionization energies](https://physics.nist.gov/cgi-bin/ASD/ie.pl?at_num_out=1&biblio=1&e_out=0&el_name_out=1&ion_charge_out=1&spectra=argon&unc_out=1&units=1) (v5.12). Raw energy values and flags transcribed from the source table. NIST designates 3 unbracketed, 12 square-bracketed and 3 parenthesized energy entries, reflecting differing provenance; do not conflate with 18 independently measured transitions.

Captures fill `1s²` (2), `2s²` (4), `2p⁶` (10, neon core), `3s²` (12), `3p⁶` (18, argon closure). All individual capture energies, uncertainties, electron configurations, cumulative sums, energy-equivalent wavelengths, closure flags, and deltas are in the ZIP/CSV delivered with the conversation. Sum of 18 ground-state capture binding differences: **14,400.8556419 eV**, under the ion/electron reference convention. **19 endpoint states / 18 transitions / 5 subshell closures.**

These threshold-equivalent wavelengths do **not** identify emitted photons or colors in an actual radiative cascade. For actual color samples, source [NIST Argon strong lines](https://physics.nist.gov/PhysRefData/Handbook/Tables/argontable2_a.htm), 8 selected Ar I lines: 588.8584, 696.5431, 706.7218, 750.3869, 763.5106, 794.8176, 811.5311, 912.2967 nm. They are not mapped to individual capture steps without state-resolved transition rates.

## Tests
PASS: 18 captures, 19 endpoint records, 5 closure locations, 8-dot/6-bar primitive exact count, total-energy summation, positive threshold energies, no invented 14-to-18 correspondence, recorded measured emission samples separately.

## Boundary
A real radiative-cascade calculation requires transition rates, energy levels, and branching fractions for Ar I–Ar XVIII. NIST's [compiled energy levels and observed spectral lines](https://www.nist.gov/publications/energy-levels-and-observed-spectral-lines-ionized-argon-ar-ii-through-ar-xviii) can provide a starting point. No cascade photon-count, branching ratio, pulse timing, or emitted spectrum has been executed here. Frozen 184/257 KET baseline unchanged.
