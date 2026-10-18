# Z317 — Triunseptium (Tus): stellar radial velocity

Classification: MN PRIME/OCTAVIA experimental symbolic cipher, Layer 1. Z317 is not a discovered element. Frozen KET core unchanged.

## Observables and geometry
- Parallax provides distance.
- Proper motion and distance yield transverse velocity: vt(km/s)=4.74047*mu(arcsec/year)*d(pc).
- Doppler spectrum yields radial velocity along the line of sight.
- Local orthogonal decomposition v=(vt,0,vr), speed=sqrt(vt^2+vr^2); real sky coordinates require sky position, both proper-motion components, frame and epoch.

## Illustrative vector
mu=0.1 arcsec/year; d=10 pc; vr=+20 km/s; vt=4.74047 km/s; speed=20.55413 km/s; positive radial velocity indicates recession.

## Tests
Executed locally on 2026-10-18: 6/6 deterministic Python arithmetic checks PASS (standalone test_z317.py). This validates only toy mathematics; no observed star or physical element.

Next Z318: propagate trajectories in a stated inertial reference frame with prediction uncertainty.

Source: https://www.esa.int/Science_Exploration/Space_Science/Gaia/How_does_Gaia_study_the_Milky_Way
