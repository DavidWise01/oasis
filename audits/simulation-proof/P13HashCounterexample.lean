import Lean

/-!
P1.3 ROOT0 counterexample schema: an unkeyed hash recomputed over a
nonadjacent message passes equality, but has no bearing on legality.
Lean file is a DRAFT and has NOT been compiler-checked in this environment.
-/
namespace ROOT0P13

def adjacent (from to : Nat) : Bool :=
  ((from + 1) % 5 == to) || ((to + 1) % 5 == from)

def hashAccepts (hashFn : String → String)
    (message receipt : String) : Prop := receipt = hashFn message

def forgedNonadjacent : String :=
  "occupied|vacant|vacant|vacant|vacant::move:0->2::vacant|vacant|occupied|vacant|vacant"

theorem recomputed_receipt_does_not_imply_legality (hashFn : String → String) :
    hashAccepts hashFn forgedNonadjacent (hashFn forgedNonadjacent) ∧
    adjacent 0 2 = false := by
  constructor
  · rfl
  · decide

end ROOT0P13
