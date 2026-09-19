import Std

/-!
Oasis.Language.OSI1.00
======================
Deterministic OSI-analog Layer 1 carrier.

This layer intentionally has no language semantics.

Primitive:
* 1 bit has 2 states.
* one channel is 4 bits wide, therefore 16 states.
* four physical lanes carry one 4-bit channel each.
* total lane-addressed carrier states = 4 × 16 = 64.

Layer 1 transports the carrier unchanged. Interpretation belongs above Layer 1.
-/

namespace Oasis.Language.OSI1

/-- One physical binary primitive. -/
abbrev Bit1 := Fin 2

/-- A four-bit channel has exactly sixteen representable states. -/
abbrev Channel4 := Fin 16

/-- Four physical lanes, addressed 0 through 3. -/
abbrev Lane4 := Fin 4

def bitWidth : Nat := 1
def bitStates : Nat := 2 ^ bitWidth

def channelWidth : Nat := 4
def channelStates : Nat := 2 ^ channelWidth

def laneCount : Nat := 4

/-- A Layer-1 carrier is only an address plus a four-bit value. -/
structure Carrier where
  lane : Lane4
  value : Channel4
  deriving DecidableEq, Repr

/-- Layer 1 is transparent: it carries the value without interpretation. -/
def transmit (c : Carrier) : Carrier := c

theorem bit_states_eq_two :
    bitStates = 2 := by
  decide

theorem channel_states_eq_sixteen :
    channelStates = 16 := by
  decide

theorem lane_count_eq_four :
    laneCount = 4 := by
  rfl

/-- Four lanes × sixteen states = sixty-four lane-addressed carrier states. -/
theorem carrier_state_space :
    laneCount * channelStates = 64 := by
  decide

/-- Layer 1 cannot silently change a carrier. -/
theorem transmit_identity (c : Carrier) :
    transmit c = c := by
  rfl

/-- Same input always yields the same Layer-1 output. -/
theorem transmit_deterministic (a b : Carrier) (h : a = b) :
    transmit a = transmit b := by
  simp [h]

/-- Canonical zero carrier on lane zero. -/
def zeroCarrier : Carrier :=
  {
    lane := ⟨0, by decide⟩
    value := ⟨0, by decide⟩
  }

/-- Canonical maximum four-bit value on lane three. -/
def maxCarrier : Carrier :=
  {
    lane := ⟨3, by decide⟩
    value := ⟨15, by decide⟩
  }

theorem zero_transmits :
    transmit zeroCarrier = zeroCarrier := by
  rfl

theorem max_transmits :
    transmit maxCarrier = maxCarrier := by
  rfl

/-- Executable closure check for the primitive Layer-1 contract. -/
def osi1Check : Bool :=
  (bitStates == 2) &&
  (channelStates == 16) &&
  (laneCount == 4) &&
  (laneCount * channelStates == 64) &&
  (transmit zeroCarrier == zeroCarrier) &&
  (transmit maxCarrier == maxCarrier)

theorem osi1_check_passes :
    osi1Check = true := by
  decide

end Oasis.Language.OSI1