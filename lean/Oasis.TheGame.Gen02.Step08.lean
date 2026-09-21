namespace Oasis.TheGame.Gen02.Step08
abbrev Ledger := List Nat
def appendTurn (ledger : Ledger) (turn : Nat) : Ledger := ledger ++ [turn]
theorem append_to_empty_has_one_record : (appendTurn [] 1).length = 1 := by decide
end Oasis.TheGame.Gen02.Step08
