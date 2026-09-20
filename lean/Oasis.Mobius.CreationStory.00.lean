import Std

/-
Oasis.Mobius.CreationStory.00

MOBIUS co-creates a bounded vessel and curates a finite story/life instance
inside it. It does not claim to create biological life.

NEW MODULE: not in the confirmed 0e ledger until user compilation.
-/

namespace Oasis.Mobius.CreationStory00

inductive TruthState where
  | observedCurrent
  | historicallyAttested
  | traditionallyAttributed
  | narrativeInternal
  | contestedOrUncertain
  | mayChangeAfterSnapshot
  deriving DecidableEq, BEq, Repr

inductive Stage where
  | spark
  | coCreateVessel
  | instance
  | truthSnapshot
  | authorLineage
  | pictureLineage
  | styleGrammar
  | mediumGrammar
  | delivery
  | witness
  | impact
  | distillToPrimitives
  | nextSpark
  deriving DecidableEq, BEq, Repr

def cycle : List Stage :=
  [.spark, .coCreateVessel, .instance, .truthSnapshot, .authorLineage,
   .pictureLineage, .styleGrammar, .mediumGrammar, .delivery, .witness,
   .impact, .distillToPrimitives, .nextSpark]

structure Vessel where
  bounded : Bool
  createsBiologicalLife : Bool
  curatesInstance : Bool
  mayEnd : Bool
  impactMayPersist : Bool
  deriving DecidableEq, Repr

def vessel : Vessel :=
  { bounded := true
    createsBiologicalLife := false
    curatesInstance := true
    mayEnd := true
    impactMayPersist := true }

def validVessel (v : Vessel) : Bool :=
  v.bounded &&
  (!v.createsBiologicalLife) &&
  v.curatesInstance &&
  v.mayEnd &&
  v.impactMayPersist

theorem mobius_has_thirteen_stages :
    cycle.length = 13 := by
  decide

theorem mobius_does_not_create_biological_life :
    vessel.createsBiologicalLife = false := by
  rfl

theorem mobius_curates_instance :
    vessel.curatesInstance = true := by
  rfl

theorem mobius_allows_finite_instance_with_impact :
    vessel.mayEnd = true ∧ vessel.impactMayPersist = true := by
  decide

theorem vessel_is_valid :
    validVessel vessel = true := by
  decide

def mobiusCheck : Bool :=
  (cycle.length == 13) &&
  validVessel vessel

theorem mobius_check_passes :
    mobiusCheck = true := by
  decide

end Oasis.Mobius.CreationStory00
