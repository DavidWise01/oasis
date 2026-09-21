namespace Oasis.TheGame.Gen03.Step01
inductive Phase where | declare | witness | append
  deriving Repr, DecidableEq
def firstPhase : Phase := .declare
theorem first_phase_is_declare : firstPhase = .declare := rfl
end Oasis.TheGame.Gen03.Step01
