namespace Oasis.TheGame.Gen02.Step09
def nextOrdinal (ledgerLength : Nat) : Nat := ledgerLength + 1
theorem first_turn_is_one : nextOrdinal 0 = 1 := by decide
theorem tenth_turn_is_ten : nextOrdinal 9 = 10 := by decide
end Oasis.TheGame.Gen02.Step09
