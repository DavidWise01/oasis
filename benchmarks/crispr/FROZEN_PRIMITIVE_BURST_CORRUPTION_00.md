# Frozen Primitive Burst Corruption 00

Status: **PASS**

Population: 1,048,576

Burst lengths:
2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 4096, 16384, 65536

Tested channels:
- PAM decision
- mismatch count
- shadow witness
- fold state

Largest contiguous burst:
- 65,536 consecutive bad ticks per channel
- exact recovery: True
- masked faults: 0
- false positives: 0

Dense same-tick overlap:
- 65,536 consecutive ticks
- 3 channels simultaneously
- 196,608 logical faults
- exact recovery across all channels: True

Frozen shell:
`+{-{ .16 .16 .1 .1 .0 .0 .1 .1 .16 .16 }+}-`

```text
2       contiguous -> PASS
4       contiguous -> PASS
8       contiguous -> PASS
16      contiguous -> PASS
32      contiguous -> PASS
64      contiguous -> PASS
128     contiguous -> PASS
256     contiguous -> PASS
512     contiguous -> PASS
1,024   contiguous -> PASS
4,096   contiguous -> PASS
16,384  contiguous -> PASS
65,536  contiguous -> PASS

65,536 ticks x 3 simultaneous channels
= 196,608 logical corruptions
-> exact recovery
-> zero masking

RESULT = 0e
```

Artifact SHA-256 (pre-embedded report JSON): `07e7c061cb5ef0885f1a730fd452a2e0c364f3d8afc10ba8d1470640df91b5dc`
