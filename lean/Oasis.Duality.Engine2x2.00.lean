import Std

/-
Oasis.Duality.Engine2x2.00
==========================

MOBIUS duality engine:
  2^2 = 4

Axis A:
  VESSEL | LIFE_INSTANCE

Axis B:
  LIVE_SEEK | TELL_STORE

The four cells encode the recursive story/vessel relation.

NEW MODULE: not in confirmed 0e ledger until user compilation.
-/

namespace Oasis.Duality.Engine2x2_00

inductive VesselLife where
  | vessel
  | lifeInstance
  deriving DecidableEq, BEq, Repr

inductive LiveTell where
  | liveSeek
  | tellStore
  deriving DecidableEq, BEq, Repr

structure Cell where
  a : VesselLife
  b : LiveTell
  deriving DecidableEq, BEq, Repr

def cells : List Cell :=
  [
    { a := .vessel, b := .liveSeek },
    { a := .vessel, b := .tellStore },
    { a := .lifeInstance, b := .liveSeek },
    { a := .lifeInstance, b := .tellStore }
  ]

theorem two_squared_is_four :
    2 ^ 2 = 4 := by
  decide

theorem duality_engine_has_four_cells :
    cells.length = 4 := by
  decide

def mobiusTurn : List String :=
  [
    "LOOK_FOR_VESSEL",
    "LIVE_INSTANCE",
    "TELL_STORY",
    "STORY_BECOMES_VESSEL"
  ]

theorem mobius_turn_has_four_steps :
    mobiusTurn.length = 4 := by
  decide

def dualityEngineCheck : Bool :=
  ((2 ^ 2) == 4) &&
  (cells.length == 4) &&
  (mobiusTurn.length == 4)

theorem duality_engine_check_passes :
    dualityEngineCheck = true := by
  decide

end Oasis.Duality.Engine2x2_00
