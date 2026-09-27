# PAL-ZIP v95 — HIGHER-RECOVERY RANK-CHAIN PREFIX COMMITMENT — FROZEN

**Parent:** PAL-ZIP v94  
**State:** FROZEN / 0e  
**Scope:** bind every v94 higher-recovery rank-chain entry to exact depth and exact previous prefix identity.

## Target

v94 proves:

```text
VALID WITNESS + VALID WITNESS
!=
VALID CHAIN
```

unless exact chain provenance and exact authority-state continuity hold.

v95 adds positional commitment.

A valid v94 chain entry is not enough by itself.

It must also occupy the exact prefix position where it belongs.

## Frozen prefix head

```text
HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-PREFIX-HEAD
::
depth
+
previous_prefix_head
+
exact v94 chain entry
```

Genesis:

```text
HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-PREFIX:ROOT
```

## Frozen placement rule

For depth `n`:

```text
P_n
:=
PREFIX_HEAD(
  depth = n,
  previous_prefix_head = P_(n-1),
  exact_v94_chain_entry = C_n
)
```

Therefore:

```text
VALID v94 CHAIN ENTRY
!=
VALID v95 PREFIX PLACEMENT
```

## Attack geometry

The following must all change prefix identity:

```text
TRUNCATE
REPLACE PREFIX
ROOT GRAFT
SAME-RANK DIFFERENT-STATE SPLICE
WRONG DEPTH
CHAIN-ENTRY TAMPER
```

## Certification

- terminal histories: 6
- prefix links: 9
- prefix-link failures: 0
- state continuity checks: 3
- state continuity failures: 0
- final prefix collisions: 0
- truncation tests: 3
- truncations preserving final identity: 0
- different-prefix replacement attacks: 6
- replacements preserving same head: 0
- same-prefix controls: 9
- same-prefix control failures: 0
- root-graft attacks: 3
- root-grafts preserving same head: 0
- same-rank/different-state splice attacks: 6
- splices preserving same head: 0
- wrong-depth attacks: 9
- wrong-depth preserving same head: 0
- chain-entry tamper attacks: 9
- chain-entry tamper preserving same head: 0
- canonical ordering tests: 66
- canonical ordering failures: 0
- terminal-extension attacks: 6
- terminal-extension false accepts: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
VALID v94 CHAIN ENTRY
+
WRONG PREFIX POSITION
::
DIFFERENT PREFIX IDENTITY
```

and:

```text
TRUNCATE
REPLACE PREFIX
ROOT GRAFT
SAME-RANK DIFFERENT-STATE SPLICE
WRONG DEPTH
CHAIN-ENTRY TAMPER
::
DIFFERENT PREFIX IDENTITY
```

No winner is selected.

v95 commits higher-recovery termination proof to exact historical placement.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
