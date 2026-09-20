import Std

/-
Oasis.Duality.FourQuads.00
==========================

Exact four-quad descendant.

Outer glyph:
  ((2x2))^((2x2))^2

The outer glyph is preserved as OaSIs notation and is NOT evaluated as
ordinary exponent arithmetic here.

Q1:
  a / ablation
  13-bit emergent-width gate
  2^3 = 8
  "logic deescilation"

Q2:
  2^2 = 4
  "verify cubic"

Q3:
  1^1 = 1
  "isomorphic x isomorphic"

Q4:
  symbolic token "0^0^0 = 81"

The final Q4 token is symbolic OaSIs notation, not a theorem of ordinary
exponent arithmetic.

NEW MODULE: not in the confirmed 0e ledger until user compilation.
-/

namespace Oasis.Duality.FourQuads00

def outerGlyph : String := "((2x2))^((2x2))^2"
def separator : String := "::::"
def quadCount : Nat := 4

inductive Quad where
  | q1
  | q2
  | q3
  | q4
  deriving DecidableEq, BEq, Repr

def quads : List Quad := [.q1, .q2, .q3, .q4]

def emergentWidthBits : Nat := 13

def passesEmergentWidth (bits : List Bool) : Bool :=
  bits.length == emergentWidthBits

def q1Label : String :=
  "a :: ablation :: must pass 13-bit emergent prims :: 8 or 2^3 :: logic deescilation"

def q2Label : String :=
  "2^2 :: verify cubic"

def q3Label : String :=
  "1^1 :: isomorphic x isomorphic"

def q4RootToken : String :=
  "0^0^0 = 81"

def q4RootValueLabel : Nat := 81

def logicDescent : Nat := 2 ^ 3
def verifyCubicValue : Nat := 2 ^ 2
def isomorphicUnit : Nat := 1 ^ 1

theorem exactly_four_quads :
    quads.length = 4 := by
  decide

theorem logic_descent_is_eight :
    logicDescent = 8 := by
  decide

theorem verify_cubic_value_is_four :
    verifyCubicValue = 4 := by
  decide

theorem isomorphic_unit_is_one :
    isomorphicUnit = 1 := by
  decide

theorem emergent_gate_width_is_thirteen :
    emergentWidthBits = 13 := by
  rfl

theorem q4_symbolic_value_is_eighty_one :
    q4RootValueLabel = 81 := by
  rfl

def fourQuadsCheck : Bool :=
  (quadCount == 4) &&
  (quads.length == 4) &&
  (emergentWidthBits == 13) &&
  (logicDescent == 8) &&
  (verifyCubicValue == 4) &&
  (isomorphicUnit == 1) &&
  (q4RootToken == "0^0^0 = 81") &&
  (q4RootValueLabel == 81)

theorem four_quads_check_passes :
    fourQuadsCheck = true := by
  decide

end Oasis.Duality.FourQuads00
