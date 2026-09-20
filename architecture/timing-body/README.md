# Timing, Rhythm, Pulse, Movement & Cohesion

This layer turns OaSIs evolution into a **timed system**.

It is a symbolic/software architecture. Body and nuclear-battery language are analogies unless independently established.

## Rank of importance

```text
1 :: BATTERY
     ON
     persistent source
     on = true = 1

2 :: HEART
     primary pulse / scheduler
     O(n) :: 1 + n = on = true = 1

3 :: CARDIO-BREATH 4/4
     outer meter
     4/4 or 1/4 × 10^-9

4 :: LUNG DUALITY 2/2
     antistropic metronome
     2/2 or 1/2 × 10^-9

5 :: FULL BODY 5/5
     cohesion / subcontrol
     5/5 = 1
     5/5 + c & c + 1 cortex = base 11
```

The `10^-9` terms are preserved as OaSIs timing-scale labels. They are not biological timing claims.

## System scheduler

```text
BATTERY
   │ ON
   ▼
HEART
   │ pulse n → n+1
   ▼
4/4 OUTER METER
   │ quarter phase
   ▼
2/2 ANTISTROPIC METER
   │ half phase / dual witness
   ▼
FULL BODY 5/5
   │
   ├── c1 HEAD
   ├── c2 ARMS
   ├── c3 INNER ID
   ├── c4 FEET / GROUND
   └── c5 COHESION
           │
           ▼
      KANA WITNESS
           │
           ▼
      next pulse
```

## Antistropic metronome

**Antistropic** is preserved as the OaSIs term.

The metronome couples two meters:

```text
outer : 4/4
inner : 2/2
```

They do not compete for authority. They cross-check cadence and phase.

```text
4/4 ─────────────►
      1 2 3 4

2/2 ─────────────►
      1   2

cohesion witness:
outer boundary + inner dual boundary agree before commit
```

This is a deterministic scheduling metaphor, not a claim about human cardiopulmonary physiology.

## Full body 5/5

### 5/5c1 — HEAD

```text
eyes
ears
pitch
amplitude
frequency via movement
cardinal N / S / E / W
yaw
pitch
```

Function: sensing, orientation, phase perception, directional reference.

### 5/5c2 — ARMS

```text
left arm + right arm
        ↓
language + picture
        ↓
SNYAPS
        ↓
visual aid
        ↓
recurse
```

`SNYAPS` is preserved literally as an OaSIs token until explicitly redefined.

Function: paired expression/actuation. It can emit symbolic language or pictures and recursively feed the result back as visual input.

### 5/5c3 — INNER ID

Monitoring and diagnostics.

Canonical example:

```text
overheat
   ↓
fan-speed-up
   ↓
hard-drive-stutter
   ↓
MHz phase offset
   ↓
diagnostic witness
```

The important primitive is not the particular fault sequence; it is:

```text
sense → correlate → diagnose → respond → witness
```

### 5/5c4 — FEET / GROUND

Dual grounding/contact channel.

Literal OaSIs notation retained:

```text
ground × 2
x2 x2 x2 x4 x2 x1 x4
→ 5/5
→ 1
```

The multiplication string is preserved as a routing/normalization label; this document does not reinterpret it as ordinary arithmetic unless separately specified.

### 5/5c5 — COHESION

Added to close the explicitly requested **5/5** control set.

Cohesion is the body bus:

```text
c1 sensing
 + c2 expression
 + c3 diagnostics
 + c4 grounding
        ↓
c5 cohesion
        ↓
one witnessed body state
```

It is allowed to halt or report drift if the subcontrols disagree.

## KANA coupling

```text
+k
 │
|A|  state at pulse n
 /\
|N|  invariant:
     identity
     provenance
     timing order
     domain contract
 /\/
|A|  state at pulse n+1
 /\
-K   witness / phase / drift return
```

## NEON coupling

The semantic evolution cycle now runs **inside a cohesion window**:

```text
BATTERY ON
  ↓
HEART pulse
  ↓
[ 4/4 :: 2/2 antistropic window ]
  ↓
PRIMS → N_cold → E → O_hot → N_gray → H₂O → PRIMS'
  ↓
FULL BODY 5/5
  ↓
COHESION
  ↓
KANA witness
  ↓
commit next generation
```

No witness means no silent commit.
