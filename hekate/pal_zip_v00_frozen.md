# PAL-ZIP v00 — FROZEN

**State:** FROZEN / 0e  
**Scope:** formal string transform only; no biological targeting or edit design.

## Transform

```text
input :: s0 s1 s2 s3 ...

VISIBLE :: s0 s2 s4 ...
SHADOW  :: s1 s3 s5 ...
```

## Direct palindrome rule

```text
if n is even:
    V == reverse(S)

if n is odd:
    V == reverse(V)
    and
    S == reverse(S)
```

No source reconstruction is required for classification.

## Frozen certification

- alphabet: `{A,C,G,T}` used only as a four-symbol formal alphabet
- exhaustive lengths: `0..12`
- strings tested: `22,369,621`
- palindromes encountered: `10,921`
- classification mismatches: `0`

**RESULT: 0e / PASS**

## Invariant

```text
PAL-ZIP-00
::
rail_check(split(x))
=
(x == reverse(x))
```
