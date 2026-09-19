import Std

/-!
Oasis.Language.OSI2.00
======================
Deterministic OSI-analog Layer 2 framing.

Layer 1 provides one 4-bit carrier.
Layer 2 binds exactly five 4-bit carriers into one 20-bit frame.

No language semantics are introduced here.

Invariant:
  5 channels × 4 bits = 20 bits

Each channel has 16 possible values, therefore:
  16^5 = 2^20 = 1,048,576 raw Layer-2 frame states.
-/

namespace Oasis.Language.OSI2

/-- One Layer-1-compatible four-bit carrier value. -/
abbrev Channel4 := Fin 16

def channelWidth : Nat := 4
def channelStates : Nat := 2 ^ channelWidth
def frameChannels : Nat := 5
def frameWidth : Nat := frameChannels * channelWidth
def frameStates : Nat := channelStates ^ frameChannels

/--
A Layer-2 frame is exactly five four-bit channels.

The fields are positional only.
Layer 2 does not assign language meaning to them.
-/
structure Frame20 where
  c0 : Channel4
  c1 : Channel4
  c2 : Channel4
  c3 : Channel4
  c4 : Channel4
  deriving DecidableEq, Repr

/-- Deterministic framing constructor. -/
def bind
    (c0 c1 c2 c3 c4 : Channel4) : Frame20 :=
  {
    c0 := c0
    c1 := c1
    c2 := c2
    c3 := c3
    c4 := c4
  }

/-- Layer 2 forwards a complete frame unchanged. -/
def transmit (f : Frame20) : Frame20 := f

/-- Project the five carriers back out without mutation. -/
def unbind (f : Frame20) :
    Channel4 × Channel4 × Channel4 × Channel4 × Channel4 :=
  (f.c0, f.c1, f.c2, f.c3, f.c4)

theorem channel_states_eq_sixteen :
    channelStates = 16 := by
  decide

theorem frame_channels_eq_five :
    frameChannels = 5 := by
  rfl

theorem frame_width_eq_twenty :
    frameWidth = 20 := by
  decide

theorem frame_states_eq_two_pow_twenty :
    frameStates = 2 ^ 20 := by
  decide

theorem frame_states_eq_1048576 :
    frameStates = 1048576 := by
  decide

/-- Binding then unbinding returns exactly the five original carriers. -/
theorem unbind_bind
    (c0 c1 c2 c3 c4 : Channel4) :
    unbind (bind c0 c1 c2 c3 c4) =
      (c0, c1, c2, c3, c4) := by
  rfl

/-- Layer 2 cannot silently mutate a frame. -/
theorem transmit_identity (f : Frame20) :
    transmit f = f := by
  rfl

/-- Canonical all-zero Layer-2 frame. -/
def zeroFrame : Frame20 :=
  bind
    ⟨0, by decide⟩
    ⟨0, by decide⟩
    ⟨0, by decide⟩
    ⟨0, by decide⟩
    ⟨0, by decide⟩

/-- Canonical all-maximum Layer-2 frame. -/
def maxFrame : Frame20 :=
  bind
    ⟨15, by decide⟩
    ⟨15, by decide⟩
    ⟨15, by decide⟩
    ⟨15, by decide⟩
    ⟨15, by decide⟩

theorem zero_frame_transmits :
    transmit zeroFrame = zeroFrame := by
  rfl

theorem max_frame_transmits :
    transmit maxFrame = maxFrame := by
  rfl

/-- Executable closure check for the Layer-2 framing contract. -/
def osi2Check : Bool :=
  (channelStates == 16) &&
  (frameChannels == 5) &&
  (frameWidth == 20) &&
  (frameStates == 1048576) &&
  (transmit zeroFrame == zeroFrame) &&
  (transmit maxFrame == maxFrame)

theorem osi2_check_passes :
    osi2Check = true := by
  decide

end Oasis.Language.OSI2