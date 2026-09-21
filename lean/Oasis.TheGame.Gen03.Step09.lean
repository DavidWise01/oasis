namespace Oasis.TheGame.Gen03.Step09
def cycleSteps : Nat := 3
def cycleSealed (steps : Nat) : Bool := steps == cycleSteps
def centerLocked : Bool := true
def generationThreeSeal : Bool := cycleSealed 3 && centerLocked
theorem generation_three_is_sealed : generationThreeSeal = true := by decide
end Oasis.TheGame.Gen03.Step09
