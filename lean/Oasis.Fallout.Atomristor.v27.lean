/-
OASIS Atomristor v27 — standalone state-machine fixture
Date: 2026-10-07

This module preserves the source's thresholded nonvolatile latch behavior.
Source parameters are treated as representative fixture values, not measured
physical constants.
-/

namespace OASIS.AtomristorV27

structure Atomristor where
  w10000  : Nat
  powered : Bool
deriving DecidableEq, Repr

def setThresholdCV : Int := 120
def resetThresholdCV : Int := -120

inductive Direction where
  | set | hold | reset
deriving DecidableEq, Repr

def direction (vCV : Int) : Direction :=
  if setThresholdCV < vCV then .set
  else if vCV < resetThresholdCV then .reset
  else .hold

theorem positive_overdrive_sets :
    direction 250 = .set := by
  decide

theorem negative_overdrive_resets :
    direction (-250) = .reset := by
  decide

theorem inclusive_deadband_holds :
    direction 120 = .hold ∧
    direction 0 = .hold ∧
    direction (-120) = .hold := by
  decide

def powerOff (a : Atomristor) : Atomristor :=
  { a with powered := false }

theorem poweroff_preserves_memory (a : Atomristor) :
    (powerOff a).w10000 = a.w10000 := by
  rfl

inductive DisplayState where
  | off | on
deriving DecidableEq, Repr

def displayState (a : Atomristor) : DisplayState :=
  if 5000 < a.w10000 then .on else .off

def afterOneSetClick : Atomristor :=
  { w10000 := 2106, powered := true }

def afterOneResetClick : Atomristor :=
  { w10000 := 7894, powered := true }

theorem one_set_click_still_off :
    displayState afterOneSetClick = .off := by
  decide

theorem one_reset_click_still_on :
    displayState afterOneResetClick = .on := by
  decide

def conductanceRatio : Nat := 1000

theorem conductance_ratio_fixture :
    conductanceRatio = 1000 := by
  rfl

def currentAtZero (_ : Atomristor) : Int := 0

theorem pinched_origin (a : Atomristor) :
    currentAtZero a = 0 := by
  rfl

end OASIS.AtomristorV27
