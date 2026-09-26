namespace HEKATE

/-
  isoKernel v11 — frozen full primitive
  -------------------------------------
  Author's shortest canonical compression:

      S+Pi-N

  This is the frozen primitive for the current SUQ quantum-OSI /
  logical shadow-ladder layer.

  Preserve literally:
    S + Pi - N

  No arithmetic, particle, or conventional pi semantics are assigned here.
-/

inductive PrimToken where
  | S
  | plus
  | Pi
  | minus
  | N
  deriving Repr, DecidableEq

def fullPrim : List PrimToken :=
  [.S, .plus, .Pi, .minus, .N]

def fullPrimLiteral : String :=
  "S+Pi-N"

theorem fullPrim_exact :
    fullPrim = [.S, .plus, .Pi, .minus, .N] := by
  rfl

theorem fullPrim_literal_exact :
    fullPrimLiteral = "S+Pi-N" := by
  rfl

/-
  FROZEN:

      .inf.inf.inf
           |
          -i^3
           |
     SUQ QUANTUM OSI
           |
     SHADOW LADDER
           |
        S+Pi-N

  STATUS: FULL PRIM / IMMUTABLE
-/

end HEKATE
