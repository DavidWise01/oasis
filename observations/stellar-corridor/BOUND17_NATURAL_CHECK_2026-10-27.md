# Natural Check 17 — Do two crossing null shells satisfy a gravitational mass junction?

Evidence: `ITD_BOUND17_DTR_REISSNER_NORDSTROM_TWO_NULL_SHELL_CROSSING_20261027`

State: **APPEND ONLY** / `EXACT_SPHERICAL_DTR_JUNCTION` / `TWO_NULL_STREAMS` / `INDEPENDENT_70_DIGIT_DECIMAL` / `729_RADIUS_SWEEP_PER_CHARGE` / `NOT_KERR` / `NOT_CONTINUOUS_EINSTEIN_EVOLUTION` / `24FACTORIAL_RANK_UNCHANGED`.

This is a successor check to [Bound 16](BOUND16_NATURAL_BOUND_2026-10-27.md), which calculated a **toy blueshift sensitivity proxy** but not the backreacted metric or a gravitational mass. Natural Check 17 tests the nonlinear null-shell crossing junction directly rather than rebranding the old proxy as physical mass inflation.

## Physical scope: a controlled, different spacetime

The exact **Dray–’t Hooft–Redmount (DTR)** relation describes a local crossing between an ingoing and outgoing thin lightlike shell, dividing a **spherically symmetric Reissner–Nordström** Einstein–Maxwell spacetime into four constant-charge vacuum regions. This metric is **electrically charged and nonrotating**. The prior Bound 14–16 calculations concern **rotating Kerr** spacetimes. They cannot be merged merely by renaming the charge ratio `Q/M` as Kerr spin `chi`.

All masses and lengths here are in **geometric units `G=c=M_background=1`**. There is **no claim that Sagittarius A*** has an electric charge, experiences these particular thin shells, or has an observed interior.

Let `q=Q/M_background`, assumed `0<q<1`, and define

    f(r;M,Q) = 1 − 2M/r + Q²/r²
    r_± = 1 ± sqrt(1−q²)
    r_cross = r_- + δ (r_+−r_-),   0<δ<1.

For the common background `M_0=1` and two independently specified positive null shell mass jumps `a=δm_in`, `b=δm_out`, write

    f0    = [(r−r+)(r−r−)]/r²         [negative between the horizons]
    fin   = f0 − 2a/r
    fout  = f0 − 2b/r

The **exact local DTR algebraic constraint** is

    f0 * ffinal = fin * fout.

Thus the post-crossing region has gravitational mass parameter

    Mfinal = 1 + a + b − [2 a b / (r f0)].

Between horizons, `f0<0` makes the nonlinear product term **positive** for positive shell jumps. As the crossing approaches an ideal inner horizon `f0 → 0−`, the formal corner mass becomes large. This is the core local crossing mechanism used in schematic mass-inflation discussions.

**Do not confuse this one crossing equation with a complete evolution of two finite stress-energy streams.** It enforces a junction/matching relation but does not integrate the Einstein–Maxwell field equations over a dynamical spacetime, determine shell trajectories, prove the requisite causal branch, or compute the physical fate of a Cauchy horizon. Additional matching/orientation and global initial data constraints are needed for a physically realizable sequence of collisions.

