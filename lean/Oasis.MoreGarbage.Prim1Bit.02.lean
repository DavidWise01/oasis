import Std

/-
Oasis.MoreGarbage.Prim1Bit.02
===============================

One-bit moji recursion correction.

The descent is not merely 8 / 3 / 2 / 1.
It is the interleaved walk:

  [ 8, [t5], 3, [t2], 1, [t1], 0, [t0 + n] ]

At the zero level:

  n = y = 1
    -> restart recursion at that same level
    -> direction = forward first

  n = 0
    -> zero resolves as either ? or found
    -> stop recursing

The recursive anchor remains:

  0.[O].0

Primitive signature remains:

  [1, 1, 2, 4] . n . n^2

The tick labels t5/t2/t1/t0 are symbolic labels here, not arithmetic.

Fresh descendant. Do not label 0e until user compiles it clean locally.
-/

namespace Oasis.MoreGarbage.Prim1Bit02

/-! ## Primitive signature -/

def primShape : List Nat := [1, 1, 2, 4]

def linearCost (n : Nat) : Nat := n

def recursiveCost (n : Nat) : Nat := n ^ 2

def primSignature (n : Nat) : List Nat × Nat × Nat :=
  (primShape, linearCost n, recursiveCost n)

theorem prim_shape_exact :
    primShape = [1, 1, 2, 4] := by
  rfl

theorem prim_shape_sum :
    primShape.sum = 8 := by
  decide

theorem signature_exact (n : Nat) :
    primSignature n = ([1, 1, 2, 4], n, n ^ 2) := by
  rfl

/-! ## Exact interleaved descent -/

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

def descent : List WalkNode :=
  [ .level8
  , .tick5
  , .level3
  , .tick2
  , .level1
  , .tick1
  , .level0
  , .tick0PlusN
  ]

theorem descent_exact :
    descent =
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

theorem descent_has_eight_nodes :
    descent.length = 8 := by
  decide

theorem descent_starts_at_eight :
    descent.head? = some .level8 := by
  decide

theorem descent_reaches_zero_before_t0_plus_n :
    descent.drop 6 = [.level0, .tick0PlusN] := by
  decide

/-! ## Bounded recursion anchor -/

def recurseAnchor : String := "0.[O].0"

theorem anchor_exact :
    recurseAnchor = "0.[O].0" := by
  rfl

/-! ## Zero-level resolution -/

inductive ZeroOutcome where
  | unknown
  | found
  deriving Repr, DecidableEq

inductive Direction where
  | forwardFirst
  deriving Repr, DecidableEq

structure Restart where
  level : Nat
  direction : Direction
  anchor : String
  deriving Repr, DecidableEq

inductive ZeroDecision where
  | stopUnknown
  | stopFound
  | restart (r : Restart)
  deriving Repr, DecidableEq

/-
nIsYOne = true encodes the supplied condition:

  n = y = 1

When true, recursion restarts at level 0 and goes forward first.
When false, level 0 is terminal: ? or found.
-/
def atZero (nIsYOne : Bool) (zero : ZeroOutcome) : ZeroDecision :=
  if nIsYOne then
    .restart
      { level := 0
        direction := .forwardFirst
        anchor := recurseAnchor }
  else
    match zero with
    | .unknown => .stopUnknown
    | .found => .stopFound

theorem n_y_one_restarts_forward_from_zero_unknown :
    atZero true .unknown =
      .restart
        { level := 0
          direction := .forwardFirst
          anchor := recurseAnchor } := by
  rfl

theorem n_y_one_restarts_forward_from_zero_found :
    atZero true .found =
      .restart
        { level := 0
          direction := .forwardFirst
          anchor := recurseAnchor } := by
  rfl

theorem zero_unknown_stops_recursing :
    atZero false .unknown = .stopUnknown := by
  rfl

theorem zero_found_stops_recursing :
    atZero false .found = .stopFound := by
  rfl

/-! ## Stop means stop: no descent below zero -/

def recursesAgain : ZeroDecision → Bool
  | .restart _ => true
  | .stopUnknown => false
  | .stopFound => false

theorem question_mark_does_not_recurse :
    recursesAgain (atZero false .unknown) = false := by
  rfl

theorem found_does_not_recurse :
    recursesAgain (atZero false .found) = false := by
  rfl

theorem n_y_one_does_recurse :
    recursesAgain (atZero true .unknown) = true := by
  rfl

/-! ## Cohesion seed retained from prior correction -/

def cohesionSeed : String := "1.1"

def cohesionContext : String := "1.1 of a nibble"

theorem cohesion_seed_literal :
    cohesionSeed = "1.1" := by
  rfl

theorem cohesion_context_literal :
    cohesionContext = "1.1 of a nibble" := by
  rfl

/-! ## Canonical v02 contract -/

theorem corrected_one_bit_contract :
    primShape = [1, 1, 2, 4] ∧
    descent =
      [ .level8
      , .tick5
      , .level3
      , .tick2
      , .level1
      , .tick1
      , .level0
      , .tick0PlusN
      ] ∧
    recurseAnchor = "0.[O].0" ∧
    atZero false .unknown = .stopUnknown ∧
    atZero false .found = .stopFound ∧
    atZero true .unknown =
      .restart
        { level := 0
          direction := .forwardFirst
          anchor := recurseAnchor } := by
  decide

end Oasis.MoreGarbage.Prim1Bit02
