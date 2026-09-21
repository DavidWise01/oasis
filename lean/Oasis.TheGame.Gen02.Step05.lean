namespace Oasis.TheGame.Gen02.Step05
def quorumPasses (yesVotes : Nat) : Bool := decide (3 ≤ yesVotes ∧ yesVotes ≤ 4)
theorem three_passes : quorumPasses 3 = true := by decide
theorem two_fails : quorumPasses 2 = false := by decide
end Oasis.TheGame.Gen02.Step05
