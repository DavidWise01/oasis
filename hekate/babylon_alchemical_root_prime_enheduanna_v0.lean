namespace BabylonAlchemyEnheduannaV0

inductive GenderState where
  | femaleDominant
  | maleDominant
  | equal
  | unresolved
  deriving Repr, DecidableEq

def referentName : String := "ENHEDUANNA"
def corridorRole : String := "UPSTREAM_MESOPOTAMIAN_REFERENT_TO_BABYLON"
def referentGender : GenderState := .femaleDominant
def polityGender : GenderState := .maleDominant

def rootPrime : List String :=
  ["NAME", "MOON", "PRIESTESS", "HYMN", "INANNA", "BIND", "CORPUS"]

def alchemicalOverlay : List String :=
  ["MOON:SILVER", "ENHEDUANNA", "VENUS:COPPER"]

theorem referent_exact :
    referentName = "ENHEDUANNA" := by
  rfl

theorem referent_gender_exact :
    referentGender = .femaleDominant := by
  rfl

theorem polity_gender_exact :
    polityGender = .maleDominant := by
  rfl

end BabylonAlchemyEnheduannaV0
