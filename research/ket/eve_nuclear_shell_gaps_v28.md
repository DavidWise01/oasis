# E.V.E. Experiment 28 — Neutron shell-gap discontinuities

Executed locally 2026-10-23; 11 isotope mass records from selected Ca and Pb isotope chains.

**Formula:** S2n(Z,A) = [M(Z,A−2)+2mn−M(Z,A)] × 931.49410242 MeV/u, Δ2n(N) = S2n(N)−S2n(N+2). Neutral-atom masses share the same Z so electron masses cancel; small electronic-binding corrections and mixed-source rounding are not modeled.

**Ca-48 (Z20, N28):** S2n(Ca46)=17.81240, S2n(Ca48)=17.22898, S2n(Ca50)=11.50711 MeV; gap at N28 = **5.72187 MeV**. Nearby gap at Ca46 ≈0.58341 MeV.

**Pb-208 (Z82, N126):** S2n(Pb206)=14.81833, S2n(Pb208)=14.10573, S2n(Pb210)=9.12255 MeV; gap at N126 = **4.98319 MeV**. Nearby gap at Pb206 ≈0.71260 MeV.

**Local tests PASS:** two discontinuities >2 MeV, stronger than immediately preceding gaps, A=Z+N checks, 11-record registry. Source masses: NIST and AME-derived PubChem/CIAAW references:
- https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?all=all&ascii=ascii2&isotype=all
- https://pubchem.ncbi.nlm.nih.gov/element/82
- https://www.ciaaw.org/lead.htm
- https://pubchem.ncbi.nlm.nih.gov/element/Calcium

**Caveat:** Only selected Ca/Pb chains; no universal shell-gap detection performance, stability guarantee, or isotope lifetime predictions. Heavy nuclear deformation, pairing and competing decay modes require additional analyses. Data/code artifact: local `eve_shell_gap_v28.py`, `shell_gap_metrics_v28.csv`, `summary_v28.json` distributed with conversation.

KET `[stable{(test-zone)}]` may store measured gap and validation scope; frozen 184/257 unchanged.
