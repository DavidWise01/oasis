# E.V.E. 46 — Alpha–alpha phase-shift data sufficiency gate

Run date: 2026-10-24. Executable `eve46.py`, `audit.csv`, and `summary.json` generated and executed in conversation.

## Independent source observations
- Heydenburg & Temmer, *Physical Review* **104**, 123 (1956), https://doi.org/10.1103/PhysRev.104.123 : alpha-on-He lab energies **150 keV to 3 MeV**; near pure Coulomb/Mott cross sections below **400 keV lab** within quoted experimental accuracy; S-wave phase shift approximately **128° at 3 MeV lab**; D-wave onset near **2.5 MeV lab**, D-wave angle about **2.5° at 3 MeV lab**. These are source-described observations, not a table of phase shift at each energy.
- Be-8 ground state lies **91.84 keV center-of-mass** above the alpha–alpha threshold, as used in EVE44. For equal-mass target/projectile scattering (nonrelativistic), **E_cm = E_lab/2**. Thus the resonance corresponds to **183.68 keV lab**, inside the earlier experiment's 150–3000 keV scan range and below its approximate 400 keV Coulomb-dominated region. Absence of a resolvable feature in the 1956 setup is not absence of the narrow resonance.

## Executed checks
1. Two-body lab/center-of-mass conversion PASS: 91.84×2=183.68 keV.
2. Experimental energy coverage PASS: 150 < 183.68 < 3000 keV.
3. Consistency with reported near-Coulomb low-energy region PASS: 183.68 < 400 keV; due to finite instrumental resolution this does **not** contradict the existence of the narrow Be-8 resonance.
4. S-wave high-energy angle, D-wave high-energy angle, D-wave approximate onset: recorded as external source anchors, **not** independently predicted.
5. Fit of Coulomb-modified effective-range parameters from independently measured phase-shift samples: **BLOCKED**, numeric phase-shift series with uncertainties not acquired.
6. Quantitative held-out phase-shift model error: **NOT RUN**. One approximate numerical S-wave anchor (128° at 3 MeV) cannot sustain a training-versus-holdout numeric test. Qualitative statements about low-energy phase shifts are not fabricated into measurements.

**Verdict:** 3 numerical consistency passes, two blocked predictive gates. Unlike EVE45, no false claim of an independent resonance-width or phase-shift prediction. Next experiment should obtain digitized experimental points with provenance, uncertainty and E_lab/E_cm units, then pre-register withheld energy intervals and fit only training data.

KET `[stable{(test-zone)}]`: preserve the physical reference observations, keep predictive-validation state open. Frozen 184/257 baseline unchanged.