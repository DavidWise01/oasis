# Frozen Primitive Physical Entropy / Measurement Provenance Plane 00

Status: **FAIL — stopped at first real failure**

Tests executed: **27**
Tests passed: **26**
Tests failed: **1**

## First failure

```text
calibration_tamper_detected -> FAIL
```

The modeled calibration chain was:

```text
record 0 -> record 1
```

where record 1 contains a hash of record 0.

Changing the contents of **record 1** does not invalidate that link, because there is no later record committing to record 1.

So this structure proves the ancestry of the current head, but **does not authenticate the current head itself**.

```text
C0 --hash--> C1
              ^
              |
        mutate C1 here

no C2 exists to expose the mutation
```

This is the first actual failure on this plane.

## What passed before failure

- independent device / calibration / clock / environment / operator provenance
- distinct measurement traces
- replay recognizability
- epoch/sample binding
- clock rollback detection
- untampered calibration chain validation

## Required next repair

Bind the current calibration head to something outside the chain, for example:

```text
C0 -> C1
       |
       +--> signed/checkpointed head commitment
```

or append a successor:

```text
C0 -> C1 -> C2
           ^
           C2 commits to C1
```

A successor only moves the vulnerable head forward, so the stronger construction is a separately witnessed/head-pinned commitment.

The broader modeled physical-capture boundary was **not promoted as the first failure**, because this calibration-head weakness occurred earlier.

RESULT = **FAIL at unpinned calibration head**
