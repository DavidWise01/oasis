import Std

/-!
Oasis.Language.OSI4.00
======================
Deterministic OSI-analog Layer 4 transport/order.

Layer 3 supplies a routed 20-bit frame.
Layer 4 adds one 4-bit sequence token.

No language semantics are introduced here.

Invariant:
* sequence token has 16 states
* delivery occurs only when received sequence = expected sequence
* accepted delivery returns the exact Layer-3 payload unchanged
-/

namespace Oasis.Language.OSI4

/-- Four-bit value used by Layer 1/2 and reused as the Layer-4 sequence token. -/
abbrev Nibble := Fin 16

/-- Layer-2-compatible 20-bit frame. -/
structure Frame20 where
  c0 : Nibble
  c1 : Nibble
  c2 : Nibble
  c3 : Nibble
  c4 : Nibble
  deriving DecidableEq, Repr

/-- Layer-3 legal address domain: 0 through 9. -/
abbrev Address10 := Fin 10

/-- Layer-3 routed object. -/
structure Routed20 where
  src : Address10
  dst : Address10
  payload : Frame20
  deriving DecidableEq, Repr

/-- Layer-4 transport object: sequence token + routed payload. -/
structure Segment20 where
  seq : Nibble
  routed : Routed20
  deriving DecidableEq, Repr

def sequenceStates : Nat := 16

/-- Deterministic transport constructor. -/
def wrap (seq : Nibble) (r : Routed20) : Segment20 :=
  {
    seq := seq
    routed := r
  }

/-- Exact sequence equality is the only acceptance rule. -/
def accepts (expected : Nibble) (s : Segment20) : Bool :=
  s.seq == expected

/--
Deliver only when the sequence token matches.
The returned routed object is unchanged.
-/
def deliver (expected : Nibble) (s : Segment20) : Option Routed20 :=
  if accepts expected s then
    some s.routed
  else
    none

theorem sequence_states_eq_sixteen :
    sequenceStates = 16 := by
  rfl

/-- Correct sequence always delivers the exact routed payload. -/
theorem deliver_matching
    (seq : Nibble)
    (r : Routed20) :
    deliver seq (wrap seq r) = some r := by
  simp [deliver, accepts, wrap]

/-- A successful delivery implies sequence equality. -/
theorem delivery_implies_sequence_match
    (expected : Nibble)
    (s : Segment20)
    (h : deliver expected s = some s.routed) :
    s.seq = expected := by
  simp [deliver, accepts] at h
  exact h

/-- Layer 4 cannot mutate an accepted routed object. -/
theorem accepted_payload_identity
    (expected : Nibble)
    (s : Segment20)
    (h : accepts expected s = true) :
    deliver expected s = some s.routed := by
  simp [deliver, h]

/-- Canonical zero frame. -/
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
  {
    src := homeAddress
    dst := vectorTwo
    payload := zeroFrame
  }

def seqZero : Nibble := ⟨0, by decide⟩
def seqOne : Nibble := ⟨1, by decide⟩

def sampleSegment : Segment20 :=
  wrap seqZero sampleRoute

theorem matching_sequence_accepts :
    accepts seqZero sampleSegment = true := by
  decide

theorem wrong_sequence_rejects :
    accepts seqOne sampleSegment = false := by
  decide

theorem wrong_sequence_does_not_deliver :
    deliver seqOne sampleSegment = none := by
  decide

theorem correct_sequence_delivers :
    deliver seqZero sampleSegment = some sampleRoute := by
  decide

/-- Executable closure check for Layer 4. -/
def osi4Check : Bool :=
  (sequenceStates == 16) &&
  accepts seqZero sampleSegment &&
  (! accepts seqOne sampleSegment) &&
  (deliver seqZero sampleSegment == some sampleRoute) &&
  (deliver seqOne sampleSegment == none)

theorem osi4_check_passes :
    osi4Check = true := by
  decide

end Oasis.Language.OSI4