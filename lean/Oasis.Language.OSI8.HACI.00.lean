import Std

/-!
Oasis.Language.OSI8.HACI.00
===========================
DLW Layer 8 / HACI human-trans accountability boundary.

Implicit 2×2:

  humanOnly  caps
      0       0   PASS
      0       1   ACCOUNT
      1       0   ACCOUNT
      1       1   PASS

Equivalently:
  PASS    := humanOnly = caps
  ACCOUNT := humanOnly XOR caps

CAPS means human eyes are required.
Layer 8 does not invent meaning; it gates accountability.
-/

namespace Oasis.Language.OSI8.HACI

structure Gate where
  humanOnly : Bool
  caps : Bool
  deriving DecidableEq, Repr

/-- Normal/justified state when both bits agree. -/
def pass (g : Gate) : Bool :=
  g.humanOnly == g.caps

/-- Accountability residue: exactly one bit differs. -/
def account (g : Gate) : Bool :=
  xor g.humanOnly g.caps

/-- CAPS always requires human eyes. -/
def humanEyesRequired (g : Gate) : Bool :=
  g.caps

/-- Human-only content without CAPS requires explanation. -/
def whyNoSignal (g : Gate) : Bool :=
  g.humanOnly && !g.caps

/-- CAPS on non-human-only content requires explanation. -/
def whyCaps (g : Gate) : Bool :=
  !g.humanOnly && g.caps

def machineNormal : Gate := { humanOnly := false, caps := false }
def machineCaps   : Gate := { humanOnly := false, caps := true  }
def humanNoCaps   : Gate := { humanOnly := true,  caps := false }
def humanCaps     : Gate := { humanOnly := true,  caps := true  }

theorem machine_normal_passes :
    pass machineNormal = true := by
  decide

theorem human_caps_passes :
    pass humanCaps = true := by
  decide

theorem machine_caps_accounts :
    account machineCaps = true := by
  decide

theorem human_no_caps_accounts :
    account humanNoCaps = true := by
  decide

theorem caps_requires_human_eyes :
    humanEyesRequired machineCaps = true ∧
    humanEyesRequired humanCaps = true := by
  decide

theorem no_caps_does_not_require_human_eyes :
    humanEyesRequired machineNormal = false ∧
    humanEyesRequired humanNoCaps = false := by
  decide

theorem pass_iff_no_account (g : Gate) :
    pass g = true ↔ account g = false := by
  cases g with
  | mk humanOnly caps =>
      cases humanOnly <;> cases caps <;> decide

/-- Executable closure check for HACI Layer 8. -/
def haci8Check : Bool :=
  pass machineNormal &&
  (!pass machineCaps) &&
  (!pass humanNoCaps) &&
  pass humanCaps &&
  (!account machineNormal) &&
  account machineCaps &&
  account humanNoCaps &&
  (!account humanCaps) &&
  whyCaps machineCaps &&
  whyNoSignal humanNoCaps

theorem haci8_check_passes :
    haci8Check = true := by
  decide

end Oasis.Language.OSI8.HACI