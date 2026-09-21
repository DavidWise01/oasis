namespace Oasis.TheGame.Gen03.Step05
abbrev RailState := Fin 26
abbrev FullState := Fin 53
def center : FullState := 52
def railToBoard (slot : RailState) : FullState := ⟨slot.val, Nat.le_trans slot.isLt (by decide)⟩
theorem rail_mapping_never_reaches_center (slot : RailState) : railToBoard slot ≠ center := by
  decide
end Oasis.TheGame.Gen03.Step05
