import Std

/-
Oasis.Duality.IsomorphicSix.00
==============================

Bounded symbolic isomorph:
  !i!
  |||...  <-> 111000

Exactly 3 bars + 3 dots = 6 positions, represented as
3 ones + 3 zeros in the paired binary alphabet.

NEW MODULE: not in confirmed 0e ledger until user compilation.
-/

namespace Oasis.Duality.IsomorphicSix00

def bound : String := "O"
def root : String := "o.0.o"
def isoToken : String := "!i!"
def symbolic : String := "|||..."
def binary : String := "111000"

def barCount : Nat := 3
def dotCount : Nat := 3
def oneCount : Nat := 3
def zeroCount : Nat := 3
def total : Nat := 6

theorem three_plus_three_is_six :
    barCount + dotCount = total := by
  decide

theorem binary_balance_is_six :
    oneCount + zeroCount = total := by
  decide

theorem symbolic_preserved :
    symbolic = "|||..." := by
  rfl

theorem binary_preserved :
    binary = "111000" := by
  rfl

theorem isomorph_token_preserved :
    isoToken = "!i!" := by
  rfl

def check : Bool :=
  (bound == "O") &&
  (root == "o.0.o") &&
  (isoToken == "!i!") &&
  (symbolic == "|||...") &&
  (binary == "111000") &&
  (barCount == 3) &&
  (dotCount == 3) &&
  (oneCount == 3) &&
  (zeroCount == 3) &&
  (total == 6)

theorem check_passes :
    check = true := by
  decide

end Oasis.Duality.IsomorphicSix00
