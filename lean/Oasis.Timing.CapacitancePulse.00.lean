import Std

/-
Oasis.Timing.CapacitancePulse.00
================================

Append-only pulse grammar descendant of Timing.BodyCohesion.00.

User-defined semantic patterns:
  root  : 3 x 3^3 with 10^-10 timing label
  heart : 4 x 1 x 4^4 x 4 ; [00 55 00] repeat ; width 6
  lungs : 2 x 1 x 2^2 x 2 ; [55 00] repeat ; width 4
  body  : 4 x 1 x 4^4 x 4 ; ..||..|||| ; :::: x ::::
  head  : 3 x 1 x 3^3 x 3 ; [77 55 00 00 55 77 00]

Body/capacitance terminology is symbolic systems language, not physiology.

NEW MODULE: do not add to the confirmed 0e ledger until user compilation.
-/

namespace Oasis.Timing.CapacitancePulse00

def symbolicOnly : Bool := true
def timebaseLabel : String := "0.0000000001"
def timebaseScientific : String := "10^-10"
def pulseWindowLabel : String := "1/3 x 3"
def dischargeShape : String := "triangulated"

def capRoot : Nat := 3 * (3 ^ 3)

def heartAmplitude : Nat := 4 * 1 * (4 ^ 4) * 4
def lungAmplitude : Nat := 2 * 1 * (2 ^ 2) * 2
def headAmplitude : Nat := 3 * 1 * (3 ^ 3) * 3

def heartPattern : List String := ["00", "55", "00"]
def lungPattern : List String := ["55", "00"]
def headPattern : List String := ["77", "55", "00", "00", "55", "77", "00"]

def bodyCarrier : String := "..||..||||"
def nobleGate : String := ":::: x ::::"

def tokenWidth : Nat := 2
def heartWidth : Nat := heartPattern.length * tokenWidth
def lungWidth : Nat := lungPattern.length * tokenWidth
def headWidthDerived : Nat := headPattern.length * tokenWidth

inductive PulsePhase where
  | charge
  | transition
  | discharge
  | witnessReset
  deriving DecidableEq, BEq, Repr

def commonPrimitive : List PulsePhase :=
  [.charge, .transition, .discharge, .witnessReset]

structure PulseContract where
  patternIdentity : Bool
  orderingPreserved : Bool
  provenancePreserved : Bool
  resetWitnessed : Bool
  kanaWitnessRequired : Bool
  deriving DecidableEq, Repr

def contract : PulseContract :=
  {
    patternIdentity := true
    orderingPreserved := true
    provenancePreserved := true
    resetWitnessed := true
    kanaWitnessRequired := true
  }

def contractPass (c : PulseContract) : Bool :=
  c.patternIdentity &&
  c.orderingPreserved &&
  c.provenancePreserved &&
  c.resetWitnessed &&
  c.kanaWitnessRequired

theorem cap_root_is_81 :
    capRoot = 81 := by
  decide

theorem heart_amplitude_is_4096 :
    heartAmplitude = 4096 := by
  decide

theorem lung_amplitude_is_16 :
    lungAmplitude = 16 := by
  decide

theorem head_amplitude_is_243 :
    headAmplitude = 243 := by
  decide

theorem heart_width_is_6 :
    heartWidth = 6 := by
  decide

theorem lung_width_is_4 :
    lungWidth = 4 := by
  decide

theorem head_width_is_14 :
    headWidthDerived = 14 := by
  decide

theorem heart_is_palindrome :
    heartPattern.reverse = heartPattern := by
  decide

theorem common_has_four_phases :
    commonPrimitive.length = 4 := by
  decide

theorem pulse_contract_passes :
    contractPass contract = true := by
  decide

def capacitancePulseCheck : Bool :=
  symbolicOnly &&
  (capRoot == 81) &&
  (heartAmplitude == 4096) &&
  (lungAmplitude == 16) &&
  (headAmplitude == 243) &&
  (heartWidth == 6) &&
  (lungWidth == 4) &&
  (headWidthDerived == 14) &&
  (bodyCarrier == "..||..||||") &&
  (nobleGate == ":::: x ::::") &&
  (commonPrimitive.length == 4) &&
  contractPass contract

theorem capacitance_pulse_check_passes :
    capacitancePulseCheck = true := by
  decide

end Oasis.Timing.CapacitancePulse00
