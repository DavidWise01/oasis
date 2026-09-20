import Std

/-
Oasis.MoreGarbage.01
====================

Primitive-scoped control model.

Read one primitive:
  aligned? Y -> +1 -> move on
  aligned? N -> down (0,0,0,-1) -> bounded local search

Base walk cost is n.
A local search across a bounded n-sized neighborhood gives the structural
worst-case n * n = n^2 search cost model.

rm / A::xx remains delete-current-and-advance.

Fresh descendant of Oasis.MoreGarbage.00.
Not 0e until user compiles it clean.
-/

namespace Oasis.MoreGarbage01

inductive Answer where
  | yes
  | no
  deriving Repr, DecidableEq

structure Down where
  x : Int
  y : Int
  z : Int
  w : Int
  deriving Repr, DecidableEq

def down : Down :=
  { x := 0, y := 0, z := 0, w := -1 }

theorem down_is_000_neg1 :
    down = { x := 0, y := 0, z := 0, w := -1 } := by
  rfl

def advance (i : Nat) : Nat :=
  i + 1

theorem yes_moves_plus_one (i : Nat) :
    advance i = i + 1 := by
  rfl

def scanCost (n : Nat) : Nat :=
  n

def localSearchCost (n : Nat) : Nat :=
  n

def recursiveSearchCost (n : Nat) : Nat :=
  scanCost n * localSearchCost n

theorem scan_is_linear (n : Nat) :
    scanCost n = n := by
  rfl

theorem recursive_search_is_n_squared (n : Nat) :
    recursiveSearchCost n = n * n := by
  rfl

inductive Decision where
  | move
  | search
  deriving Repr, DecidableEq

def decideStep : Answer → Decision
  | .yes => .move
  | .no => .search

theorem yes_means_move :
    decideStep .yes = .move := by
  rfl

theorem no_means_search :
    decideStep .no = .search := by
  rfl

def rmCurrent {α : Type} (_current : α) : Option α :=
  none

theorem rm_means_delete {α : Type} (current : α) :
    rmCurrent current = none := by
  rfl

def archimedesDrill {α : Type} : List α → List α
  | [] => []
  | _current :: rest => rest

theorem drill_delete_and_move_forward {α : Type}
    (current : α) (rest : List α) :
    archimedesDrill (current :: rest) = rest := by
  rfl

structure PrimitiveStep where
  index : Nat
  answer : Answer
  deriving Repr, DecidableEq

def nextIndex (s : PrimitiveStep) : Nat :=
  advance s.index

theorem every_completed_step_moves_forward (s : PrimitiveStep) :
    nextIndex s = s.index + 1 := by
  rfl

end Oasis.MoreGarbage01
