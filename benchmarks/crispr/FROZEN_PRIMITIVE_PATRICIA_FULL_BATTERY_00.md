# Patricia / SAPPHON Full Battery To Failure 00

Status: **FAIL — first structural alias found**

Frozen identity hash:
`d201d4329ee5a3f16bbb28388fd4d5861898a9deb501e24ee15c5de0730996df`

Tests executed: **48**
Tests passed: **46**
Tests failed: **2**

First failure:
`phase_drift_shift_2`

Second equivalent failure:
`phase_drift_shift_4`

Coverage:
- frozen identity integrity
- role/code/A,etherNet mutations
- exact HOME0 ladder integrity
- photon sign corruption
- `t^4y` threshold boundaries
- symbolic Planck/zero ISO gating
- repeated ISO cycles through 8,192 loops
- phase drift
- 256 nested-ring isolation stress
- 10,000 identity-hash replays
- 5,000 random identity mutations
- 5,000 random HOME0 corruptions
- 5,000 random photon corruptions
- frozen-reference compromise boundary

## First true failure

The canonical photon witness is:

```text
p- p+ p- p+ p- p+
```

It has period 2. Therefore cyclic phase rotations by 2 or 4 positions reproduce the same pattern.

```text
shift 1 -> different -> DETECT
shift 2 -> identical -> ALIAS / FAIL
shift 3 -> different -> DETECT
shift 4 -> identical -> ALIAS / FAIL
shift 5 -> different -> DETECT
```

So the current photon witness proves parity, but not absolute phase origin.

## Required repair

Add an absolute phase/origin witness that is not period-2 invariant, such as a frozen ring index, unique origin token, or address-bound phase marker.

```text
alternating sign witness
+
absolute origin witness
=
phase identity
```

RESULT: **FAIL at even phase rotation**
