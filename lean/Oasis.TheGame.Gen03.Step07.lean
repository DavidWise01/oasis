namespace Oasis.TheGame.Gen03.Step07
inductive Rail where | a | b
  deriving Repr, DecidableEq
def mirror : Rail → Rail
  | .a => .b
  | .b => .a
theorem mirror_flips_a : mirror .a = .b := rfl
theorem mirror_flips_b : mirror .b = .a := rfl
end Oasis.TheGame.Gen03.Step07
