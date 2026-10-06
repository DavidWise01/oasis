import Std

/-!
Oasis.ESpectrum.PlankBubbleCycle.01
===================================

Append-only successor to Oasis.ESpectrum.VectorVoxelVogel.00.Frozen.

Aligned symbolic model:

  FULL SPECTRUM
    -E+

  PRIM packet
    -E -E +E +E +P +P

  FORCE decoration
    weak / medium / strong applied to every signed E/P token

  NEST
    x16 tape-measure/fractal expansion

  SPINE
    three E substrates share one pinned zero-spine

  PLANK BUBBLE
    t = -1 -> 0 -> +1
    g = 1 throughout the local cycle
    x propagation grows occupancy to 999/1000
    t = +1 is local closure
    closure yields a mitotic pair for the next generation

This is a symbolic/computational formalization of the user's model,
not a claim about established cosmology or particle physics.
-/

namespace Oasis.ESpectrum.PlankBubble

inductive Sign where
  | minus
  | plus
  deriving DecidableEq, BEq, Repr

inductive Kind where
  | E
  | P
  deriving DecidableEq, BEq, Repr

structure SignedToken where
  sign : Sign
  kind : Kind
  deriving DecidableEq, BEq, Repr

def prim : List SignedToken :=
  [
    { sign := .minus, kind := .E },
    { sign := .minus, kind := .E },
    { sign := .plus,  kind := .E },
    { sign := .plus,  kind := .E },
    { sign := .plus,  kind := .P },
    { sign := .plus,  kind := .P }
  ]

inductive Force where
  | weak
  | medium
  | strong
  deriving DecidableEq, BEq, Repr

def forces : List Force := [.weak, .medium, .strong]

structure DecoratedToken where
  token : SignedToken
  force : Force
  deriving DecidableEq, BEq, Repr

def decorate (xs : List SignedToken) : List DecoratedToken :=
  xs.flatMap (fun tok => forces.map (fun f => { token := tok, force := f }))

def nestFactor : Nat := 16

/-- Three E-substrate lanes sharing one pinned spine. -/
def substrateCount : Nat := 3
def pinnedSpine : Int := 0

/-- Structural leaf count when each substrate carries the full decorated prim. -/
def leavesPerSubstrate : Nat := prim.length * forces.length * nestFactor
def leavesOnSpine : Nat := substrateCount * leavesPerSubstrate

inductive TimeState where
  | pre      -- t = -1
  | zero     -- t = 0
  | closed   -- t = +1
  deriving DecidableEq, BEq, Repr

def timeValue : TimeState → Int
  | .pre => -1
  | .zero => 0
  | .closed => 1

/-- Exact occupancy as numerator / 1000. -/
structure Occupancy where
  milli : Nat
  bound : milli ≤ 1000
  deriving Repr

def occ0 : Occupancy := ⟨0, by decide⟩
def occQuarter : Occupancy := ⟨250, by decide⟩
def occHalf : Occupancy := ⟨500, by decide⟩
def occThreeQuarter : Occupancy := ⟨750, by decide⟩
def occThreshold : Occupancy := ⟨999, by decide⟩

structure Bubble where
  generation : Nat
  t : TimeState
  gravity : Nat
  occupancy : Occupancy
  deriving Repr

def enter (generation : Nat := 0) : Bubble :=
  {
    generation := generation
    t := .pre
    gravity := 1
    occupancy := occ0
  }

def pinZero (b : Bubble) : Bubble :=
  { b with t := .zero }

/-- x-linear propagation updates occupancy while preserving g = 1. -/
def propagate (b : Bubble) (o : Occupancy) : Bubble :=
  { b with occupancy := o }

/-- Local closure at t=+1. -/
def close (b : Bubble) : Bubble :=
  { b with t := .closed }

/-- Mitotic replication creates two next-generation pre-state plank bubbles. -/
def mitosis (b : Bubble) : Bubble × Bubble :=
  (enter (b.generation + 1), enter (b.generation + 1))

def oneCycle : Bubble × (Bubble × Bubble) :=
  let b0 := enter 0
  let b1 := pinZero b0
  let b2 := propagate b1 occQuarter
  let b3 := propagate b2 occHalf
  let b4 := propagate b3 occThreeQuarter
  let b5 := propagate b4 occThreshold
  let bc := close b5
  (bc, mitosis bc)

def frozen : Bool := true
def appendOnly : Bool := true

theorem prim_is_six :
    prim.length = 6 := by
  decide

theorem force_stack_is_three :
    forces.length = 3 := by
  decide

theorem decorated_prim_is_eighteen :
    (decorate prim).length = 18 := by
  decide

theorem leaves_per_substrate_is_288 :
    leavesPerSubstrate = 288 := by
  decide

theorem three_substrate_spine_is_864 :
    leavesOnSpine = 864 := by
  decide

theorem gravity_is_one_at_entry :
    (enter 0).gravity = 1 := by
  rfl

theorem gravity_is_preserved_by_pin (b : Bubble) :
    (pinZero b).gravity = b.gravity := by
  rfl

theorem gravity_is_preserved_by_propagation (b : Bubble) (o : Occupancy) :
    (propagate b o).gravity = b.gravity := by
  rfl

theorem gravity_is_preserved_by_close (b : Bubble) :
    (close b).gravity = b.gravity := by
  rfl

theorem ternary_time_shell :
    timeValue .pre = -1 ∧ timeValue .zero = 0 ∧ timeValue .closed = 1 := by
  decide

theorem threshold_is_999_per_1000 :
    occThreshold.milli = 999 := by
  rfl

theorem one_cycle_closes_at_t_one :
    timeValue oneCycle.1.t = 1 := by
  rfl

theorem one_cycle_closes_at_threshold :
    oneCycle.1.occupancy.milli = 999 := by
  rfl

theorem one_cycle_keeps_gravity_one :
    oneCycle.1.gravity = 1 := by
  rfl

theorem mitosis_doubles :
    let daughters := oneCycle.2
    daughters.1.generation = 1 ∧
    daughters.2.generation = 1 := by
  decide

theorem daughters_restart_prestate :
    let daughters := oneCycle.2
    timeValue daughters.1.t = -1 ∧
    timeValue daughters.2.t = -1 ∧
    daughters.1.gravity = 1 ∧
    daughters.2.gravity = 1 := by
  decide

/-- Pure structural count after one mitotic split: two copies of the 864-leaf spine. -/
def leavesAfterMitosis : Nat := 2 * leavesOnSpine

theorem leaves_after_mitosis_is_1728 :
    leavesAfterMitosis = 1728 := by
  decide

def alignedCheck : Bool :=
  (prim.length == 6) &&
  (forces.length == 3) &&
  (decorate prim).length == 18 &&
  (nestFactor == 16) &&
  (substrateCount == 3) &&
  (pinnedSpine == 0) &&
  (leavesPerSubstrate == 288) &&
  (leavesOnSpine == 864) &&
  (oneCycle.1.gravity == 1) &&
  (oneCycle.1.occupancy.milli == 999) &&
  (timeValue oneCycle.1.t == 1) &&
  frozen &&
  appendOnly

theorem aligned_check_passes :
    alignedCheck = true := by
  decide

end Oasis.ESpectrum.PlankBubble
