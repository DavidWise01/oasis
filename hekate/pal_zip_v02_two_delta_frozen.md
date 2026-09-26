# PAL-ZIP v02 — TWO-DELTA CHARACTERIZATION — FROZEN

**Parent:** PAL-ZIP v01  
**State:** FROZEN / 0e  
**Scope:** formal symbol-string transform only.

## Target

Characterize two simultaneous nontrivial symbol substitutions directly from PAL-ZIP rail symmetry.

## Certified rule

For each mirror pair `{i, n-1-i}`:

```text
final[i] == final[n-1-i]
::
no rail mismatch for that pair

final[i] != final[n-1-i]
::
that exact mirror pair is localized
```

This means two edits are not automatically equivalent to two detectable errors.

### Different mirror pairs

Two substitutions on two different non-center mirror pairs produce two localized pairs, unless later changes restore equality inside a pair.

### Same mirror pair

Starting from a palindrome, both endpoints originally match.

```text
both endpoints changed to SAME new symbol
::
palindrome symmetry preserved
::
rail-only checker cannot detect the change

both endpoints changed to DIFFERENT new symbols
::
one mirror-pair mismatch
::
pair localized
```

### Odd center + off-center delta

The center remains symmetry-invisible. The off-center mirror pair is still localized exactly.

## Exhaustive certification

Alphabet: `{A,C,G,T}` as a formal four-symbol alphabet.  
Palindrome lengths: `0..12`.

- palindromes exercised: 10,921
- two-delta cases: 5,335,668
- theory matches: 5,335,668
- theory mismatches: 0
- same-mirror-pair cases: 507,924
- same-pair / equal replacement / symmetry-invisible: 169,308
- same-pair / unequal replacement / pair detected: 338,616
- different-pair cases: 4,368,960
- different-pair exact localization sets: 4,368,960
- center+pair cases: 458,784
- center+pair exact localization: 458,784

**RESULT: 0e / PASS**

## Information boundary

PAL-ZIP is a symmetry checker, not an oracle.

```text
SYMMETRY-PRESERVING CHANGE
::
can be invisible without a trusted reference

SYMMETRY-BREAKING CHANGE
::
localizes the affected mirror pair(s)
```

Therefore a trusted baseline/hash/provenance anchor is required to detect changes that preserve palindrome symmetry.
