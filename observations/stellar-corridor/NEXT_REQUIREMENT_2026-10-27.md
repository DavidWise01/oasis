# Requirement 02 — Deep Gaia / infrared observed-star corridor (2026-10-27)

Status: `QUERY_SPECIFIED` + `INGESTOR_IMPLEMENTED` + `LOCAL_SYNTHETIC_FIXTURE_PASS` + `LIVE_GAIA_RESULTS_NOT_RETRIEVED` + `INFRARED_JOIN_PENDING`.

This is an **append-only extension**, not a replacement, correction, or fake completion of the 729-star bright-star snapshot in `index.html` and `SGRA_EARTH_HYG729_20261027.csv`.

## Baseline and problem
- The modeled axis is Sun → Sgr A*, with direction RA = 266.41683°, DEC = −29.00781° (ICRS), adopted 8,277 pc (~27,000 ly).
- The numerical construction is `(3×3)^3 = 729` equal-distance **stations**, including endpoints; station-to-station spacing ~11.37 pc (~37.1 ly).
- The original 729 bright-star nearest-axis selection spans only ~741 ly from the Sun **along the projected axis**. It cannot fill the remaining ~26,255 ly.
- A **zero-width mathematical line is not likely to intersect exactly 729 stars**; observational work must use a disclosed cylindrical tolerance and distance uncertainty.

## Artifacts
1. `gaia_dr3_corridor.adql`: public Gaia DR3 sky-cone candidate query. All source columns match the ingestor.
2. `gaia_ingest.py`: offline filtering and 3D dot-product projection into 729 axis stations, preserving Gaia `source_id`, ICRS position, GSP-Phot distance median and 16th/84th percentiles, RUWE, perpendicular distance, and provenance. Outputs:
   - `gaia_accepted_observations.csv`: **only real input catalog records** accepted by explicit quality criteria
   - `gaia_729_station_witnesses.csv`: 729 mathematical stations; one nearest-off-axis candidate where available, otherwise an explicit `NO_CATALOG_MATCH`
   - `gaia_ingest_audit.json`: actual input count, rejections by reason, occupied/unoccupied stations, provenance and model scope
3. No synthetic data is committed as actual observations.

## Query / run
1. Open https://gea.esac.esa.int/archive/ or an authorized Gaia TAP mirror; submit `gaia_dr3_corridor.adql` as an asynchronous ADQL query (larger queries require async service).
2. Download the resulting **real CSV**. The `TOP 100000` cutoff means it may be incomplete, and its ordering is not a population sample; for scientific completeness use separately documented narrower distance and angular tiles without an arbitrary TOP cutoff.
3. Run locally with Python >= 3.9 (standard library only):

```sh
python gaia_ingest.py gaia_tap_download.csv --out measured-gaia --offset-pc 50 --max-ci 0.6
```

4. Examine `measured-gaia/gaia_ingest_audit.json`. The script never calls Gaia itself; it audits and ingests **downloaded data only**.

The Gaia CSV distance is a *photometric posterior estimate*, not a geometrically direct distance. `distance_gspphot_lower` and `_upper` are 16th/84th percentile bounds. Input quality gates: positive median and ordered bounds, relative 68% interval width at most 0.6, RUWE <= 1.4, projection within Sun–Sgr A*, and perpendicular offset <= 50 pc. The radius is a **tolerance**, not a gravitational field boundary. Geometry is projected at the measured epoch without orbit propagation. Multiple observed stars can map to one station, but only one is shown as its station witness (others remain in the accepted CSV).

## Test receipt — performed locally using a clearly marked synthetic **fixture only**
- 8 fabricated *test input rows*, designed to exercise validators; they were **not merged with the real observations**.
- 3 accepted fixture observations; 3/729 witness stations occupied; 726 explicitly missing.
- 1 duplicate, 1 excessive distance interval, 1 RUWE reject, 1 off-axis reject, 1 outside-axis reject.
- Checks passed: exactly 729 output stations, all station witnesses explicitly marked as **not a star at the exact numerical center**, empty-station integrity.
- This does **not** demonstrate the accuracy of live Gaia results, complete Galactic coverage, or gravitational force calculation.

## Infrared follow-up requirement (not yet ingested)
Crossmatch under matched coordinate/distance uncertainty with:
- SDSS/APOGEE DR17 + StarHorse IR spectrophotometric distances, keeping uncertainties, sample selection and separate provenance: https://www.sdss4.org/dr17/irspec/spectro_data/
- VVV/VVVX Galactic bulge infrared survey, with appropriate available photometric-distance analysis and strong crowding/extinction flags: https://vvvsurvey.org/data-releases/

Neither raw near-infrared apparent magnitude **nor** projected sky proximity is a direct 3D distance. Do not convert from parallax by naive 1/parallax for low-SNR objects. Deduplicate crossmatched source identities and preserve every conflicting distance inference as distinct observed evidence.

## Next physical gate
Only after positional coverage is audited, estimate individual stellar masses from justified models (with error bounds), add diffuse galactic matter and dark-matter potential, compute **vector** accelerations at a chosen target (e.g. Sun/Earth), and compare against a baseline Milky Way dynamical model. **Never** treat the observed counts, the 729 station construction, or an arbitrary 1/4 partition as a measured gravitational law.

## Source/authority
- Gaia DR3 official field definitions: https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html
- Gaia official ADQL query examples: https://www.cosmos.esa.int/web/gaia-users/archive/writing-queries
- APOGEE data access: https://www.sdss4.org/dr17/irspec/spectro_data/
- VVV/VVVX data releases: https://vvvsurvey.org/data-releases/

Append corrections or new source/commit receipts as **new dated records**, not overwritten past observations.
