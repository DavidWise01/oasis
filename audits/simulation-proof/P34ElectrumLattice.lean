/-! ROOT0 P3.4 FCC counts; Lean 4 DRAFT (not compiled). -/
import Lean
namespace ROOT0P34
theorem fcc_unit_cells : (10 : Nat) * 10 * 10 = 1000 := by decide
theorem fcc_atomic_sites : (10 : Nat) * 10 * 10 * 4 = 4000 := by decide
theorem fcc_bonds : (4000 : Nat) * 12 / 2 = 24000 := by decide
theorem electrum_weight_sum : (79 : Nat) + 21 = 100 := by decide
theorem example_sites : (2693 : Nat) + 1307 = 4000 := by decide
theorem photon_cipher_round_trip_length : (208 : Nat) + 208 = 416 := by decide
end ROOT0P34
