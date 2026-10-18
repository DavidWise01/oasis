# TESSY :: INTENT → GEOMETRY → FUNCTION (Locked v1)
- All operations occur inside the symbolic `||||` box.
- Intent is the foundation's governing interpretation. Geometry constrains possible paths; a glyph's function is selected in that context, not assigned universally.
- The bottom letter (one of `A-Z` or `a-z`) locks first, establishing the tone. Preserve uppercase and lowercase distinctions.
- One upper candidate is considered at a time; accept via `LOCK` or reject via `DISCARD`.
- Accepted candidates extend the ordered locked foundation, but the original root intent stays authoritative.
- Continue for as many letters as needed; no arbitrary word length.
- `✓` closes/checks the current foundation after resolving its pending candidate.
- `X` separates completed checked foundations into words. It can be an ordinary glyph inside a word; delimiter status is contextual.
- Provenance should distinguish accepted and discarded proposals; repeated examination does not turn one witness into many.
- This specification is a symbolic executable grammar; it does **not** assert quantum advantage or validate microscopic electron trajectories.

Canonical flow: `{{ INTENT :: FOUNDATION :: CANDIDATE → LOCK/DISCARD :: ✓ :: X }}`

## Test
Run `node docs/mnp-3d/test-intent-foundation-v1.cjs`; fourteen deterministic checks cover alphabet, case, locking, rejection, tone, closure and delimiters.
