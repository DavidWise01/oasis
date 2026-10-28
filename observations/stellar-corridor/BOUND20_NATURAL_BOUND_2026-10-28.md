# Natural Bound 20 — One continuous rectangular double-null scalar-tail evolution

Evidence: `ITD_BOUND20_LONG_NULL_TAIL_CHARACTERISTIC_20261028`
Date: 2026-10-28

State: `APPEND_ONLY / COUPLED_SPHERICAL_EM_SCALAR / PRESCRIBED_DECAYING_INGOING_TAIL / FOUR_CONTROL_RUNS / TWO_NULL_CONSTRAINTS / FOUR_RESOLUTION_CONVERGENCE / PREINNER_GUARD / NOT_LOCAL_AMR / MASS_INFLATION_NOT_ESTABLISHED`

Parent: [Bound 19, pre-Cauchy constraints and mass-flux gate](BOUND19_NATURAL_BOUND_2026-10-28.md). Bounds 01–19 are not changed.

## What is new

Unlike Bound 19's separate near-inner-radius initial-value snapshots, **this bound evolves one self-consistent connected rectangular double-null characteristic spacetime per input choice**, with a long numerical ingoing coordinate v interval. It uses the same *spherical Einstein–Maxwell–neutral real massless scalar* system, not Kerr. The full metric and scalar field evolve together rather than prescribing a background curvature response.

A single characteristic initial-value problem is specified on two intersecting null arms:

- u from 0 to 0.2, v from 0 to 4.25, both in the chosen **geometric coordinate gauge**, with G=c=M0=1.
- Fixed assumed RN electric charge Q=0.8 and initial corner radius r0=1.2.
- Outgoing-arm scalar phi(u,0) = A sin²(pi u/0.2); for the baseline A=0.012.
- Ingoing-arm scalar derivative phi_v(0,v) = B(1+v/v0)^(-p), with baseline B=0.0005, v0=1, p=3, integrated from phi(0,0)=0.
- Both arms use r_s=F(r)/2, F=1-2/r+Q²/r², and integrate the initial null Einstein constraint for sigma: sigma=(1/2)ln(-F)+integral r(phi_s)²/F ds.

**The power-law input is an assumed analytic finite-domain boundary condition.** No realistic exterior collapse or Price-tail calculation has been performed. Consequently the chosen numerical v coordinate is **not** independently identified with the usual far-field advanced time, nor is it the proper time of a falling observer. The interval 4.25 is not a physical measurement at Sagittarius A*.

## Fully coupled field equations and invariants

Using ds² = -exp(2sigma)du dv + r²dOmega²:

    r_uv     = -r_u r_v/r - exp(2sigma)(1-Q²/r²)/(4r)
    sigma_uv =  r_u r_v/r² + exp(2sigma)(1-2Q²/r²)/(4r²) - phi_u phi_v
    phi_uv   = -(r_u phi_v+r_v phi_u)/r

The separately monitored null constraints are

    Cuu = r_uu - 2sigma_u r_u + r (phi_u)² = 0
    Cvv = r_vv - 2sigma_v r_v + r (phi_v)² = 0.

The renormalized spherical charged mass function (often called the charged Hawking/Misner–Sharp mass parameter) is

    m = r/2 [1+4exp(-2sigma) r_u r_v + Q²/r²].

The two independent continuum mass-flux identities are

    m_u = -2r² exp(-2sigma) r_v (phi_u)²
    m_v = -2r² exp(-2sigma) r_u (phi_v)².

Their left sides are independently estimated from the numerical mass grid; their right sides are calculated from scalar derivatives. Both residuals must show second-order decay under resolution halving. The equations and charge are in assumed model units.

## Four input controls and numerical verification

Every control is a **different** finite characteristic initial-value problem, not a separate time point in one longer run. Use grid refinements [12×48, 24×96, 48×192, 96×384], with u×v coordinate extent fixed.

| Initial-value control | A, u-arm pulse | B, v-arm tail | N=96×384 midpoint mass | N=96×384 last corner radius |
| --- | ---: | ---: | ---: | ---: |
| No scalar (vacuum RN check) | 0 | 0 | 1.00000001493 | 0.4046954500 |
| u pulse only | 0.012 | 0 | 1.00257164054 | 0.4037519173 |
| v-tail only | 0 | 0.0005 | 1.00000008337 | 0.4046954274 |
| Both | 0.012 | 0.0005 | **1.00257261459** | **0.4037517311** |

All four controls **passed** solution, Cuu, Cvv and both independent flux-identity refinement checks on the full rectangular grids. The nonzero mixed response is small and finite; neither a mass-inflation divergence nor a quantum core is implied.

