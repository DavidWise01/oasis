# PAL-ZIP v26 — RESERVE QUARANTINE IN APPEND-ONLY HISTORY — FROZEN

**Parent:** PAL-ZIP v25  
**State:** FROZEN / 0e  
**Scope:** formal provenance for reserve-authority failure.

## Target

v25 detects reserve equivocation.

v26 records that consequence without deleting the contradictory reserve votes.

## Frozen event

```text
RESERVE-QUARANTINE
::
vacuum_root
+
reserve_committee
+
quarantined reserve voter set
+
exact contradictory reserve-vote references
```

## History rule

```text
contradictory reserve evidence
::
unchanged

reserve quarantine
::
append-only consequence
```

So:

```text
RESERVE QUARANTINE
!=
rewrite emergency history
```

## Certification

- conflict scenarios: 10
- quarantine events built: 10
- evidence histories preserved: 10
- evidence-history mutations: 0
- context mutation tests: 20
- context mutations preserving same event: 0
- evidence-ref mutation tests: 20
- evidence-ref mutations preserving same event: 0
- quarantine-set mutation tests: 20
- quarantine-set mutations preserving same event: 0
- append-prefix tests: 10
- append-prefix failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
RESERVE FAILURE EVIDENCE
::
preserved

RESERVE AUTHORITY CONSEQUENCE
::
appended

VACUUM ROOT
::
remains part of provenance
```

If reserve authority is fully quarantined, v26 intentionally leaves the system in
a safe halt rather than inventing a third unanchored authority source.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
