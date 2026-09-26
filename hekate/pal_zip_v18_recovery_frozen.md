# PAL-ZIP v18 — RECOVERY / SUCCESSOR COMMITTEE — FROZEN

**Parent:** PAL-ZIP v17  
**State:** FROZEN / 0e  
**Scope:** formal recovery geometry after quarantine.

## Target

Restore a path to liveness after v16/v17 quarantine **without**:

```text
resurrecting quarantined authority
rewriting contradictory evidence
rewriting the prior head
```

## Frozen recovery geometry

```text
RECOVER
::
prior_head
+
exact_quarantine_event
+
old_committee
+
quarantined_set
+
successor_committee
```

The successor committee is canonicalized by sorted unique member identity plus threshold.

## Hard rule

```text
quarantined identity
∩
successor committee
::
EMPTY
```

A quarantined identity cannot silently re-enter through the recovery constructor.

## Baseline

```text
old committee
::
G0 G1 G2 G3

threshold
::
3 / 4

quarantined
::
G1 G2

survivors
::
G0 G3
```

Candidate successor committees preserve the two survivors and add two new identities.

## Certification

- valid successor candidates: 6
- valid recovery events: 6
- constructor failures on valid candidates: 0
- quarantined re-entry attacks: 4
- quarantined re-entry rejections: 4
- quarantined re-entry false accepts: 0
- member-order tests: 144
- member-order failures: 0
- quarantine-event binding mutations: 6
- quarantine mutations preserving same event: 0
- prior-head mutations: 6
- prior-head mutations preserving same event: 0
- old-committee mutations: 6
- old-committee mutations preserving same event: 0
- append-prefix tests: 6
- append-prefix failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
RECOVERY
!=
UNDO QUARANTINE
```

Instead:

```text
OLD HEAD
+
QUARANTINE EVIDENCE
+
SURVIVING AUTHORITY
+
NEW COMMITTEE IDENTITY
::
SUCCESSOR CONFIGURATION
```

This v18 object defines the successor configuration only.
It does **not** yet decide who has authority to approve that reconfiguration.

That approval is intentionally the next layer.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
