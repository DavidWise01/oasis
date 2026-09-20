import Std

/-
Oasis.GroundTruth.IBangI.00
===========================

Terminal bounded symbolic primitive:
  i!i

Canonical indexed forms:
  0 :: i .
  1 :: i i .
  2 :: i i i .

Canonical set forms:
  [0, {inf, 0, 0}]
  [1, {inf, i, i, .}]
  [2, {inf, i, i, i, .}]

inf 0,0 is represented as a bounded sandboxy box.

NEW MODULE: not in confirmed 0e ledger until user compilation.
-/

namespace Oasis.GroundTruth.IBangI00

def primitive : String := "i!i"
def terminal : Bool := true
def furtherDescent : Bool := false

structure IndexedForm where
  index : Nat
  body : String
  deriving DecidableEq, Repr

def indexed : List IndexedForm :=
  [
    { index := 0, body := "i ." },
    { index := 1, body := "i i ." },
    { index := 2, body := "i i i ." }
  ]

structure SetForm where
  index : Nat
  body : String
  deriving DecidableEq, Repr

def sets : List SetForm :=
  [
    { index := 0, body := "{ inf , 0 , 0 }" },
    { index := 1, body := "{ inf , i , i , . }" },
    { index := 2, body := "{ inf , i , i , i , . }" }
  ]

def cross : String := "::::x::"
def isomorphic : String := ":::: isomorphic"
def endToken : String := "::::x end ."

def sandboxToken : String := "inf 0,0"
def sandboxMeaning : String := "bounded sandboxy box"
def sandboxBounded : Bool := true

theorem primitive_preserved :
    primitive = "i!i" := by
  rfl

theorem exactly_three_indexed_forms :
    indexed.length = 3 := by
  decide

theorem exactly_three_set_forms :
    sets.length = 3 := by
  decide

theorem terminal_floor :
    terminal = true ∧ furtherDescent = false := by
  decide

theorem sandbox_is_bounded :
    sandboxBounded = true := by
  rfl

def groundTruthCheck : Bool :=
  (primitive == "i!i") &&
  terminal &&
  (!furtherDescent) &&
  (indexed.length == 3) &&
  (sets.length == 3) &&
  (cross == "::::x::") &&
  (isomorphic == ":::: isomorphic") &&
  (endToken == "::::x end .") &&
  (sandboxToken == "inf 0,0") &&
  sandboxBounded

theorem ground_truth_check_passes :
    groundTruthCheck = true := by
  decide

end Oasis.GroundTruth.IBangI00
