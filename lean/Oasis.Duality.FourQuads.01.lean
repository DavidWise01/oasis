import Std

/-
Oasis.Duality.FourQuads.01
==========================

All operators/tokens in this module are symbolic within the O bound.

Canonical:
  O
  o`0`o
  ((2x2))^((2x2))^2

Exactly four quads, separated by ::::

No exponent-looking token is interpreted as ordinary exponent arithmetic.

NEW MODULE: not in confirmed 0e ledger until user compilation.
-/

namespace Oasis.Duality.FourQuads01

def bound : String := "O"
def ouroboros : String := "O"
def isomorphicRoot : String := "o`0`o"
def outerGlyph : String := "((2x2))^((2x2))^2"
def separator : String := "::::"

inductive Quad where
  | q1
  | q2
  | q3
  | q4
  deriving DecidableEq, BEq, Repr

def quads : List Quad := [.q1, .q2, .q3, .q4]

def q1 : String :=
  "a :: ablation :: must pass 13-bit emergent prims :: 8 or 2^3 :: logic deescilation"

def q2 : String :=
  "2^2 :: verify cubic"

def q3 : String :=
  "1^1 :: isomorphic x isomorphic"

def q4 : String :=
  "0^0^0 = 81"

def symbolicOnly : Bool := true
def bounded : Bool := true
def isomorphic : Bool := true
def closesToO : Bool := true

theorem exactly_four_quads :
    quads.length = 4 := by
  decide

theorem root_is_o0o :
    isomorphicRoot = "o`0`o" := by
  rfl

theorem bound_is_O :
    bound = "O" := by
  rfl

theorem q1_preserved :
    q1 = "a :: ablation :: must pass 13-bit emergent prims :: 8 or 2^3 :: logic deescilation" := by
  rfl

theorem q2_preserved :
    q2 = "2^2 :: verify cubic" := by
  rfl

theorem q3_preserved :
    q3 = "1^1 :: isomorphic x isomorphic" := by
  rfl

theorem q4_preserved :
    q4 = "0^0^0 = 81" := by
  rfl

def fourQuadsCheck : Bool :=
  symbolicOnly &&
  bounded &&
  isomorphic &&
  closesToO &&
  (quads.length == 4) &&
  (bound == "O") &&
  (isomorphicRoot == "o`0`o") &&
  (outerGlyph == "((2x2))^((2x2))^2") &&
  (separator == "::::")

theorem four_quads_check_passes :
    fourQuadsCheck = true := by
  decide

end Oasis.Duality.FourQuads01
