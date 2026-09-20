import Std

/-
Oasis.Duality.ODotZeroO.00
===========================

Symbolic definition of the bounded isomorphic root:

  o . 0 . o
  o^n . 0^n . o^n

Three boxies:
  boxy1 permutates o
  boxy2 permutates 0
  boxy3 permutates o

The dot token is a ground-truth blast zone bounded to 0.
It is not a fourth box.

NEW MODULE: not in confirmed 0e ledger until user compilation.
-/

namespace Oasis.Duality.ODotZeroO00

def bound : String := "O"
def root : String := "o.0.o"
def scalable : String := "o^n.0^n.o^n"
def blastToken : String := "."
def blastName : String := "ground truth blast zone"
def blastBound : String := "0"

inductive Boxy where
  | boxy1
  | boxy2
  | boxy3
  deriving DecidableEq, BEq, Repr

def boxies : List Boxy := [.boxy1, .boxy2, .boxy3]

def symbol : Boxy → String
  | .boxy1 => "o"
  | .boxy2 => "0"
  | .boxy3 => "o"

def operation : Boxy → String
  | .boxy1 => "permutate"
  | .boxy2 => "permutate"
  | .boxy3 => "permutate"

def blastZoneCount : Nat := 2
def blastIsBox : Bool := false
def symbolicOnly : Bool := true

theorem exactly_three_boxies :
    boxies.length = 3 := by
  decide

theorem exactly_two_blast_zones :
    blastZoneCount = 2 := by
  rfl

theorem center_is_zero :
    symbol .boxy2 = "0" := by
  rfl

theorem outer_symbols_are_isomorphic_family :
    symbol .boxy1 = symbol .boxy3 := by
  rfl

theorem blast_zone_bounded_to_zero :
    blastBound = "0" := by
  rfl

theorem blast_zone_is_not_box :
    blastIsBox = false := by
  rfl

def rootCheck : Bool :=
  symbolicOnly &&
  (bound == "O") &&
  (root == "o.0.o") &&
  (scalable == "o^n.0^n.o^n") &&
  (boxies.length == 3) &&
  (blastZoneCount == 2) &&
  (!blastIsBox) &&
  (blastToken == ".") &&
  (blastBound == "0") &&
  (symbol .boxy1 == symbol .boxy3)

theorem root_check_passes :
    rootCheck = true := by
  decide

end Oasis.Duality.ODotZeroO00
