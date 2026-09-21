/-!
OaSIs / TheGame Runtime 05
Append-only companion contract for the Play Session 04 surface.
The frozen 53-state board remains the source contract.
-/

namespace Oasis.TheGame.Runtime05

abbrev RailSlot := Fin 26
abbrev BoardState := Fin 53

def pinnedCenter : BoardState := 52
def railAStart : RailSlot := 0
def railBStart : RailSlot := 0
def forwardStep : Nat := 2
def checkpointWidth : Nat := 4
def quorumRequired : Nat := 3

def advance (slot : RailSlot) : RailSlot :=
  ⟨Nat.min 25 (slot.val + forwardStep), by
    exact Nat.le_trans (Nat.min_le_left _ _) (by decide)⟩

def checkpointPasses (yesVotes : Nat) : Bool :=
  quorumRequired ≤ yesVotes && yesVotes ≤ checkpointWidth

structure Session where
  a : RailSlot
  b : RailSlot
  center : BoardState
  deriving Repr, DecidableEq

def initial : Session := { a := railAStart, b := railBStart, center := pinnedCenter }

def stepA (s : Session) : Session := { s with a := advance s.a }
def stepB (s : Session) : Session := { s with b := advance s.b }

theorem center_is_pinned (s : Session) : s.center = pinnedCenter := by
  cases s
  simp [pinnedCenter]

theorem initial_has_53_state_space : pinnedCenter.val + 1 = 53 := by decide
theorem advance_is_plus_two_from_zero : (advance 0).val = 2 := by decide
theorem quorum_three_of_four : checkpointPasses 3 = true := by decide
theorem quorum_two_of_four_fails : checkpointPasses 2 = false := by decide
theorem center_stays_pinned_after_steps :
    (stepB (stepA initial)).center = pinnedCenter := by decide

def runtime05Check : Bool :=
  (pinnedCenter.val + 1 == 53) &&
  ((advance 0).val == 2) &&
  checkpointPasses 3 &&
  !(checkpointPasses 2) &&
  ((stepB (stepA initial)).center.val == pinnedCenter.val)

theorem runtime05_verified : runtime05Check = true := by decide

end Oasis.TheGame.Runtime05
