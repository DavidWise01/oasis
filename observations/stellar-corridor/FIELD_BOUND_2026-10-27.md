# Physical bound 03 — Sgr A* gravity versus Milky Way orbital field (2026-10-27)

Status: `PRIMARY_MEASUREMENTS_CHECKED` + `CALCULATED_729_STATION_BH_FIELD` + `SENSITIVITY_ENVELOPE` + `STELLAR_MASSES_UNKNOWN` + `GALACTIC_MODEL_UNRESOLVED`

An append-only descendant of `NEXT_REQUIREMENT_2026-10-27.md`. Do **not** interpret the 729 mathematical samples as a chain of 729 measured gravitational sources. Neither the existing bright-star catalog nor the Gaia ingestor currently contains an independently verified mass for each star.

## Artifacts
- [Interactive browser page](field-bound.html): Sgr A* field from 729 numerical positions, with acceleration/tidal-gradient modes and quarter-distance demonstration.
- [729 station values](SGRA_EARTH_729_GRAVITY_BOUND_20261027.csv): each sampled distance from Sgr A*, point-mass acceleration and radial tidal gradient. At station **1**, r = 0, the point-mass formula is undefined; **blank**, not infinity or zero.
- [Constants / sensitivity JSON](SGRA_EARTH_GRAVITY_BOUND_20261027.json).
- [Optional provenance-gated point-mass vector calculator](gravity_mass_gate.py): input real star-mass estimates with independent mass source URLs. No missing mass is filled or assigned zero.

## Physical anchors (public records, independently sourced)
1. GRAVITY Collaboration (2022), stellar-orbit inference: distance `R0 = 8277 ± 9 pc` and mass `M_BH = (4.297 ± 0.012) × 10^6 solar masses` (quoted errors statistical; authors discuss ~30 pc and ~40,000 solar masses systematics). https://doi.org/10.1051/0004-6361/202142465
2. Gaia DR3 circular-velocity inference by Jiao et al. (2023): circular speed near the Sun `v_c(R0) = 233 ± 7 km/s`. This describes the **galactic total** radial acceleration inferred from approximately circular dynamics, not a direct measured sum of individual stars. https://doi.org/10.1051/0004-6361/202346474
3. Adopt nominal solar GM `1.3271244e20 m³/s²` and `1 pc = 3.0856775814913673e16 m`. Reference: https://ssd.jpl.nasa.gov/astro_par.html
4. For subsequent realistic galactic models: galpy's **MWPotential2014** separately includes bulge, disk and dark halo. Its historical normalization `220 km/s at 8 kpc` must not be misrepresented as the 233 km/s Gaia inference. https://docs.galpy.org/en/v1.11.2/reference/potential.html

## Computation

```text
GM_BH            = (4.297e6) (1.3271244e20) m³/s²
R0               = 8277 (3.0856775814913673e16) m
g_BH(R0)         = GM_BH / R0²                  = 8.742386181306883e-15 m/s²
g_circ(R0)       = (233000 m/s)² / R0            = 2.1256332831296986e-10 m/s²
g_BH / g_circ    = 4.1128383953580826e-5      = 0.004112838395358083%
|dg_BH/dr|(R0)  = 2 GM_BH / R0³                 = 6.845993494431305e-35 s⁻²

mass_equivalent_spherical = v_c² R0 / G = 1.044777252821256e11 solar masses
                      ^^^ DO NOT treat as a measured enclosed mass:
                          the real disk geometry is not spherical.
```

The ratio is approximately one in 24,314 (the Milky Way orbit depends overwhelmingly on non-black-hole galactic mass). It measures the **radial BH contribution relative to a circular-orbit dynamical proxy at the Sun**; it is not the black hole's share of all matter in the Milky Way, nor the fraction of force holding Earth to the Sun.

### Conservative sensitivity, not a statistical confidence interval

Independently vary mass by ±40,000 solar masses, center distance by ±30 pc, and circular speed by ±7 km/s. The resulting approximate bounding range for `g_BH/g_circ` is:

```text
0.0000382646764161 to 0.0000442830614986
0.0038265% to 0.0044283%
```

This rectangle-of-parameters range is NOT a joint error posterior, and excludes other astrophysical systematics.

## Quarter-field rule (user's 1/4 × 4 = 1)

```text
same M at r    -> g
same M at 2r   -> g/4
same M at 4r   -> g/16

different mass M/4 at distance r/2 -> g (same magnitude)
```

These are exact point-source Newtonian magnitude identities. The physical size of a star does not shrink in this calculation. Gravitational vectors from different stars need not align. A point mass potential is not a physical description inside the event horizon, and extrapolating the BH as the *only* galactic mass is invalid.

## Mandatory missing mass gate

Existing `SGRA_EARTH_HYG729_20261027.csv`: astrometry and distance only. **Mass field unknown.** Existing `gaia_ingest.py`: distance estimates and error bounds only. **Mass field unknown.**

For any subsequent field sum, one candidate row needs:
`source_id, ra_deg, dec_deg, distance_median_pc` (or `dist_sun_pc`) and **mass_msun with mass_source_uri** (independent source URL).

The separate script `gravity_mass_gate.py` requires a source URL for any mass, rejects unphysical values and duplicate IDs, performs 3D vector addition in heliocentric equatorial coordinates, and retains missing masses as unknown rather than zero. Input reference frame, epoch, distance validity and scientific reliability of each mass source must be checked separately.

Quick check:

```sh
python3 gravity_mass_gate.py --self-test
python3 gravity_mass_gate.py measured_with_vetted_mass_column.csv --out catalog_mass_partial.json
```

The result is a **partial observed-star vector sum only**. It does not fill the Galaxy's gravitational potential, does not include diffuse gas or dark matter, and cannot be subtracted from the measured galactic orbital value to infer a unique set of unobserved stellar masses.

## Validation gates

- 729 positions including endpoint positions Sgr A* (undefined BH point mass at exact r=0) and Sun (8,277 pc).
- Every finite radial BH acceleration strictly decreases with increasing r.
- `g(2r) / g(r) = 1/4` and `g(r/2) / g(r) = 4` for fixed BH mass.
- At the Sun, no mass is assigned to any missing star.
- Three distinct observable/model scopes: (1) direct Sgr A* central mass estimate, (2) inferred solar galactic circular speed, (3) positional star-catalog candidates without verified masses.
- Cannot use a 1/4 factor, a 729 sampling scheme, or a toroidal diagram to infer or verify a Yang–Mills mass gap.

## Next boundary

Obtain deep infrared/optical **distance plus mass posterior** measurements, crossmatch duplicates, and calculate 3D vector contributions with uncertainties. For a full gravitational field, then introduce a published Milky Way bulge+disk+halo potential and compare the combined predicted local radial acceleration to a measured rotation curve. Keep gravitational acceleration, tidal gradient and angular apparent size in separate fields.
