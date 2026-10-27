# Sgr A* → Sun: 729 stellar axial projections (2026-10-27)

## Deliverables
- [Interactive line viewer](index.html)
- [729 real bright-star records](SGRA_EARTH_HYG729_20261027.csv)
- [729 uniformly spaced model stations](SGRA_EARTH_729_STATIONS_20261027.csv)

## Method and evidence
Target: Sgr A* sky position RA 266.41683°, Dec −29.00781°; adopted line length 8,277 pc (approximately 27,000 ly). The Sun is the zero-coordinate origin. `along = d cos(angle)`, `offset = d sin(angle)`. Only strictly positive axial projections within 8,277 pc retained. Rank candidates by smallest 3D perpendicular offset and take first 729. The output stars are sorted from Sgr A* toward the Sun by their projected position, not placed at artificial equal distances.

Data source: https://github.com/isene/starmap/blob/master/data/stars.csv (blob SHA `c7b9458deeb6aaa2d8fc71e98c47ea8cfcca4f6c`); source compilation of Yale Bright Star Catalog 5th Revised Edition positions and visual magnitudes and Hipparcos parallaxes with unreliable distances excluded. Read source provenance: https://github.com/isene/starmap/blob/master/data/README.md.

**Critical limitation:** the brightest-star database is not a full survey of the Galactic Center. All 729 selected records lie in the approximately first 741 ly along the axis from the Sun; no stars from this list populate the remaining ~26,255 ly. Their maximum perpendicular offset is ~34.77 pc. A zero-width straight line generally intersects no stars. This is a *cylindrical nearest-neighbor projection*, not proof of a physical string of stars, and not a gravity-force calculation. No stellar masses are assumed. Interstellar dust, crowding, parallax precision and selection bias require near-infrared surveys and distance posteriors to populate the inner Milky Way.

The `729` stations are uniform numerical positions including endpoints Sgr A* and Sun, **not** 729 observed stars; no station claims a coincident physical star.

Astronomical direction corroborated by SIMBAD; independent distance-estimation limitations described by C. A. L. Bailer-Jones et al. (2021), https://arxiv.org/abs/2012.05220 .
