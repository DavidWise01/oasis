# P3.40 — Symbolic color exhaustion to wave continuation
2026-10-09.

User design: after color hierarchy reaches terminal quaternary tier, represent further variations by wavelength × amplitude, with `{hz...}` spectral namespace. Four named prime identities remain: Jane/pink, Patricia/purple, Toph/green, Icarium/blue. Motion remains four hops ×360=1440, independently of Greg's calendar cycle.

Unit-consistent implementation: amplitude is dimensionless, wavelength measured in meters, `wavelengthTimesAmplitude` is meters, whereas `hz=propagationSpeed/wavelength`. Frequency is not dimensionally equal to wavelength times amplitude. Color tags are symbolic identities and need not correspond to electromagnetic wavelengths. The wave sampler is a classical sinusoid, not a single-photon quantum-state amplitude.

Local Node test executed: PASS 23040 addresses (1440 × 4 primes ×4 tiers), six wavelength examples, invalid-parameter rejection, index recovery, fixed root. GitHub commit is source/test/audit, remote CI not verified.
