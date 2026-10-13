# KET — Signed Five-Pair Amplitudes at Zero (v1.4)
Date: 2026-10-12
Status: user-corrected symbolic amplitude geometry, **provisional** mathematical parsing of exponent. Append-only successor to v1.3.

## Exact user declaration — never rewrite silently

```text
its -5 amplitudes at 0 + {{n}1.25}}^{{sqrt5}^1x1.616158^10-35}}
```

## Structural correction

```text
  -5 -4 -3 -2 -1 |0| +1 +2 +3 +4 +5
          5 minus    zero    5 plus
```

This is **eleven signed coordinate addresses, a pinned center zero, and five matched amplitude pairs**, NOT eleven independent species/colors or a claim about eleven measured extra dimensions. Former v1.3 stellar/color labels are possible metadata, not the amplitude definitions.

Let `a_n` denote the five positive amplitude magnitudes (n=1..5). The mirrored state is

```text
x = [-a5,-a4,-a3,-a2,-a1,0,+a1,+a2,+a3,+a4,+a5].
unit(x)=x/sqrt(2*sum(n=1..5, a_n*a_n)).
```

If pairs are exactly antisymmetric and center pinned, the allowed linear states have **five degrees of freedom in R^11**. Intersection with the radius-one 11D sphere is **S^4** (intrinsic dimension four), not the unconstrained v1.3 S^10. Both facts are true in their respective model scopes.

## Literal syntax preserved; ambiguity NOT frozen

The string `{{n}1.25}}^{{sqrt5}^1x1.616158^10-35}}` does not uniquely fix exponent grouping or whether `{n}1.25` means `n × 1.25` or `1.25^n`. Two bounded **demonstration candidates** are calculated:

```text
epsilon := (1.616158e-35 metres)/(1 metre), dimensionless
alpha   := (sqrt(5))^epsilon
case A  : a_n = (n * 1.25)^alpha
case B  : a_n = (1.25^n)^alpha, n=1..5
```

The explicit reference length **1 metre is a computation convention for this experiment only**; it is not supplied or authorized as a kernel invariant. Numerically `alpha - 1 = 1.3005529788418354e-35`, requiring arbitrary precision not ordinary double. No interpretation of a **dimensionful length as a direct mathematical exponent** is allowed without unit normalization. Both candidates are provisional, not a correction to user's exact glyphs.

## Five existing named operators

Continue v1.3 radial dynamics in the paired subspace:
- gravity: `-0.12*x`
- expansion: `+0.30*x`
- compression: `-0.18*x`
- containment: `-0.75*(||x||²-1)*x`
- explosion: externally declared `x *= b` at chosen events

Since expansion = gravity + compression, the resulting between-explosion flow is `dx/dt=0.75*(1-||x||²)*x`, and the signed pairing and zero center remain invariant. Any nonzero initial radius converges to unity under this specific flow; if the radial coefficients lose balance or impulses do not cease, convergence is not guaranteed. No forced 11-channel skew rotation was added because it could break the pinned/mirrored constraint.

## Actual local execution

A reproducible companion ZIP `KET_Signed_Five_Amplitude_v14.zip` was generated in the conversation:
- `signed_amplitudes.py` Python 100-digit Decimal model with both base interpretations, exact scalar logistic radial integration;
- `results.json` (complete two 11-address normalized high-precision vectors and 241 radius checkpoints);
- `signed_amplitude_manifold.svg` source diagram;
- `audit.json`, `README.md`, and `SHA256SUMS`.

Execution used `dt=0.25`, 240 steps, r(0)=0.5, scripted explosion multipliers ×1.55 at t=15 and ×1.35 at t=35. Final r = `1.00000000000000001167872151515...`; convergence within 1.17e−17. 11-address mirror constraints, pinned-zero, 100-digit normalized norms, five operators, deterministic replay, SHA-256 manifest, parseable SVG, ZIP CRC all checked. SHA256 of JSON: `79cc6fa1f975a9e627b9e0c1203c68fa5d2a28c28f80fd139e7bff10881e572f`.

**The GitHub record is a mathematical/report artifact only**; companion ZIP has the executable source and is provided separately, not falsely represented as included in the repository.

## Reality check and old kernel compatibility

User constant `1.616158 × 10^-35` is retained without rewriting. CODATA Planck length is approximately `1.616255 × 10^-35 m`, a small numerical mismatch. See NIST 2022 recommended constants: https://physics.nist.gov/cuu/Constants/ .

This mathematical construct does not derive string theory/M-theory, make 11 independent spacetime dimensions, predict stars or elements, or prove new life. LEVIATHAN/0root, C/carbon, N/CATGNO, KCF observer triad, 24! LIFE ENGINE, 13.8-Ga symbolic bubble clock, and 366 local / 6006 parent allocations remain unchanged. No underlying neural-network retraining and no physical Planck-time simulation.
