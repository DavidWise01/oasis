namespace Oasis.TheGame.Gen02.Step07
structure Session where
  a : Fin 26
  b : Fin 26
def center (_ : Session) : Fin 53 := 52
theorem center_is_constant (s : Session) : center s = 52 := rfl
end Oasis.TheGame.Gen02.Step07
