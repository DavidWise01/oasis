import Std

/-
Oasis.MoreGarbage.Prim1Bit.01
===============================

Correction to Prim1Bit.00:

The delete/mojibake search does NOT run as a forward 1..8 tick schedule.

At one-bit scope, once a moji is found, the search runs in reverse order:

  8 / 3 / 2 / 1

and recurses through the bounded anchor:

  0.[O].0

until the search resolves to Y/N:
  Y = repair
  N = no repair

Cohesion may still be established from the literal seed:

  1.1 of a nibble

independently of whether the repair verdict is Y or N.
This does NOT say the original primitive was recovered after N; it says
the surviving state can still cohere from the supplied 1.1 seed.

"1.1" is preserved symbolically and is not numerically reinterpreted.

Primitive signature remains:

  [1, 1, 2, 4] . n . n^2

Fresh descendant. Do not label 0e until user compiles it clean locally.
-/

namespace Oasis.MoreGarbage.Prim1Bit01

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

def reverseWalk : List Nat := [8, 3, 2, 1]

theorem reverse_walk_exact :
    reverseWalk = [8, 3, 2, 1] := by
  rfl

theorem reverse_walk_has_four_stages :
    reverseWalk.length = 4 := by
  decide

theorem reverse_walk_starts_at_eight :
    reverseWalk.head? = some 8 := by
  decide

theorem reverse_walk_ends_at_one :
    reverseWalk.reverse.head? = some 1 := by
  decide

def oldForwardWalk : List Nat := [1, 2, 3, 4, 5, 6, 7, 8]

theorem reverse_walk_is_not_old_forward_walk :
    reverseWalk ≠ oldForwardWalk := by
  decide

def recurseAnchor : String := "0.[O].0"

structure Frame where
  anchor : String
  stage : Nat
  deriving Repr, DecidableEq

def frames : List Frame :=
  reverseWalk.map fun stage =>
    { anchor := recurseAnchor, stage := stage }

def allFramesAnchored : Bool :=
  frames.all fun frame => frame.anchor == recurseAnchor

theorem recursion_stays_at_zero_O_zero :
    allFramesAnchored = true := by
  decide

inductive PrimitiveRead where
  | aligned
  | moji
  deriving Repr, DecidableEq

inductive Action where
  | move
  | recurse
  deriving Repr, DecidableEq

def dispatch : PrimitiveRead → Action
  | .aligned => .move
  | .moji => .recurse

theorem aligned_moves :
    dispatch .aligned = .move := by
  rfl

theorem moji_recurses :
    dispatch .moji = .recurse := by
  rfl

inductive Probe where
  | unresolved
  | yes
  | no
  deriving Repr, DecidableEq

inductive Verdict where
  | yesRepair
  | noRepair
  deriving Repr, DecidableEq

structure Resolution where
  anchor : String
  verdict : Verdict
  deriving Repr, DecidableEq

def recurse
    (probe : Nat → Probe)
    (anchor : String)
    : List Nat → Resolution
  | [] =>
      { anchor := anchor, verdict := .noRepair }
  | stage :: rest =>
      match probe stage with
      | .yes =>
          { anchor := anchor, verdict := .yesRepair }
      | .no =>
          { anchor := anchor, verdict := .noRepair }
      | .unresolved =>
          recurse probe anchor rest

def resolveMoji (probe : Nat → Probe) : Resolution :=
  recurse probe recurseAnchor reverseWalk

def yesAtOne : Nat → Probe
  | 8 => .unresolved
  | 3 => .unresolved
  | 2 => .unresolved
  | 1 => .yes
  | _ => .no

def noAtOne : Nat → Probe
  | 8 => .unresolved
  | 3 => .unresolved
  | 2 => .unresolved
  | 1 => .no
  | _ => .no

def yesAtThree : Nat → Probe
  | 8 => .unresolved
  | 3 => .yes
  | _ => .no

theorem reverse_recurses_8_3_2_1_until_yes :
    (resolveMoji yesAtOne).verdict = .yesRepair := by
  decide

theorem reverse_recurses_8_3_2_1_until_no :
    (resolveMoji noAtOne).verdict = .noRepair := by
  decide

theorem reverse_can_resolve_early_at_three :
    (resolveMoji yesAtThree).verdict = .yesRepair := by
  decide

theorem yes_resolution_preserves_anchor :
    (resolveMoji yesAtOne).anchor = recurseAnchor := by
  decide

theorem no_resolution_preserves_anchor :
    (resolveMoji noAtOne).anchor = recurseAnchor := by
  decide

def cohesionSeed : String := "1.1"

def cohesionContext : String := "1.1 of a nibble"

structure Cohesion where
  seed : String
  coherent : Bool
  deriving Repr, DecidableEq

def cohereFromOneOne (_verdict : Verdict) : Cohesion :=
  { seed := cohesionSeed, coherent := true }

theorem one_one_seed_is_literal :
    cohesionSeed = "1.1" := by
  rfl

theorem one_one_context_is_literal :
    cohesionContext = "1.1 of a nibble" := by
  rfl

theorem yes_can_cohere_from_one_one :
    (cohereFromOneOne .yesRepair).coherent = true := by
  rfl

theorem no_repair_can_still_cohere_from_one_one :
    (cohereFromOneOne .noRepair).coherent = true := by
  rfl

theorem no_repair_does_not_claim_original_recovery :
    (resolveMoji noAtOne).verdict = .noRepair := by
  decide

theorem cohesion_seed_survives_yes :
    (cohereFromOneOne .yesRepair).seed = "1.1" := by
  rfl

theorem cohesion_seed_survives_no :
    (cohereFromOneOne .noRepair).seed = "1.1" := by
  rfl

theorem corrected_one_bit_moji_contract :
    primShape = [1, 1, 2, 4] ∧
    reverseWalk = [8, 3, 2, 1] ∧
    recurseAnchor = "0.[O].0" ∧
    cohesionSeed = "1.1" ∧
    (resolveMoji yesAtOne).verdict = .yesRepair ∧
    (resolveMoji noAtOne).verdict = .noRepair ∧
    (cohereFromOneOne .yesRepair).coherent = true ∧
    (cohereFromOneOne .noRepair).coherent = true := by
  decide

end Oasis.MoreGarbage.Prim1Bit01
