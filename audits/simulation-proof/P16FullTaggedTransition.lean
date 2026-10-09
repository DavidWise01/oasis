/-!
ROOT0 P1.6 -- source-conservative tagged spectator model.
Lean 4 proof DRAFT, NOT compiler-verified in current runner.
This formalizes only the observer/transition separation in the proposed
extension of the actual T2 occupied-to-vacant move.
-/
import Lean
namespace ROOT0P16

inductive Cell where
  | inbound | outbound | vacant | occupied
  deriving DecidableEq, Repr

structure FullState where
  slots : Fin 5 → Cell
  axes : Fin 3 → Fin 3
  witnessed : Bool

def witness (s : FullState) : FullState := { s with witnessed := true }

def moveOn (s : FullState) (source target : Fin 5) : FullState :=
  { s with slots := fun k =>
      if k = source then Cell.vacant
      else if k = target then Cell.occupied
      else s.slots k }

theorem witness_preserves_physical (s : FullState) :
    (witness s).slots = s.slots := by rfl

theorem move_preserves_axes (s : FullState) (i j : Fin 5) :
    (moveOn s i j).axes = s.axes := by rfl

theorem move_preserves_witness (s : FullState) (i j : Fin 5) :
    (moveOn s i j).witnessed = s.witnessed := by rfl

theorem untouched_slot (s : FullState) (i j k : Fin 5)
    (hi : k ≠ i) (hj : k ≠ j) :
    (moveOn s i j).slots k = s.slots k := by
  simp [moveOn, hi, hj]

theorem move_witness_commute (s : FullState) (i j : Fin 5) :
    moveOn (witness s) i j = witness (moveOn s i j) := by
  cases s
  rfl

-- NOT yet proved: tag transport at the seam, dimensional physical
-- time prediction, scheduler reversibility, actual-world simulation.
end ROOT0P16
