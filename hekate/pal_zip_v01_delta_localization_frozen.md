# PAL-ZIP v01 — DELTA LOCALIZATION — FROZEN

**Parent:** PAL-ZIP v00  
**State:** FROZEN / 0e  
**Scope:** formal string transform only.

## New invariant

For a known-palindromic source with exactly one nontrivial symbol substitution:

```text
off-center delta
::
rail symmetry identifies the exact mirror PAIR
{ i , n-1-i }

but
::
symmetry alone does not identify which endpoint changed
```

For odd-length strings:

```text
center index
::
i = n-1-i

center-only substitution
::
remains palindrome-symmetric

therefore
::
not detectable by palindrome symmetry alone
```

## Certification

Exhaustive palindromes tested through length `16`.

- palindromes: `174,761`
- one-symbol deltas: `7,776,948`
- off-center deltas: `7,514,808`
- exact mirror-pair localizations: `7,514,808`
- missed off-center deltas: `0`
- wrong-pair localizations: `0`
- center deltas: `262,140`
- center deltas correctly symmetry-invisible: `262,140`
- unexpected center flags: `0`
- baseline false flags: `0`

**RESULT: 0e / PASS**

## Even geometry

```text
V[k]  <---- mirror pair ---->  S[m-1-k]
```

## Odd geometry

```text
V[k]  <---- mirror pair ---->  V[len(V)-1-k]
S[k]  <---- mirror pair ---->  S[len(S)-1-k]
```

## Information limit

```text
ONE MISMATCHED MIRROR PAIR
::
localizes {"left endpoint","right endpoint"}

WITHOUT REFERENCE DATA
::
cannot decide which endpoint is the altered one
```

This limit is preserved rather than guessed through.
