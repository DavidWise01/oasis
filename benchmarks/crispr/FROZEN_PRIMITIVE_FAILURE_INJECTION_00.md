# Frozen Primitive Failure Injection 00

Status: **PASS**

- Population: 1,048,576
- Injection tick: 524,287
- Corruption classes: shadow witness, PAM decision, mismatch count, fold state
- Corruptions detected: 4/4
- Exact-location detections: 4/4
- Clean-baseline false positives: 0
- Frozen shell: `+{-{ .16 .16 .1 .1 .0 .0 .1 .1 .16 .16 }+}-`

## Result

All four one-change corruptions were detected at the exact injected location. No false positives were observed in the clean control.

```text
shadow witness   -> DETECT @ exact lane
PAM decision     -> DETECT @ exact tick
mismatch count   -> DETECT @ exact tick
fold state       -> DETECT @ exact fold pair

RESULT = 0e
```
