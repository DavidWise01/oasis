import Std

/-!
Oasis.Language.OSI5.00
======================
Deterministic OSI-analog Layer 5 session/bind.

Layer 4 supplies an ordered transport segment.
Layer 5 adds only a bounded session state.

Invariant:
* CLOSED sessions do not release the Layer-4 segment.
* OPEN sessions release the exact Layer-4 segment unchanged.
* Layer 5 does not interpret payload semantics.
-/

namespace Oasis.Language.OSI5

/-- Four-bit primitive reused from the lower layers. -/
abbrev Nibble := Fin 16

/-- Layer-2-compatible 20-bit frame. -/
structure Frame20 where
  c0 : Nibble
  c1 : Nibble
  c2 : Nibble
  c3 : Nibble
  c4 : Nibble
  deriving DecidableEq, Repr

/-- Layer-3 legal address domain. -/
abbrev Address10 := Fin 10

/-- Layer-3 routed frame. -/
structure Routed20 where
  src : Address10
  dst : Address10
  payload : Frame20
  deriving DecidableEq, Repr

/-- Layer-4 ordered transport segment. -/
structure Segment20 where
  seq : Nibble
  routed : Routed20
  deriving DecidableEq, Repr

/-- Layer-5 session has exactly two states. -/
inductive SessionState where
  | closed
  | open
  deriving DecidableEq, BEq, Repr

/-- A bounded Layer-5 session around one Layer-4 segment. -/
structure Session20 where
  state : SessionState
  segment : Segment20
  deriving DecidableEq, Repr

/-- Construct a closed session. -/
def bindClosed (s : Segment20) : Session20 :=
  {
    state := .closed
    segment := s
  }

/-- Construct an open session. -/
def bindOpen (s : Segment20) : Session20 :=
  {
    state := .open
    segment := s
  }

/-- Open an existing session without changing its segment. -/
def openSession (s : Session20) : Session20 :=
  {
    state := .open
    segment := s.segment
  }

/-- Close an existing session without changing its segment. -/
def closeSession (s : Session20) : Session20 :=
  {
    state := .closed
    segment := s.segment
  }

/-- Only an open session releases its Layer-4 segment. -/
def release (s : Session20) : Option Segment20 :=
  match s.state with
  | .closed => none
  | .open => some s.segment

theorem closed_does_not_release (seg : Segment20) :
    release (bindClosed seg) = none := by
  rfl

theorem open_releases_exact_segment (seg : Segment20) :
    release (bindOpen seg) = some seg := by
  rfl

theorem opening_preserves_segment (s : Session20) :
    (openSession s).segment = s.segment := by
  rfl

theorem closing_preserves_segment (s : Session20) :
    (closeSession s).segment = s.segment := by
  rfl

theorem open_after_close_releases_original (s : Session20) :
    release (openSession (closeSession s)) = some s.segment := by
  rfl

theorem close_after_open_is_closed (s : Session20) :
    (closeSession (openSession s)).state = .closed := by
  rfl

/-- Canonical lower-layer sample for executable closure. -/
def zeroNibble : Nibble := ⟨0, by decide⟩

def zeroFrame : Frame20 :=
  {
    c0 := zeroNibble
    c1 := zeroNibble
    c2 := zeroNibble
    c3 := zeroNibble
    c4 := zeroNibble
  }

def homeAddress : Address10 := ⟨0, by decide⟩
def vectorTwo : Address10 := ⟨2, by decide⟩

def sampleRoute : Routed20 :=
  {
    src := homeAddress
    dst := vectorTwo
    payload := zeroFrame
  }

def sampleSegment : Segment20 :=
  {
    seq := zeroNibble
    routed := sampleRoute
  }

def closedSample : Session20 :=
  bindClosed sampleSegment

def openSample : Session20 :=
  bindOpen sampleSegment

/-- Executable closure check for Layer 5. -/
def osi5Check : Bool :=
  (closedSample.state == .closed) &&
  (openSample.state == .open) &&
  (release closedSample == none) &&
  (release openSample == some sampleSegment) &&
  (openSession closedSample).segment == sampleSegment &&
  (closeSession openSample).segment == sampleSegment

theorem osi5_check_passes :
    osi5Check = true := by
  decide

end Oasis.Language.OSI5