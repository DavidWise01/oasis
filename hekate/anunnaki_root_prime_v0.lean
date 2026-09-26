namespace AnunnakiRootPrimeV0

inductive GenderState where
  | mixed
  | maleDominant
  | femaleDominant
  | equal
  | unresolved
  deriving Repr, DecidableEq

def canonicalNames : List String :=
  ["ANUNNA", "ANUNA", "ANUNNAKI", "ANUNNAKU"]

def rootPrime : List String :=
  ["GROUP", "HIGH_GODS", "FATE", "JUDGMENT", "HEAVEN", "NETHERWORLD"]

def gender : GenderState := .mixed
def dominance : GenderState := .unresolved

def cipher : List String :=
  ["VESSEL", "COUNCIL", "TEST", "FIX"]

theorem group_gender_mixed :
    gender = .mixed := by
  rfl

theorem dominance_unresolved :
    dominance = .unresolved := by
  rfl

end AnunnakiRootPrimeV0
