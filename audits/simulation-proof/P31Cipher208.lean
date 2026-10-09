/-! ROOT0 P3.1 finite geometry draft: NOT MACHINE CHECKED.
The wave inverse is conditional on the externally supplied complex gate. -/
import Lean
namespace ROOT0P31
theorem sixteen_shared_seams : (16 : Nat) * 13 = 208 := by decide
theorem sixteen_fourteen_glyph_windows : (16 : Nat) * 14 - 16 = 208 := by decide
theorem two_full_passes : (208 : Nat) + 208 = 416 := by decide
theorem global_dot_bar_count : (104 : Nat) + 104 = 208 := by decide
def flipZ (n : Fin 10) : Fin 10 :=
  ⟨(10-n.val)%10, Nat.mod_lt _ (by decide)⟩
theorem flipZ_is_its_own_inverse (n : Fin 10) :
    flipZ (flipZ n) = n := by fin_cases n <;> decide
def mirror (p : Fin 10000 × Fin 10000) := (p.2,p.1)
theorem mirror_involutive (p : Fin 10000 × Fin 10000) :
    mirror (mirror p) = p := by cases p; rfl
end ROOT0P31
