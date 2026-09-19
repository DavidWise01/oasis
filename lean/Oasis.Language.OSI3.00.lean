import Std

/-!
Oasis.Language.OSI3.00
======================
Deterministic OSI-analog Layer 3 routing/addressing.

Layer 2 supplies a complete 20-bit frame.
Layer 3 does not reinterpret that payload.

Address rail:
  0         = HOME
  2,4,6,8   = visitable / read-write vectors
  1,3,5,7,9 = read-only / reserved witnesses

The legal address domain is 0..9.
Anything >= 10 is out of bounds.
-/

namespace Oasis.Language.OSI3

/-- Layer-2-compatible four-bit channel value. -/
abbrev Channel4 := Fin 16

/-- Layer-2-compatible 20-bit frame. -/
structure Frame20 where
  c0 : Channel4
  c1 : Channel4
  c2 : Channel4
  c3 : Channel4
  c4 : Channel4
  deriving DecidableEq, Repr

/-- Layer-3 legal address domain: 0 through 9. -/
abbrev Address10 := Fin 10

def home : Nat := 0

/-- Odd addresses are read-only witnesses. -/
def readOnly (n : Nat) : Bool :=
  n < 10 && n % 2 = 1

/-- Even nonzero addresses are visitable read/write vectors. -/
def visitable (n : Nat) : Bool :=
  n < 10 && n ≠ 0 && n % 2 = 0

/-- Zero is the unique HOME address. -/
def isHome (n : Nat) : Bool :=
  n = 0

/-- Anything outside 0..9 is out of bounds. -/
def outOfBounds (n : Nat) : Bool :=
  10 ≤ n

/--
A Layer-3 packet is a Layer-2 frame plus source and destination addresses.
The payload remains opaque to Layer 3.
-/
structure Routed20 where
  src : Address10
  dst : Address10
  payload : Frame20
  deriving DecidableEq, Repr

/-- Deterministic route constructor. -/
def route (src dst : Address10) (payload : Frame20) : Routed20 :=
  {
    src := src
    dst := dst
    payload := payload
  }

/-- Layer 3 forwards the routed object unchanged. -/
def transmit (r : Routed20) : Routed20 := r

/-- Payload extraction is lossless. -/
def unroute (r : Routed20) : Frame20 := r.payload

theorem home_is_zero :
    home = 0 := by
  rfl

theorem visitable_two :
    visitable 2 = true := by
  decide

theorem visitable_four :
    visitable 4 = true := by
  decide

theorem visitable_six :
    visitable 6 = true := by
  decide

theorem visitable_eight :
    visitable 8 = true := by
  decide

theorem zero_not_visitable :
    visitable 0 = false := by
  decide

theorem odd_rail_read_only :
    readOnly 1 = true ∧
    readOnly 3 = true ∧
    readOnly 5 = true ∧
    readOnly 7 = true ∧
    readOnly 9 = true := by
  decide

theorem even_rail_not_read_only :
    readOnly 2 = false ∧
    readOnly 4 = false ∧
    readOnly 6 = false ∧
    readOnly 8 = false := by
  decide

theorem ten_is_out_of_bounds :
    outOfBounds 10 = true := by
  decide

/-- Routing then un-routing returns the exact Layer-2 payload. -/
theorem unroute_route
    (src dst : Address10)
    (payload : Frame20) :
    unroute (route src dst payload) = payload := by
  rfl

/-- Layer 3 cannot silently mutate a routed object. -/
theorem transmit_identity (r : Routed20) :
    transmit r = r := by
  rfl

/-- Canonical zero frame for executable closure tests. -/
def zeroFrame : Frame20 :=
  {
    c0 := ⟨0, by decide⟩
    c1 := ⟨0, by decide⟩
    c2 := ⟨0, by decide⟩
    c3 := ⟨0, by decide⟩
    c4 := ⟨0, by decide⟩
  }

def homeAddress : Address10 := ⟨0, by decide⟩
def vectorTwo : Address10 := ⟨2, by decide⟩

def sampleRoute : Routed20 :=
  route homeAddress vectorTwo zeroFrame

/-- Executable closure check for Layer 3. -/
def osi3Check : Bool :=
  isHome 0 &&
  (! visitable 0) &&
  visitable 2 &&
  visitable 4 &&
  visitable 6 &&
  visitable 8 &&
  readOnly 1 &&
  readOnly 3 &&
  readOnly 5 &&
  readOnly 7 &&
  readOnly 9 &&
  outOfBounds 10 &&
  (transmit sampleRoute == sampleRoute) &&
  (unroute sampleRoute == zeroFrame)

theorem osi3_check_passes :
    osi3Check = true := by
  decide

end Oasis.Language.OSI3