For the both-input case, the numerical checkpoint solution refinement ratios are **3.9302 and 3.9832**. The last constraint error ratios are **3.9524 (Cuu)** and **4.0003 (Cvv)**. The last mass-flux-identity residual ratios are **4.0814 (m_u)** and **4.0019 (m_v)**. The N=96×384 both-input RMS residuals are Cuu **6.7617×10^-5** and Cvv **1.0513×10^-5**. These are grid-coordinate residuals, not physical observation errors.

The vacuum mass approaches exactly 1 with refinement (at N=96×384 it differs by +1.493×10^-8). The continuous source term and mass function are calculated from the evolving numerical fields.

## Independently tested initial constraints

A separate source, [Bound 20 independent boundary validator](bound20_independent_boundary_constraints.js), evaluates Css=r_ss-2sigma_s r_s+r(phi_s)² using numerical central differences on each **initial** null arm, not using the interior field evolution as a substitute.

- u-arm residual L2 refinement ratios: 3.6921, 3.8866, **3.9541**.
- v-arm residual L2 refinement ratios: 3.9584, 3.9910, **3.9981**.
- The input derivative power law is checked directly against finite differences of the integrated ingoing scalar.
- At the end of v=4.25, the assumed scalar derivative is only **0.0069107** of its initial value, because (1+4.25)^(-3)=0.0069107.

The incoming scalar tail is therefore implemented, not merely described. This is still not a proof that this tail arises from gravitational-wave/radiative scattering outside the black hole.

## Hard numerical stopping point and missing AMR

The background RN inner and outer radii in model units are r- = 0.4 and r+ = 1.6. The deliberately chosen *pre-inner numerical guard* is

    r_guard=0.4+0.0005*(1.6-0.4)=0.4006.

The frozen baseline's last corner radius is 0.4037517 and does **not** cross it. Test lengths L_v=2,3,4,4.25,4.5 were explored on lower-resolution grids; L_v=5 triggers an interior-radius guard and L_v=8 violates the initial characteristic-radius guard. **A coarse result at v=4.5 is not certified by four-level convergence, and is not part of this scientific freeze.**

The implementation escalates globally uniform rectangular grids to confirm convergence. **It does not implement genuine local AMR.** No external-event-horizon data, long asymptotic v→infinity control, curvature-invariant blow-up or Cauchy-horizon limit is computed. A screen button deliberately requests v=8 and shows STOP rather than reporting stale previously accepted values.

## Registry and GitHub artifacts

- [Core rectangular double-null coupled evolution](bound20_long_advanced_tail_core.js).
- [Independent initial null boundary constraints](bound20_independent_boundary_constraints.js).
- [Interactive self-contained HTML with mass/radius plots and exact 24! ring](bound20-one-long-null-tail.html).
- [2,916 actual numerical field records: four controls × 27×27 interior points](BOUND20_729_ONE_RECTANGLE_TAIL_FIELD_WITNESSES_20261028.csv).
- [All 16 grid/refinement and both flux-identity diagnostics](BOUND20_FOUR_STREAMS_RECTANGULAR_CONVERGENCE_20261028.csv).
- [Eight initial-constraint finite-difference receipts](BOUND20_TWO_BOUNDARY_CONSTRAINTS_20261028.csv).
- [Seven finite-domain-length and hard-abort receipts](BOUND20_ADVANCED_NULL_LENGTH_GATES_20261028.csv).
- [Machine-readable provenance and scientific caveats](BOUND20_AUDIT_20261028.json).

The original exact 24! SJT/Gray address register remains logically independent: 000→001, final→000, and reverse. A 729 numerical sampling grid is not a collection of physical stars or a gravitational time period.

## Published scientific context

- Dafermos (2005), [The interior of charged black holes and the problem of uniqueness in general relativity](https://doi.org/10.1002/cpa.20071), establishes a mathematical mass-inflation scenario for suitable characteristic data with Price-tail assumptions. **Its theorem is not reproduced in this finite experiment.**
- Mädler, Gannouji and Gallo (2025), [Characteristic initial value problems for the Einstein–Maxwell–scalar field equations in spherical symmetry](https://doi.org/10.1103/f5fc-zpld), provides a framework for such characteristic data.
- Gautam (2024), [Late-time tails and mass inflation for the spherically symmetric Einstein–Maxwell–scalar field system](https://arxiv.org/abs/2412.17927), demonstrates the significance of external decay behavior and generic-class assumptions.

## Next natural Bound 21

Construct a genuinely **locally adaptive** double-null evolution with verified patch interpolation and AMR conservation, and an externally matched or physically normalized late-time scalar input. Converge the Hawking mass and curvature invariants along a **single** inner-horizon approach before declaring mass inflation. Stop if constraints, causal data or classical validity fail. Rotating Kerr requires a separate nonspherical perturbation program.

**Freeze:** Bound 20 is append-only. Bounds 01–19 retain their original data and tests. The physical center, the Kerr interior, and the Planck regime remain unresolved.
