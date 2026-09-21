/-!
OaSIs / TheGame Runtime 06
Append-only correction: the shared center is a constant function, so no session
can supply or move a different center value.
-/

namespace Oasis.TheGame.Runtime06

abbrev RailSlot := Fin 26
abbrev BoardState := Fin 53

def pinnedCenter : BoardState := 52
def forwardStep : Nat := 2
def checkpointWidth : Nat := 4
def quorumRequired : Nat := 3

def advance (slot : RailSlot) : RailSlot :=
  ⟨Nat.min 25 (slot.val + forwardStep), Nat.min_le_left _ _⟩

def checkpointPasses (yesVotes : Nat) : Bool :=
  decide (quorumRequired ≤ yesVotes ∧ yesVotes ≤ checkpointWidth)

structure Session where
  a : RailSlot
  b : RailSlot
  deriving Repr, DecidableEq

def initial : Session := { a := 0, b := 0 }

def center (_ : Session) : BoardState := pinnedCenter
def stepA (s : Session) : Session := { s with a := advance s.a }
def stepB (s : Session) : Session := { s with b := advance s.b }

theorem center_is_pinned (s : Session) : center s = pinnedCenter := rfl
theorem initial_has_53_state_space : pinnedCenter.val + 1 = 53 := by decide
theorem advance_is_plus_two_from_zero : (advance 0).val = 2 := by decide
theorem quorum_three_of_four : checkpointPasses 3 = true := by decide
theorem quorum_two_of_four_fails : checkpointPasses 2 = false := by decide
theorem center_stays_pinned_after_steps :
    center (stepB (stepA initial)) = pinnedCenter := rfl

def runtime06Check : Bool :=
  (pinnedCenter.val + 1 == 53) &&
  ((advance 0).val == 2) &&
  checkpointPasses 3 &&
  !(checkpointPasses 2) &&
  ((center (stepB (stepA initial))).val == pinnedCenter.val)

theorem runtime06_verified : runtime06Check = true := by decide

end Oasis.TheGame.Runtime06
