import Std

/-!
Oasis.Language.OSI6.00
======================
Deterministic OSI-analog Layer 6 presentation/representation.

This is the first layer that gives the carrier a fixed language-shaped representation.

Invariant:
  26 language cells × 4 bits = 104 bits
  5 frame cells    × 4 bits =  20 bits
                              --------
                               124 bits

The outer 4-bit BOXY coupler is intentionally NOT part of Layer 6.
It remains outside the 124-bit OSI body.

Layer 6 does not decide human meaning; HACI / Layer 8 owns the human boundary.
-/

namespace Oasis.Language.OSI6

/-- One four-bit language/frame cell. -/
abbrev Nibble := Fin 16

def languageCells : Nat := 26
def cellWidth : Nat := 4
def languageWidth : Nat := languageCells * cellWidth

def frameCells : Nat := 5
def frameWidth : Nat := frameCells * cellWidth

def osiBodyWidth : Nat := languageWidth + frameWidth

/-- Fixed-size 26-cell language representation. -/
abbrev Language104 := Fin 26 → Nibble

/-- Fixed-size 5-cell frame representation. -/
abbrev Frame20 := Fin 5 → Nibble

/-- Exact Layer-6 body: 104-bit language representation + 20-bit frame. -/
structure Body124 where
  language : Language104
  frame : Frame20

/-- Deterministic constructor. -/
def bind (language : Language104) (frame : Frame20) : Body124 :=
  {
    language := language
    frame := frame
  }

/-- Layer 6 forwards a complete represented body unchanged. -/
def transmit (b : Body124) : Body124 := b

/-- Projection is lossless. -/
def unbind (b : Body124) : Language104 × Frame20 :=
  (b.language, b.frame)

theorem language_width_eq_104 :
    languageWidth = 104 := by
  decide

theorem frame_width_eq_20 :
    frameWidth = 20 := by
  decide

theorem osi_body_width_eq_124 :
    osiBodyWidth = 124 := by
  decide

theorem unbind_bind
    (language : Language104)
    (frame : Frame20) :
    unbind (bind language frame) = (language, frame) := by
  rfl

theorem transmit_identity (b : Body124) :
    transmit b = b := by
  rfl

/-- Canonical zero language representation. -/
def zeroLanguage : Language104 :=
  fun _ => ⟨0, by decide⟩

/-- Canonical zero frame. -/
def zeroFrame : Frame20 :=
  fun _ => ⟨0, by decide⟩

def zeroBody : Body124 :=
  bind zeroLanguage zeroFrame

/-- Outer BOXY shell is deliberately reserved outside OSI6. -/
def outerCouplerWidth : Nat := 4

def boxyWidth : Nat := osiBodyWidth + outerCouplerWidth

theorem outer_coupler_width_eq_four :
    outerCouplerWidth = 4 := by
  rfl

theorem boxy_width_eq_128 :
    boxyWidth = 128 := by
  decide

/-- Executable closure check for Layer 6. -/
def osi6Check : Bool :=
  (languageCells == 26) &&
  (cellWidth == 4) &&
  (languageWidth == 104) &&
  (frameCells == 5) &&
  (frameWidth == 20) &&
  (osiBodyWidth == 124) &&
  (outerCouplerWidth == 4) &&
  (boxyWidth == 128)

theorem osi6_check_passes :
    osi6Check = true := by
  decide

end Oasis.Language.OSI6