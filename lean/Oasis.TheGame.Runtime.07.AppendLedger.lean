/-!
OaSIs / TheGame Runtime 07
Append-only accepted-turn ledger contract.
Lifecycle: declare → local 3-of-4 witness quorum → append one immutable record.
-/

namespace Oasis.TheGame.Runtime07

inductive Side where
  | aGoodForward
  | bDevilMirror
  deriving Repr, DecidableEq

inductive Action where
  | forwardTwo
  | mirrorTwo
  | holdCheckpoint
  | witnessDivergence
  deriving Repr, DecidableEq

structure Turn where
  ordinal : Nat
  side : Side
  vessel : String
  action : Action
  witnessYes : Nat
  deriving Repr, DecidableEq

abbrev Ledger := List Turn

def quorumPasses (yesVotes : Nat) : Bool :=
  decide (3 ≤ yesVotes ∧ yesVotes ≤ 4)

def accepted (turn : Turn) : Bool := quorumPasses turn.witnessYes

def appendAccepted (ledger : Ledger) (turn : Turn) : Ledger :=
  if accepted turn then ledger ++ [turn] else ledger

def flashForward : Turn :=
  { ordinal := 1, side := .aGoodForward, vessel := "Flash",
    action := .forwardTwo, witnessYes := 3 }

def rejectedMirror : Turn :=
  { ordinal := 2, side := .bDevilMirror, vessel := "Batman",
    action := .mirrorTwo, witnessYes := 2 }

theorem three_of_four_accepts : accepted flashForward = true := by decide
theorem two_of_four_rejects : accepted rejectedMirror = false := by decide
theorem accepted_turn_appends_once :
    (appendAccepted [] flashForward).length = 1 := by decide
theorem rejected_turn_does_not_append :
    (appendAccepted [] rejectedMirror).length = 0 := by decide

def runtime07Check : Bool :=
  accepted flashForward &&
  !(accepted rejectedMirror) &&
  ((appendAccepted [] flashForward).length == 1) &&
  ((appendAccepted [] rejectedMirror).length == 0)

theorem runtime07_verified : runtime07Check = true := by decide

end Oasis.TheGame.Runtime07
