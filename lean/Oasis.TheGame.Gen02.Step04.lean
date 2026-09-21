namespace Oasis.TheGame.Gen02.Step04
def pinnedCenter : Fin 53 := 52
def aLast : Fin 53 := 25
def bLast : Fin 53 := 51
theorem center_is_separate_from_rails : pinnedCenter ≠ aLast ∧ pinnedCenter ≠ bLast := by decide
end Oasis.TheGame.Gen02.Step04
