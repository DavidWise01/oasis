# PAL-ZIP v28 — PRE-ANCHOR TIMING / NO POST-HOC AUTHORITY — FROZEN

**Parent:** PAL-ZIP v27  
**State:** FROZEN / 0e  
**Scope:** formal ancestry requirement for safe-halt exit authority.

## Target

v27 permits a safe-halt exit only through a separately pre-anchored authority source.

v28 freezes what **pre-anchored** means:

```text
authority registration
must already occur
before
the SAFE-HALT event
in append-only history
```

A source introduced after the halt is not retroactively authoritative.

## Frozen registration

```text
AUTH-REGISTER
::
source identity
```

and:

```text
AUTH-REGISTER(source) index
<
SAFE-HALT index
```

is required for that source to authorize exit.

## Certification

- pre-halt registration positions tested: 4
- pre-halt positive failures: 0
- post-halt registration positions tested: 4
- post-halt false accepts: 0
- missing-source tests: 3
- missing-source false accepts: 0
- before/after halt reorder tests: 3
- reorder false equivalences: 0
- wrong-source tests: 3
- wrong-source false accepts: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
AUTHORITY INTRODUCED AFTER HALT
::
NOT AUTHORITY FOR THAT HALT
```

and:

```text
T0 registered before halt
::
does not authorize T1
```

So the safe-halt escape path is bound to real ancestry rather than a boolean flag
that could be asserted after the fact.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
