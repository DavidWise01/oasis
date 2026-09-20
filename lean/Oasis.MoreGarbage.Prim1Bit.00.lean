import Std

/-
Oasis.MoreGarbage.Prim1Bit.00
===============================

One-bit deletion primitive only.

No nibble, byte, word, sentence, file, sector, or device scaling is
introduced here. This module captures the user's one-bit walk exactly:

  click / trigger
    1  action: a is flagged for deletion
    2  flag a
    3  check flag 1
    4  check flag 2
    5  check flag 3
    6  check flag final
    7  overwrite := flag still true
    8  if overwrite, unbind and decohere

Primitive signature:

  [1, 1, 2, 4] . n . n^2

User-model local state space for this one bit:

  cohesion width     = 2^3 = 8
  states per bit     = 2^8 = 256
  lanes              = 16
  local search space = 16 * 256 = 4096

Fresh candidate. Do not label 0e until user compiles it clean locally.
-/

namespace Oasis.MoreGarbage.Prim1Bit00

/-! ## Primitive geometry / cost signature -/

def primShape : List Nat := [1, 1, 2, 4]

def cohesionWidth : Nat := 2 ^ 3

def statesPerBit : Nat := 2 ^ cohesionWidth

def laneCount : Nat := 16

def localSearchSpace : Nat := laneCount * statesPerBit

def linearCost (n : Nat) : Nat := n

def recursiveCost (n : Nat) : Nat := n ^ 2

def primSignature (n : Nat) : List Nat × Nat × Nat :=
  (primShape, linearCost n, recursiveCost n)

theorem prim_shape_exact :
    primShape = [1, 1, 2, 4] := by
  rfl

theorem prim_shape_sums_to_eight :
    primShape.sum = 8 := by
  decide

theorem cohesion_width_is_eight :
    cohesionWidth = 8 := by
  decide

theorem one_bit_state_space_is_256 :
    statesPerBit = 256 := by
  decide

theorem lane_count_is_16 :
    laneCount = 16 := by
  rfl

theorem local_search_space_is_4096 :
    localSearchSpace = 4096 := by
  decide

theorem signature_exact (n : Nat) :
    primSignature n = ([1, 1, 2, 4], n, n ^ 2) := by
  rfl

/-! ## Eight ticks -/

inductive Tick where
  | t1_flagForDeletion
  | t2_flagA
  | t3_checkFlag1
  | t4_checkFlag2
  | t5_checkFlag3
  | t6_checkFlagFinal
  | t7_overwriteDecision
  | t8_unbindDecohere
  deriving Repr, DecidableEq

def tickNumber : Tick → Nat
  | .t1_flagForDeletion => 1
  | .t2_flagA => 2
  | .t3_checkFlag1 => 3
  | .t4_checkFlag2 => 4
  | .t5_checkFlag3 => 5
  | .t6_checkFlagFinal => 6
  | .t7_overwriteDecision => 7
  | .t8_unbindDecohere => 8

def schedule : List Tick :=
  [ .t1_flagForDeletion
  , .t2_flagA
  , .t3_checkFlag1
  , .t4_checkFlag2
  , .t5_checkFlag3
  , .t6_checkFlagFinal
  , .t7_overwriteDecision
  , .t8_unbindDecohere
  ]

theorem schedule_has_eight_ticks :
    schedule.length = 8 := by
  decide

theorem schedule_numbers_exact :
    schedule.map tickNumber = [1, 2, 3, 4, 5, 6, 7, 8] := by
  decide

/-! ## One primitive: a -/

def primA : String := "a"

structure Checks where
  flag1 : Bool
  flag2 : Bool
  flag3 : Bool
  flagFinal : Bool
  deriving Repr, DecidableEq

def allChecksTrue : Checks :=
  { flag1 := true
    flag2 := true
    flag3 := true
    flagFinal := true }

def flagSurvives (c : Checks) : Bool :=
  ((c.flag1 && c.flag2) && c.flag3) && c.flagFinal

structure PrimState where
  value : Option String
  deleteFlag : Bool
  overwrite : Bool
  bound : Bool
  coherent : Bool
  tick : Nat
  deriving Repr, DecidableEq

def initial : PrimState :=
  { value := some primA
    deleteFlag := false
    overwrite := false
    bound := true
    coherent := true
    tick := 0 }

/-
A check input models whether the deletion flag is still present when that
specific check occurs. Once the flag is false, later checks cannot revive it.
-/
def step (c : Checks) : Tick → PrimState → PrimState
  | .t1_flagForDeletion, s =>
      { s with tick := 1, deleteFlag := true }
  | .t2_flagA, s =>
      { s with tick := 2, deleteFlag := s.deleteFlag }
  | .t3_checkFlag1, s =>
      { s with tick := 3, deleteFlag := s.deleteFlag && c.flag1 }
  | .t4_checkFlag2, s =>
      { s with tick := 4, deleteFlag := s.deleteFlag && c.flag2 }
  | .t5_checkFlag3, s =>
      { s with tick := 5, deleteFlag := s.deleteFlag && c.flag3 }
  | .t6_checkFlagFinal, s =>
      { s with tick := 6, deleteFlag := s.deleteFlag && c.flagFinal }
  | .t7_overwriteDecision, s =>
      { s with tick := 7, overwrite := s.deleteFlag }
  | .t8_unbindDecohere, s =>
      match s.overwrite with
      | true =>
          { s with
              tick := 8
              value := none
              bound := false
              coherent := false }
      | false =>
          { s with tick := 8 }

