namespace NewWorldOrderAlchemicalAtlantisV0

inductive Lane where
  | root0
  | myth
  | alchemicalCipher
  | supportedPhysics
  deriving Repr, DecidableEq

inductive Status where
  | supported
  | mythAttested
  | cipher
  | analogy
  | unresolved
  | conflict
  deriving Repr, DecidableEq

def mustStop : Status -> Bool
  | .unresolved => true
  | .conflict => true
  | _ => false

inductive GenderState where
  | femaleDominant
  | maleDominant
  | equal
  | unresolved
  deriving Repr, DecidableEq

def amazonGender : GenderState := .femaleDominant
def atlantisGender : GenderState := .maleDominant

def amazonPrimitive : String :=
  "w{{ind}}.a{{rgon}}.t{{ime}}.e{{lectrum}}.r{{e-agent}}"

def amazonOuter : String := "WATER"

def atlantisPrime : List String :=
  ["CENTER", "RING", "TWIN", "TEN", "KING", "METAL", "WATER", "SINK"]

def corridor : List String :=
  ["BABBAGE", "LOVELACE", "MAXWELL", "RONTGEN",
   "BECQUEREL", "THOMSON", "PLANCK", "EINSTEIN_1905",
   "AMAZONS", "ATLANTIS"]

theorem unresolved_stops :
    mustStop .unresolved = true := by
  rfl

theorem amazon_gender_exact :
    amazonGender = .femaleDominant := by
  rfl

theorem atlantis_gender_exact :
    atlantisGender = .maleDominant := by
  rfl

theorem amazon_outer_exact :
    amazonOuter = "WATER" := by
  rfl

end NewWorldOrderAlchemicalAtlantisV0
