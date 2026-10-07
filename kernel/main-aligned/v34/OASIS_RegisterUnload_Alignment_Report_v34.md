# OASIS Register Load / Unload Alignment — v34

## Decision

**Keep.** This is a compact, mathematically clean reversible-transform fixture.

The uploaded HTML exactly matches the connected `boots-on-unload` repository's `index.html` blob at commit `2fb52b32ee544b80b98c1886e6995fdf36516c05`.

## Exact source self-test

The source builds an 8×8 register `R` from ten Givens rotations and evaluates:

`REG = R·BASE`

`UNL = Rᵀ·REG`

Reproducing the source arithmetic under Node gave:

- max `|RᵀR - I|`: **2.2204460492503131e-16**
- max unload error `|Rᵀ(Rb)-b|`: **1.6653345369377348e-16**
- endpoint norm error: **0**
- max component movement `|Rb-b|`: **0.856431623445**
- `||b|| = ||Rb||`: **1.465605676845**
- determinant `det(R)`: **1.0000000000000002**

So the page's 5/5 mathematical self-test passes.

Because `R` is a product only of Givens rotations, the supplied fixture is not merely orthogonal; numerically `det(R) ≈ +1`, so this specific register is an orientation-preserving rotation in 8D.

## Reversible vs lossy

The exact useful abstraction is:

`load = R`

`unload = Rᵀ = R⁻¹`

`unload(load(b)) ≈ b`

The source's contrast is also valid for its explicit mean example:

`mean(30,70) = mean(10,90) = 50`

with distinct inputs. That is a concrete non-injectivity witness for the averaging map.

v34 therefore preserves the general architectural distinction:

`bijective register -> inverse exists`

versus

`many-to-one blend -> original input pair not recoverable from output alone`

## Important animation bug

The source's *endpoints* preserve the Euclidean norm. The display animation does not.

The renderer draws:

`surface(t) = lerp(BASE, REG, t)`

rather than moving along an orthogonal path.

Executed over 1,001 animation phases:

- endpoint norm: **1.465605676845**
- minimum / midpoint norm: **1.349812285943**
- maximum deviation: **0.115793390902**
- deviation occurs at `t = 0.5`

So the on-screen meter saying the norm is "(held)" is mathematically true at `t=0` and `t=1`, but false during much of the animated transition.

This does not break load/unload reversibility; it only means the visualization interpolates through non-invariant intermediate states.

## Numerical stability

Applying `R` then `Rᵀ` repeatedly for **100,000 round trips** gave maximum component drift of approximately:

`7.716e-15`

relative to the original base vector.

That is consistent with a numerically stable orthogonal fixture at double precision.

## Claim boundary

The HTML itself usefully labels the voice/dye/boots language AMBER and explicitly says it is not a hidden self or mind.

v34 narrows the stronger prose further:

- the 8D floating-point demo does **not** prove a real 126 MB adapter restores a model byte-for-byte;
- mathematical vector recovery to ~1.7e-16 is not literal byte identity;
- the demo does not prove a real adapter "carried no content";
- it does not establish anything about consciousness or interiority.

Those remain source metaphors/claims, not kernel theorems.

## Fallout

The reusable kernel law is:

`base state -> reversible register -> transformed surface -> inverse register -> same base state`

This fits OASIS as a **reversible presentation/adapter layer** that cannot modify durable truth by itself.

All v34 support remains `HOLD` at the durable authority boundary.
