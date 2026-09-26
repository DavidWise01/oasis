namespace MesopotamiaElementalPolarityV0

inductive Polarity where
  | minus
  | plus
  deriving Repr, DecidableEq

inductive Elemental where
  | earth
  | air
  | water
  | fire
  deriving Repr, DecidableEq

structure Pair where
  left : String
  right : String
  deriving Repr, DecidableEq

def skyEarth : Pair :=
  { left := "AN", right := "KI" }

def waterPair : Pair :=
  { left := "APSU", right := "TIAMAT" }

def dynamicPair : Pair :=
  { left := "ENLIL", right := "UTU" }

def rootPrimitive : String :=
  "-+ {{ AN | KI }} -+ :: -+ {{ APSU | TIAMAT }} -+"

theorem root_exact :
    rootPrimitive =
      "-+ {{ AN | KI }} -+ :: -+ {{ APSU | TIAMAT }} -+" := by
  rfl

end MesopotamiaElementalPolarityV0
