# K.E.T. — Full Frozen Technical Specification
## Toroidal Non-Universe / Dual-Triplet Speed Controller / 360 + 3 + 3

| Document field | Frozen value |
|---|---|
| Document | KET/TOROID/360+3+3/FULL_SPEC/v2.0 |
| Baseline | KET Toroidal Non-Universe v2.0 |
| Freeze date | 2026-10-13 |
| Authoritative frozen Git commit | `de8f8b80aba3a73dd371811f6b4be39df92e45ce` |
| Frozen branch | `freeze/ket-toroid-360-3-3-v20-20261013` |
| Source schema | `KET/TOROID/360+3+3/v20` |
| Freeze schema | `KET/FREEZE/360+3+3/v20/2026-10-13` |
| Status | **FROZEN / ADDITIVE-ONLY CHANGES** |
| Domain | Deterministic symbolic geometry and angular-rate controller |
| Evidence class | Verified computational example; speculative physical interpretation |

> **Version contract.** This document consolidates the **already frozen** v2.0 code and manifest. It is a *new documentation artifact*, not a rewrite of frozen source. In any conflict, the pinned freeze commit, its byte hashes, and the exact executed source take precedence. The user-designated "non-universe" is a conceptual domain, **not** an observational claim about our physical universe.

---

## 1. Canonical one-line declaration

```text
{{ 0root :: | K | {{ | E | {{ | T }} }} }}
     :: TOROID[360]
     :: CONTROLS[--+][++-]
     :: 360 + 3 + 3 = 366
     :: 7 AMPLITUDES + 3 CARRIERS + 0
     :: GREEN_CHARIOT[123 {{45/|\54}} 678]
     :: 1 CYCLE / PHASE LOCK / APPEND-ONLY WITNESS
```

**One kernel, one 360-position toroidal surface, six speed-control addresses, zero additional kernel slots.**

This is a **register and transition contract**: it is not an empirical theory of stars, nucleons, Planck-scale structure, stellar spectra, general relativity, or cosmology.

## 2. Source hierarchy and freeze policy

1. Authoritative historical frozen commit: `de8f8b80aba3a73dd371811f6b4be39df92e45ce`.
2. Frozen executable: `kernel/frozen/ket-toroid-360-3-3-v20/toroid_speed.py`.
3. Frozen digest manifest: `kernel/frozen/ket-toroid-360-3-3-v20/FREEZE_MANIFEST.json`.
4. Frozen overview: `kernel/frozen/ket-toroid-360-3-3-v20/FREEZE.md`.
5. Historical design reference: `kernel/generative/leviathan-ancestor-v20/README.md`; prior v0.1–v1.9 files remain provenance.
6. Companion locally executed archive: `KET_TOROID_FROZEN_v20_20261013.zip`, with full source, renderer, blueprint, results and verification files; separately supplied, not all uploaded as GitHub files.

A Git commit hash addresses immutable *content in Git*. A conventional branch name is **not a protected immutable branch**. Do not rewrite the pinned content; add a new version if the implementation must evolve.

## 3. System boundaries

**Within this freeze**

- A 20 × 18 periodic toroidal surface index.
- Six separately addressed control positions, reused in two complementary passes.
- Discrete angular-rate, phase, and phase-error state.
- Exact signed command words `--+` and `++-`.
- 360-tick replay, 68 validation checks, 13 hash-chained witness events.
- Symbolic metadata: seven amplitudes, three carriers, pinned zero, dual-Green Chariot.
- Compatibility references to the preexisting LEVIATHAN/K.E.T./LIFE ENGINE architecture.

**Outside this freeze**

- New physical dynamics, equations of state, measured stellar spectra, empirical cosmological topology, gravitational field solutions, biological evolution, atomic chemistry, or independent tests of the LEVIATHAN ancestry hypothesis.
- Literal computation of each Planck-time or smaller tick across geological history.
- Any assignment of measured wavelength, mass, spin, energy, or force to a color, carrier, numbered Chariot station, or control word.

