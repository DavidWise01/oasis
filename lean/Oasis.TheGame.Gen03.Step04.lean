namespace Oasis.TheGame.Gen03.Step04
inductive Phase where | declare | witness | append
  deriving Repr, DecidableEq
def mayAppend : Phase → Bool
  | .append => true
  | _ => false
theorem only_append_phase_writes : mayAppend .append = true ∧ mayAppend .witness = false := by decide
end Oasis.TheGame.Gen03.Step04
