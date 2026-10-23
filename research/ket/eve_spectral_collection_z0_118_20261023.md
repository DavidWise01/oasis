# KET E.V.E. spectral shell atlas — verified execution 2026-10-23

E.V.E. = **Extrapolate → Verify → Execute**. Target: Z0 pinned reference through Z118 oganesson. **Scope:** source-backed atomic *spectral transitions* and KET closure generations, not physical tunneling through atomic shells.

## Execute
Offline Python build `eve_build.py` and helper `collect_1_118.py` generated outputs:
- `observed_lines.csv`: **70 source-checked selected NIST strong-line records covering 11 elements:** H(1), He(2), Li(3), Ne(10), Na(11), Ca(20), Fe(26), Au(79), Rn(86), U(92), Es(99).
- `coverage_0_118.csv`: **119 addresses** (Z0 symbolic plus 118 established elements), 7 inherited generations with closures 2,10,18,36,54,86,118.
- `hydrogen_extrapolated.csv`: 13 calculated Balmer series transitions n=3..15; **predictions not counted among the 70 measured entries**.
- `eve_summary.json`: machine-readable counts and warnings.

## Verify
All entries: positive wavelength, correct KET period/index, source URL, color-bin classification, unique (element, ion, wavelength) key, and photon energy with E[eV] = 1239.841984 / lambda[nm]. Offline checks **PASS**.

Hydrogen model is reduced-mass Rydberg formula in vacuum, converted approximately to air for comparison with published hydrogen Balmer lines:
| Transition | Predicted air nm | Published line air nm | Difference nm |
|---|---:|---:|---:|
| 3→2 | 656.288315 | 656.2711 | +0.01721 |
| 4→2 | 486.137986 | 486.12786 | +0.01013 |
| 5→2 | 434.050993 | 434.0462 | +0.00479 |
The nonzero differences are expected from approximations and neglected structure (Rydberg-only). Do not claim precision atomic physics from this formula.

## Classified measured subset
UV 44; violet 10; blue 3; teal/cyan 1; green 2; red 5; IR 5. Not a full population statistic; specifically sampled lines. No orange/yellow line happened to be among the chosen records, which does not imply they do not exist.

## Source evidence
NIST SRD108 strong lines tables:
https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable2.htm
https://physics.nist.gov/PhysRefData/Handbook/Tables/heliumtable2.htm
https://physics.nist.gov/PhysRefData/Handbook/Tables/lithiumtable2.htm
https://physics.nist.gov/PhysRefData/Handbook/Tables/neontable2.htm
https://physics.nist.gov/PhysRefData/Handbook/Tables/sodiumtable2.htm
https://physics.nist.gov/PhysRefData/Handbook/Tables/calciumtable2.htm
https://physics.nist.gov/PhysRefData/Handbook/Tables/irontable2.htm
https://physics.nist.gov/PhysRefData/Handbook/Tables/goldtable2.htm
https://physics.nist.gov/PhysRefData/Handbook/Tables/radontable2.htm
https://physics.nist.gov/PhysRefData/Handbook/Tables/uraniumtable2.htm
https://physics.nist.gov/PhysRefData/Handbook/Tables/einsteiniumtable2.htm

NIST handbook covers selected lines Z1–99 (~12,000 published) and its finding list groups all of these by wavelength. NIST ASD has wider transitions and higher-ionization stages. In this ChatGPT runtime, container outbound DNS is blocked, so the **full bulk-download was not executed**. The packaged Python collector supports `--fetch` for internet-enabled runtime; the 88 not-yet-collected handbook elements and Z100–118 are explicitly unpopulated rather than assigned fabricated wavelengths.

## Reproduction
In conversation artifact `KET_EVE_Spectral_Atlas_Z0_118.zip`, extract and run:
```
python eve_build.py
python eve_build.py --fetch
```
The second form requires an internet connection and requests each NIST strong-line page, recomputing coverage.

The KET 184/257 frozen reference unchanged.
