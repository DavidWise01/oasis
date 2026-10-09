/-!
ROOT0 P2.6: finite classical register != a complex superposition space.
Lean 4 DRAFT; no Lean compiler was available in the test environment.
The exact Maxwell rotation no-go is argued analytically in the accompanying
report and tested on an order-nine orbit by the executable benchmark.
-/
import Lean
namespace ROOT0P26

/-- Three Boolean digits yield eight basis labels. -/
theorem eight_labels : (2 : Nat) ^ 3 = 8 := by decide

/-- Numerator two denotes a one-hot amplitude; zero otherwise. -/
def onehotNumerator (code coord : Fin 8) : Nat :=
  if code = coord then 2 else 0

/-- A field mixture has two nonzero components of numerator one. -/
def mixtureNumerator (coord : Fin 8) : Nat :=
  if coord = 0 then 1 else if coord = 4 then 1 else 0

theorem onehot_component_cannot_equal_half (code : Fin 8) :
    onehotNumerator code 0 ≠ 1 := by
  by_cases h : code = 0
  · simp [onehotNumerator, h]
  · simp [onehotNumerator, h]

/-- One-hot code cannot equal a two-component mixture. -/
theorem no_onehot_represents_mixture (code : Fin 8) :
    onehotNumerator code ≠ mixtureNumerator := by
  intro h
  have h0 : onehotNumerator code 0 = mixtureNumerator 0 :=
    congrArg (fun f : Fin 8 → Nat => f 0) h
  have hm : onehotNumerator code 0 = 1 := by
    simpa [mixtureNumerator] using h0
  exact onehot_component_cannot_equal_half code hm

/-- Added field-amplitude state, NOT derived from the frozen v92 source. -/
structure AddedAmplitude (Scalar : Type) where
  coeff : Fin 8 → Scalar
end ROOT0P26
