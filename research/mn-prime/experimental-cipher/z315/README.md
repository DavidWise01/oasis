# Z315 — Triunpentium (Tup): two-observer stellar triangulation

Status: MN PRIME / OCTAVIA Layer 1 symbolic mapping, not evidence of element 315 or new astronomy.

## Physical anchor
Annual stellar parallax p in arcseconds maps to distance d in parsecs by d=1/p.
Parallax p is half the apparent angular displacement between opposite Earth-orbit vantage points, corresponding to a 1 AU reference baseline.
Illustrative measurement: p=0.1 arcsec -> d=10 pc -> approximately 32.6 light years, giving approximately 32.6 years of light travel in the stationary simplified case.

## KET analog
- i: stable source identity and measured direction.
- u: geometry of independent observer positions and light propagation.
- u.s: reconstructed position/distance with measurement time, frame, and uncertainty.

## Proposed deterministic test vectors
- p=1 arcsec -> 1 pc
- p=0.1 arcsec -> 10 pc
- p=0.05 arcsec -> 20 pc
- p<=0 -> reject naive reciprocal calculation (requires alternative inference)
- halve p -> double distance when p>0
- record observed angle, observer baseline, reference epoch and uncertainty independently

## Scope safeguards
No physical properties assigned to a hypothetical Z315 nucleus.
A single parallax measurement does not provide a complete 3D position without sky direction.
Proper motion, distance uncertainty, binary systems and other systematics matter for real catalogs.
The KET core stays frozen and unchanged.

Sources:
https://openstax.org/books/astronomy/pages/19-2-surveying-the-stars
https://science.nasa.gov/mission/hubble/multimedia/hubble-glossary/