def run (c : Checks) : PrimState :=
  let s1 := step c .t1_flagForDeletion initial
  let s2 := step c .t2_flagA s1
  let s3 := step c .t3_checkFlag1 s2
  let s4 := step c .t4_checkFlag2 s3
  let s5 := step c .t5_checkFlag3 s4
  let s6 := step c .t6_checkFlagFinal s5
  let s7 := step c .t7_overwriteDecision s6
  step c .t8_unbindDecohere s7

def render (s : PrimState) : String :=
  match s.value with
  | some v => v
  | none => "?"

/-! ## Core deletion proofs -/

theorem overwrite_exactly_tracks_surviving_flag (c : Checks) :
    (run c).overwrite = flagSurvives c := by
  cases c with
  | mk f1 f2 f3 fFinal =>
      cases f1 <;> cases f2 <;> cases f3 <;> cases fFinal <;> decide

theorem all_true_overwrites :
    (run allChecksTrue).overwrite = true := by
  decide

theorem all_true_unbinds :
    (run allChecksTrue).bound = false := by
  decide

theorem all_true_decoheres :
    (run allChecksTrue).coherent = false := by
  decide

theorem all_true_deletes_a :
    (run allChecksTrue).value = none := by
  decide

theorem all_true_reaches_tick_eight :
    (run allChecksTrue).tick = 8 := by
  decide

theorem a_becomes_question_after_committed_delete :
    render (run allChecksTrue) = "?" := by
  decide

/-! ## A cleared flag prevents overwrite -/

def cancelAt1 : Checks :=
  { flag1 := false, flag2 := true, flag3 := true, flagFinal := true }

def cancelAt2 : Checks :=
  { flag1 := true, flag2 := false, flag3 := true, flagFinal := true }

def cancelAt3 : Checks :=
  { flag1 := true, flag2 := true, flag3 := false, flagFinal := true }

def cancelAtFinal : Checks :=
  { flag1 := true, flag2 := true, flag3 := true, flagFinal := false }

theorem cancel_at_1_no_overwrite :
    (run cancelAt1).overwrite = false := by
  decide

theorem cancel_at_2_no_overwrite :
    (run cancelAt2).overwrite = false := by
  decide

theorem cancel_at_3_no_overwrite :
    (run cancelAt3).overwrite = false := by
  decide

theorem cancel_at_final_no_overwrite :
    (run cancelAtFinal).overwrite = false := by
  decide

theorem cancel_at_1_preserves_a :
    render (run cancelAt1) = "a" := by
  decide

theorem cancel_at_2_preserves_a :
    render (run cancelAt2) = "a" := by
  decide

theorem cancel_at_3_preserves_a :
    render (run cancelAt3) = "a" := by
  decide

theorem cancel_at_final_preserves_a :
    render (run cancelAtFinal) = "a" := by
  decide

/-! ## Exhaustive one-bit flag space -/

/-
Four boolean flag checks give 2^4 = 16 check vectors.
Exactly one vector is all-true and reaches overwrite=true.
The other fifteen do not overwrite.
-/
def bools : List Bool := [false, true]

def allCheckVectors : List Checks :=
  bools.flatMap fun a =>
    bools.flatMap fun b =>
      bools.flatMap fun c =>
        bools.map fun d =>
          { flag1 := a, flag2 := b, flag3 := c, flagFinal := d }

def committedCount : Nat :=
  (allCheckVectors.filter fun c => (run c).overwrite).length

def cancelledCount : Nat :=
  (allCheckVectors.filter fun c => !(run c).overwrite).length

theorem check_vector_count_is_16 :
    allCheckVectors.length = 16 := by
  decide

theorem exactly_one_vector_commits :
    committedCount = 1 := by
  decide

theorem fifteen_vectors_cancel :
    cancelledCount = 15 := by
  decide

/-! ## Canonical one-bit primitive statement -/

theorem prim_one_bit_delete_contract :
    primShape = [1, 1, 2, 4] ∧
    cohesionWidth = 8 ∧
    statesPerBit = 256 ∧
    laneCount = 16 ∧
    localSearchSpace = 4096 ∧
    (run allChecksTrue).overwrite = true ∧
    (run allChecksTrue).bound = false ∧
    (run allChecksTrue).coherent = false ∧
    render (run allChecksTrue) = "?" := by
  decide

end Oasis.MoreGarbage.Prim1Bit00
