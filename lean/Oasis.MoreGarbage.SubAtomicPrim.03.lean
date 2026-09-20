import Std

/-
Oasis.MoreGarbage.SubAtomicPrim.03
===================================

Fresh descendant of the one-bit/moji recursion work.

Current user model:

  MANDEL = the search

  mantissa = 360
  directions = 6
    forward / backward / up / down / in / out

  directional search = 360 * 6
  plus 2 controls = start / stop

  JULIET = the boundary between "a" and "?"

The search job is:

  search as much JULIET as allowed at v - n
  to determine whether the boundary is bound to MANDEL

  bound       -> recover "a"
  not bound   -> "?" / gone forever

This is kept at the user's sub-atomic primitive scale.
No byte/string/file scaling is introduced here.

The earlier recursion ladder remains provenance:

  [ 8 , [t5] , 3 , [t2] , 1 , [t1] , 0 , [t0 + n] ]

and 0 remains the recursion floor.

Fresh candidate. Do not label 0e until user compiles it clean locally.
-/

namespace Oasis.MoreGarbage.SubAtomicPrim03

/-! ## Scale / inherited primitive signature -/

def scale : String := "sub-atomic prim"

def primShape : List Nat := [1, 1, 2, 4]

def linearCost (n : Nat) : Nat := n

def recursiveCost (n : Nat) : Nat := n ^ 2

def primSignature (n : Nat) : List Nat × Nat × Nat :=
  (primShape, linearCost n, recursiveCost n)

theorem scale_exact :
    scale = "sub-atomic prim" := by
  rfl

theorem prim_signature_exact (n : Nat) :
    primSignature n = ([1, 1, 2, 4], n, n ^ 2) := by
  rfl

/-! ## Mandel search geometry -/

inductive Direction where
  | forward
  | backward
  | up
  | down
  | inward
  | outward
  deriving Repr, DecidableEq

def directions : List Direction :=
  [ .forward
  , .backward
  , .up
  , .down
  , .inward
  , .outward
  ]

def mandelMantissa : Nat := 360

def mandelDirectionalSpace : Nat :=
  mandelMantissa * directions.length

def mandelStartStop : Nat := 2

def mandelEnvelope : Nat :=
  mandelDirectionalSpace + mandelStartStop

theorem six_directions :
    directions.length = 6 := by
  decide

theorem mandel_directional_space_is_2160 :
    mandelDirectionalSpace = 2160 := by
  decide

theorem mandel_start_stop_is_two :
    mandelStartStop = 2 := by
  rfl

theorem mandel_envelope_is_2162 :
    mandelEnvelope = 2162 := by
  decide

/-! ## Juliet: boundary of a and ? -/

structure Juliet where
  index : Nat
  left : String
  right : String
  boundToMandel : Bool
  deriving Repr, DecidableEq

def julietAt (bound : Nat → Bool) (index : Nat) : Juliet :=
  { index := index
    left := "a"
    right := "?"
    boundToMandel := bound index }

theorem juliet_left_is_a (bound : Nat → Bool) (i : Nat) :
    (julietAt bound i).left = "a" := by
  rfl

theorem juliet_right_is_question (bound : Nat → Bool) (i : Nat) :
    (julietAt bound i).right = "?" := by
  rfl

/-! ## v - n search budget -/

def julietBudget (v n : Nat) : Nat :=
  v - n

theorem juliet_budget_is_v_minus_n (v n : Nat) :
    julietBudget v n = v - n := by
  rfl

/-! ## Search as much Juliet as v - n permits -/

inductive SearchResult where
  | bound (index : Nat)
  | goneForever
  deriving Repr, DecidableEq

def searchJuliet
    (bound : Nat → Bool)
    : Nat → Nat → SearchResult
  | 0, _ =>
      .goneForever
  | fuel + 1, index =>
      if bound index then
        .bound index
      else
        searchJuliet bound fuel (index + 1)

def mandelSearch
    (bound : Nat → Bool)
    (v n : Nat)
    : SearchResult :=
  searchJuliet bound (julietBudget v n) 0

def renderBoundary : SearchResult → String
  | .bound _ => "a"
  | .goneForever => "?"

theorem gone_forever_renders_question :
    renderBoundary .goneForever = "?" := by
  rfl

theorem bound_renders_a (i : Nat) :
    renderBoundary (.bound i) = "a" := by
  rfl

/-! ## Deterministic witnesses -/

def boundAt3 : Nat → Bool
  | 3 => true
  | _ => false

def neverBound : Nat → Bool :=
  fun _ => false

def boundAt0 : Nat → Bool
  | 0 => true
  | _ => false

theorem finds_bound_juliet_inside_budget :
    mandelSearch boundAt3 4 0 = .bound 3 := by
  decide

theorem exhausted_juliet_is_gone_forever :
    mandelSearch neverBound 4 0 = .goneForever := by
  decide

theorem first_juliet_can_bind_immediately :
    mandelSearch boundAt0 1 0 = .bound 0 := by
  decide

theorem zero_budget_stops_with_question :
    renderBoundary (mandelSearch neverBound 0 0) = "?" := by
  decide

/-! ## Earlier recursion floor retained literally -/

inductive WalkNode where
  | level8
  | tick5
  | level3
  | tick2
  | level1
  | tick1
  | level0
  | tick0PlusN
  deriving Repr, DecidableEq

def inheritedLadder : List WalkNode :=
  [ .level8
  , .tick5
  , .level3
  , .tick2
  , .level1
  , .tick1
  , .level0
  , .tick0PlusN
  ]

def recurseAnchor : String := "0.[O].0"

theorem inherited_ladder_exact :
    inheritedLadder =
      [ .level8
      , .tick5
      , .level3
      , .tick2
      , .level1
      , .tick1
      , .level0
      , .tick0PlusN
      ] := by
  rfl

theorem recursion_floor_remains_zero :
    inheritedLadder.drop 6 = [.level0, .tick0PlusN] := by
  decide

theorem anchor_remains_zero_O_zero :
    recurseAnchor = "0.[O].0" := by
  rfl

/-! ## Canonical sub-atomic contract -/

theorem sub_atomic_mandel_juliet_contract :
    scale = "sub-atomic prim" ∧
    mandelMantissa = 360 ∧
    directions.length = 6 ∧
    mandelDirectionalSpace = 2160 ∧
    mandelStartStop = 2 ∧
    mandelEnvelope = 2162 ∧
    (julietAt neverBound 0).left = "a" ∧
    (julietAt neverBound 0).right = "?" ∧
    mandelSearch boundAt3 4 0 = .bound 3 ∧
    mandelSearch neverBound 4 0 = .goneForever := by
  decide

end Oasis.MoreGarbage.SubAtomicPrim03
