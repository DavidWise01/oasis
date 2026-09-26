namespace Universe1905Gravity1

/-
  {{universe_1905_gravity_1}}
  Historical comparison scaffold.
  Physics facts are documented in the companion Markdown file.
-/

inductive EraNode where
  | babbageLovelace
  | thermodynamics
  | maxwell
  | radiationAtomBreak
  | planck
  | einstein1905
  deriving Repr, DecidableEq

def timeline : List EraNode :=
  [.babbageLovelace, .thermodynamics, .maxwell,
   .radiationAtomBreak, .planck, .einstein1905]

theorem six_scaffold_nodes :
    timeline.length = 6 := by
  rfl

inductive CompareStatus where
  | supported
  | unresolved
  deriving Repr, DecidableEq

def einstein1905SpecialRelativity : CompareStatus := .supported
def einstein1905GeneralRelativity : CompareStatus := .unresolved

theorem stop_gravity_at_1905 :
    einstein1905GeneralRelativity = .unresolved := by
  rfl

def rootLabel : String := "{{universe_1905_gravity_1}}"

theorem root_label_exact :
    rootLabel = "{{universe_1905_gravity_1}}" := by
  rfl

end Universe1905Gravity1