namespace Oasis.TheGame.Gen03.Step02
def nextPhase : Bool → Bool
  | false => true
  | true => false
theorem declared_state_enters_witness : nextPhase false = true := rfl
end Oasis.TheGame.Gen03.Step02
