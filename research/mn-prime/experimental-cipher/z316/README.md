# Z316 — Triunhexium (Tuh): time-dependent star map

Classification: Layer 1 symbolic research, not discovered chemistry.

## Toy astrometric model
x(t)=x0 + mu*t + p*cos(2*pi*t)
Here t is in years, phase is known, and geometry is restricted to one dimension.
For x0=10, mu=2, p=0.4:
t=0 -> 10.4; t=0.25 -> 10.5; t=0.75 -> 11.5.
Derive mu=(y075-y025)/0.5, x0=y025-mu/4, p=y0-x0.

## Execution evidence
Local Python test_z316.py execution: 5/5 PASS.
1. sample generation
2. parameter recovery
3. annual proper-motion increment
4. half-year parallax displacement
5. pure linear-motion comparison
Checks are toy arithmetic, not astrophysical validation.

## KET tracks
i: source identity
u: observer displacement and propagation
u.s: repeated time-stamped observations and reconstructed motion

## Limitations
Real astrometry requires 2D angular coordinates, reference epoch, frame, scan/observer geometry, noise treatment and ideally radial velocity for 3D space motion. Three samples are sufficient here only given the fixed cosine phase and the simplified model. No novel claim about Z316 physical element.
Core frozen KET untouched.

## References
ESA Gaia explanation: https://www.esa.int/Science_Exploration/Space_Science/Gaia/How_does_Gaia_study_the_Milky_Way
