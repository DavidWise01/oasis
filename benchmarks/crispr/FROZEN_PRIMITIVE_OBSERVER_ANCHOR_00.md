# Frozen Primitive Observer-of-Observer Anchoring 00

Status: **PASS**

Truth snapshot hash:
`c5062ab5a44599e9a66d0b141ea09394d7c75532e4a1add43c8cd7f0fd7d1bcd`

Poison snapshot hash:
`b4e801ecc5f495fa9ebbce8045b0a5e2aaa0b5744037ced4e022eca1f8dd570f`

Rule:

```text
observer vote counts only if
observer snapshot hash
==
pre-consensus immutable anchor commitment
AND
anchor epoch matches
AND
observer identity matches
```

Results:

```text
clean anchored consensus                 -> ACCEPT TRUTH
late single snapshot rewrite             -> DETECT / EXCLUDE
late two-observer collusion               -> REJECT POISON
anchor content tamper                     -> DETECT / EXCLUDE
stale valid anchor replay                 -> DETECT / EXCLUDE
observer-anchor identity swap             -> DETECT / EXCLUDE
1 observer+anchor pair compromised        -> TRUTH STILL WINS
2 independent pairs compromised @2 quorum -> FALSE CONSENSUS boundary
```

Key result:

```text
pre-consensus immutable commitments
prevent later observer history rewriting.

Remaining boundary:
threshold-many independent observer+anchor pairs
must be compromised consistently.
```

RESULT = 0e
