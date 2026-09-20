import Std

/-
Oasis.MoreGarbage.SubAtomicPrim.04
===================================

Fresh descendant of SubAtomicPrim.03.

Scope: user's symbolic sub-atomic primitive search model.

New escape / re-entry branch:

  current universe:
    MANDEL | JULIET | || NEXT UNIVERSE

If local MANDEL cannot recover the JULIET-bound primitive, the search may:

  1. go outward to U^2
  2. attempt a drill / signed punch-through across the || universe boundary
  3. start the process in reverse from outside
  4. search inward toward JULIET / MANDEL

The user's literal drill phrase is preserved exactly:

  ax::tehter::mandel{bound{juliet + u + n} || ax||:: attempt punch through

("tehter" is preserved as supplied, not silently corrected.)

This file does not assert physical cosmology. It formalizes the symbolic
search topology only.

Fresh candidate. Do not label 0e until user compiles it clean locally.
-/

namespace Oasis.MoreGarbage.SubAtomicPrim04

/-! ## Existing local trio -/

inductive Region where
  | mandel
  | juliet
  | nextUniverse
  deriving Repr, DecidableEq

def localTopology : List Region :=
  [.mandel, .juliet, .nextUniverse]

theorem local_topology_exact :
    localTopology = [.mandel, .juliet, .nextUniverse] := by
  rfl

/-! ## Universe boundary -/

def universeBoundary : String := "||"

def outerLevel : String := "U^2"

def recursiveAnchor : String := "0.[O].0"

theorem boundary_exact :
    universeBoundary = "||" := by
  rfl

theorem outer_level_exact :
    outerLevel = "U^2" := by
  rfl

/-! ## Drill / sign literal -/

def drillLiteral : String :=
  "ax::tehter::mandel{bound{juliet + u + n} || ax||:: attempt punch through"

def drillTag : String := "ax::x::"

def drillSign : String := "drill and sign"

theorem drill_literal_preserved :
    drillLiteral =
      "ax::tehter::mandel{bound{juliet + u + n} || ax||:: attempt punch through" := by
  rfl

/-! ## Directional mode -/

inductive SearchDirection where
  | outward
  | inward
  deriving Repr, DecidableEq

inductive SearchPhase where
  | local
  | punchThrough
  | outer
  | reverseInward
  | stop
  deriving Repr, DecidableEq

structure SearchState where
  phase : SearchPhase
  direction : SearchDirection
  level : String
  signed : Bool
  deriving Repr, DecidableEq

def localState : SearchState :=
  { phase := .local
    direction := .outward
    level := "U"
    signed := false }

def punchedState : SearchState :=
  { phase := .punchThrough
    direction := .outward
    level := outerLevel
    signed := true }

def reverseInwardState : SearchState :=
  { phase := .reverseInward
    direction := .inward
    level := outerLevel
    signed := true }

theorem punch_through_is_signed :
    punchedState.signed = true := by
  rfl

theorem reverse_starts_at_u2 :
    reverseInwardState.level = "U^2" := by
  rfl

theorem reverse_goes_inward :
    reverseInwardState.direction = .inward := by
  rfl

/-! ## Binding status -/

inductive Binding where
  | bound
  | unresolved
  | goneForever
  deriving Repr, DecidableEq

inductive LocalResult where
  | recovered
  | escape
  deriving Repr, DecidableEq

def decideLocal : Binding → LocalResult
  | .bound => .recovered
  | .unresolved => .escape
  | .goneForever => .escape

theorem bound_stays_local :
    decideLocal .bound = .recovered := by
  rfl

theorem unresolved_may_escape :
    decideLocal .unresolved = .escape := by
  rfl

theorem gone_local_may_still_trigger_outer_search :
    decideLocal .goneForever = .escape := by
  rfl

/-! ## Escape then reverse inward -/

def escapePath : List SearchPhase :=
  [ .local
  , .punchThrough
  , .outer
  , .reverseInward
  ]

theorem escape_path_exact :
    escapePath =
      [ .local
      , .punchThrough
      , .outer
      , .reverseInward
      ] := by
  rfl

theorem escape_path_ends_reverse_inward :
    escapePath.reverse.head? = some .reverseInward := by
  decide

/-! ## Mandel / Juliet search relation retained -/

def mantissa : Nat := 360

def directions : Nat := 6

def startStop : Nat := 2

def mandelEnvelope : Nat :=
  mantissa * directions + startStop

theorem mandel_envelope_is_2162 :
    mandelEnvelope = 2162 := by
  decide

def julietBoundary : String := "a|?"

theorem juliet_boundary_exact :
    julietBoundary = "a|?" := by
  rfl

/-! ## Outer search is independent of current M/J bounds -/

/-
"unbounded from both m/j" is represented structurally:
the outer search state carries no local Mandel/Juliet bound value.
It only carries U^2, direction, phase, and signed drill state.
-/
structure OuterSearch where
  level : String
  direction : SearchDirection
  signed : Bool
  deriving Repr, DecidableEq

def outerSearch : OuterSearch :=
  { level := outerLevel
    direction := .inward
    signed := true }

theorem outer_search_has_no_local_bound_field :
    outerSearch =
      { level := "U^2"
        direction := .inward
        signed := true } := by
  rfl

/-! ## Canonical v04 contract -/

theorem sub_atomic_escape_reverse_contract :
    localTopology = [.mandel, .juliet, .nextUniverse] ∧
    universeBoundary = "||" ∧
    outerLevel = "U^2" ∧
    drillTag = "ax::x::" ∧
    drillLiteral =
      "ax::tehter::mandel{bound{juliet + u + n} || ax||:: attempt punch through" ∧
    escapePath =
      [.local, .punchThrough, .outer, .reverseInward] ∧
    reverseInwardState.direction = .inward ∧
    reverseInwardState.level = "U^2" ∧
    mandelEnvelope = 2162 ∧
    julietBoundary = "a|?" := by
  decide

end Oasis.MoreGarbage.SubAtomicPrim04
