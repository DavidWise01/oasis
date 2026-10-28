# Natural Bound 09 — One outward Galactic train, Sgr A* → Sun / Earth (2026-10-27)

Evidence ID: ITD_BOUND09_GALACTIC_COMMON_MODE_TRAIN_20261027

Status: SHARED_BOOST_BOUND / 729_COORDINATE_STATIONS_TRANSLATE / SUN_ORBIT_SEPARATE / 24_FACTORIAL_RANK_NOT_TIME / 72_BOOST_INVARIANCE_CASES_PASS.

Append-only successor to [Bound 08](BOUND08_NATURAL_BOUND_2026-10-27.md). Nothing in the prior gravity model or stellar evidence has been overwritten.

## Canonical statement

If Sgr A* is part of a galaxy that translates in a chosen outward direction, the Sun, Earth and the intervening coordinate grid can share the same velocity. The Sun can be *further back along the train* because of its initial position, but shared translation alone cannot change the distance between bodies or their mutual gravitational attraction.

~~~text
+forward >>
      [Sgr A* / station 000] ... [729 model sample positions] ... [Sun/Earth / 728]
      common worldline X(t)                         same added worldline X(t)

worldline for coordinate sample i:
  x_i(t) = X_train(t) + r_i(t)
  v_i(t) = V_train + v_i,relative(t)

separation:
  x_i(t)-x_j(t) = r_i(t)-r_j(t)

Newtonian gravitational contribution:
  g_i = SUM_j G*m_j*(r_j-r_i)/|r_j-r_i|^3
~~~

The train heading defines an arbitrary observer coordinate, not an absolute preferred universal frame or a measured direction of Galactic bulk motion. As the Sun orbits Sgr A*, its projection onto the chosen forward axis changes; its separation remains approximately 8.277 kpc in the circular-orbit illustration. At quarter and half of an idealized orbit, the Sun is sideways and then ahead respectively. A permanent “behind” configuration only exists in the rigid-position mode or over a limited orbital phase.

## Physical witness anchors

- GRAVITY Collaboration (2022), stellar-orbit black-hole distance estimate R0 = 8277 pc: https://doi.org/10.1051/0004-6361/202142465
- Jiao et al. (2023), Gaia DR3 circular speed near the Sun v_c = 233 ± 7 km/s: https://doi.org/10.1051/0004-6361/202346474
- Reid & Brunthaler (2004), apparent Sgr A* radio proper motion 6.379 ± 0.024 mas/year dominated by solar orbital reflex, not a directly measured absolute Galactic bulk velocity: https://doi.org/10.1086/424960

**Chosen train velocity and heading are scenario parameters**, defaulting to 320 km/s and +X direction. They are NOT measured velocities for the Milky Way or Sgr A*. No cataloged stars are assigned artificial 3D velocities.

## Two separately supported kinematic modes

1. Rigid-position coordinate mode: x_station = X_train - radius_station * forward_unit_vector. Fixed relative line, no actual stellar orbital integration.
2. Circular Sun orbit mode: x_sun = X_train - R0 * [cos(omega*t)*forward + sin(omega*t)*side] with omega = v_c/R0. The 729 station grid is a rotating **reference ray**, not 729 actual stars orbiting rigidly. Earth is plotted at Sun because its 1 AU orbit is unresolvable at kiloparsec resolution.

The earlier four-component Sgr A*+bulge+disk+halo gravitational-field values are read unchanged. Uniform boost is coordinate-only and makes no extra gravitational term. Accelerating and rotating frames would require separate inertial terms.

## Verified numerical witness

~~~text
R0                                    8.277 kpc
Sun circular speed                    233 km/s (model)
Idealized solar orbit period          218.2445868607662 Myr
1 km/s over 1 Myr                     1.022712165045695 pc
Illustrative common bulk speed        320 km/s
Illustrative elapsed time             10 Myr
Center world displacement             +3.2726789281462243 kpc
Sun world X, circular mode            −4.663666694453095 kpc
Sun world Y, circular mode            −2.3501376892958032 kpc
Sun / Sgr A* separation               8.277 kpc
Sun trailing projection, rigid        8.277 kpc
Sun trailing projection, circular     7.936345622599319 kpc
~~~

The 729-row data sheet contains these world coordinates for all station positions in both modes, plus an unchanged original gravity-model entry. The raw star catalog has not been converted into a measured dynamical population.

## Committed artifacts

- [Interactive self-contained HTML, external vs. boost-subtracted frames](bound09-galactic-train.html)
- [Pure shared-motion coordinate engine and deterministic tests](bound09_shared_motion_core.js)
- [729-position numeric witness with preserved field](BOUND09_729_COMMON_TRAIN_WITNESS_20261027.csv)
- [Machine-readable facts, provenance, test receipt, limits](BOUND09_MOTION_AUDIT_20261027.json)
- [Prior 24! toroidal traversal](bound08-24factorial-toroid.html)

## Three witnesses — no agreement or quorum

A: Astrometric and orbital evidence, including the measured galactic center distance and the apparent Sgr A* radio proper motion.

B: Kinematic reference-frame calculation, with precisely the same added bulk motion for all entities. Verified by 72 test scenarios of stationary and circular spoke geometry, multiple times, coordinate stations and shared speeds.

C: Independent logical 24! address ring. Rank 0 = Gray 000 and station 000; rank 1 = Gray 001 and station 001; rank 24!−1 = Gray 100 and station 728; final-to-first is a *logical* seam, not physical travel. Physical time and permutation rank must not be equated.

Checks completed on the actual committed source: JavaScript self-test PASS for the moving-frame engine; 72 invariance scenarios PASS; station radius and Sun/Sgr A* separation preserved; relative velocities unchanged by uniform boost; 1 AU Earth offset PASS; 24! endpoint mapping PASS; three scripts from the new HTML syntax-compiled; simulated browser DOM interactions passed (speed, time, station, orbit mode, next rank, last/first seam, reverse seam, out-of-range rank guard).

**Not verified:** live GitHub Pages deployment, browser screenshot rendering, real measured Galactic bulk velocity vector, individual Gaia stellar 6D orbital trajectories, full general-relativistic dynamics.

## Next natural Bound 10

Attach actual Gaia DR3 proper motions and radial velocities, with their errors/covariance, to cataloged stars with identified distances. Transform each 6D phase-space observation to the same consistent Galactocentric frame. The common arbitrary bulk-motion vector cancels under subtraction; any remaining lag or advance must be explained by **observed relative motion** or a justified Galactic potential, not by a train-position assumption. Empty station observations remain unknown.

Freeze: retain previous Bounds 01–08; Bound 09 is the append-only moving-reference layer.