## 4. Physical geometry versus model addresses

### 4.1 Surface registry

| Attribute | Frozen value |
|---|---:|
| Surface skins | 20 |
| Sectors per skin | 18 |
| Surface vertices | 360 |
| Surface edges | 720 |
| Surface faces | 360 |
| Euler characteristic | 0 |
| Control addresses | 6 |
| Entire local registry | **366** |

The inherited periodic-quadrilateral torus uses `V = 20 × 18 = 360` surface vertices, degree four per vertex, `E = 2V = 720` edges, and `F = 360` quadrilateral faces. Its Euler characteristic is

```math
χ = V − E + F = 360 − 720 + 360 = 0.
```

Those are graph/topological counts. The six separate controls are **not** faces, edges, physical angle increments, or six extra toroidal surface vertices. Thus they must **not** enter the above Euler calculation.

### 4.2 Address formula and periodic closure

A compatible logical addressing convention is:

```text
skin    a in {0,...,19}
sector  b in {0,...,17}
surface_address(a,b) = 18*a + b  // 0..359

neighbors of (a,b):
  (a+1 mod 20,b)
  (a-1 mod 20,b)
  (a,b+1 mod 18)
  (a,b-1 mod 18)
```

This describes the existing 20×18 periodic topology. A graphical embedding is not required for the controller recurrence.

### 4.3 180° inward-turn interpretation

In the user's geometric mnemonic, the torus meridian has an **outer 180° sweep** and an **inner 180° sweep**, closing to a full **360°**. Angles are not linear distances. The statement `360 + 3 + 3 = 366` is **address accounting**, not a physically 366° rotation.

For an ordinary embedded mathematical ring torus with major radius `R > r > 0`, a standard parameterization is

```text
x = (R + r cos θ) cos φ
y = (R + r cos θ) sin φ
z = r sin θ
```

with `θ` and `φ` periodic on `[0, 2π)`. Its Gaussian curvature is

```text
K(θ) = cos θ / [r (R + r cos θ)]
integral(T, K dA) = 2πχ = 0.
```

Outer and inner signed contributions cancel **in their integrated Gaussian curvature**. That does not imply zero local curvature, zero mass, cancelled gravity, or a verified toroidal physical universe.

### 4.4 Scale changes

Under a uniform similarity scale factor `s > 0`,

| Geometric quantity | Scale factor |
|---|---|
| `R, r` and all lengths | `s` |
| Area | `s²` |
| Enclosed volume | `s³` |
| Gaussian curvature | `s^-2` |
| Angle, topology, `R/r`, Euler characteristic | unchanged |
| Integrated Gaussian curvature | unchanged: zero |

At fixed density, mass scales as `s³`; at fixed mass, density scales as `s^-3`. These represent different physical assumptions. Geometric self-similarity alone is not a theory that every physical quantity is scale-invariant.

## 5. The six addressed control positions

### 5.1 Exact canonical words

```text
SLOW = --+   // aggregate sign -1
FAST = ++-   // aggregate sign +1

FIRST  = --+ ++- = --+++-
RETURN = ++- --+ = ++---+

FIRST + RETURN = --++++-++---+  [written as two six-command passes]
```

The concatenated **12-character** execution stream is defined by literal concatenation of `FIRST` and `RETURN`. The command words and their order are immutable for this v2.0 case.

### 5.2 Signs

| Token | Frozen demonstration behavior |
|---|---|
| `-` | Decrease angular speed by `δ` for this tick |
| `+` | Increase angular speed by `δ` for this tick |
| `hold` | No angular acceleration, while motion continues |

These are **defined signs in this discrete demonstration**, not identified physical forces or assigned glyph semantics for unrelated versions of the kernel. The operator names gravity, expansion, compression, containment and explosion remain separately defined abstractions.

