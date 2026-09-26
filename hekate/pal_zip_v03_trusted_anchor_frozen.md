# PAL-ZIP v03 — TRUSTED ANCHOR — FROZEN

**Parent:** PAL-ZIP v02  
**State:** FROZEN / 0e  
**Scope:** formal symbol-string transform only.

## Why v03 exists

PAL-ZIP symmetry detects symmetry-breaking changes, but a change can preserve palindrome symmetry.

Examples already certified:

```text
odd center delta
::
symmetry may remain intact

both endpoints of one mirror pair -> same new symbol
::
symmetry remains intact
```

Therefore PAL-ZIP needs a trusted reference if the requirement is:

```text
UNCHANGED
not merely
STILL SYMMETRIC
```

## Frozen anchor

For the formal alphabet `{A,C,G,T}`, use an exact collision-free reference encoding:

```text
A -> 1
C -> 2
G -> 3
T -> 4

anchor(s)
::
(length(s), base5(s))
```

Because the length is preserved separately and every symbol is a non-zero base-5 digit,
this mapping is injective for finite strings over the stated alphabet.

```text
anchor(x) = anchor(y)
::
x = y
```

within this formal alphabet.

## Combined checker

```text
PAL-ZIP
::
checks structural palindrome symmetry

EXACT ANCHOR
::
checks identity against trusted baseline

TOGETHER
::
symmetry state + unchanged/changed state
```

## Exhaustive certification

Palindrome source lengths: `0..12`

- source palindromes: 10,921
- single-symbol deltas: 354,996
- two-symbol deltas: 5,335,668
- total changed strings: 5,690,664
- symmetry-preserving changed strings: 185,688
- symmetry-breaking changed strings: 5,504,976
- exact-anchor misses: 0
- SHA-256 operational samples: 100,000
- SHA-256 sample collisions observed: 0

**RESULT: 0e / PASS**

## Important distinction

```text
EXACT BASE-5 ANCHOR
::
mathematically injective for the declared finite alphabet

SHA-256
::
compact operational fingerprint
::
collision-resistant, not claimed collision-free
```

## Contract bind

```text
{{ -i \::/ { e | r } }}

e
::
EMPH reference / content identity

r
::
route / authority / provenance / time

trusted anchor
::
binds expected e-state to r provenance
```

Thus:

```text
PAL-ZIP says
::
is the geometry still symmetric?

ANCHOR says
::
is it still the same content?
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
