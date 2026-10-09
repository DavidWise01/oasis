/-! ROOT0 P2.8 Complex[0] ternary local geometry.
User's '^10' semantics intentionally unspecified.
Lean 4 DRAFT; not compiled in this session. -/
import Lean
namespace ROOT0P28
def positiveStartY : Int := 1
def positiveEndY : Int := 0
def negativeStartY : Int := 0
def negativeEndY : Int := -1
theorem balanced_labels : (-1 : Int) + 0 + 1 = 0 := by decide
theorem positive_moves_negative_y : positiveEndY - positiveStartY = -1 := by decide
theorem negative_moves_negative_y : negativeEndY - negativeStartY = -1 := by decide
theorem edges_compose : positiveEndY = negativeStartY := by rfl
theorem directed_path_total :
    (positiveEndY - positiveStartY) + (negativeEndY - negativeStartY) = -2 := by decide
theorem carrier_plane : 10 * 10 = 100 := by decide
theorem previous_floor : 9 * 1 * 9 = 81 := by decide
theorem optional_carrier_excess : (100 : Nat) - 81 = 19 := by decide
end ROOT0P28
