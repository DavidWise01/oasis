import Std

/-!
Oasis.TheGame.StateSpace.01.Frozen
===================================
Frozen one-board state space for TheGame.

Per player rail:
  A-Y letters  = 25 positions
  []0 carrier  = 1 retained position
  rail total   = 26 positions

Board:
  two rails    = 52 active positions
  pinned center = 1 shared position
  full mantissa = 53 positions

This is an append-only descendant of O^1.
-/

namespace Oasis.TheGame.StateSpace

def lettersPerRail : Nat := 25
def retainedCarrierPerRail : Nat := 1
def positionsPerRail : Nat := lettersPerRail + retainedCarrierPerRail

def playerCount : Nat := 2
def activePositions : Nat := playerCount * positionsPerRail
def sharedPinnedCenter : Nat := 1
def fullBoardPositions : Nat := activePositions + sharedPinnedCenter

/-- The one complete TheGame board: 53 addressable positions. -/
abbrev TheGameState := Fin 53

/-- Shared gyro / pinned-center address after both 26-position rails. -/
def pinnedCenter : TheGameState :=
  ⟨52, by decide⟩

def frozen : Bool := true
def appendOnly : Bool := true

theorem rail_has_twenty_six_positions :
    positionsPerRail = 26 := by
  decide

theorem two_rails_have_fifty_two_positions :
    activePositions = 52 := by
  decide

theorem board_mantissa_is_fifty_three :
    fullBoardPositions = 53 := by
  decide

theorem pinned_center_is_last_board_position :
    pinnedCenter.val = 52 := by
  rfl

/-- Executable closure test for the frozen TheGame state space. -/
def theGameCheck : Bool :=
  (lettersPerRail == 25) &&
  (retainedCarrierPerRail == 1) &&
  (positionsPerRail == 26) &&
  (playerCount == 2) &&
  (activePositions == 52) &&
  (sharedPinnedCenter == 1) &&
  (fullBoardPositions == 53) &&
  (pinnedCenter.val == 52) &&
  frozen &&
  appendOnly

theorem the_game_check_passes :
    theGameCheck = true := by
  decide

end Oasis.TheGame.StateSpace
