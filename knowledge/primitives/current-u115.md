# Unit U115 — 2026-H2 through 2026-09-19

```text
ROOT COMMUNICATION PRIMITIVE

Alice
  │ intent/state
  v
ENCODE
  │
  v
[ BOUNDED BOX / CHANNEL ]
  │
  v
DECODE
  │
  v
Bob
  │
  └── witness / ack / error / provenance ──> return to Alice
```

The return path is the **toroidal** part of this OaSIs architecture: a closed verification loop, not a claim that the physical Internet is a torus.

## 1. Electronics

```text
physical:
potential → current → switch → threshold

digital:
LOW/HIGH → gate → state → clock → memory

machine:
bit → byte → word → opcode → register/ALU → control

boundary:
pin → bus/lane → controller → DMA/MMIO → IOMMU → witness
```

**Keep:** state, timing, explicit boundaries, measurement.  
**Retire:** pretending a digital abstraction makes analog noise, timing, leakage, heat, or power disappear.  
**Integrate:** every digital box ultimately needs a physical witness.

## 2. Networking

```text
message
→ frame
→ packet
→ address/name
→ route
→ transport stream
→ security
→ application
→ observation
```

**Keep:** packet switching, layered endpoints, naming indirection, ACK/error paths, encrypted transport.  
**Retire:** obsolete base specifications and new designs that assume old TLS.  
**Integrate:** modern TCP spec, QUIC/HTTP3 where useful, TLS 1.3 baseline, algorithm agility and post-quantum transition.

## 3. Storage / hard-drive isolation

```text
file
  ↓
filesystem
  ↓
volume / namespace
  ↓
block
  ↓
controller
  ↓
bus / DMA
  ↓
physical media
```

Isolation has to block the relevant path:

```text
permissions
< read-only filesystem
< namespace / volume boundary
< encryption + separate key
< device offline / driver unbound
< controller / IOMMU / DMA boundary
< physical write blocker / removed data path
< power removal / physical removal / separate host
```

Sanitization/destruction is a **different lifecycle operation** used when media leaves service.

## 4. Java

```text
source token
→ type
→ statement/control
→ object/method
→ class file / bytecode
→ verifier / class loader
→ interpreter/JIT
→ heap + GC
→ thread/concurrency
→ module/runtime image
```

**Keep:** JVM portability, type safety, managed memory, compatibility, explicit modules.  
**Retire:** applet-era assumptions and dependence on JDK internals.  
**Integrate:** stable LTS operations with awareness of the current Java SE specification and six-month evolution.

## 5. Feng Shui / spatial layer

Encoded as a **cultural spatial-design heuristic**, not physical law:

```text
site
→ boundary
→ entrance
→ path
→ center
→ orientation
→ balance
→ material/light
→ human fit
```

**Keep:** circulation, orientation, clear entrances, sightlines, light, clutter control, balance, personal/cultural meaning.  
**Retire:** treating qi or auspicious mappings as experimentally established engineering quantities.  
**Integrate:** test practical choices against accessibility, observation, actual use, environmental measurements, and occupant preference.

## 6. Art & Beauty

```text
point / line
→ shape
→ value
→ color
→ texture
→ space
→ hierarchy
→ rhythm
→ figure / ground
→ human meaning
```

Beauty is not one deterministic score.

**Keep:** hierarchy, contrast, negative space, alignment, grouping, rhythm, legibility, meaning.  
**Retire:** decoration that overwhelms the content or claims one universal taste.  
**Integrate:** perceptual structure + accessibility + culture/context + individual preference.

## Compression rule

The engine may retain all 486 primitive atoms internally.

The human surface should normally expose only the smallest number of choices needed for a meaningful decision.