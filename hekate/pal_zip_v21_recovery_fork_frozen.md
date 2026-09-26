# PAL-ZIP v21 — RECOVERY FORK PROTECTION — FROZEN

**Parent:** PAL-ZIP v20  
**State:** FROZEN / 0e  
**Scope:** formal fork preservation across committee recovery.

## Target

Two different successor committees may be proposed from the same frozen recovery root.

They must not silently collapse into the same history.

```text
RECOVERY_ROOT
      |
      +---- RECOVER_A -> RCERT_A -> ACTIVATE_A
      |
      +---- RECOVER_B -> RCERT_B -> ACTIVATE_B
```

## Frozen rule

Each successor branch contains the exact:

```text
recovery_root
quarantine event
old committee
successor committee
RECOVER object
RCERT
ACTIVATE object
```

The branch head therefore contains its ancestry.

Different successor committees produce different branch heads.

## Certification

Successor candidates preserve `G0,G3` and choose two newcomers from `N0..N3`.

- successor branches: 6
- unique successor heads: 6
- branch pairs tested: 15
- accidental equal-head failures: 0
- identical-tail tests: 15
- silent rejoins after identical tail: 0
- explicit MERGE2 tests: 15
- MERGE2 order failures: 0
- MERGE2-equals-parent failures: 0
- successor-member order tests: 144
- member-order failures: 0
- branches bound to exact recovery root: 6
- recovery-root binding failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
DIFFERENT SUCCESSOR CONFIG
::
DIFFERENT RECOVERY BRANCH
```

and:

```text
SAME LATER PAYLOAD
!=
SAME RECOVERY HISTORY
```

A fork may only be joined explicitly by a new parent-preserving merge object:

```text
ACTIVATE_A ----\
                >---- MERGE2
ACTIVATE_B ----/
```

That merge preserves both recovery branches as ancestry.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
