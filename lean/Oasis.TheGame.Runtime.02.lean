import Std

/-!
Oasis.TheGame.Runtime.02
========================
Append-only deterministic runtime contract for the frozen 53-slot board.

The board definition remains in Oasis.TheGame.StateSpace.01.Frozen.
This module adds only runtime checks:
  A +2 forward pair
  B +2 mirror pair
  2x1x2 local cell
  3/4 quorum
  pinned center excluded from movement
-/

namespace Oasis.TheGame.Runtime

def railPositions : Nat := 26
def forwardDelta : Nat := 2
def forwardPairs : Nat := 13
def playerRails : Nat := 2
def pinnedCenter : Nat := 1
def boardPositions : Nat := playerRails * railPositions + pinnedCenter

def localCellPositions : Nat := 4
def quorumRequired : Nat := 3

/-- A local checkpoint passes only at three or four positive positions. -/
def checkpointPass (votes : Nat) : Bool :=
  (votes == 3) || (votes == 4)

/-- The pin is a fixed board position, not a movable rail position. -/
def pinMoves : Bool := false

theorem forward_pairs_cover_one_rail :
    forwardDelta * forwardPairs = railPositions := by
  decide

theorem two_rails_and_pin_are_fifty_three :
    boardPositions = 53 := by
  decide

theorem local_cell_is_two_by_one_by_two :
    localCellPositions = 2 * 1 * 2 := by
  decide

theorem three_of_four_passes :
    checkpointPass 3 = true := by
  decide

theorem four_of_four_passes :
    checkpointPass 4 = true := by
  decide

theorem two_of_four_holds :
    checkpointPass 2 = false := by
  decide

theorem pin_stays_fixed :
    pinMoves = false := by
  rfl

def runtimeCheck : Bool :=
  (forwardDelta * forwardPairs == railPositions) &&
  (boardPositions == 53) &&
  (localCellPositions == 2 * 1 * 2) &&
  (quorumRequired == 3) &&
  checkpointPass 3 &&
  checkpointPass 4 &&
  (!checkpointPass 2) &&
  (!pinMoves)

theorem runtime_check_passes :
    runtimeCheck = true := by
  decide

end Oasis.TheGame.Runtime
