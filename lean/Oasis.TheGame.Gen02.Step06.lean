namespace Oasis.TheGame.Gen02.Step06
def advance (slot : Fin 26) : Fin 26 := ⟨Nat.min 25 (slot.val + 2), Nat.min_le_left _ _⟩
theorem initial_advance_is_two : (advance 0).val = 2 := by decide
theorem advance_caps_at_carrier : (advance 25).val = 25 := by decide
end Oasis.TheGame.Gen02.Step06
