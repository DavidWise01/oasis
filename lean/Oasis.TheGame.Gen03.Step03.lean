namespace Oasis.TheGame.Gen03.Step03
def witnessCount : Nat := 4
def acceptedAt : Nat := 3
def accepts (votes : Nat) : Bool := decide (acceptedAt ≤ votes ∧ votes ≤ witnessCount)
theorem exact_quorum_accepts : accepts 3 = true := by decide
end Oasis.TheGame.Gen03.Step03