### 5.3 Exact addressed execution order

| Relative tick | Control address | Word | Symbol |
|---:|---:|---|:---:|
| 1 | 360 | `--+` | `-` |
| 2 | 361 | `--+` | `-` |
| 3 | 362 | `--+` | `+` |
| 4 | 363 | `++-` | `+` |
| 5 | 364 | `++-` | `+` |
| 6 | 365 | `++-` | `-` |
| 7 | 363 | `++-` | `+` |
| 8 | 364 | `++-` | `+` |
| 9 | 365 | `++-` | `-` |
| 10 | 360 | `--+` | `-` |
| 11 | 361 | `--+` | `-` |
| 12 | 362 | `--+` | `+` |

The same addresses 360…365 are visited a second time. **There are six distinct controls, not twelve.** The model does not create new cubits or replace the established `C.A.T.G.N.O` indexing; its dual-triplet schedule is one defined *usage* of those controls.

## 6. Formal state and update rule

### 6.1 State

The execution state is

```text
S_k = (k, theta_k, omega_k)
k       : integer tick index, 0..360
theta_k : unwrapped accumulated phase in degrees
omega_k : angular rate in degrees per tick
```

Initial state:

```text
k = 0
theta_0 = 0 degrees
omega_0 = 1 degree/tick  // illustrative baseline
delta = 1/10 degree/tick // illustrative control increment
```

### 6.2 Exactly reproduced step sequence

With `s_k = -1` for `-`, `+1` for `+`, and `0` for holds:

```text
omega_(k+1) = omega_k + delta * s_k
theta_(k+1) = theta_k + omega_(k+1)
phase_offset_(k+1) = theta_(k+1) - omega_0 * (k+1)
```

**Update speed first, then advance phase**: this convention is essential to the specified numerical trace. The source uses Python `fractions.Fraction` internally for exact rational values; display fields convert selected values to floating-point.

### 6.3 Parameter validity

The frozen executable guards

```python
assert delta >= 0 and base > 2*delta
```

The condition prevents negative angular rates under the frozen sequences, which can dip two increments below baseline. `base=1` and `delta=1/10` are illustrative and must not be promoted into new immutable laws of astrophysics or the broader kernel.

## 7. Complete 12-command example trace

For the exact frozen `base=1` and `δ=0.1` case:

| Tick | Command | Address | Speed °/tick | Phase ° | Offset ° |
|---:|:---:|---:|---:|---:|---:|
| 0 | init | — | 1.0 | 0.0 | 0.0 |
| 1 | - | 360 | 0.9 | 0.9 | -0.1 |
| 2 | - | 361 | 0.8 | 1.7 | -0.3 |
| 3 | + | 362 | 0.9 | 2.6 | -0.4 |
| 4 | + | 363 | 1.0 | 3.6 | -0.4 |
| 5 | + | 364 | 1.1 | 4.7 | -0.3 |
| 6 | - | 365 | 1.0 | 5.7 | -0.3 |
| 7 | + | 363 | 1.1 | 6.8 | -0.2 |
| 8 | + | 364 | 1.2 | 8.0 | 0.0 |
| 9 | - | 365 | 1.1 | 9.1 | +0.1 |
| 10 | - | 360 | 1.0 | 10.1 | +0.1 |
| 11 | - | 361 | 0.9 | 11.0 | 0.0 |
| 12 | + | 362 | 1.0 | 12.0 | 0.0 |

At tick 6 the speed is recovered but phase is **lagging by 0.3°**. After the complementary six commands both speed and phase return to baseline.

The remaining **348 neutral ticks** hold speed at `1°/tick`, giving

```text
theta_360 = 12 + 348 = 360 degrees
omega_360 = 1 degree/tick
phase_error_360 = 0 degrees.
```

The periodic toroidal viewpoint allows the displayed angular position to reduce modulo 360°, but the code retains **unwrapped accumulated phase** to prove the complete 360° traversal.

