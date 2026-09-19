import Std

/-!
Oasis.Language.OSI9.00
======================
Deterministic OSI-analog Layer 9 human-origin ingress.

Layer 9 is above HACI / Layer 8.

Invariant:
* human-originated material is bound to a Carbon identifier
* Layer 9 does not cross directly to Layer 7
* the only legal downward path is through Layer 8 / HACI
* Layer 9 preserves the submitted payload unchanged

This layer does not decide HACI accountability.
It only prepares the human-origin envelope for Layer 8.
-/

namespace Oasis.Language.OSI9

/-- Opaque Carbon identifier for a human-facing reference. -/
structure CarbonId where
  n : Nat
  deriving DecidableEq, Repr

/-- Human-origin envelope presented to HACI / Layer 8. -/
structure HumanEnvelope where
  carbon : CarbonId
  payload : String
  caps : Bool
  deriving DecidableEq, Repr

/-- The only downward destination permitted from Layer 9. -/
inductive DownTarget where
  | haci8
  | osi7
  deriving DecidableEq, BEq, Repr

/-- Bind human-origin material to its Carbon identifier. -/
def bindHuman (c : CarbonId) (payload : String) (caps : Bool) :
    HumanEnvelope :=
  {
    carbon := c
    payload := payload
    caps := caps
  }

/-- Layer 9 preserves the human envelope unchanged. -/
def transmit (e : HumanEnvelope) : HumanEnvelope := e

/-- Only HACI / Layer 8 is a legal downward destination. -/
def canDescendTo : DownTarget → Bool
  | .haci8 => true
  | .osi7 => false

theorem haci8_is_legal_downward_target :
    canDescendTo .haci8 = true := by
  rfl

theorem osi7_direct_bypass_is_forbidden :
    canDescendTo .osi7 = false := by
  rfl

theorem transmit_identity (e : HumanEnvelope) :
    transmit e = e := by
  rfl

theorem bind_preserves_carbon
    (c : CarbonId) (payload : String) (caps : Bool) :
    (bindHuman c payload caps).carbon = c := by
  rfl

theorem bind_preserves_payload
    (c : CarbonId) (payload : String) (caps : Bool) :
    (bindHuman c payload caps).payload = payload := by
  rfl

theorem bind_preserves_caps
    (c : CarbonId) (payload : String) (caps : Bool) :
    (bindHuman c payload caps).caps = caps := by
  rfl

/-- Canonical sample. -/
def carbon0 : CarbonId := { n := 0 }

def sample : HumanEnvelope :=
  bindHuman carbon0 "ROOT0" true

/-- Executable closure check for Layer 9. -/
def osi9Check : Bool :=
  canDescendTo .haci8 &&
  (! canDescendTo .osi7) &&
  ((transmit sample).carbon == carbon0) &&
  ((transmit sample).payload == "ROOT0") &&
  ((transmit sample).caps == true)

theorem osi9_check_passes :
    osi9Check = true := by
  decide

end Oasis.Language.OSI9