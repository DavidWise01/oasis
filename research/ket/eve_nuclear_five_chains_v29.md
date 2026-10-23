# E.V.E. Experiment 29 — Five nuclear-shell chains

Executed 2026-10-23. Local reproducible Python and CSV files included in conversation ZIP `KET_EVE_Nuclear_v29.zip`.

Mass inputs: 23 isotope records from oxygen, nickel, tin, calcium, lead. Computed 13 adjacent two-neutron shell differences using `S2n(Z,A)=[M(Z,A-2)+2 m_n-M(Z,A)] c²`, `gap=S2n(N)-S2n(N+2)` with `m_n=1.00866491595 u`, `u c²=931.49410242 MeV`. Full precision retained in script.

| Isotope | Neutron shell | Gap (MeV) | Lifetime evidence |
|---|---:|---:|---|
| O-16 | 8 | 16.69865 | stable |
| Ni-78 | 50 | 3.41020 | 122.2 ms; **mass estimates**, tentative quantitative gap |
| Sn-132 | 82 | 6.52713 | 39.7 s |
| Ca-48 | 28 | 5.72187 | extremely long lived |
| Pb-208 | 126 | 4.98319 | stable |

Numerical PASS: 23 unique A/Z records, 13 computed gaps, isotope N=A-Z, positive computed S2n. These selected closures have positive discontinuities; this does not establish generic predictive accuracy of gap as a half-life estimator. Nickel isotope masses are estimated in NIST and/or AME sources, so the quoted Ni-78 gap is not independently experimentally established by this run. Sources: https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=8&isotype=all ; https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Ni&isotype=all ; https://pubchem.ncbi.nlm.nih.gov/element/Tin ; earlier Ca/Pb reference masses from v28.

Data partition: physical isotope mass estimates/measurements versus KET `[stable{(test-zone)}]` hypothesis. Closed nuclear shells need not imply stability. Next step should perform leave-one-nucleus-out predictions on held-out isotope chains and compare log half-life after conditioning on decay mode. Frozen 184/257 unchanged.