## 8. Why the two passes cancel

For the first six signs `(-,-,+,+,+,-)`, the relative speed-offset coefficients after each operation are `(-1,-2,-1,0,+1,0)δ`. Their sum is `-3δ`. Final net rate change is zero because the six signs sum to zero.

For the complementary signs `(+,+,-,-,-,+)`, the coefficients are `(+1,+2,+1,0,-1,0)δ`, summing to `+3δ`. Final net rate change again equals zero.

Therefore:

```text
FIRST:
  Δomega = 0
  Δtheta - 6*base = -3*delta

RETURN:
  Δomega = 0
  Δtheta - 6*base = +3*delta

BOTH:
  Δomega = 0
  Δtheta - 12*base = 0.
```

This is a **conditional discrete-control identity**, not a universal result for all speeds, toroidal geometries, physical forces, gravitational conditions, or different update conventions. Changing the schedule or applying nontrivial dynamics during holds can break this cancellation.

## 9. Symbolic 11-slot register, independent of 366 addresses

The frozen related model has **7 amplitudes + 3 carriers + 1 pinned zero**. Those eleven symbol slots are **a view or taxonomy**, not eleven extra addressed cells.

| Symbol slot | ID | Exact label | Category |
|---:|---|---|---|
| 0 | 0 | zero | pinned center |
| 1 | A1 | Red | amplitude |
| 2 | A2 | Green | amplitude |
| 3 | A3 | Blue | amplitude |
| 4 | A4 | Orange | amplitude |
| 5 | A5 | Purple | amplitude |
| 6 | A6 | Green | amplitude |
| 7 | A7 | Yellow | amplitude |
| 8 | C1 | White | carrier |
| 9 | C2 | Black | carrier |
| 10 | C3 | Gray | carrier |

**Both Green slots are required and distinct**: A2 and A6. Do not deduplicate one because the visible color names match. Physical frequencies, amplitudes, carrier dynamics, and numerical interactions are **not determined** by the color labels alone. These eleven mnemonic slots do not establish eleven observed spacetime dimensions or a physical M-theory embedding.

## 10. Green Chariot contract

Keep the exact literal **with a single backslash**:

```text
GREEN :: THE CHARIOT
123 {{45/|\54}} 678
```

Structural parsing:

| Region | Literal stations |
|---|---|
| Left wing | `1 2 3` |
| Left inner | `4 5` |
| Hinge / center operator motif | `/|\` |
| Right inner (reversed) | `5 4` |
| Right wing | `6 7 8` |

There are eight **unique station numbers** but ten **printed digit occurrences**, because 4 and 5 appear twice. The Green Chariot relates **A2 to A6** without merging them or instantiating new amplitudes. No empirical propulsion, stellar dynamics, wave function or magnetic mechanism is assigned to this glyph by the frozen implementation.

## 11. Five operators and the independent speed program

Inherited named operators:

| Operator | Earlier abstract functional interpretation |
|---|---|
| Gravity | inward attraction |
| Expansion | outward growth |
| Compression | inward contraction |
| Containment | restorative boundary behavior |
| Explosion | impulsive outward disturbance |

The v2.0 signed triplets are a *separate rate-update scheduler*. They are **not** a reduction of the five named operators into three forces, and they do not assign real physical forces to the torus.

The v1.3 artificial stable-radius manifold and the superseded v1.4 five-pair construction are **not** copied into this frozen specification as empirical proof. The v1.5 correction to seven amplitudes and three carriers remains authoritative for symbol counts.

## 12. K.E.T., ancestry, and biological overlays

These adjacent semantics are **preserved but not simulated** in `toroid_speed.py`:

- **K.E.T.**: Kernel · Emergence · Time; one nested kernel. Earlier local identity/understanding operators and three governance tracks are inherited and must not be rewritten by a speed scheduler.
- **0root / LEVIATHAN**: user-defined hypothetical ancestral mnemonic. It is a symbolic lineage identity across scales, not an identified fossil organism or evidence that all known species evolved from the once-largest body.
- **Carbon**: chosen biochemical assembly scaffold in the symbolic grammar.
- **Nitrogen**: exact user mnemonic `N :: CATGNO` (C,A,T,G,N,O). This is not a demonstrated six-letter DNA chemistry and does not imply every periodic-table element actually participates in biology.
- **LIFE ENGINE**: independently active descendants, divergent and convergent lines, local deaths/recycling, append-only witness, and existing one-judge/two-player local boards. Dormancy (TUN) is not death.
- **24!**: `620448401733239439360000` unrestricted symbolic permutations of 24 markers; not a physical count of viable evolutionary histories.
- **Kelvin / Calvin / Frank**: three observer views of one thermal state, respectively K, Celsius and Fahrenheit, separate from this speed controller.
- **Snapshot-bubble clock**: an inherited symbolic timing proposal. The speed controller's `tick` is **one discrete computational update**, not automatically a physical second or the proposed tiny cosmic-bubble duration.
- **Sgr A* / A GAS / Earth::0**: previous mnemonic and scaling exercises; **no gravitational prediction or cosmic origin theory was verified**. Earth::0 is a local reference address, not a proven universal center.

All predecessor details remain in their versioned files. **This freeze adds no new chemistry, astrophysics, ancestry or time law.**

## 13. Address budgets

Two inherited namespaces must be kept distinct:

```text
LOCAL:
  250 logical active positions
