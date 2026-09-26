# PAL-ZIP v15 — 3-OF-4 QUORUM INTERSECTION / EQUIVOCATION — FROZEN

**Parent:** PAL-ZIP v14  
**State:** FROZEN / 0e  
**Scope:** formal quorum geometry.

## Target

Characterize what happens if two conflicting MERGE2 identities both appear to have 3-of-4 approval for the same head and committee.

## Quorum geometry

With four eligible identities and threshold three:

```text
any two 3-of-4 quorums
::
intersect in at least 2 identities
```

Exhaustive subset result:

- distinct 3-of-4 quorums: 4
- distinct quorum pairs: 6
- minimum intersection: 2
- intersection-rule failures: 0

## Conflicting merge consequence

If quorum A approves `MERGE:A` and quorum B approves `MERGE:B`
for the same prior head and committee, every identity in their intersection
has approved both conflicting merges.

That is an equivocation record:

```text
same voter
same prior head
same committee
different merge
approve + approve
```

## Certification

- conflicting quorum scenarios: 6
- scenarios requiring equivocation: 6
- scenarios without equivocation: 0
- equivocation detection failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
3/4 + 3/4
on conflicting decisions
::
intersection >= 2
```

Therefore simultaneous conflicting 3-of-4 certificates for the same context
cannot exist without at least two voter identities appearing in both approval sets.

This primitive detects and exposes the contradiction. It does not choose which branch should win.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
