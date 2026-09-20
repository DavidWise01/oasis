import Std

/-
Oasis.Duality.LightDark.00
===========================

Append-only clarification of the OaSIs root duality:

  LIGHT | DARK

Shadow is not a third primitive pole. It remains an exception/multiplicity
result in the existing Duality.Exception engine.

NEW MODULE: not in confirmed 0e ledger until user compilation.
-/

namespace Oasis.Duality.LightDark00

inductive Pole where
  | light
  | dark
  deriving DecidableEq, BEq, Repr

def flip : Pole → Pole
  | .light => .dark
  | .dark => .light

theorem flip_twice (p : Pole) :
    flip (flip p) = p := by
  cases p <;> rfl

def poleCount : Nat := 2

inductive ShadowRole where
  | exceptionMultiplicity
  deriving DecidableEq, BEq, Repr

structure DualityContract where
  lightPresent : Bool
  darkPresent : Bool
  moralRanking : Bool
  shadowIsThirdPole : Bool
  kanaWitnessRequired : Bool
  deriving DecidableEq, Repr

def contract : DualityContract :=
  {
    lightPresent := true
    darkPresent := true
    moralRanking := false
    shadowIsThirdPole := false
    kanaWitnessRequired := true
  }

def contractPass (c : DualityContract) : Bool :=
  c.lightPresent &&
  c.darkPresent &&
  (!c.moralRanking) &&
  (!c.shadowIsThirdPole) &&
  c.kanaWitnessRequired

theorem exactly_two_poles :
    poleCount = 2 := by
  rfl

theorem shadow_is_not_third_pole :
    contract.shadowIsThirdPole = false := by
  rfl

theorem no_default_moral_ranking :
    contract.moralRanking = false := by
  rfl

theorem duality_contract_passes :
    contractPass contract = true := by
  decide

def dualityCheck : Bool :=
  (poleCount == 2) &&
  (!contract.moralRanking) &&
  (!contract.shadowIsThirdPole) &&
  contract.kanaWitnessRequired &&
  contractPass contract

theorem duality_check_passes :
    dualityCheck = true := by
  decide

end Oasis.Duality.LightDark00