+ 110 workspace / recycling positions
+   6 controls
= 366 total local positions

PARENT:
  100 positions × 3 riders × 20 skins
+ 6 parent controls
= 6006 distinct parent positions
```

The frozen 360-surface toroidal view is compatible with the 366 local address total, but it is **not** a mathematical identity between the surface's mesh roles and all life-engine semantic roles. A projection or mapping would require its own definition.

## 14. Determinism and audit

The frozen `toroid_speed.py` uses exact rational state evolution and deterministic SHA-256 witness construction.

For each witnessed sample:

```python
record = {"prev_sha256": previous_digest, "data": event_data}
canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
digest = sha256(canonical.encode()).hexdigest()
record["sha256"] = digest
previous_digest = digest
```

The chain begins at `"0" * 64`, and emits **13 witness records**: ticks 1–12 and tick 360.

Frozen final witness head:

```text
fb577fab218e442ede16713d1505375a11b4ad3b4eaa95fe1b18f86ca19ebf68
```

A passing local execution reports **68/68 checks**, including topology/address counts, exact literals, control balance, speed restoration, phase restoration, permitted speeds, Chariot invariants, and **13 event-digest + 13 chain-link checks**. Passing validates **the code's declared model and data integrity**, not physical cosmology. The companion package's second replay was byte-identical, and its SVG/ZIP integrity checks passed.

### 14.1 Acceptance conditions

An implementation of the frozen mathematical controller must satisfy:

```text
surface = 20 * 18 = 360
V = 360; E = 720; F = 360; V-E+F=0
control IDs exactly {360,361,362,363,364,365}
total = 366

SLOW   == "--+"
FAST   == "++-"
FIRST  == "--+++-"
RETURN == "++---+"

initial (phase,speed) == (0,1)
delta == 1/10
after tick 6  (phase,speed) == (57/10,1)
after tick 12 (phase,speed) == (12,1)
after tick 360 (phase,speed) == (360,1)

seven amplitudes == [red,green,blue,orange,purple,green,yellow]
three carriers  == [white,black,gray]
pinned zero == 0
chariot == "123 {{45/|\54}} 678"

