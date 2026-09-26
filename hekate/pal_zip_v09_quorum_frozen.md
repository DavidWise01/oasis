# PAL-ZIP v09 — MERGE2 AUTHORITY / 3-OF-4 QUORUM — FROZEN

**Parent:** PAL-ZIP v08  
**State:** FROZEN / 0e  
**Scope:** formal merge authorization only.

## Target

`MERGE2` proves that two fork heads can be joined without erasing either history.

v09 adds the missing distinction:

```text
STRUCTURALLY VALID MERGE
!=
AUTHORIZED MERGE
```

## Frozen quorum

```text
ELIGIBLE
::
G0 G1 G2 G3

THRESHOLD
::
3 of 4
```

A merge is accepted only when at least three **distinct eligible voters**
approve the **exact same MERGE2 identity**.

## Vote bind

```text
vote
::
voter
+
merge_anchor
+
decision
```

The vote is therefore about a specific merge, not "a merge in general."

## Exhaustive certification

- all approval subsets tested: 16
- expected accepted subsets: 5
- actual accepted subsets: 5
- subset mismatches: 0

### Adversarial cases

- duplicate-vote attacks: 12
- duplicate-vote false accepts: 0
- unauthorized-voter attacks: 6
- unauthorized-voter false accepts: 0
- wrong-merge attacks: 4
- wrong-merge false accepts: 0
- invalid-decision attacks: 4
- invalid-decision false accepts: 0

**RESULT: 0e / PASS**

## Frozen invariants

```text
2 / 4
::
NOT ENOUGH

3 / 4
::
ACCEPT

4 / 4
::
ACCEPT
```

and:

```text
DUPLICATE IDENTITY
::
does not create another vote

OUTSIDER
::
does not create authority

VOTE FOR DIFFERENT MERGE
::
does not transfer

VALID GEOMETRY
::
does not imply permission
```

## Stack

```text
v08 :: MERGE2 geometry
v09 :: 3-of-4 authority over that exact MERGE2
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