The published connection is supported by [Poisson and Israel, PRL 63, 1663 (1989)](https://harvest.aps.org/v2/journals/articles/10.1103/PhysRevLett.63.1663/fulltext), [Ori, PRL 67, 789 (1991)](https://doi.org/10.1103/PhysRevLett.67.789), the [1999 DTR shell crossing analysis](https://academic.oup.com/ptp/article/101/5/989/1821765), and the [2026 RN-type DTR formula](https://doi.org/10.1103/nrd7-j6hs). Ori's work solves an exact mass-inflation spacetime; this check does **not** reproduce that complete solution.

## Four independent witness controls

The deterministic controls distinguish nonlinear crossing from merely adding two positive energy contributions:

| Control | Inputs | Expected post-crossing mass |
| --- | --- | --- |
| Both shells | `a>0, b>0` | `1+a+b−2ab/(r f0)` |
| Incoming only | `a>0, b=0` | `1+a` |
| Outgoing only | `a=0, b>0` | `1+b` |
| Neither | `a=0, b=0` | `1` |

Exchanging `a` and `b` leaves `Mfinal` unchanged. The DTR product condition is verified numerically for **all** 4 × 729 crossing points. The result therefore contains a genuinely **bilinear** interaction rather than an arbitrary fitted growth curve.

### Reproducible fixed-input example

Assume `q=0.8`, `a=b=0.0001`, with `r−=0.4`, `r+=1.6`.

| Distance parameter δ | Crossing corner mass `Mfinal` | Nonlinear mass term |
| ---: | ---: | ---: |
| 0.1 | 1.0002000802469136 | 0.0000000802469136 |
| 0.001 | 1.0002055778000222 | 0.0000055778000222 |
| 0.000001 | 1.0057555777778000 | 0.0055555777778000 |
| 0.000000001 | 6.5557555777777778 | 5.5555555777777778 |
| 0.0000000001 | 56.5557555777777778 | 55.5555555777777778 |

These values were reproduced by a **completely separate Python standard-library `decimal` computation at 70-digit precision**. The same four-region junction identity evaluates to zero or smaller than `10^-70` in the high-precision reference at these points, consistent with the JavaScript residuals near `10^-16`.

**Near-horizon warning:** for fixed nonzero shell jumps, `2δm/(r |f0|)` grows without bound as `δ→0`. A declared optional *small relative shell-jump criterion* requires each `2δm/r ≤ 0.1|f0|`. Most near-horizon rows **fail** this optional small-background-perturbation check, even though the **nonlinear DTR algebra** remains balanced. We do not claim those samples describe a physically valid small-perturbation continuum.

## Full model registry

A new [2,916-row crossing witness](BOUND17_729_DTR_CHARGED_NULL_SHELL_CROSSINGS_20261027.csv) includes 729 logarithmically spaced `δ` values `10^-1` through `10^-10` for each of four *charge* scenarios `q=0.5,0.8,0.95,0.99`.

| Assumed RN charge ratio | Largest formal corner mass on sample grid | Rows satisfying optional small-shell / reference-lapse criterion |
| ---: | ---: | ---: |
| 0.50 | 9.93184 | 247 / 729 |
| 0.80 | 56.55576 | 183 / 729 |
| 0.95 | 353.69256 | 118 / 729 |
| 0.99 | 2,159.12241 | 53 / 729 |

**These are not four Kerr spin scenarios** and are not measurements of an astrophysical mass growth. The charge approaches extremal RN configurations, which require their own care with nonuniform limits.

A separate [four-case zero/one/two-stream table](BOUND17_ZERO_STREAM_CAUSAL_CONTROLS_20261027.csv) records the bilinear interaction at `q=0.8, δ=10^-6`. The charged-background parameter `q=0` is disallowed in this model: the Schwarzschild limit has no distinct inner Cauchy horizon at positive radius.

## Three verifiable sources of evidence

1. **Published junction equation.** DTR matching is a local exact relation between metric functions for crossing null shells in a spherical spacetime.
2. **Independent numerical implementations.** The committed [dependency-free JS engine](bound17_null_shell_dtr_core.js) is read back and executed, and a separate [Python 70-digit Decimal witness](bound17_dtr_decimal_witness.py) reproduces its representative numbers and tests the DTR product identity.
3. **Explicit observational limitation.** Neither the RN charge, the mass jumps, the crossing radii nor the final corner masses are measured at Sagittarius A*. The model’s mathematical validity does not establish a Kerr interior.

### Interactive page and testing

The [self-contained interactive local crossing viewer](bound17-two-stream-dtr-check.html) lets the investigator select RN charge ratio, input shell masses, switch either or both streams off, sweep the crossing point, inspect all four metric sectors, and verify the normalized DTR residual. The original exact 24! SJT/Gray register remains an independent logical address.

Checks actually executed: four × 729 crossing samples; DTR product residual; positive-crossing mass in trapped RN region; one-/zero-stream controls; swap symmetry; bilinear cross difference; near-horizon inverse-δ amplification; invalid charge guard; independent high-precision Decimal reference; three compiled page scripts; and simulated controls testing `000→001`, `last→000`, and reverse seam. No real-browser render or live GitHub Pages deployment was independently confirmed.

## Next natural Bound 18: constraint-propagating evolution

A physically stronger next step requires **initial data on intersecting null surfaces**, an explicit Einstein–matter system and an appropriate numerical solver. In spherical symmetry, the Einstein–Maxwell–massless-scalar characteristic formulation provides a tractable starting point. It would evolve the metric, scalar field flux and mass function, check both null constraints and convergence under increasing resolution, and stop before unreliable curvature regimes. Kerr rotation and nonspherical gravitational modes would still require a separate subsequent step.

**Freeze:** All Bounds 01–16 remain unmodified. This check is strictly a new append-only null-shell witness and the 24! logical cycle does not become a physical time loop or transport of matter.
