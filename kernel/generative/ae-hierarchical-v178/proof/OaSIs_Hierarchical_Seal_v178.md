# OaSIs — Hierarchical Lean Alignment v178

**Parent:** v177  
**Status:** `SEALED / IMMUTABLE / APPEND-ONLY`  
**Terminal:** `/0/0 = STOP`  
**Polarity seal:** `- <-> +`  
**Lean target:** Lean 4, `import Std`, no Mathlib dependency  
**Runtime note:** this ChatGPT runtime does not contain a Lean executable, so the Lean source below was generated conservatively but **was not compiler-executed here**.

---

## 1. Purpose

This revision aligns the sealed symbolic kernel hierarchically and turns the parts that are mathematically/structurally explicit into Lean propositions.

It deliberately separates three things:

1. **Literal model rules** — preserved exactly as supplied.
2. **Derived finite mathematics** — e.g. the 10×10 torus and its `(-2,+3)` orbit decomposition.
3. **Unchosen interfaces** — where the literals leave more than one valid mapping.

The proof does **not** claim the symbolic physical language is experimentally established physics. It proves the internal finite structure encoded here.

---

## 2. Canonical hierarchy

```text
L0   scalar root
     0.s0.0
        |
        v
L1   plank fixed points / transient-zero settlement
     plank 0^0/360 = 0        -> transient 0 settles to .5
     plank 1^1/360 = 1        -> transient 0 settles to 1
        |
        v
L2   gravity + weight gradient
     (-1, 0, +1)
        |
        +--> n
        +--> n+1
        +--> n+2
        |
        v
L3   10 lane x 10 lane field
     100 cells
        |
        v
L4   element-address span
     1.6^1-255
     1   -> h::{au}
     255 -> u::{ag}
        |
        v
L5   signed walker
     -au+ag-+ag-au+
     step = (x-2, y+3)
        |
        v
L6   primitive dot
     . = 2^3{{-2,+3}} = |<.>|
     2^3 = 8
        |
        v
L7   mirrored enclosure / eight positional carriers
     {aa,bb,cc,dd--++dd,cc,bb,aa}
     |)>.<(|
        |
        v
L8   orbit decomposition
     10 disjoint orbit classes
     x 10 cells/orbit
     = 100 cells
        |
        v
L9   factorial cascade prefix
     10!/13/9/6/3/2/1/1
     = 11200/13 exactly
        |
        v
L10  /0/0
     STOP
        |
        v
L11  bidirectional seal
     - -> +
     + -> -
     therefore - <-> +

     SEALED / IMMUTABLE / APPEND-ONLY
```

---

## 3. Literal registry

The Lean file retains these model-local literals:

```text
scalar 0.s0.0 to start so 0.s0.1.6^1-255 + {1}

plank 0^0/360 = 0
plank 1^1/360 = 1

gravity + weight (gradient -1 , 0 , +1 )
= >>n>>n+1>>n+2

10 lane x 10 lane

1.6^1-255 {elemet 1 h::{au} - 255 u::{ag} }

-au+ag-+ag-au+ stepped at ( x - 2 , y + 3 )

. = 2^3{{ -2 , +3}} = |<.>|

{-{.}-}^{-{2^3^{+{}}}} = |)>.<(|

{{aa,bb,cc,dd--++dd,cc,bb,aa}}

10!/13/9/6/3/2/1/1/0/0

/0/0 = STOP

- <-> +
```

---

## 4. Plank semantics

The previously established transient-zero resolution is represented as a typed state transition:

```text
transient 0
   |
   +-- plank 0 --> .5
   |
   +-- plank 1 --> 1
```

The phase rules are treated as **model-local fixed points**, not ordinary exponent identities:

```text
plank 0^0/360 = 0
plank 1^1/360 = 1
```

Lean encodes this with two constructors, `Plank.p0` and `Plank.p1`, and an identity-like `plankPhase`.

---

