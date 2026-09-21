import Std

/-!
Oasis.Cardinal.Hourglass.00.Frozen
===================================
Frozen cardinal-hourglass attachment.

Per hourglass:
  N :: -++-
  S :: +-+-
  W :: +-+-
  E :: +-+-
  center :: 1 x 1 x 0 x 1 x 1
  pin :: [] 0

Four identical hourglasses carry the same local cardinal contract.
This is an append-only descendant; its contents are frozen.
-/

namespace Oasis.Cardinal.Hourglass

inductive Sign where
  | minus
  | plus
  deriving DecidableEq, BEq, Repr

abbrev DirectionCode := List Sign
abbrev CenterCode := List Bool

/-- One complete cardinal hourglass, with its local pinned center. -/
structure Hourglass where
  north : DirectionCode
  south : DirectionCode
  west : DirectionCode
  east : DirectionCode
  center : CenterCode
  pinnedZero : Nat
  deriving DecidableEq, BEq, Repr

def northCode : DirectionCode :=
  [.minus, .plus, .plus, .minus]

def southCode : DirectionCode :=
  [.plus, .minus, .plus, .minus]

def westCode : DirectionCode :=
  [.plus, .minus, .plus, .minus]

def eastCode : DirectionCode :=
  [.plus, .minus, .plus, .minus]

/-- Four active supports around one pinned zero: 1 x 1 x 0 x 1 x 1. -/
def centerCode : CenterCode :=
  [true, true, false, true, true]

def centerWidth : Nat := 5
def centerSupports : Nat := 4
def pinnedCenterIndex : Nat := 2

def canonical : Hourglass :=
  {
    north := northCode
    south := southCode
    west := westCode
    east := eastCode
    center := centerCode
    pinnedZero := 0
  }

/-- The cardinal arrangement repeats once per hourglass, four times. -/
abbrev HourglassSet := Fin 4 → Hourglass
def fourHourglasses : HourglassSet :=
  fun _ => canonical

def frozen : Bool := true
def appendOnly : Bool := true

theorem north_is_minus_plus_plus_minus :
    northCode = [.minus, .plus, .plus, .minus] := by
  rfl

theorem south_is_plus_minus_plus_minus :
    southCode = [.plus, .minus, .plus, .minus] := by
  rfl

theorem west_is_plus_minus_plus_minus :
    westCode = [.plus, .minus, .plus, .minus] := by
  rfl

theorem east_is_plus_minus_plus_minus :
    eastCode = [.plus, .minus, .plus, .minus] := by
  rfl

theorem center_is_one_one_zero_one_one :
    centerCode = [true, true, false, true, true] := by
  rfl

theorem center_has_four_supports :
    centerSupports = 4 ∧ centerWidth = 5 ∧ pinnedCenterIndex = 2 := by
  decide

theorem pin_is_zero :
    canonical.pinnedZero = 0 := by
  rfl

theorem each_hourglass_is_canonical (i : Fin 4) :
    fourHourglasses i = canonical := by
  rfl

def cardinalHourglassCheck : Bool :=
  (northCode == [.minus, .plus, .plus, .minus]) &&
  (southCode == [.plus, .minus, .plus, .minus]) &&
  (westCode == [.plus, .minus, .plus, .minus]) &&
  (eastCode == [.plus, .minus, .plus, .minus]) &&
  (centerCode == [true, true, false, true, true]) &&
  (canonical.pinnedZero == 0) &&
  frozen &&
  appendOnly

theorem cardinal_hourglass_check_passes :
    cardinalHourglassCheck = true := by
  decide

end Oasis.Cardinal.Hourglass
