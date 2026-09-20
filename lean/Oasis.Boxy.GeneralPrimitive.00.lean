import Std

/-
Oasis.Boxy.GeneralPrimitive.00
===============================

General BOXy primitive.

Literal user relation:

  a 6 in a 4
  trying to be a 3
  while 2 = ?
  1 pushes
  0 is the total

This is relational notation, not ordinary arithmetic.
No Mandel / Juliet / mojibake semantics are required by the primitive;
those are applications of this more general BOXy relation.

Fresh candidate. Do not label 0e until user compiles it clean locally.
-/

namespace Oasis.Boxy.GeneralPrimitive00

structure BoxyPrimitive where
  inside : Nat
  box : Nat
  target : Nat
  query : Nat
  push : Nat
  total : Nat
  deriving Repr, DecidableEq

def boxy : BoxyPrimitive :=
  { inside := 6
    box := 4
    target := 3
    query := 2
    push := 1
    total := 0 }

theorem six_is_inside :
    boxy.inside = 6 := by
  rfl

theorem four_is_box :
    boxy.box = 4 := by
  rfl

theorem three_is_target :
    boxy.target = 3 := by
  rfl

theorem two_is_query :
    boxy.query = 2 := by
  rfl

theorem one_is_push :
    boxy.push = 1 := by
  rfl

theorem zero_is_total :
    boxy.total = 0 := by
  rfl

/-!
Compact symbolic read:

  6 ∈ BOX(4)
  6 ->? 3
  2 = ?
  1 = PUSH
  0 = TOTAL
-/

def literal : String :=
  "6 in 4 trying to be 3 while 2 ? 1 pushes and 0 is total"

theorem literal_exact :
    literal =
      "6 in 4 trying to be 3 while 2 ? 1 pushes and 0 is total" := by
  rfl

inductive Role where
  | inside
  | box
  | target
  | query
  | push
  | total
  deriving Repr, DecidableEq

def valueOf : Role → Nat
  | .inside => 6
  | .box => 4
  | .target => 3
  | .query => 2
  | .push => 1
  | .total => 0

theorem role_vector :
    [ valueOf .inside
    , valueOf .box
    , valueOf .target
    , valueOf .query
    , valueOf .push
    , valueOf .total
    ] = [6, 4, 3, 2, 1, 0] := by
  rfl

/-!
The primitive does not claim that 6 = 3.
It records that 6 is the current inside value and 3 is the target role.
-/
def trying : Nat × Nat :=
  (boxy.inside, boxy.target)

theorem trying_is_six_to_three :
    trying = (6, 3) := by
  rfl

/-!
2 remains the unresolved/query role.
-/
def unresolved : Nat := boxy.query

theorem unresolved_is_two :
    unresolved = 2 := by
  rfl

/-!
1 is the active push role.
-/
def activePush : Nat := boxy.push

theorem active_push_is_one :
    activePush = 1 := by
  rfl

/-!
0 closes the relation as TOTAL.
-/
def closure : Nat := boxy.total

theorem closure_is_zero :
    closure = 0 := by
  rfl

theorem boxy_general_contract :
    boxy.inside = 6 ∧
    boxy.box = 4 ∧
    boxy.target = 3 ∧
    boxy.query = 2 ∧
    boxy.push = 1 ∧
    boxy.total = 0 ∧
    trying = (6, 3) := by
  decide

end Oasis.Boxy.GeneralPrimitive00