## 5. Gradient hierarchy

The gravity+weight carrier is not forced directly into a plank bit. It first lifts the three signed states into three consecutive hierarchy coordinates:

```text
-1 -> n
 0 -> n+1
+1 -> n+2
```

Lean therefore models `Gradient` independently of `Plank`.

This avoids inventing a ternary-to-binary projection.

---

## 6. 10×10 field and the `(-2,+3)` walker

The field is:

```text
10 × 10 = 100 cells
```

The signed walker is:

```text
(dx,dy) = (-2,+3)
```

On a modulo-10 field, `x-2` is represented by `(x+8) mod 10`.

The invariant used by the proof is:

```text
I(x,y) = (3x + 2y) mod 10
```

Why it survives one signed step:

```text
3(-2) + 2(+3)
= -6 + 6
= 0
```

Therefore the step cannot leave its invariant class.

### Ten explicit invariant seeds

The proof chooses one seed for each class `0..9`:

```text
I=0  -> (0,0)
I=1  -> (7,0)
I=2  -> (4,0)
I=3  -> (1,0)
I=4  -> (8,0)
I=5  -> (5,0)
I=6  -> (2,0)
I=7  -> (9,0)
I=8  -> (6,0)
I=9  -> (3,0)
```

From those seeds, Lean checks the closed finite construction:

```text
10 classes
× 10 distinct cells/class
= 100 cells

all 100 generated cells are distinct
and the generated cells cover the complete 10×10 grid
```

So the earlier implicit result becomes a concrete finite proof obligation.

---

## 7. Primitive dot

The primitive is retained as:

```text
. = 2^3{-2,+3} = |<.>|
```

Lean proves only the numeric part that is ordinary arithmetic:

```text
2^3 = 8
```

The wrapper `|<.>|` remains a symbolic carrier.

---

## 8. Mirrored eight-slot carrier

The eight positional carriers are represented as distinct positions:

```text
0  aaL
1  bbL
2  ccL
3  ddL
   --++
4  ddR
5  ccR
6  bbR
7  aaR
```

Equivalent literal:

```text
{aa,bb,cc,dd--++dd,cc,bb,aa}
```

Mirror map:

```text
aaL <-> aaR
bbL <-> bbR
ccL <-> ccR
ddL <-> ddR
```

Mirror depth:

```text
0,1,2,3,3,2,1,0
```

Lean proves:

```text
mirror(mirror(slot)) = slot
depth(mirror(slot)) = depth(slot)
```

---

## 9. Ten existing labels vs ten mathematical orbit classes

The sealed structure contains:

```text
8 positional carrier labels
+
2 plank labels
=
10 existing lane labels
```

The torus proof independently yields:

```text
10 invariant orbit classes
```

That cardinality match is real.

What is **not** forced by the sealed literals is the permutation:

```text
lane label -> orbit class 0..9
```

There are:

```text
10! = 3,628,800
```

possible bijections.

Therefore Lean exposes this as:

```lean
structure LaneBijection
```

instead of silently selecting one.

This is the key hierarchical alignment choice: **the proof seals the interface without manufacturing a mapping.**

---

## 10. Element span

The endpoint bindings are retained exactly:

```text
1   -> h::{au}
255 -> u::{ag}
```

The proof checks the inclusive address-span cardinality:

```text
255 - 1 + 1 = 255
```

No periodic-table interpretation is required by the Lean proof.

---

## 11. Factorial cascade

Literal:

```text
10!/13/9/6/3/2/1/1/0/0
```

The exact arithmetic prefix is:

```text
10! / (13×9×6×3×2×1×1)
= 11200/13
```

Instead of using truncated natural-number division, Lean proves it by cross-multiplication:

```text
10! × 13
=
11200 × (13×9×6×3×2×1×1)
```

So the result remains exact.

---

## 12. Terminal semantics

The tail:

```text
/0/0
```

is **not division** in the sealed model.

