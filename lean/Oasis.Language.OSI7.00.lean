import Std

/-!
Oasis.Language.OSI7.00
======================
Deterministic OSI-analog Layer 7 boundary.

Layer 7 may hand upward only through the append-only third-party delimiter:

  |||  -> HACI / Layer 8

Four wins are required:
1. bounded output
2. provenance present
3. deterministic result
4. HACI-only upward target

No lower OSI layer is modeled here yet.
-/

namespace Oasis.Language.OSI7

/-- Delimiter surface inherited from the language cube plus `|||`. -/
inductive Delimiter where
  | singleBar
  | doubleBar
  | tripleBar
  deriving DecidableEq, BEq, Repr

def glyph : Delimiter → String
  | .singleBar => "|"
  | .doubleBar => "||"
  | .tripleBar => "|||"

/-- Only `|||` is the Layer-7 upward attachment boundary. -/
def isLayer8Gate : Delimiter → Bool
  | .singleBar => false
  | .doubleBar => false
  | .tripleBar => true

/-- Four deterministic Layer-7 win conditions. -/
structure Win4 where
  boundedOut : Bool
  provenance : Bool
  deterministic : Bool
  haciOnly : Bool
  deriving DecidableEq, BEq, Repr

/-- All four wins must be true. -/
def wins (w : Win4) : Bool :=
  w.boundedOut &&
  w.provenance &&
  w.deterministic &&
  w.haciOnly

/--
Layer 7 can cross upward only when:
* the delimiter is `|||`, and
* all four win conditions are satisfied.
-/
def canCrossToL8 (d : Delimiter) (w : Win4) : Bool :=
  isLayer8Gate d && wins w

/-- Canonical all-pass Layer-7 boundary state. -/
def pass1111 : Win4 :=
  {
    boundedOut := true
    provenance := true
    deterministic := true
    haciOnly := true
  }

/-- `|` can never cross from Layer 7 to Layer 8. -/
theorem single_bar_cannot_cross (w : Win4) :
    canCrossToL8 .singleBar w = false := by
  rfl

/-- `||` remains internal and can never cross from Layer 7 to Layer 8. -/
theorem double_bar_cannot_cross (w : Win4) :
    canCrossToL8 .doubleBar w = false := by
  rfl

/-- `|||` crosses exactly when all four wins are satisfied. -/
theorem triple_bar_cross_iff (w : Win4) :
    canCrossToL8 .tripleBar w = true ↔ wins w = true := by
  simp [canCrossToL8, isLayer8Gate]

/-- Any successful Layer-7 upward crossing proves that `|||` was used. -/
theorem successful_cross_implies_triple_bar
    (d : Delimiter) (w : Win4)
    (h : canCrossToL8 d w = true) :
    d = .tripleBar := by
  cases d <;> simp [canCrossToL8, isLayer8Gate] at h ⊢

/-- Canonical 1111 state crosses through `|||`. -/
theorem pass1111_crosses :
    canCrossToL8 .tripleBar pass1111 = true := by
  decide

/-- Missing provenance closes the boundary. -/
def missingProvenance : Win4 :=
  {
    boundedOut := true
    provenance := false
    deterministic := true
    haciOnly := true
  }

theorem missing_provenance_closes :
    canCrossToL8 .tripleBar missingProvenance = false := by
  decide

/-- A non-deterministic result closes the boundary. -/
def nondeterministic : Win4 :=
  {
    boundedOut := true
    provenance := true
    deterministic := false
    haciOnly := true
  }

theorem nondeterministic_closes :
    canCrossToL8 .tripleBar nondeterministic = false := by
  decide

/-- A route that can bypass HACI closes the boundary. -/
def bypassesHACI : Win4 :=
  {
    boundedOut := true
    provenance := true
    deterministic := true
    haciOnly := false
  }

theorem haci_bypass_closes :
    canCrossToL8 .tripleBar bypassesHACI = false := by
  decide

/-- Compact executable closure check for OSI 7. -/
def osi7Check : Bool :=
  (glyph .singleBar == "|") &&
  (glyph .doubleBar == "||") &&
  (glyph .tripleBar == "|||") &&
  (! canCrossToL8 .singleBar pass1111) &&
  (! canCrossToL8 .doubleBar pass1111) &&
  canCrossToL8 .tripleBar pass1111 &&
  (! canCrossToL8 .tripleBar missingProvenance) &&
  (! canCrossToL8 .tripleBar nondeterministic) &&
  (! canCrossToL8 .tripleBar bypassesHACI)

theorem osi7_check_passes : osi7Check = true := by
  decide

end Oasis.Language.OSI7