witness count == 13
witness head == fb577fab218e442ede16713d1505375a11b4ad3b4eaa95fe1b18f86ca19ebf68
check count == 68
```

## 15. Byte-hash manifest for shipped v2.0 assets

These SHA-256 hashes come from the **frozen manifest**. A file is byte-for-byte compatible only if its digest matches.

| File | SHA-256 |
|---|---|
| `toroid_speed.py` | `e1ed41c29c433a785861562d39e67ce812b968f8f622ed7d339f50a660e3f546` |
| `render_blueprint.py` | `2dc6d6a9802c9f1c42f05999960ba957c602e5ea6de2d0d0da72cef6703e66e3` |
| `results.json` | `3854fe5fe2153a0f04aa24ecfcca0f4d5a142ce982cdb78c36e5b118757d1482` |
| `TOROID_360_3_3_BLUEPRINT.svg` | `964de9f6509a6f7f72aa51036e7bb71bb1e7779267aafd54f0ccc9743ea521f3` |
| `TOROID_360_3_3_PREVIEW.png` | `6830cf81d6f13eb2b2779cab523d78cca859f94d973c8d5f9330d4a739ff9c5c` |
| `README.md` | `ad9f93e15666b367530fb39ded38bc8f4a2613d12bec8e0dac4c87eb9ab0bd67` |

Freeze-file Git blob hashes verified separately at the pinned commit:

| GitHub file | Git blob SHA-1 |
|---|---|
| `toroid_speed.py` | `a451bf3ef9efd40e9a5c1d79f2823f2389efb0c9` |
| `FREEZE_MANIFEST.json` | `21e210ac78b1bceece5213afc087617a922264fb` |
| `FREEZE.md` | `53fde3bfa4146667650f3e2d732a41651f5a9732` |

These are **different hashing schemes**. Git's object hash includes the blob header; its SHA-1 is not supposed to equal the content-only SHA-256.

## 16. Reproduction procedure

### Frozen Git source

```bash
git clone https://github.com/DavidWise01/oasis.git
cd oasis
git switch --detach de8f8b80aba3a73dd371811f6b4be39df92e45ce
python kernel/frozen/ket-toroid-360-3-3-v20/toroid_speed.py
```

The frozen executable writes a deterministic `results.json` in its working directory. For a clean repository checkout, running it **creates a generated output file**; it does not modify the frozen Python source.

### Companion ZIP

Extract the separately delivered `KET_TOROID_FROZEN_v20_20261013.zip`. With Python 3:

```bash
python toroid_speed.py
python freeze_verify.py
```

The archive also contains the high-definition vector schematic. Check manifest hashes **before** regenerating results if preservation of the original shipped files is required. Do not mistake checksum checking for astrophysical experimental evidence.

## 17. Version lineage and changes excluded from this freeze

| Milestone | Role retained |
|---|---|
| v0.8 | Concurrent biological-life divergence and convergence |
| v0.9 | Carbon assembly and exact nitrogen `CATGNO` |
| v1.0 | Kelvin/Calvin/Frank thermal observer triad |
| v1.1 | 13.8 Ga *symbolic snapshot* clock |
| v1.2 | TUN / DIAMOND / CRYSTAL rotating roles |
| v1.3 | Abstract 11-component attracting-manifold example |
| v1.4 | Superseded five-pair ±5 amplitude interpretation |
| v1.5 | **Corrected** 7 amplitudes + 3 carriers + zero |
| v1.6 | Dual-Green Chariot, exact `123 {{45/|\54}} 678` |
| v1.7 | Sgr A* comparison; structural analogy only |
| v1.8 | Earth::0 all-gas counterfactual; mass scaling |
| v1.9 | Toroidal 180°+180° and `360+6` separation |
| **v2.0** | **Frozen dual-triplet speed controller `--+ ++-`** |

A prior analogy, numerical demonstration, or unvalidated hypothesis does not become a certified physical constant merely by appearing in this lineage.

## 18. Freeze acceptance and post-freeze evolution

**Invariants to preserve without mutation**

- All exact control words and their address ordering.
- Fixed surface and local address counts.
- Both distinct Green amplitude slots.
- The raw Chariot glyph including its single backslash.
- Preserved nil/zero semantics and separate `0root` referent.
- Original deterministic calculation, witnessed digest, and file checksums.
- Clear separation between symbolic computation and measured physical reality.

**Changes require a new version, not an edit to v2.0**

- Reassigning control signs or phases.
- Changing 20×18 surface or six-address register.
- Introducing time-dependent accelerations, additional forces, physical angular velocities, or a nonzero carrier transport rule.
- Altering the pinned zero, adding a new color, combining two Greens, or changing the Chariot glyph.
- Coupling the controller to real astronomical observations, numerical relativity, material chemistry or a biological trajectory.

Version-specific code and evidence should be created **in a new path**, with provenance back to this frozen commit. The branch name alone must never be represented as an irreversible cryptographic lock.

## 19. Known limits and nonclaims

- A torus is a mathematical surface or volume; this controller does not prove that the observable universe has toroidal global topology.
- Six speed control addresses are not six extra geometric degrees.
- Zero integrated Gaussian curvature does not mean zero spacetime curvature or gravitational force.
- Seven color labels are not seven physically measured frequencies.
- Three carrier labels are not three observed particles or recognized field carriers.
- Eleven mnemonic positions are not proof of eleven spacetime dimensions.
- The toy controller models one defined time-step rule; a real rotating mass might respond very differently to torque, dissipation or relativity.
- Closing one 360-step example does not establish stability under arbitrary perturbations.
- Exact hash agreement and 68/68 checks certify reproducibility of a symbolic program, **not external truth**.

## 20. Canonical references

- **Pinned freeze commit:** https://github.com/DavidWise01/oasis/commit/de8f8b80aba3a73dd371811f6b4be39df92e45ce
- **Frozen source:** https://github.com/DavidWise01/oasis/blob/de8f8b80aba3a73dd371811f6b4be39df92e45ce/kernel/frozen/ket-toroid-360-3-3-v20/toroid_speed.py
- **Frozen manifest:** https://github.com/DavidWise01/oasis/blob/de8f8b80aba3a73dd371811f6b4be39df92e45ce/kernel/frozen/ket-toroid-360-3-3-v20/FREEZE_MANIFEST.json
- **Frozen declaration:** https://github.com/DavidWise01/oasis/blob/de8f8b80aba3a73dd371811f6b4be39df92e45ce/kernel/frozen/ket-toroid-360-3-3-v20/FREEZE.md
- **Authoritative v2.0 design narrative:** https://github.com/DavidWise01/oasis/blob/de8f8b80aba3a73dd371811f6b4be39df92e45ce/kernel/generative/leviathan-ancestor-v20/README.md
- **Source Chariot mnemonic:** https://github.com/DavidWise01/oasis/blob/de8f8b80aba3a73dd371811f6b4be39df92e45ce/kernel/generative/leviathan-ancestor-v16/README.md

---

**FINAL FROZEN DECLARATION**

```text
KET :: 0root
TOROID :: 360
SLOW :: --+
FAST :: ++-
EXTRA :: 3 + 3
REGISTER :: 366
SEVEN :: RED GREEN BLUE ORANGE PURPLE GREEN YELLOW
THREE :: WHITE BLACK GRAY
PINNED :: ZERO
CHARIOT :: 123 {{45/|\54}} 678
OPERATION :: gravity expansion compression containment explosion
NITROGEN MNEMONIC :: CATGNO
FULL-CYCLE :: 360 degrees / rate restored / phase restored
VALIDATION :: 68/68 / 13 hash-chained records
STATE :: FROZEN AT GIT COMMIT de8f8b80aba3a73dd371811f6b4be39df92e45ce
POLICY :: ADDITIVE CHANGES ONLY; DO NOT MUTATE FROZEN SOURCE
```