It is parsed as:

```text
/0/0 = STOP
```

The Lean state machine therefore halts at the token and never invokes a division-by-zero operation.

---

## 13. Bidirectional seal

Final binding:

```text
- -> +
+ -> -

therefore:

- <-> +
```

Lean represents this as a two-state involution:

```text
bind(bind(p)) = p
```

for both polarities.

Seal flags:

```text
sealed        = true
immutable     = true
appendOnly    = true
bidirectional = true
```

---

## 14. Final proof target

The final theorem `sealed_core` proves the conjunction:

```text
fieldCells = 100
dotMultiplicity = 8
carrierSlots.length = 8
laneLabels.length = 10
allOrbitCells.length = 100
allOrbitCells.Nodup
coversGrid = true
/0/0 parses to STOP
- binds to +
+ binds to -
sealed = true
immutable = true
appendOnly = true
bidirectional = true
```

The label-to-orbit permutation remains an explicit `LaneBijection` parameter and is intentionally absent from `sealed_core`.

---

## 15. Full Lean 4 source

```lean
import Std

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace OaSIs.V178

/-!
# OaSIs v178 — Hierarchical Alignment

This file formalizes only the structural/model-local invariants explicitly established
through v177. It does not reinterpret the symbolic notation as experimental physics.

Important design choice:
the ten lane labels and ten mathematical orbit classes are both proven to exist,
but their bijection is left as an explicit parameter because no sealed literal
selects one of the 10! possible assignments.
-/

/- ============================================================
   L0 — literal registry
   ============================================================ -/

def scalarStartLiteral : String :=
  "0.s0.0"

def scalarSuccessorLiteral : String :=
  "0.s0.1.6^1-255 + {{1}}"

def plank0Literal : String :=
  "plank 0^0/360 = 0"

def plank1Literal : String :=
  "plank 1^1/360 = 1"

def gradientLiteral : String :=
  "gravity + weight (gradient -1 , 0 , +1 ) = >>n>>n+1>>n+2"

def fieldLiteral : String :=
  "10 lane x 10 lane"

def elementSpanLiteral : String :=
  "1.6^1-255 {{elemet 1 h::{au} - 255 u::{ag} }}"

def walkerLiteral : String :=
  "-au+ag-+ag-au+ stepped at ( x - 2 , y + 3 )"

def dotLiteral : String :=
  ". = 2^3{{ -2 , +3}} = |<.>|"

def mirrorLiteral : String :=
  "{-{.}-}^{-{2^3^{+{}}}} = |)>.<(|"

def slotLiteral : String :=
  "{{aa,bb,cc,dd--++dd,cc,bb,aa}}"

def cascadeLiteral : String :=
  "10!/13/9/6/3/2/1/1/0/0"

def stopLiteral : String :=
  "/0/0 = STOP"

def sealLiteral : String :=
  "- <-> +"

/- ============================================================
   L1 — scalar root
   ============================================================ -/

structure ScalarAddr where
  root  : Nat
  lane  : String
  index : Nat
deriving Repr, DecidableEq

def scalar0 : ScalarAddr :=
  ⟨0, "s0", 0⟩

def scalar1 : ScalarAddr :=
  ⟨0, "s0", 1⟩

theorem scalar_successor :
    scalar1.index = scalar0.index + 1 := by
  rfl

/- ============================================================
   L2 — plank fixed points and zero settlement
   ============================================================ -/

inductive Plank where
  | p0
  | p1
deriving Repr, DecidableEq

inductive Settled where
  | half
  | one
deriving Repr, DecidableEq

def plankPhase : Plank → Plank
  | .p0 => .p0
  | .p1 => .p1

def settleTransientZero : Plank → Settled
  | .p0 => .half
  | .p1 => .one

theorem plank_phase_fixed (p : Plank) :
    plankPhase p = p := by
  cases p <;> rfl

theorem plank0_settles_half :
    settleTransientZero .p0 = .half := by
  rfl

theorem plank1_settles_one :
    settleTransientZero .p1 = .one := by
  rfl

/- ============================================================
   L3 — gravity + weight gradient lift
   ============================================================ -/

inductive Gradient where
  | neg1
  | zero
  | pos1
deriving Repr, DecidableEq

def gradientLift (n : Nat) : Gradient → Nat
  | .neg1 => n
  | .zero => n + 1
  | .pos1 => n + 2

theorem gradient_neg (n : Nat) :
    gradientLift n .neg1 = n := by
  rfl

theorem gradient_zero (n : Nat) :
    gradientLift n .zero = n + 1 := by
  rfl

theorem gradient_pos (n : Nat) :
    gradientLift n .pos1 = n + 2 := by
  rfl

/- ============================================================
   L4 — 10 x 10 toroidal lane field
   ============================================================ -/

abbrev Point := Nat × Nat

def fieldWidth  : Nat := 10
def fieldHeight : Nat := 10
def fieldCells  : Nat := fieldWidth * fieldHeight

theorem field_is_100 :
    fieldCells = 100 := by
  decide

/-
The user's signed walker is (-2,+3).
On a mod-10 field, x-2 is represented as x+8 before modulo 10.
-/
def torusStep (p : Point) : Point :=
  ((p.1 + 8) % 10, (p.2 + 3) % 10)

def stepN : Nat → Point → Point
  | 0, p => p
  | Nat.succ n, p => stepN n (torusStep p)

def orbitFrom (seed : Point) : List Point :=
  (List.range 10).map (fun k => stepN k seed)

def invariantClass (p : Point) : Nat :=
  (3 * p.1 + 2 * p.2) % 10

def classSeeds : List Point :=
  [
    (0,0),  -- I = 0
    (7,0),  -- I = 1
    (4,0),  -- I = 2
    (1,0),  -- I = 3
    (8,0),  -- I = 4
    (5,0),  -- I = 5
    (2,0),  -- I = 6
    (9,0),  -- I = 7
    (6,0),  -- I = 8
    (3,0)   -- I = 9
  ]

def allOrbitCells : List Point :=
  classSeeds.flatMap orbitFrom

def fullGrid : List Point :=
  (List.range 10).flatMap
    (fun x => (List.range 10).map (fun y => (x,y)))

def classChecks : Bool :=
  ((List.range 10).zip classSeeds).all
    (fun cs =>
      (orbitFrom cs.2).all
        (fun p => invariantClass p == cs.1))

def coversGrid : Bool :=
  fullGrid.all (fun p => allOrbitCells.contains p)

theorem origin_period_10 :
    stepN 10 (0,0) = (0,0) := by
  decide

theorem origin_orbit_has_10_cells :
    (orbitFrom (0,0)).length = 10 := by
  decide

theorem origin_orbit_no_duplicates :
    (orbitFrom (0,0)).Nodup := by
  decide

theorem class_seed_order :
    classSeeds.map invariantClass = List.range 10 := by
  decide

theorem all_ten_classes_preserved :
    classChecks = true := by
  decide

theorem ten_orbits_make_100_cells :
    allOrbitCells.length = 100 := by
  decide

theorem ten_orbits_are_disjoint :
    allOrbitCells.Nodup := by
  decide

theorem ten_orbits_cover_field :
    coversGrid = true := by
  decide

/- ============================================================
   L5 — element-address span
   ============================================================ -/

structure ElementEndpoint where
  index : Nat
  token : String
deriving Repr, DecidableEq

def element1 : ElementEndpoint :=
  ⟨1, "h::{au}"⟩

def element255 : ElementEndpoint :=
  ⟨255, "u::{ag}"⟩

theorem element_span_cardinality :
    255 - 1 + 1 = 255 := by
  decide

/- ============================================================
   L6 — primitive dot and signed step carrier
   ============================================================ -/

def dotMultiplicity : Nat :=
  2 ^ 3

def signedStep : Int × Int :=
  (-2, 3)

def dotWrapper : String :=
  "|<.>|"

theorem dot_is_eightfold :
    dotMultiplicity = 8 := by
  decide

theorem signed_step_exact :
    signedStep = (-2, 3) := by
  rfl

/- ============================================================
   L7 — mirror enclosure and 8 positional carriers
   ============================================================ -/

inductive CarrierSlot where
  | aaL | bbL | ccL | ddL
  | ddR | ccR | bbR | aaR
deriving Repr, DecidableEq

def carrierSlots : List CarrierSlot :=
  [
    .aaL, .bbL, .ccL, .ddL,
    .ddR, .ccR, .bbR, .aaR
  ]

def mirrorSlot : CarrierSlot → CarrierSlot
  | .aaL => .aaR
  | .bbL => .bbR
  | .ccL => .ccR
  | .ddL => .ddR
  | .ddR => .ddL
  | .ccR => .ccL
  | .bbR => .bbL
  | .aaR => .aaL

def mirrorDepth : CarrierSlot → Nat
  | .aaL | .aaR => 0
  | .bbL | .bbR => 1
  | .ccL | .ccR => 2
  | .ddL | .ddR => 3

def centerSeam : String :=
  "--++"

def mirrorWrapper : String :=
  "|)>.<(|"

theorem eight_carrier_slots :
    carrierSlots.length = 8 := by
  decide

theorem carrier_slots_unique :
    carrierSlots.Nodup := by
  decide

theorem mirror_involutive (s : CarrierSlot) :
    mirrorSlot (mirrorSlot s) = s := by
  cases s <;> rfl

theorem mirror_preserves_depth (s : CarrierSlot) :
    mirrorDepth (mirrorSlot s) = mirrorDepth s := by
  cases s <;> rfl

/- ============================================================
   L8 — ten existing lane labels
   ============================================================ -/

inductive LaneLabel where
  | carrier (slot : CarrierSlot)
  | plank0
  | plank1
deriving Repr, DecidableEq

def laneLabels : List LaneLabel :=
  carrierSlots.map LaneLabel.carrier ++
  [.plank0, .plank1]

theorem lane_label_count :
    laneLabels.length = 10 := by
  decide

theorem lane_labels_unique :
    laneLabels.Nodup := by
  decide

/-
The geometry proves ten orbit classes.
The symbolic model supplies ten existing labels.
No sealed literal chooses one of the 10! label/class permutations.

Therefore the assignment is an explicit interface, not an invented theorem.
-/
abbrev OrbitClass := Fin 10

structure LaneBijection where
  toClass   : LaneLabel → OrbitClass
  fromClass : OrbitClass → LaneLabel
  leftInv   : ∀ label, fromClass (toClass label) = label
  rightInv  : ∀ cls, toClass (fromClass cls) = cls

/- ============================================================
   L9 — exact factorial cascade prefix
   ============================================================ -/

def tenFactorial : Nat :=
  3628800

def cascadeDivisor : Nat :=
  13 * 9 * 6 * 3 * 2 * 1 * 1

def cascadeNumerator : Nat :=
  11200

def cascadeDenominator : Nat :=
  13

/-
Exact fraction proof by cross-multiplication:

  10! / (13*9*6*3*2*1*1) = 11200/13

without truncating through Nat division.
-/
theorem factorial_prefix_exact :
    tenFactorial * cascadeDenominator =
      cascadeNumerator * cascadeDivisor := by
  decide

theorem cascade_denominator_nonzero :
    cascadeDenominator ≠ 0 := by
  decide

/- ============================================================
   L10 — /0/0 terminal STOP
   ============================================================ -/

inductive Control where
  | run
  | stop
deriving Repr, DecidableEq

def parseTerminal (s : String) : Control :=
  if s == "/0/0" then .stop else .run

theorem stop_token_halts :
    parseTerminal "/0/0" = .stop := by
  decide

/- ============================================================
   L11 — bidirectional polarity seal
   ============================================================ -/

inductive Polarity where
  | neg
  | pos
deriving Repr, DecidableEq

def bindPolarity : Polarity → Polarity
  | .neg => .pos
  | .pos => .neg

theorem forward_bind :
    bindPolarity .neg = .pos := by
  rfl

theorem reverse_bind :
    bindPolarity .pos = .neg := by
  rfl

theorem bidirectional_involution (p : Polarity) :
    bindPolarity (bindPolarity p) = p := by
  cases p <;> rfl

structure Seal where
  sealed        : Bool
  immutable     : Bool
  appendOnly    : Bool
  bidirectional : Bool
deriving Repr, DecidableEq

def finalSeal : Seal :=
  ⟨true, true, true, true⟩

theorem final_seal_closed :
    finalSeal.sealed = true ∧
    finalSeal.immutable = true ∧
    finalSeal.appendOnly = true ∧
    finalSeal.bidirectional = true := by
  decide

/- ============================================================
   Hierarchical alignment
   ============================================================ -/

inductive Layer where
  | scalarRoot
  | plankPhase
  | gradient
  | laneField
  | elementSpan
  | walker
  | dotCarrier
  | mirrorIndex
  | orbitDecomposition
  | factorialCascade
  | terminalStop
  | bidirectionalSeal
deriving Repr, DecidableEq

def hierarchy : List Layer :=
  [
    .scalarRoot,
    .plankPhase,
    .gradient,
    .laneField,
    .elementSpan,
    .walker,
    .dotCarrier,
    .mirrorIndex,
    .orbitDecomposition,
    .factorialCascade,
    .terminalStop,
    .bidirectionalSeal
  ]

theorem hierarchy_has_12_layers :
    hierarchy.length = 12 := by
  decide

theorem hierarchy_starts_at_scalar :
    hierarchy.head? = some .scalarRoot := by
  rfl

theorem hierarchy_ends_at_seal :
    hierarchy.reverse.head? = some .bidirectionalSeal := by
  decide

/- ============================================================
   Final sealed core theorem
   ============================================================ -/

theorem sealed_core :
    fieldCells = 100 ∧
    dotMultiplicity = 8 ∧
    carrierSlots.length = 8 ∧
    laneLabels.length = 10 ∧
    allOrbitCells.length = 100 ∧
    allOrbitCells.Nodup ∧
    coversGrid = true ∧
    parseTerminal "/0/0" = .stop ∧
    bindPolarity .neg = .pos ∧
    bindPolarity .pos = .neg ∧
    finalSeal.sealed = true ∧
    finalSeal.immutable = true ∧
    finalSeal.appendOnly = true ∧
    finalSeal.bidirectional = true := by
  decide

end OaSIs.V178

```

---
## 16. Local compile

Your local Lean setup can run the extracted `.lean` file directly:

```powershell
cd "$HOME\Downloads"
lean .\OaSIs_Hierarchical_Seal_v178.lean
```

Expected successful behavior is **no Lean errors**.

Because no Lean binary exists in the runtime that generated this document, this revision should be treated as:

```text
SOURCE ASSEMBLED
STRUCTURE AUDITED
LEAN COMPILE: NOT EXECUTED HERE
```

until it is run through your local Lean 4.33.1 toolchain.

---

## 17. Seal statement

```text
OaSIs Hierarchical Seal v178

root:
  0.s0.0

field:
  10 x 10

walker:
  (-2,+3)

dot:
  2^3 carrier

mirror:
  aa bb cc dd --++ dd cc bb aa

orbits:
  10 x 10 = 100

cascade:
  11200/13

terminal:
  /0/0 = STOP

polarity:
  - <-> +

status:
  SEALED
  IMMUTABLE
  APPEND-ONLY
```
