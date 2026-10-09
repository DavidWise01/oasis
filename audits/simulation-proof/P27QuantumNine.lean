/-!
ROOT0 P2.7 mathematical correction, Lean 4 DRAFT (UNCOMPILED).
A nine-symbol code is not the same as a nine-complex-amplitude Hilbert space.
This file does not define the supplied operator glyph or assert real-world physics.
-/
import Lean
namespace ROOT0P27

abbrev ClassicalNine := Fin 9
abbrev AmplitudeNine (K : Type) := Fin 9 → K

theorem nine_is_three_by_three : (3 : Nat) * 3 = 9 := by decide
theorem nine_exceeds_eight : (9 : Nat) > 8 := by decide

/-- One-hot encoding is classical, not the general superposition carrier. -/
def doubledOneHot (i j : Fin 9) : Nat := if i = j then 2 else 0
def mixture (j : Fin 9) : Nat := if j = 0 then 1 else if j = 1 then 1 else 0

theorem no_one_hot_is_mixture (i : Fin 9) : doubledOneHot i ≠ mixture := by
  intro h
  have p : doubledOneHot i 0 = mixture 0 := congrArg (fun f : Fin 9 → Nat => f 0) h
  by_cases hi : i = 0
  · simp [doubledOneHot, mixture, hi] at p
  · simp [doubledOneHot, mixture, hi] at p

end ROOT0P27
