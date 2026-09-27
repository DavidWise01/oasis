# Frozen Primitive Canonical Palindromic / Isomorphic Retest V2

Status: **PASS**

Canonical core:
```text
| -> ` -> 1 1 -> ` -> |
11 ≡ | |
start ≡ end
forward ≅ reverse
```

Full phase:
```text
-+++-Aa+---+Pp-+++-Nn-++-+
```

Tests: **70 / 70 PASS**

Important correction:
A sequence may be palindromic without being the canonical `i` sequence.
The validator now requires both:
1. reversal symmetry, and
2. exact equality to the frozen canonical palindrome.

Thus:
```text
A B C B A -> palindrome, but NOT canonical i
| ` 1 1 ` | -> palindrome AND canonical i
```

Stress:
- all 25 nonzero phase rotations rejected
- malformed HOME0 rejected
- ISO/t^4y misuse blocked
- 65,536 repeated exact cycles stable
- 10,000 palindrome mutations detected
- 10,000 phase mutations detected
- 10,000 Patricia mutations detected

Remaining trust boundary:
```text
canonical core replaced coherently
+
external origin/reference replaced coherently
=
no independent reference remains
```

RESULT = 0e
