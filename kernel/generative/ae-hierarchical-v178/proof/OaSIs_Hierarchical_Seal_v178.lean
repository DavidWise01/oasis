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
