/-!
ROOT0 P2.4: conditional no-go for eight *classical cube-corner directions*.
Lean 4 DRAFT, NOT compiled in this environment. No physical-world premise.
The 2^3 bits need not mean eight literal photon directions in the frozen canon.
-/
import Lean
namespace ROOT0P24

/-- Each normalized (±1,±1,±1)/√3 corner has x⁴ = x²y² = 1/9.
After summing with arbitrary weights, only their total remains. -/
def cornerFourth (totalWeight : ℚ) : ℚ := totalWeight / 9

theorem corner_fourth_for_normalized_weights (w : ℚ) (h : w = 1) :
    cornerFourth w = (1 : ℚ) / 9 := by
  simp [cornerFourth, h]

/-- Rotational invariance in 3D requires E[x⁴] = 1/5. -/
theorem normalized_corners_cannot_have_isotropic_fourth_moment
    (w : ℚ) (h : w = 1) :
    cornerFourth w ≠ (1 : ℚ) / 5 := by
  rw [corner_fourth_for_normalized_weights w h]
  decide

/-- The same corner support gives E[x²y²] = 1/9 instead of 1/15. -/
theorem normalized_corners_mixed_fourth_mismatch
    (w : ℚ) (h : w = 1) :
    cornerFourth w ≠ (1 : ℚ) / 15 := by
  rw [corner_fourth_for_normalized_weights w h]
  decide

/-- The classic axis/diagonal fourth-moment gap is 4/27. -/
theorem axis_diagonal_fourth_gap :
    ((7 : ℚ) / 27) - ((1 : ℚ) / 9) = (4 : ℚ) / 27 := by
  decide

/-! Caveat: the theorem assumes a classical mixture restricted to exactly eight
spatial directions. Quantum interference, additional carrier states and
continuum/emergent Maxwell fields are outside its scope. -/
end ROOT0P24
