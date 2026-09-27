# Frozen Primitive Validator Self-Corruption 00

Status: **PASS**

Population: 1,048,576

Tested validator failures:
- single-lane witness/comparator logic flip
- one-tick stale channel
- fold-pair mapping corruption
- frozen expected-shell corruption
- decision-rule corruption (`<=3` changed to `<=4`)
- common-mode corruption where light and shadow are both wrong in the same way

Key result:
- Local light/shadow agreement alone is **not sufficient** under common-mode corruption.
- The immutable frozen reference and canonical fold-pair map provide an independent witness.
- The intentionally wrong fold map demonstrated a value-alias case: values could still compare equal, but the canonical mapping witness caught the validator defect.

Frozen shell:
`+{-{ .16 .16 .1 .1 .0 .0 .1 .1 .16 .16 }+}-`

```text
logic flip            -> DETECT
1-tick stale channel  -> DETECT
wrong fold map        -> DETECT (mapping witness)
bad expected shell    -> DETECT
bad decision rule     -> DETECT
common-mode validator -> DETECT via immutable reference

RESULT = 0e
```
