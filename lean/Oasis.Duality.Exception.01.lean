import Std

/-!
Oasis.Duality.Exception.01
==========================
Deterministic duality / exception engine.

Core rule:
  every primitive has at least four usable views:
    1. forward
    2. backward
    3. upside-down
    4. reserve (unchanged reference)

CEPT / Waldo rule:
* if exactly one Waldo is expected and exactly one is found -> MATCH
* if Waldo is expected and none is found -> MISSING
* if Waldo is not expected and exactly one is found -> UNEXPECTED
* if more than one is found -> SHADOW / multiplicity branch

Seed walk:
  -0.5, +0.25a, +0.25b, -0.5, repeat

Quarter-unit representation:
  -0.5  = -2
  +0.25 = +1
-/

namespace Oasis.Duality.Exception01

inductive View where
  | forward
  | backward
  | upsideDown
  | reserve
  deriving DecidableEq, BEq, Repr

def viewCount : Nat := 4

def applyView : View → List Int → List Int
  | .forward, xs => xs
  | .backward, xs => xs.reverse
  | .upsideDown, xs => xs.map Int.neg
  | .reserve, xs => xs

theorem four_views :
    viewCount = 4 := by
  rfl

theorem reserve_preserves (xs : List Int) :
    applyView .reserve xs = xs := by
  rfl

theorem backward_twice (xs : List Int) :
    applyView .backward (applyView .backward xs) = xs := by
  simp [applyView]

theorem upside_down_twice (xs : List Int) :
    applyView .upsideDown (applyView .upsideDown xs) = xs := by
  induction xs with
  | nil =>
      rfl
  | cons x xs ih =>
      simp [applyView, ih]

def quarterBit : Bool → Int
  | false => 0
  | true => 1

def seedWalk (a b : Bool) : List Int :=
  [-2, quarterBit a, quarterBit b, -2]

theorem seed_walk_tt :
    seedWalk true true = [-2, 1, 1, -2] := by
  rfl

theorem seed_walk_tf :
    seedWalk true false = [-2, 1, 0, -2] := by
  rfl

theorem seed_walk_ft :
    seedWalk false true = [-2, 0, 1, -2] := by
  rfl

theorem seed_walk_ff :
    seedWalk false false = [-2, 0, 0, -2] := by
  rfl

structure ABCheck where
  a : Bool
  b : Bool
  deriving DecidableEq, Repr

def checkAB (a b : Bool) : ABCheck :=
  { a := a, b := b }

theorem check_a_preserved (a b : Bool) :
    (checkAB a b).a = a := by
  rfl

theorem check_b_preserved (a b : Bool) :
    (checkAB a b).b = b := by
  rfl

def countTrue : List Bool → Nat
  | [] => 0
  | x :: xs => (if x then 1 else 0) + countTrue xs

inductive WaldoResult where
  | match
  | missingWaldo
  | unexpectedWaldo
  | shadowWaldo (count : Nat)
  deriving DecidableEq, BEq, Repr

def classifyWaldo (expected : Bool) (observations : List Bool) : WaldoResult :=
  let n := countTrue observations
  if n > 1 then
    .shadowWaldo n
  else if expected then
    if n == 1 then .match else .missingWaldo
  else
    if n == 0 then .match else .unexpectedWaldo

theorem expected_one_matches :
    classifyWaldo true [false, true, false] = .match := by
  decide

theorem expected_none_is_missing :
    classifyWaldo true [false, false, false] = .missingWaldo := by
  decide

theorem unexpected_one_reverses_question :
    classifyWaldo false [false, true, false] = .unexpectedWaldo := by
  decide

theorem two_waldos_are_shadow :
    classifyWaldo true [true, false, true] = .shadowWaldo 2 := by
  decide

theorem two_unexpected_waldos_are_shadow :
    classifyWaldo false [true, true, false] = .shadowWaldo 2 := by
  decide

theorem expected_clear_matches :
    classifyWaldo false [false, false, false] = .match := by
  decide

structure Perception where
  expectedWaldo : Bool
  observations : List Bool
  deriving DecidableEq, Repr

inductive IonAction where
  | proceed
  | investigateMissing
  | investigateUnexpected
  | splitShadow (count : Nat)
  deriving DecidableEq, BEq, Repr

def ion (p : Perception) : IonAction :=
  match classifyWaldo p.expectedWaldo p.observations with
  | .match => .proceed
  | .missingWaldo => .investigateMissing
  | .unexpectedWaldo => .investigateUnexpected
  | .shadowWaldo n => .splitShadow n

def sampleExpected : Perception :=
  { expectedWaldo := true, observations := [false, true, false] }

def sampleUnexpected : Perception :=
  { expectedWaldo := false, observations := [false, true, false] }

def sampleShadow : Perception :=
  { expectedWaldo := true, observations := [true, false, true] }

theorem ion_expected_proceeds :
    ion sampleExpected = .proceed := by
  decide

theorem ion_unexpected_investigates :
    ion sampleUnexpected = .investigateUnexpected := by
  decide

theorem ion_shadow_splits :
    ion sampleShadow = .splitShadow 2 := by
  decide

def dualityExceptionCheck : Bool :=
  (viewCount == 4) &&
  (seedWalk true true == [-2, 1, 1, -2]) &&
  (seedWalk true false == [-2, 1, 0, -2]) &&
  (classifyWaldo true [false, true, false] == .match) &&
  (classifyWaldo false [false, true, false] == .unexpectedWaldo) &&
  (classifyWaldo true [true, false, true] == .shadowWaldo 2) &&
  (ion sampleExpected == .proceed) &&
  (ion sampleUnexpected == .investigateUnexpected) &&
  (ion sampleShadow == .splitShadow 2)

theorem duality_exception_check_passes :
    dualityExceptionCheck = true := by
  decide

end Oasis.Duality.Exception01
