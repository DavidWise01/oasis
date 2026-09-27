# Frozen Primitive Multi-Fault Collision 00

Status: **PASS**

Population: 1,048,576

Fault schedule per class: 2, 4, 8, 16, 64, 256, 1024, 4096

Tested classes:
- PAM decision corruption
- mismatch-count corruption
- shadow-witness corruption
- fold-state corruption
- dense overlapping three-channel corruption on the same 4,096 ticks

Results:
- Exact-location recovery: True
- Aliased faults: 0
- False positives: 0
- Dense overlap exact across all three channels: True

Frozen shell:
`+{-{ .16 .16 .1 .1 .0 .0 .1 .1 .16 .16 }+}-`

```text
2      faults -> PASS
4      faults -> PASS
8      faults -> PASS
16     faults -> PASS
64     faults -> PASS
256    faults -> PASS
1,024  faults -> PASS
4,096  faults -> PASS

4,096 same-tick, 3-channel overlaps
= 12,288 logical corruptions
-> exact recovery
-> no aliasing

RESULT = 0e
```
