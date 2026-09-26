namespace HEKATE

/-
  isoKernel v16 — three Cubis per universe
  ----------------------------------------
  Author correction:

      just 3 per universe
      {{ u_p , u_a , u_n }}

  Preserve literally.
  This layer does not expand p/a/n into particle semantics.
-/

inductive UniverseCubi where
  | u_p
  | u_a
  | u_n
  deriving Repr, DecidableEq

def universeTriad : List UniverseCubi :=
  [.u_p, .u_a, .u_n]

theorem universe_has_three_cubis :
    universeTriad.length = 3 := by
  rfl

theorem universe_triad_exact :
    universeTriad = [.u_p, .u_a, .u_n] := by
  rfl

/-
  Canonical universe primitive:

      U
      |
      +-- u_p
      +-- u_a
      +-- u_n

  Compact:
      {{ u_p , u_a , u_n }}

  Exactly three Cubis per universe.
-/

end HEKATE
