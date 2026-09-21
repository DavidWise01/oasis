namespace Oasis.TheGame.Gen03.Step06
def batchWidth : Nat := 3
def batchSealed (completed : Nat) : Bool := completed == batchWidth
theorem three_steps_seal_batch : batchSealed 3 = true := by decide
theorem two_steps_do_not_seal_batch : batchSealed 2 = false := by decide
end Oasis.TheGame.Gen03.Step06
